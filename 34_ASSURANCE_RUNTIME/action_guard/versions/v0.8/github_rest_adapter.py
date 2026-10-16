"""Strict GitHub merge-request builder used for dry-run and mocked transport tests.

No network transport is provided here and no live GitHub requests are sent. The request
shape matches GitHub's documented merge endpoint; expected head SHA is passed as `sha`.
GitHub does not expose an equivalent atomic expected-base-SHA condition on this endpoint.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HTTPRequestPreview:
    method: str
    url: str
    headers: dict[str, str]
    json_body: dict[str, Any]


def build_merge_request(action: dict[str, Any], *, api_version: str = "2026-03-10") -> HTTPRequestPreview:
    required = {"tool", "repo", "pull_request", "head_sha", "base_sha", "merge_method"}
    if not isinstance(action, dict) or not required.issubset(action):
        raise ValueError("action_missing_required_field")
    if action["tool"] != "github.merge":
        raise ValueError("unsupported_tool")
    repo = action["repo"]
    if not isinstance(repo, str) or repo.count("/") != 1:
        raise ValueError("repo_must_be_owner_slash_name")
    owner, name = repo.split("/")
    for part in (owner, name):
        if (not part or part in (".", "..") or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-" for ch in part)):
            raise ValueError("invalid_repo_component")
    pr = action["pull_request"]
    if isinstance(pr, bool) or not isinstance(pr, int) or pr < 1:
        raise ValueError("invalid_pull_request_number")
    for field in ("head_sha", "base_sha"):
        val = action[field]
        if not isinstance(val, str) or not val or any(ch not in "0123456789abcdefABCDEF" for ch in val):
            raise ValueError("invalid_" + field)
    merge_method = action["merge_method"]
    if merge_method not in ("merge", "squash", "rebase"):
        raise ValueError("invalid_merge_method")
    # The endpoint only supports an expected head SHA. We preserve base_sha in the
    # signed approval/intent but do not pretend GitHub atomically enforces it here.
    return HTTPRequestPreview(
        method="PUT",
        url=f"https://api.github.com/repos/{owner}/{name}/pulls/{pr}/merge",
        headers={"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": api_version},
        json_body={"sha": action["head_sha"], "merge_method": merge_method},
    )


def dry_run_merge(action: dict[str, Any]) -> dict[str, Any]:
    """Return a request preview without credentials, HTTP transport, or side effects."""
    request = build_merge_request(action)
    return {"status": "DRY_RUN_ONLY", "side_effect_performed": False,
            "request": {"method": request.method, "url": request.url,
                        "headers": request.headers, "json_body": request.json_body},
            "notes": ["No HTTP call was made.",
                      "Expected head SHA is sent to GitHub's documented merge endpoint.",
                      "Base SHA remains approval metadata; this endpoint has no expected-base-SHA parameter."]}
