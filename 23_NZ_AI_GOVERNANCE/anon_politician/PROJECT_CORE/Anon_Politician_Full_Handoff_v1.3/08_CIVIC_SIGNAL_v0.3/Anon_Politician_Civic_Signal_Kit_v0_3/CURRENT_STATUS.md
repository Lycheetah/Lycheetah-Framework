# Current Status — Civic Signal Integrity Kit v0.3

Date: 16 October 2026 (Pacific/Auckland)

## Completed

- Drafted a three-channel public-input model: open public voice, probability-sample population measurement, and informed deliberation.
- Added distinctions for formal consultation and stakeholder submissions.
- Built a Python metadata validator and browser-only diagnostic.
- Added neutral development-levies question wording and a public-response ledger.
- Added JSON schemas, official source register and synthetic examples.
- Added 16 unit tests and test-run instructions.

## Validation results

The 16 Python tests pass. The valid open-pulse example exits successfully and is labelled descriptive. The intentionally invalid example exits with errors, including an unsupported national-consensus claim. Embedded JavaScript syntax checks pass. A headless Chromium smoke test timed out because of environment-level DBus/zygote issues, so actual interaction should still be tested manually in a normal browser.

## Still unproven / incomplete

- No real participant data is collected or analysed.
- No survey-methods expert, Māori/iwi representatives, accessibility experts, privacy/security specialist or affected community has reviewed this draft.
- The validator cannot verify that the declared recruitment design was executed or that a sample is representative.
- No evidence yet shows that monthly feedback changes political incentives or policy outcomes.
- The development-levies questions are draft research prompts, not an official submission or live consultation.
