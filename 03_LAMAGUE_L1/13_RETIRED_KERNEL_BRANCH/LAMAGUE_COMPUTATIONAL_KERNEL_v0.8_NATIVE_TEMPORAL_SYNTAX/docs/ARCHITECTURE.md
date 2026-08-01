# Kernel Architecture

## Front end

The parser reads a line-oriented language with typed declarations.

```text
unknown rare_failure protected required_for=ordinary_release
authority operator scope=pilot "Human operator"
effect MayAffect<pilot_participant>
```

## Semantic IR

Compilation normalises source into a stable representation containing typed entities, expanded operation paths, declared effects, gates, risk, irreversibility, recovery rules, and a semantic identifier.

## Type and effect checker

A consequential program with no authority does not execute. An irreversible program without four gates does not execute. A protected unknown cannot be declared without activating `U`.

## Runtime

Every immutable transition creates:

```text
before hash
operation
after hash
outcome
explanation
```

## Continuity

Reports can be classified as `CONTINUATION`, `DESCENDANT`, `FORK`, or `IMPOSTOR`.
