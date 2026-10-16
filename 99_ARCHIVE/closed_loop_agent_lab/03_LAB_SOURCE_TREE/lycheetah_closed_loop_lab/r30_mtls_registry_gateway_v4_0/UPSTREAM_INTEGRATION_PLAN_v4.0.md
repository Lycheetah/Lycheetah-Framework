# Upstream Integration Plan v4.0

## Keep the patch narrow

Do not alter the existing registry business logic or claim the reference server is production-ready. Integrate the mTLS gateway as an optional adapter around the existing quorum-guarded dispatcher with configuration parsed by a typed deployment layer.

## Required gates before promotion

1. Rebase on a fresh checkout and rerun the existing policy/registry/quorum suite unchanged.
2. Run the new gateway suite under all supported Python versions; keep test groups in separate invocations because process-lifecycle tests may hang in a shared interpreter.
3. Add production-grade certificate configuration validation, chain/SAN rules, CA and leaf rotation procedure, revocation strategy, and secret-manager integration.
4. Set global connection/worker/rate limits; measure TLS-handshake resource behavior under bounded floods and slow clients.
5. Use separate machines and separate administrative credentials for witnesses; validate network ACLs and firewall assumptions.
6. Exercise restore/rollback, loss of quorum, partial witness outage, and coordinator restart on a staging topology.
7. Verify client response signatures and the request-ID binding in the real consuming client.
8. Run the full project CI matrix and perform code review. No claim of production safety before these gates pass.

## Repository status

This artifact includes research/reference files only. It does not create a branch, modify the upstream repository or represent a completed pull request. Existing GitHub integration in this session has returned HTTP 403 for branch creation.
