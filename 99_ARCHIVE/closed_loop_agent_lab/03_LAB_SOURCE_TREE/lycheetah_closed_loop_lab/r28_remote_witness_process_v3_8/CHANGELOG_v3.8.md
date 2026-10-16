# Changelog v3.8

- Added a real HTTP client boundary between the checkpoint coordinator and four witness service subprocesses.
- Added numeric-loopback-only server and client guards; redirects are disabled.
- Added HMAC-SHA256 transport authentication bound to HTTP method, exact path/body hash, timestamp and unique request ID.
- Added durable SQLite RPC replay-ID ledger with fresh timestamp validation.
- Added bounded request-body parsing, strict route/body schemas, generic internal errors and lost-response failpoint.
- Added tests for restart durability, one/two witness outages, dropped vote response after commit, request replay, wrong API key, tampered request body, malformed nonce, unknown route and oversized Content-Length.
- Preserved explicit limitation that four subprocesses on one host are not independent administrative/failure domains.
- No upstream source or remote hosted service was changed/accessed by this experiment.
