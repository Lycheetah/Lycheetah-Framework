# Pack Manifest v4.6

The v4.6 standalone package includes the revised same-host shared ingress quota store, the mTLS gateway, retained coordinator/quorum/remote-witness dependencies, four local test modules, the preserved v4.5 shared-ingress baseline fixture, a differential probe, source-pin metadata, runners, test logs and documentation.

Verification: 16 local source fingerprints; 24 ingress, 13 coordinator, 38 quorum and 53 gateway tests passed (128 total). `results_v4.6.json` records the timeout anomaly from the first buffered gateway run and the later successful full unbuffered run.

These files pin a local research artifact, not the upstream repository. No pull request or source change was made upstream.
