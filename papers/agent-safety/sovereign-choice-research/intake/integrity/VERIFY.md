# Verifying the Handoff

From the extracted archive root (`LYCHEETAH_SOVEREIGN_WILL_HANDOFF_2026-10-19`):

```bash
sha256sum -c integrity/FILE_SHA256.txt
```

The list covers every file in the handoff except itself. ZIP-level integrity is checked separately by a complete read/CRC test of the final package. The original Forge archives can be compared against `integrity/SOURCES.json`.
