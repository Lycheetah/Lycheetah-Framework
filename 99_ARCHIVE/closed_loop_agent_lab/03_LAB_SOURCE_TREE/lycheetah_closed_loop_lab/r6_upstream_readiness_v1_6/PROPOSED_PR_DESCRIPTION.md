# Draft pull-request description (not submitted)

## Summary

Align the Lycheetah Assurance Runtime's policy/receipt wire contracts across JSON Schema validation and deserialization. Reject values that are silently coerced into strings/numbers or normalized away before canonical digest verification, and add a read-only compatibility inventory so persisted records are reviewed before stricter parsing is adopted.

## Changes

- Reject non-string `TextRule` id/pattern/title/description/status-basis fields before any `str()` conversion.
- Reject non-string receipt schema versions, wrong typed finding fields, Boolean/non-finite confidence, malformed evidence items and malformed control-reference fields.
- Reject unknown control-reference fields to match the proposed closed schema, validate `policy.sha256` on receipt ingestion, and reject explicit null `cap_reason` when the serializer's canonical wire representation omits the field.
- Tighten policy/receipt schemas to match intended wire shapes and parser-level constraints that JSON Schema can express.
- Add regression tests and a read-only inventory tool for persisted JSON/JSONL records.

## Security/compatibility notes

This is input-contract hardening, not a claim of HMAC forgery, production bypass, or runtime-agent safety improvement. The current receipt HMAC continues to authenticate the canonical digest string. Records rejected only by the candidate contract must be reviewed for legacy extension usage before rollout. Parser semantics that JSON Schema cannot represent—regular-expression compilation, unique policy rule IDs, evidence caps and receipt-chain validation—remain explicit parser/runtime responsibilities.

## Test plan

- New receipt wire-type and policy parser tests
- Candidate JSON Schema generated-record tests
- Existing model, policy, receipt, runtime and schema suites
- Full repository test suite and CI on the branch
- Compatibility audit over stored policy/receipt records before deployment

## Current status

This PR body is a draft only. No upstream branch or PR was created by the connected integration; a branch creation attempt returned HTTP 403. All upstream tests and CI must be run before this description is used in a real pull request.
