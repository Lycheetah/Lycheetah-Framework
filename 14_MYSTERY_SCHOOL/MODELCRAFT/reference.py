"""Local reference contracts. No model calls, persistence or app integration."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from functools import lru_cache
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker

HOME = Path(__file__).resolve().parent
POLICY = json.loads((HOME / 'data/policy.json').read_text())


def date(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00').replace('z', '+00:00'))


FORMATS = FormatChecker()


@FORMATS.checks('date-time', raises=ValueError)
def timestamp(value):
    """Check timestamps even without jsonschema's optional format packages."""
    if not isinstance(value, str):
        return True  # The schema's type constraint handles other values.
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})', value):
        return False
    return date(value).tzinfo is not None


@lru_cache(maxsize=None)
def validator(name):
    schema = json.loads((HOME / 'schemas' / (name + '.schema.json')).read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FORMATS)


def errors(name, payload, now=None):
    """Shape checks plus local consistency; evidence is not authenticated."""
    now = now or datetime.now(timezone.utc)
    found = [e.message for e in validator(name).iter_errors(payload)]
    if found:
        return found
    if name == 'ranking-request':
        budget = payload['budget']
        if budget['kind'] == 'ZERO' and (budget['max_amount'] != 0 or budget['currency'] is not None):
            found.append('ZERO budget requires amount 0 and no currency.')
        if budget['kind'] == 'LIMITED' and (budget['max_amount'] is None or budget['max_amount'] <= 0 or not re.fullmatch('[A-Z]{3}', budget['currency'] or '')):
            found.append('LIMITED budget requires a positive amount and explicit currency.')
        if budget['kind'] == 'UNSPECIFIED' and (budget['max_amount'] is not None or budget['currency'] is not None):
            found.append('UNSPECIFIED budget cannot carry an inferred amount or currency.')
    if name == 'recommendation':
        cost = payload['cost']
        if cost['verified_at'] and date(cost['verified_at']) > now:
            found.append('A future timestamp is not a completed cost verification.')
    if name == 'recommendation-event' and date(payload['recorded_at']) > now:
        found.append('An event cannot be recorded in the future.')
    if name != 'trick':
        return found
    runs = payload['reproductions']
    if len({r['run_id'] for r in runs}) != len(runs):
        found.append('Duplicate run IDs cannot increase reproduction counts.')
    supported = [r for r in runs if r['result'] == 'SUPPORT']
    count = len({r['run_id'] for r in supported})
    if payload['reproduction_count'] != count:
        found.append('Reproduction count must equal unique supporting runs.')
    maturity = payload['maturity']
    needed = {'HYPOTHESIS': 0, 'REPRODUCED_ONCE': 1, 'REPRODUCED_MULTI_RUN': 2, 'REPRODUCED_MULTI_USER': 2}[maturity]
    if count < needed:
        found.append('Promotion requires the declared number of supporting runs.')
    if maturity == 'REPRODUCED_MULTI_USER' and len({r['runner_id'] for r in supported}) < 2:
        found.append('MULTI_USER requires distinct runner IDs; their independence remains unverified.')
    if payload['applicability'] == 'CROSS_MODEL' and len({r['model_family'] for r in supported}) < 2:
        found.append('CROSS_MODEL requires supporting records from distinct model families.')
    if payload['lifecycle'] == 'FAILED_REPLICATION' and not any(r['result'] == 'FAIL' for r in runs):
        found.append('FAILED_REPLICATION requires a failure record.')
    if not runs:
        if payload['freshness'] != 'UNTESTED' or payload['last_tested_at'] is not None or payload['stale_after'] is not None or payload['observed_effect'] is not None:
            found.append('Untested items cannot claim dated observations or current evidence.')
        return found
    if payload['freshness'] == 'UNTESTED' or payload['observed_effect'] is None:
        found.append('A tested item needs a visible observation and dated freshness state.')
    if any(date(r['tested_at']) > now for r in runs):
        found.append('Future tests cannot count as completed runs.')
    if payload['last_tested_at'] is None or date(payload['last_tested_at']) != max(date(r['tested_at']) for r in runs):
        found.append('Last-tested timestamp must match the newest run, including failures.')
    if payload['stale_after'] is None:
        found.append('Tested items require an explicit review deadline.')
    elif payload['last_tested_at'] and date(payload['stale_after']) <= date(payload['last_tested_at']):
        found.append('Review deadline must follow the latest test.')
    elif payload['freshness'] == 'CURRENT' and date(payload['stale_after']) <= now:
        found.append('Expired evidence must not be labelled CURRENT.')
    for run in runs:
        if (run['baseline_cost'] is not None or run['technique_cost'] is not None) and not re.fullmatch('[A-Z]{3}', run['currency'] or ''):
            found.append('Measured costs require an explicit currency.')
    return found


