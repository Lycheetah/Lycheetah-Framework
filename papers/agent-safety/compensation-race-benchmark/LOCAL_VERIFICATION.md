# Local Compensation Race witness

**Status: MEASURED synthetic experiment, 4 October 2026. No independent or production validation.**

Five unit methods passed on Python 3.12.3. A separate 1,000-round-per-case run reproduced 1,000 weak overwrites, 1,000 sequential partial repairs, 1,000 atomic stale refusals, zero atomic partial repairs and 1,000 clean atomic successes. These deterministic fixtures estimate no real-world failure rate.

Commands from this directory:

```sh
python3 -m unittest discover -s tests -v
python3 -m compensation_race.benchmark --rounds 1000 --output /tmp/compensation-race.json
```

The six-entry supplied manifest matched the incoming packet before integration. It is preserved as `SOURCE_MANIFEST.sha256`; generated Python caches were excluded. The maintained `MANIFEST.sha256` covers the current files, including six incoming files absent from that short source manifest and this local witness. The root archive preserves the complete source packet. No proprietary Candidate B mechanism was imported. Conventional transactional fencing is the comparator, not a novelty claim.
