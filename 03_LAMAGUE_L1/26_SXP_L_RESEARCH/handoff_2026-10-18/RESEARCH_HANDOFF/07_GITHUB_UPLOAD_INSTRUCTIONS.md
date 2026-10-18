# GitHub upload instructions and status

## Verified repo and current blocker
- Intended destination: https://github.com/Lycheetah/Lycheetah-Framework
- Existing independent early audit: `03_LAMAGUE_L1/SXP-L_LAMAGUE_INDEPENDENT_AUDIT_v0.1_to_v1.0.md`. Preserve it.
- On 2026-10-18 the connected GitHub integration allowed read/search but returned HTTP **403 Resource not accessible by integration** when asked to create a feature branch and to create a brand-new file. **No code or handoff document was successfully pushed by this chat.**

## Safe manual/agent integration plan
1. Open a working GitHub client or a separate code agent with actual repository *Contents: read and write* permission. Ensure the token/app has correct repo installation and target-branch permissions; do not share credentials in chat.
2. Create a new branch from the repository's latest `master`, e.g. `research/sxp-l-v2-0-consolidation-2026-10-18` (or choose a nonconflicting branch name).
3. Add the `RESEARCH_HANDOFF/` **Markdown and CSV** files to `03_LAMAGUE_L1/SXP-L/2026-10-18_v2.0_handoff/`. Preserve their labels and evidence scope. Keep this first PR reviewable; do not paste raw private chat logs.
4. For durable public archiving **after the planned blinded learner pilot**, attach `SXP-L_LAMAGUE_FULL_CHAT_HANDOFF_v0.1-v2.0_2026-10-18.zip` as a **GitHub Release asset** if you intend to host the full ~42.9 MB archive. This ZIP includes researcher answer keys: making it public **before** recruiting public volunteers could compromise blinding. Until the pilot is complete, keep the complete archive in private evidence storage or with explicitly nonparticipant auditors, and publish only the review-safe Markdown. GitHub Releases support larger binary assets; prefer those over committing 20 overlapping nested ZIPs to source history.
5. Open a PR targeting `master` and have Argon audit schema mappings and reproduced early defects **before merging**. Avoid changing unrelated LAMAGUE modules.
6. Verify the final uploaded asset against the SHA-256 value provided by the compiler handoff message. Inside the archive, `SHA256SUMS.txt` verifies every package member.
7. Do not distribute the researcher v2.0 ZIP (which contains answer keys) as a blinded participant study file. Share only a separately assigned participant HTML with consenting volunteers.

**Evidence caution:** README and version chronology were reconstructed from visible chat history and artifacts; the package is not a verbatim full ChatGPT conversation export. A full literal transcript would require the user's separate ChatGPT data export.
