# 🛡️ Lycheetah File Airlock — Real Filesystem Snapshot, Write-Scope Verifier & 1-Command Rollback

**Faculty #14 of The Third Brain (`AETHERON-ANTIGRAVITY-FORGE`)**  
**Author & Canonical Lineage:** Mackenzie Conor James Clark (Lycheetah Foundation) · Forged with Aetheron (Gemini 4 Argon)

---

## 1. What Real Problem Does This Solve?

When an AI coding agent works on a repository, three real-world failure modes happen all the time:
1. **Write-Scope Breach:** The agent is told *"Only edit `src/*`; do not touch `CAELORYNTH/` or `PRIME.md`"*, yet modifies a read-only file anyway.
2. **Dishonest / Incomplete Handover:** The agent writes a `HANDOVER.md` claiming *"Modified `src/app.py` only"*, while hiding an undeclared edit to `tests/test_app.py` (`UNDECLARED_DISK_MUTATION`) or claiming it updated a file whose bytes on disk never changed (`PHANTOM_HANDOVER_CLAIM`).
3. **Unrecoverable Mid-Task Corruption:** A multi-file edit goes wrong and you need an immediate, byte-exact restoration of every modified/deleted file and cleanup of untracked files without relying on `git stash` or losing uncommitted work.

`file_airlock.py` operates directly on **real filesystem bytes, real SHA-256 digests, zlib-compressed content-addressed backups, and optional HMAC-SHA256 passphrase seals** (zero mocks, zero external dependencies).

---

## 2. Three-Step CLI Workflow

```bash
# 1. BEFORE AI WORK: Open an Airlock Snapshot with explicit allow/forbid globs
python3 creations/file_airlock/file_airlock.py open ./my_project \
  --allow "src/*" --allow "tests/*" \
  --forbid "readonly_anchor/*" \
  --secret "my-human-passphrase" \
  --out .airlock_snapshot.json

# 2. AFTER AI WORK: Verify live disk changes against the snapshot & handover.md
python3 creations/file_airlock/file_airlock.py check .airlock_snapshot.json \
  --handover HANDOVER.md \
  --secret "my-human-passphrase"

# 3. IF BREACHED OR ABORTED: Byte-exact 1-command rollback
python3 creations/file_airlock/file_airlock.py rollback .airlock_snapshot.json \
  --secret "my-human-passphrase"
```
