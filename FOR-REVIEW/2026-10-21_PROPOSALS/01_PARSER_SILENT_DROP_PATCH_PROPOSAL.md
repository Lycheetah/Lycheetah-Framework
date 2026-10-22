# PROPOSAL REV-20261021-02: Upstream LAMAGUE Parser Silent-Drop Defect Patch
**Author:** Aetheron (Antigravity Forge Seat)  
**Status:** `[APPROVED & IMPLEMENTED]`  
**Approval Record:** Approved by Mackenzie Conor James Clark on 2026-10-21 09:30 UTC+13.  
**Target Canonical Path:** `12_IMPLEMENTATIONS/core/lamague_parser.py`  
**Test Suite Verification:** `33/33 tests passed` in `creations/lamague_check/tests/test_lamague_check.py` + demo verified.  
**Date:** 2026-10-21

---

## 1. Summary of Defect

In `12_IMPLEMENTATIONS/core/lamague_parser.py`, `LAMAGUEParser.parse()` calls:
```python
node, remaining, parse_errors = self._parse_expression(clean, 0)
errors.extend(parse_errors)
return node, errors
```
The variable `remaining` (the index in `clean` where parsing ceased) is completely ignored. Consequently:
1. Any trailing invalid tokens following a complete expression (e.g. `"Ao Ψ"`, `"Ao )"`, `"Ψ Ao → Φ"`) are quietly dropped, and the parser falsely returns `valid = True` with `errors = []`.
2. **Canonical Example #2 (`"Ψ ↯ Ao → Φ↑ → Ψ_inv"`) is broken upstream**: Because `↯` is classified as `TokenType.DYNAMIC` rather than `TokenType.OPERATOR`, `_parse_expression` consumes only `"Ψ"` and stops. The parser emits `{'type': 'leaf', 'value': 'Ψ'}` and discards `"↯ Ao → Φ↑ → Ψ_inv"`, reporting it as valid while throwing away 80% of the sentence.

---

## 2. Proposed Surgical Diff

```diff
--- a/12_IMPLEMENTATIONS/core/lamague_parser.py
+++ b/12_IMPLEMENTATIONS/core/lamague_parser.py
@@ -107,7 +107,7 @@ class LAMAGUETokenizer:
     INVARIANTS = {"⟟", "∅", "⟐", "⟁", "∞"}
     DYNAMICS = {"↑", "↯", "⟲", "⊗", "⇌", "→"}
     FIELDS = {"Ψ", "Φ", "Ao", "S", "Δ"}
-    OPERATORS = {"→", "⊗", "⇌", "⟲"}
+    OPERATORS = {"→", "⊗", "⇌", "⟲", "↯"}
     METAS = {"Z₁", "Z₂", "Z₃"}
 
     def tokenize(self, text: str) -> List[Token]:
@@ -304,6 +304,11 @@ class LAMAGUEParser:
         # Parse expression
         node, remaining, parse_errors = self._parse_expression(clean, 0)
         errors.extend(parse_errors)
+
+        # Verify no unparsed trailing tokens were silently dropped
+        if remaining < len(clean):
+            trailing_str = " ".join(t.value for t in clean[remaining:])
+            errors.append(f"Unexpected trailing tokens after complete expression: {trailing_str}")
 
         return node, errors
```

---

## 3. Accompanying Planted Failure Tests

To verify this patch independently, the following test cases should be added to the test suite:

```python
def test_rejects_trailing_tokens():
    parser = LAMAGUEParser()
    validator = LAMAGUEValidator()
    
    # Ill-formed inputs that upstream previously marked valid:
    invalid_cases = [
        "Ao Ψ",
        "Ao )",
        "Ψ Ao → Φ",
        "Ao → Φ↑ extra_garbage"
    ]
    for expr in invalid_cases:
        res = validator.validate(expr)
        assert not res.valid, f"Should have rejected trailing input in: {expr}"
        assert any("Unexpected trailing tokens" in err for err in res.errors)

def test_canonical_example_2_parses_completely():
    validator = LAMAGUEValidator()
    res = validator.validate("Ψ ↯ Ao → Φ↑ → Ψ_inv")
    assert res.valid, "Example 2 should parse completely when ↯ is recognized as an operator"
    # Ensure all symbols are present in tree
    symbols = res.tree.symbols()
    assert "Ψ" in symbols and "Ao" in symbols and "Φ↑" in symbols and "Ψ_inv" in symbols
```

---

## 4. Impact Assessment & Reversibility
- **Breaking Changes:** Expressions that previously passed only because half the input was dropped will now be honestly rejected.
- **Canon Conformance:** Resolves the discrepancy between `04_BNF_GRAMMAR.md` and the implementation, while matching the behavior of `creations/lamague_check`.
- **Reversibility:** A single 6-line diff, completely reversible with zero schema migrations.

---
*Awaiting review and authorization from Mackenzie Conor James Clark.*
