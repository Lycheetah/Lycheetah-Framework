# Next Model Handoff — Civic Signal Integrity Kit v0.3

Read this file after the kit README. This increment develops the core monthly-citizen-input mechanism in Anon Politician.

## What changed

- Formalised three distinct types of civic evidence: open public voice, population measurement, and informed deliberation.
- Added a validator that blocks representative/consensus language unsupported by a declared recruitment method.
- Added a public-response ledger that records how input was disposed of and who owns follow-up.
- Added a neutral draft question set for the development-levies policy case.
- Added an offline HTML checker and automated tests.

## What must not be claimed

- Passing tests proves only that specified checks run as coded.
- The validator does not inspect real sampling or data and cannot certify representativeness.
- The example datasets are synthetic.
- The draft development-levies question set is not a formal public consultation and has not been reviewed by affected communities.
- This work does not show that regular polling changes politicians' incentives or improves policy outcomes.

## Next tasks

1. Run `python -m unittest discover -s tests -v` and `python src/civic_signal_validator.py examples/invalid_consensus_claim.json`.
2. Have a survey-methods researcher review the channel distinctions and validator's false-positive/false-negative behaviour.
3. Engage appropriate Māori/iwi and accessibility expertise before finalising public-input design.
4. Test the HTML checker in a normal browser; it is advisory and should not be described as certification.
5. Integrate the metadata checks into Policy Lab without collecting actual personal data.
6. Conduct a threat model for coordinated flooding, bots, repeat submissions, shared devices, pseudonymous access and exclusion of people with limited digital access.
7. In parallel, run the separately defined blinded analysis comparison only after generating each arm under controlled, recorded conditions. Do not claim results from this kit as a substitute.
8. Test the decision-response ledger on a real, public decision record and verify every claimed policy change from primary-source history.

## Source status

Sources used here are primarily the official MCERT development-levies page and technical Q&A, Treasury Living Standards Framework and CBAx page, and OECD citizen-participation guidance. See `SOURCE_REGISTER.csv`. Recheck live documents before a future policy submission or public release.