def require(name, payload, now):
    problems = errors(name, payload, now)
    if problems:
        raise ValueError(name + ': ' + '; '.join(problems))


def rank(candidates, request, now=None, limit=5):
    """Return up to five suggestions from explicit input; no logs or storage."""
    now = now or datetime.now(timezone.utc)
    require('ranking-request', request, now)
    if type(limit) is not int or not 1 <= limit <= POLICY['maximum_results']:
        raise ValueError('Result limit must be an integer from 1 to 5.')
    ids = set()
    for item in candidates:
        require('recommendation', item, now)
        if item['id'] in ids:
            raise ValueError('Duplicate recommendation IDs are ambiguous.')
        ids.add(item['id'])
    result = []
    for item in candidates:
        matched_goals = sorted(set(item['goal_ids']) & set(request['goal_ids']))
        if not matched_goals:
            continue
        if not set(item['requires_tools']) <= set(request['tool_ids']):
            continue
        if not set(item['prerequisites']) <= set(request['completed_prerequisites']):
            continue
        if item['type'] == 'CONTINUE' and item['project_ref'] not in request['unfinished_project_ids']:
            continue
        if item['expires_at'] and date(item['expires_at']) <= now:
            continue
        cost = item['cost']
        if cost['kind'] in {'FREE_TIER', 'PAID'} and now - date(cost['verified_at']) >= timedelta(days=POLICY['cost_freshness_days']):
            continue
        budget = request['budget']
        if budget['kind'] == 'ZERO' and cost['kind'] not in {'ZERO', 'FREE_TIER'}:
            continue
        if budget['kind'] == 'LIMITED':
            if cost['kind'] == 'UNKNOWN':
                continue
            if cost['kind'] == 'PAID' and (cost['currency'] != budget['currency'] or cost['amount'] > budget['max_amount']):
                continue
        matches = sorted(set(item['task_tags']) & set(request['task_tags']))
        same_difficulty = item['difficulty'] == request['difficulty']
        weights = POLICY['weights']
        components = {'explicit_goal': weights['explicit_goal'] * len(matched_goals),
                      'task_match': weights['task_match'] * len(matches),
                      'difficulty_match': weights['difficulty_match'] * int(same_difficulty)}
        reasons = ['EXPLICIT_GOAL_MATCH']
        if matches:
            reasons.append('TASK_MATCH')
        if same_difficulty:
            reasons.append('DIFFICULTY_MATCH')
        if cost['kind'] in {'ZERO', 'FREE_TIER'}:
            reasons.append('ZERO_COST_ROUTE')
        if cost['kind'] == 'UNKNOWN':
            reasons.append('COST_UNKNOWN')
        if item['type'] == 'CONTINUE':
            reasons.append('EXPLICIT_UNFINISHED_WORK')
        shown = deepcopy(item)
        shown.update(score=sum(components.values()), score_components=components,
                     ranking_version=POLICY['ranking_version'], ranking_reason_codes=reasons,
                     matched_goal_ids=matched_goals, matched_task_tags=matches,
                     why_this='You selected ' + ', '.join(matched_goals) + '. ' + item['why_this'])
        result.append(shown)
    return sorted(result, key=lambda r: (-r['score'], r['id']))[:limit]


if __name__ == '__main__':
    catalogue = json.loads((HOME / 'data/recommendations.json').read_text())
    request = json.loads((HOME / 'examples/ranking-request.json').read_text())
    print(json.dumps(rank(catalogue['recommendations'], request), ensure_ascii=False, indent=2))
