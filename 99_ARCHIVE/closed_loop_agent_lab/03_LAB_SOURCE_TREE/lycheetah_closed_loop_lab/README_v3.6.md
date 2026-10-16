# Current milestone: v3.6 Registry Clock Monotonicity

The latest lab iteration hardens the external spent-challenge registry against backward wall-clock movement and unbounded growth of request-ID replay records. It records an HMAC-authenticated clock floor, pins the accepted replay window, protects current replay-cache entries, and rejects consumption before a challenge's issue time.

Local verification: 82 test methods passed in one invocation, including 11 new tests; retained source-pin checks, compilation, historical negative controls and local demos passed.

Important: this is still a local service simulator. Coordinated rollback of both database trust domains is a retained negative control. The next actual milestone requires an independently administered remote monotonic/append-only store and deployment-level backup/restore conformance.
