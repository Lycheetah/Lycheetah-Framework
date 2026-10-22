# Security policy

## Reporting a vulnerability

Report privately. Do not open a public issue for anything exploitable.

> **Review note, 2026-10-22 (RV35): neither route below works today.**
> Private vulnerability reporting is switched **off** for this repository (the GitHub
> API reports `enabled: false`), so the advisory link does not open a private
> thread. The domain `lycheetah.nz` has no DNS record (NXDOMAIN), so mail to the
> address below cannot be delivered. Both were checked on this date. Until the owner
> enables private vulnerability reporting and names a working address, there is no
> private channel. Do **not** fall back to a public issue with exploit detail: open a
> public issue that says only "security contact needed", and we will reach you.

- **Preferred:** [open a private security advisory](https://github.com/Lycheetah/Lycheetah-Framework/security/advisories/new)
  on the repository. This gives us a private thread and a CVE path if one is warranted.
- **Alternative:** email **mac@lycheetah.nz** with `SECURITY` in the subject.

Please include what you need to make the problem reproducible: affected version or
commit, platform and Python version, the steps, and what an attacker gets out of it.
A proof of concept helps and is welcome; a description of impact without one is still
worth sending.

### What to expect

We are a small project and will not pretend to an enterprise rota. What we commit to:

| Stage | Target |
|---|---|
| Acknowledgement that a human has read it | 5 working days |
| Initial assessment, severity, and a plan | 15 working days |
| Fix or documented mitigation for a confirmed high-severity issue | 90 days from acknowledgement |

If a deadline is going to slip you will be told, with a reason, before it does. If you
get no acknowledgement inside 10 working days, assume the mail went astray and open a
private advisory instead.

We will credit you in the advisory and `CHANGELOG.md` unless you would rather stay
anonymous. We will not take legal action over good-faith research that follows this
policy.

## Supported versions

| Version | Supported |
|---|---|
| `master` (and the latest tagged release) | yes |
| earlier tags | no — please reproduce against `master` first |

## Scope

In scope — the code in this repository:

- the `lycheetah` package and all eleven of its console scripts (`lycheetah-check`,
  `lycheetah-web`, `lycheetah-guard`, `lycheetah-assure`, `lycheetah-compact`,
  `lycheetah-consensus`, `lycheetah-sovereign`, `lycheetah-handoff`, `lycheetah-sol`,
  `lycheetah-alexandria`, `lycheetah-cascade`); `pyproject.toml` is the list of record
- the assurance runtime in `lycheetah/assurance/` (the action guard, gateway,
  policy, receipts and checkpoint authority)
- the implementations under `12_IMPLEMENTATIONS/`
- the MCP servers in `12_IMPLEMENTATIONS/applications/lycheetah_guard_mcp.py` and
  `12_IMPLEMENTATIONS/applications/sol_workspace_mcp.py` (the second one writes files)
- the web demo in `12_IMPLEMENTATIONS/applications/web_demo.py`
- the desktop app in `cascade-pc/`, including its local read-only API on port 7432
- the CI workflows and the tooling in `tools/`

Out of scope:

- vulnerabilities in third-party dependencies — report those upstream, though do tell
  us if this repository's usage makes an upstream issue meaningfully worse
- the contents of `99_ARCHIVE/`, which is a frozen historical record and is not run
- results, claims, or methodology in the research corpus. Those matter, but they are
  a correctness question, not a security one — the
  [Failure Museum](28_DEFENSE/FAILURE_MUSEUM.md) and the issue tracker are the right
  places, and being wrong in public is something this project already invites

### Two things worth knowing before you test

**The web demo and the MCP server are development tools.** `web_demo.py` runs Flask
with `debug=False` on `127.0.0.1` by default and has had no hardening review. It is
not intended to face a network, and "it is exploitable when exposed to the internet"
is expected rather than a finding. Exposure of the *loopback* default, or a way to
reach it that does not require deliberately binding elsewhere, is a finding.

**This project performs no alignment guarantee.** `lycheetah.check()` returns scores
from a text analyser. A report that adversarial text can produce a misleading
alignment score is a correctness issue and genuinely useful — send it — but treating
these scores as a safety control is a misuse of the tool, and the repository says so
in its own documentation.

~~Nothing here should be relied on as a security boundary.~~ *(Struck 2026-10-22,
RV35: the assurance runtime is a pre-execution control. It decides whether a proposed
action runs, so it is meant to hold a boundary.)* A way to make the assurance guard or
gateway allow an action its policy refuses, forge or replay a receipt, or skip a
checkpoint **is** a security finding. The same goes for path escape or unauthenticated
writes through `sol_workspace_mcp.py`, and for reading the `cascade-pc` local API from
a web page. The alignment scores from `lycheetah.check()` remain a correctness
question, as above.

## Handling of secrets

No credential, token, or key belongs in this repository. The `_PROPRIETARY/` vault is
gitignored and must never be committed. If you find a secret in the history, report it
privately rather than opening an issue — the value needs rotating before the finding
becomes public.
