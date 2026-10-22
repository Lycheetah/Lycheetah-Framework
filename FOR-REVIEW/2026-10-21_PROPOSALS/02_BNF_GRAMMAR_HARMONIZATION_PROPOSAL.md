# PROPOSAL REV-20261021-03: BNF Grammar Specification Harmonization
**Author:** Aetheron (Antigravity Forge Seat)  
**Status:** `[AWAITING_REVIEW]`  
**Target Canonical Path:** `03_LAMAGUE_L1/04_BNF_GRAMMAR.md`  
**Date:** 2026-10-21

---

## 1. Summary & Motivation

Following the approved patch to `12_IMPLEMENTATIONS/core/lamague_parser.py` (which added `↯` to `OPERATORS` and enforced full parse completion), the canonical BNF specification document [`04_BNF_GRAMMAR.md`](../../03_LAMAGUE_L1/04_BNF_GRAMMAR.md) should be synchronized to reflect this truth.

Currently:
1. In `04_BNF_GRAMMAR.md`, `<operator>` lists only `"→"`, `"⊗"`, `"⇌"`, `"⟲"`. `↯` is listed only under `<dynamic>` (line 38) and as a scaffolded junction (line 73).
2. The canonical phrase `Ao → Φ↑ → Ψ` is technically ill-formed under the raw BNF because `Φ` is a `<field>` and `↑` is a `<dynamic>`, without a compound production rule.
3. The pipe symbol `|` is used in examples (`Ao → Φ↑ → Ψ → Ψ_inv | C(Ψ_t) ≥ C(Ψ₀)`) but omitted from the grammar productions.
4. The middle dot connector `·` (`SIMUL` simultaneous execution from the operating guides) is unformalized.

---

## 2. Proposed Specification Diff

```diff
--- a/03_LAMAGUE_L1/04_BNF_GRAMMAR.md
+++ b/03_LAMAGUE_L1/04_BNF_GRAMMAR.md
@@ -17,21 +17,24 @@ LAMAGUE is a **context-free language** over four symbol classes.
 ```bnf
 <expression>  ::= <invariant>
                 | <dynamic>
-                | <field>
+                | <field_expr>
                 | <meta>
                 | <composition>
+                | <guarded_expression>
 
-<composition> ::= <expression> <operator> <expression>
+<guarded_expression> ::= <composition> "|" <constraint>
+
+<composition> ::= <term> ( <operator> <term> )*
+<term>        ::= <invariant> | <dynamic> | <field_expr> | <meta> | "(" <composition> ")"
 
 <operator>    ::= "→"     (projection / transformation)
                 | "⊗"     (fusion / tensor product)
                 | "⇌"     (bidirectional exchange)
                 | "⟲"     (recursion / cycle return)
+                | "↯"     (entropy collapse / drift correction junction)
+                | "·"     (simultaneous execution connector)
 
 <invariant>   ::= "⟟"    (fixed point / stable attractor)
                 | "∅"    (zero-node / null state)
@@ -43,6 +46,8 @@ LAMAGUE is a **context-free language** over four symbol classes.
 <dynamic>     ::= "↑"    (ascent / orientation toward purpose)
                 | "↯"    (collapse / entropy spike)
 
+<field_expr>  ::= <field> [ "↑" | "_" <subscript> ]
+
 <field>       ::= "Ψ"    (drift field / deviation from invariant)
                 | "Φ"    (orientation field / purpose vector)
                 | "Ao"   (anchor field / low-entropy baseline)
```

---

## 3. Impact Assessment & Reversibility
- **Zero Runtime Breakage:** Matches the newly verified behavior in `lamague_parser.py` and `creations/lamague_check`.
- **Epistemic Clarity:** Eliminates the contradiction where the parser's own Canonical Example #2 was valid in code but divergent in the written BNF.
- **Reversibility:** Clean Markdown edit with an explicit 2026-10-21 ratification note.

---
*Awaiting review and authorization from Mackenzie Conor James Clark.*
