"""
Lycheetah Framework — GitHub API Poster
========================================
Posts directly to GitHub Discussions, Issues, and Releases via the GraphQL/REST API.
No gh CLI required. Requires a GitHub Personal Access Token (PAT).

Token setup (one-time):
  Set env var:  GITHUB_TOKEN=ghp_yourtoken
  Or pass:      python github_post.py --token ghp_yourtoken ...

Token needs scopes: public_repo (for issues/releases), discussions:write

Usage:
  python github_post.py discussion --title "..." --body "..."
  python github_post.py discussion --from-promote       # auto-generates body from promote.py
  python github_post.py issue --title "..." --body "..."
  python github_post.py list-categories                  # show available discussion categories
  python github_post.py list-discussions                 # show recent discussions

Author: Mackenzie Clark / Sol Aureum Azoth Veritas
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

REPO_OWNER = "Lycheetah"
REPO_NAME  = "Lycheetah-Framework"
REPO_ROOT  = Path(__file__).parent

API_REST    = "https://api.github.com"
API_GRAPHQL = "https://api.github.com/graphql"


# =============================================================================
# HTTP helpers — stdlib only, no requests dependency
# =============================================================================

def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def graphql(token: str, query: str, variables: dict | None = None) -> dict:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(API_GRAPHQL, data=payload, headers=_headers(token))
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    if "errors" in data:
        for err in data["errors"]:
            print(f"GraphQL error: {err.get('message')}", file=sys.stderr)
        sys.exit(1)
    return data["data"]


def rest(token: str, method: str, path: str, payload: dict | None = None) -> dict:
    url = f"{API_REST}{path}"
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers(token))
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


# =============================================================================
# GitHub API operations
# =============================================================================

def get_repo_id(token: str) -> str:
    data = graphql(token, """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) { id }
        }
    """, {"owner": REPO_OWNER, "name": REPO_NAME})
    return data["repository"]["id"]


def list_discussion_categories(token: str) -> list[dict]:
    data = graphql(token, """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            discussionCategories(first: 20) {
              nodes { id name slug }
            }
          }
        }
    """, {"owner": REPO_OWNER, "name": REPO_NAME})
    return data["repository"]["discussionCategories"]["nodes"]


def create_discussion(token: str, title: str, body: str,
                      category_slug: str = "announcements") -> dict:
    repo_id = get_repo_id(token)
    categories = list_discussion_categories(token)

    # Find matching category (case-insensitive slug or name match)
    cat = next(
        (c for c in categories
         if c["slug"].lower() == category_slug.lower()
         or c["name"].lower() == category_slug.lower()),
        None
    )
    if cat is None:
        available = ", ".join(c["slug"] for c in categories)
        print(f"Category '{category_slug}' not found. Available: {available}", file=sys.stderr)
        sys.exit(1)

    data = graphql(token, """
        mutation($repoId: ID!, $catId: ID!, $title: String!, $body: String!) {
          createDiscussion(input: {
            repositoryId: $repoId,
            categoryId: $catId,
            title: $title,
            body: $body
          }) {
            discussion { url number }
          }
        }
    """, {
        "repoId": repo_id,
        "catId":  cat["id"],
        "title":  title,
        "body":   body,
    })
    return data["createDiscussion"]["discussion"]


def list_discussions(token: str, count: int = 5) -> list[dict]:
    data = graphql(token, """
        query($owner: String!, $name: String!, $count: Int!) {
          repository(owner: $owner, name: $name) {
            discussions(first: $count, orderBy: {field: CREATED_AT, direction: DESC}) {
              nodes { number title url createdAt }
            }
          }
        }
    """, {"owner": REPO_OWNER, "name": REPO_NAME, "count": count})
    return data["repository"]["discussions"]["nodes"]


def pin_discussion(token: str, discussion_number: int) -> bool:
    """Pin a discussion to the top of the Discussions page."""
    # Get discussion node ID
    data = graphql(token, """
        query($owner: String!, $name: String!, $num: Int!) {
          repository(owner: $owner, name: $name) {
            discussion(number: $num) { id }
          }
        }
    """, {"owner": REPO_OWNER, "name": REPO_NAME, "num": discussion_number})
    disc_id = data["repository"]["discussion"]["id"]

    result = graphql(token, """
        mutation PinDiscussion($id: ID!) {
          pinDiscussion(input: { discussionId: $id }) {
            pinnedDiscussion { pinnedAt }
          }
        }
    """, {"id": disc_id})
    return bool(result.get("pinDiscussion"))


def create_issue(token: str, title: str, body: str,
                 labels: list[str] | None = None) -> dict:
    payload: dict = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels
    return rest(token, "POST",
                f"/repos/{REPO_OWNER}/{REPO_NAME}/issues", payload)


def update_discussion(token: str, discussion_number: int,
                      title: str | None = None, body: str | None = None) -> dict:
    # Get discussion node ID first
    data = graphql(token, """
        query($owner: String!, $name: String!, $num: Int!) {
          repository(owner: $owner, name: $name) {
            discussion(number: $num) { id title body }
          }
        }
    """, {"owner": REPO_OWNER, "name": REPO_NAME, "num": discussion_number})
    node = data["repository"]["discussion"]
    disc_id = node["id"]

    updated = graphql(token, """
        mutation($id: ID!, $title: String, $body: String) {
          updateDiscussion(input: { discussionId: $id, title: $title, body: $body }) {
            discussion { url number }
          }
        }
    """, {
        "id":    disc_id,
        "title": title or node["title"],
        "body":  body  or node["body"],
    })
    return updated["updateDiscussion"]["discussion"]


# =============================================================================
# Promote.py integration — pull body from the generator
# =============================================================================

def body_from_promote(platform: str = "gh-discussion") -> tuple[str, str]:
    """Import promote.py directly and extract title + body for the given platform."""
    import importlib.util, types

    spec = importlib.util.spec_from_file_location("promote", REPO_ROOT / "promote.py")
    mod = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(mod)  # type: ignore

    repo = mod.RepoState()
    state = repo.summary()
    gen = mod.ContentGenerator(state)

    # Map platform slug to method
    method_map = {
        "gh-discussion": "github_discussion",
        "github_discussion": "github_discussion",
        "x": "x_thread",
        "hn": "hacker_news",
        "reddit": "reddit",
        "discord": "discord",
    }
    method_name = method_map.get(platform, "github_discussion")
    raw = getattr(gen, method_name)()

    # raw starts with "== GITHUB DISCUSSION DRAFT ==\nTitle: ...\nCategory: ...\n---\n..."
    lines = raw.splitlines()
    title = ""
    body_lines = []
    past_title = False

    for line in lines:
        if line.startswith("== "):
            continue
        if line.startswith("Title:"):
            title = line.replace("Title:", "").strip()
            past_title = True
            continue
        if past_title and (line.startswith("Category:") or line.strip() == "---"):
            continue
        if past_title:
            body_lines.append(line)

    # Drop leading blank lines
    while body_lines and body_lines[0].strip() == "":
        body_lines.pop(0)

    body = "\n".join(body_lines).strip()
    return title, body


# =============================================================================
# CLI
# =============================================================================

def get_token(args_token: str | None) -> str:
    token = args_token or os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(
            "No GitHub token found.\n"
            "Set env var GITHUB_TOKEN=ghp_... or pass --token ghp_...\n"
            "Create a PAT at: https://github.com/settings/tokens\n"
            "Required scopes: public_repo, discussions:write",
            file=sys.stderr
        )
        sys.exit(1)
    return token


def main():
    parser = argparse.ArgumentParser(description="GitHub API poster for Lycheetah Framework")
    parser.add_argument("--token", help="GitHub PAT (or set GITHUB_TOKEN env var)")

    sub = parser.add_subparsers(dest="command")

    # --- discussion ---
    disc = sub.add_parser("discussion", help="Create a GitHub Discussion")
    disc.add_argument("--title", help="Discussion title")
    disc.add_argument("--body",  help="Discussion body (Markdown)")
    disc.add_argument("--body-file", help="Read body from a file")
    disc.add_argument("--category", default="announcements",
                      help="Discussion category slug (default: announcements)")
    disc.add_argument("--from-promote", action="store_true",
                      help="Auto-generate title+body from promote.py")
    disc.add_argument("--dry-run", action="store_true",
                      help="Print what would be posted without posting")

    # --- update-discussion ---
    upd = sub.add_parser("update-discussion", help="Edit an existing Discussion")
    upd.add_argument("number", type=int, help="Discussion number")
    upd.add_argument("--title", help="New title (optional)")
    upd.add_argument("--body",  help="New body (optional)")
    upd.add_argument("--body-file", help="Read body from a file")

    # --- issue ---
    iss = sub.add_parser("issue", help="Create a GitHub Issue")
    iss.add_argument("--title", required=True)
    iss.add_argument("--body",  default="")
    iss.add_argument("--body-file", help="Read body from a file")
    iss.add_argument("--label", action="append", dest="labels", help="Label name(s)")

    # --- pin ---
    pin = sub.add_parser("pin", help="Pin a Discussion to the top of the Discussions page")
    pin.add_argument("number", type=int, help="Discussion number to pin")

    # --- list-categories ---
    sub.add_parser("list-categories", help="List available Discussion categories")

    # --- list-discussions ---
    ld = sub.add_parser("list-discussions", help="List recent Discussions")
    ld.add_argument("--count", type=int, default=10)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Dry run and content generation don't need a token
    dry = getattr(args, "dry_run", False)
    token = get_token(args.token) if not dry else (args.token or os.environ.get("GITHUB_TOKEN", "dummy"))

    # ---- pin ----
    if args.command == "pin":
        ok = pin_discussion(token, args.number)
        if ok:
            print(f"Discussion #{args.number} pinned.")
        else:
            print(f"Pin request sent for #{args.number} (check GitHub to confirm).")
        return

    # ---- list-categories ----
    if args.command == "list-categories":
        cats = list_discussion_categories(token)
        print(f"Discussion categories for {REPO_OWNER}/{REPO_NAME}:")
        for c in cats:
            print(f"  {c['slug']:30s}  {c['name']}")
        return

    # ---- list-discussions ----
    if args.command == "list-discussions":
        discs = list_discussions(token, args.count)
        print(f"Recent discussions in {REPO_OWNER}/{REPO_NAME}:")
        for d in discs:
            print(f"  #{d['number']:4d}  {d['title'][:60]}  {d['createdAt'][:10]}")
            print(f"         {d['url']}")
        return

    # ---- discussion ----
    if args.command == "discussion":
        if args.from_promote:
            title, body = body_from_promote("gh-discussion")
            print(f"Generated title: {title}")
        else:
            title = args.title or ""
            body  = args.body or ""

        if args.body_file:
            body = Path(args.body_file).read_text(encoding="utf-8")

        if not title:
            print("Error: --title is required (or use --from-promote)", file=sys.stderr)
            sys.exit(1)

        if args.dry_run:
            print(f"\n[DRY RUN] Would post discussion:")
            print(f"  Title:    {title}")
            print(f"  Category: {args.category}")
            print(f"  Body ({len(body)} chars):\n")
            print(body[:800] + ("..." if len(body) > 800 else ""))
            return

        disc = create_discussion(token, title, body, args.category)
        print(f"Discussion created: #{disc['number']}")
        print(f"URL: {disc['url']}")
        return

    # ---- update-discussion ----
    if args.command == "update-discussion":
        body = args.body
        if args.body_file:
            body = Path(args.body_file).read_text(encoding="utf-8")
        result = update_discussion(token, args.number, args.title, body)
        print(f"Discussion #{result['number']} updated.")
        print(f"URL: {result['url']}")
        return

    # ---- issue ----
    if args.command == "issue":
        body = args.body
        if args.body_file:
            body = Path(args.body_file).read_text(encoding="utf-8")
        iss = create_issue(token, args.title, body, args.labels)
        print(f"Issue created: #{iss['number']}")
        print(f"URL: {iss['html_url']}")
        return


if __name__ == "__main__":
    main()
