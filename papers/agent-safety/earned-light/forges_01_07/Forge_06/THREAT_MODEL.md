# Forge VI Threat Model (toy prototype)

**Protected interests:** user's authority to stop, distinguish committed effects, retain later human work, understand consequence and recover eligible local state.

**Trust roots:** injected operator HMAC secret and caller, controller SQLite storage, simulated provider SQLite service, clock, and Python process. **All are trusted assumptions, not secure platform implementations.**

**Potential adversaries:** malicious delegated agent, misleading external content, competing writer, compromised provider, compromised approval interface, leaked shared secret, provider failure, network packet loss, replayed operation.

**Attacks exercised:** out-of-scope action, replayed operator signature, expired operator signature, misbound action/target, stale write, third-party edit, same-value edit (ABA-like), operation-ID collision, revoked-before-dispatch, in-flight commit after revoke, lost acknowledgment, unavailable provider, and compromised mock signing secret.

**Not exercised:** real external identity, multi-host race, distributed transactional integrity, clock compromise, cryptographic key rotation, safe credential revocation across third-party APIs, process crashes at every execution cut point, actual delivery of notifications, colluding provider/observer, third-party attestations, malicious OS user, resource exhaustion, usability or consent studies.

**Do not deploy:** The HMAC secret sits in memory and the simulated provider adapter is under the same local control; `operator_request` verification does not establish that a real person approved an action through an independent trusted interface. Calling `revoke` is not equivalent to revoking live connector tokens. All effects are synthetic.
