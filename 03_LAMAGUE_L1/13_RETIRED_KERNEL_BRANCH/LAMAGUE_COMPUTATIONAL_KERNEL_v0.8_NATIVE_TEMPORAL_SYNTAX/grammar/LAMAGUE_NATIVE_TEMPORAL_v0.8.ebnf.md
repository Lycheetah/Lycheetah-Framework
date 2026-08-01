# LAMAGUE v0.8 Native Temporal Syntax

```ebnf
program          = packet_decl, observability_decl, { statement } ;
packet_decl      = "packet", identifier, ";" ;
observability_decl = "observability", observability, ";" ;
observability    = "WHITE_BOX" | "INSTRUMENTED_COLLABORATOR"
                 | "BLACK_BOX" | "UNOBSERVABLE" ;

statement        = boundary_decl | recover_decl | evidence_decl | unknown_decl
                 | conflict_decl | drift_decl | intent_decl | action_decl
                 | invariant_decl | preserve_decl | block_decl | analyze_decl ;

boundary_decl    = "boundary", [ "discrepancy=", number ],
                   [ "critical=", number ], [ "min_invariant=", number ], ";" ;
recover_decl     = "recover", "horizon=", number, ";" ;

evidence_decl   = provenance, identifier, "key=", scalar, "value=", scalar,
                   [ "unit=", scalar ], [ "operator=", scalar ],
                   [ "source=", scalar ], [ "at=", number ], ";" ;
provenance       = "observe" | "declare" | "calculate" | "infer" ;

unknown_decl     = "unknown", identifier, [ "expected=", scalar ],
                   [ "source=", scalar ], [ "protected=", boolean ], ";" ;

conflict_decl    = "conflict", identifier, "branches=", csv,
                   [ "dimensions=", csv ], [ "status=", conflict_status ], ";" ;
conflict_status  = "UNRESOLVED" | "RESOLVED" | "REJECTED" ;

drift_decl      = "drift", identifier, [ "scale=", number ],
                   [ "weight=", number ], ";" ;
intent_decl      = "intent", identifier, "at=", number, "value=", number, ";" ;
action_decl      = "action", identifier, "at=", number, "value=", number,
                   [ "source=", scalar ], ";" ;
invariant_decl   = "invariant", identifier, "at=", number,
                   "preserved=", (boolean | "null"),
                   [ "weight=", number ], [ "source=", scalar ], ";" ;

preserve_decl    = "preserve", identifier, ";" ;
block_decl       = "block", identifier, ";" ;
analyze_decl     = "analyze", ";" ;

boolean          = "true" | "false" ;
scalar           = quoted_string | identifier | number | boolean | "null" ;
csv              = identifier, { ",", identifier } ;
```

## Binding semantics

- `observe`, `declare`, `calculate`, and `infer` compile to distinct provenance classes.
- `unknown` never compiles to a guessed value.
- `conflict` preserves all named branches.
- `drift` declares scale and weight for a temporal dimension.
- every `intent` requires a matching `drift` declaration.
- `recover` sets the breach-recovery horizon.
- `preserve` must reference an existing evidence branch, unknown, or invariant.
- `block` is carried into the deterministic analysis packet.
- symbolic or mythic notation cannot override this grammar.
