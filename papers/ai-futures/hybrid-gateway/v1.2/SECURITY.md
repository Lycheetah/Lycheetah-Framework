# Security status and reporting

**LOCAL RESEARCH PROTOTYPE — NOT APPROVED FOR PRODUCTION OR INTERNET EXPOSURE.**

Do not expose the HTTP Review Desk outside `127.0.0.1`. It lacks TLS, user identity proof,
managed key custody, isolated signing service, a network security perimeter, comprehensive
penetration testing, and deployment hardening. The CASCADE subprocess is process-separated,
**not an operating-system sandbox**; it must only load trusted code.

An HMAC verifies possession of a configured secret; it does not establish that a human read
and understood evidence. The new v1.2 witness only helps detect rollback **if** its HMAC
secret and checkpoint are retained independently of SQLite. The reference implementation
returns the checkpoint to its caller; independent storage is not implemented.

Do not submit private or customer documents to demonstrations; fixtures are fictional.
Never commit real passwords, signing keys, model provider tokens, or SQLite databases.

For a suspected vulnerability, use the repository's private GitHub vulnerability reporting
feature if enabled. Otherwise contact the repository maintainers through a private channel;
please do not publicly post working exploits that could put users at risk.
