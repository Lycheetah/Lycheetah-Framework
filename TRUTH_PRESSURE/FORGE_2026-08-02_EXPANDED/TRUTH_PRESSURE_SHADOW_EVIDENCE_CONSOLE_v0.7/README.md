# Truth Pressure Shadow Evidence Console v0.7

This bundle extends the Sovereign Sol shadow bridge into a complete local evidence-collection and engineering-review layer.

## It now provides

- historical and candidate engines running in parallel;
- privacy-safe bounded local storage;
- a React Native analysis hook;
- a candidate research-preview card;
- a shadow evidence review hook;
- a React Native research console;
- pressure distributions;
- warning frequencies;
- legacy/candidate delta analysis;
- explicit engineering gates;
- JSON and Markdown evidence exports;
- a Node report generator;
- an article evidence ledger;
- an installer that refuses to overwrite existing app paths.

## Initial release posture

```text
mode: shadow
historical result: visible
candidate result: private
raw text in evidence dataset: forbidden
automatic reorganisation: forbidden
```

## Verify

```bash
npm run verify
npm run typecheck
```

## Analyze an exported dataset

```bash
npm run analyze:shadow -- shadow-dataset.json shadow-report.md
```

## Engineering checkpoint

A candidate research preview is not considered technically ready until:

- at least 100 privacy-safe comparisons exist;
- no non-finite values exist;
- normalized output remains within `[0,1]`;
- text mode remains `TRIAGE_ONLY`;
- no raw content is stored;
- every comparable trigger disagreement has been reviewed.

This is not scientific validation.

## Still required for the exact live app patch

The uploaded source does not include the live files that call `scoreCASCADE`, render the Library score, render the Onion profile, or wrap app persistence.

Upload those files for a line-level patch. Until then, the installer adds only new non-destructive paths.
