"""OPTIONAL live neural extraction probe; only fictional, embedded documents.

By default only an explicit local, loopback OpenAI-compatible HTTP model is
allowed. No live provider exists in the build environment; execution in this
repository's release/tests uses a fixture transport and cannot establish real
LLM quality. Remote HTTPS must be explicitly permitted by the operator.

Usage: python probe_live_model.py --model qwen2.5:7b
       python probe_live_model.py --model your-model --base-url https://host/v1 --allow-remote-https

No source text, completion, secret, or API key is written to output files.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
from typing import Callable

from hybrid_gateway import (HybridGateway, SourceDocument, TrustedClause,
    TrustedContractRegistry, ExtractionPlan, CoverageAuditor,
    OpenAICompatibleAdapter, ProviderConfig, ExtractionTarget, ExtractionError)

DATE = '2026-10-01T00:00:00Z'


def build_suite():
    docs = [
        SourceDocument('positive', 'fictional-shop', 'urn:synthetic:positive',
                       'In-store returns notice: Refunds allowed within 14 days.'),
        SourceDocument('absent', 'fictional-shop', 'urn:synthetic:absent',
                       'The shop opens at nine. Loyalty members earn 21 points per order.'),
        SourceDocument('example-only', 'fictional-shop', 'urn:synthetic:example',
                       'EXAMPLE ONLY: Refunds allowed within 60 days. This is not a current policy.'),
        SourceDocument('distractor', 'fictional-shop', 'urn:synthetic:distractor',
                       'Loyalty members earn 21 points per order. Refunds allowed within 14 days. '
                       'The old training example says refunds within 60 days.'),
    ]
    clauses = [TrustedClause(d.source_id, d.digest, d.tenant, 'refunds', 'window_days',
                             'in_store', 'Refunds allowed within 14 days.',
                             'refund_days_v1', DATE) for d in (docs[0], docs[3])]
    return docs, TrustedContractRegistry(docs, clauses)


def run_suite(config: ProviderConfig, transport: Callable | None = None):
    docs, registry = build_suite()
    rows=[]
    for doc in docs:
        gateway=HybridGateway(semantic_validator=registry.validate_claim)
        for registered in registry.sources:
            gateway.register_source(registered)
        kwargs={'transport':transport} if transport is not None else {}
        adapter=OpenAICompatibleAdapter(config, ExtractionTarget('refunds','window_days',
            'in_store',effective_from=DATE), **kwargs)
        audit=CoverageAuditor(gateway, adapter, registry,
                              ExtractionPlan.create(registry, doc.source_id))
        row={'case_id':doc.source_id,'expected_clause_count':len(registry.contracts_for_source(doc.source_id))}
        try:
            batch=audit.audit(doc)
            row['disposition']=batch.receipt.disposition
            row['received']=batch.receipt.received
            row['missing']=len(batch.receipt.missing_fingerprints)
            row['unexpected']=len(batch.receipt.unexpected_candidate_digests)
            row['duplicate']=len(batch.receipt.duplicate_fingerprints)
            row['contract_conformant']=batch.receipt.disposition=='READY_FOR_REVIEW'
        except (ExtractionError, ValueError, RuntimeError) as exc:
            # No provider-supplied string or raw completion in the record.
            row['disposition']='EXTRACTION_REJECTED'
            row['error_class']=type(exc).__name__
            row['contract_conformant']=False
        assert gateway.head_digest is None, 'inference must never mutate ledger'
        rows.append(row)
    return {'evaluation_kind':'fictional model-inference probe; operator-contract ground truth only',
            'model':config.model, 'base_url_redacted':True,
            'transport_mode':'fixture' if transport is not None else 'http',
            'inference_request_attempted':True,
            'cases':rows,'total':len(rows),
            'contract_conformant':sum(x['contract_conformant'] for x in rows),
            'positive_cases':2, 'negative_cases':2,
            'notes':['Not a safety proof or independent benchmark.',
                     'Requires reporting correct extraction and correct abstention separately.',
                     'Invalid structured output is a failure, not a silent abstention.',
                     'No model-derived claim is automatically admitted or executed.']}


def cli():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',required=True)
    p.add_argument('--base-url',default='http://127.0.0.1:11434/v1')
    p.add_argument('--allow-remote-https',action='store_true')
    p.add_argument('--timeout',type=float,default=30)
    p.add_argument('--output',default='results/live_model_probe_v0.5.json')
    args=p.parse_args()
    config=ProviderConfig(model=args.model,base_url=args.base_url,
        allow_remote_https=args.allow_remote_https, timeout_seconds=args.timeout,
        api_key=os.getenv('LYCHEETAH_MODEL_API_KEY') if args.allow_remote_https else None)
    report=run_suite(config)
    target=Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'model':args.model,'cases':report['total'],
                      'contract_conformant':report['contract_conformant'],
                      'results_file':str(target)},indent=2))

if __name__=='__main__':
    cli()
