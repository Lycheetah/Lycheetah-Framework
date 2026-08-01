# Next Forge — LAMAGUE Core v0.4

## Canonical Meaning, Rewrite Confluence, and Semantic Hash Stability

### Required work

1. Define the rewrite system formally.
2. Enumerate all critical rewrite overlaps.
3. Prove or computationally verify local confluence over the implemented core.
4. Test termination of normalization.
5. Generate equivalent surface expressions through multiple rewrite routes.
6. Confirm identical canonical normal form.
7. Confirm identical semantic hash.
8. Define hash-version and canonicalization-version fields.
9. Add golden semantic vectors.
10. Add corruption and hash-instability tests.
11. Build an independent slow reference normalizer.
12. Differentially compare both normalizers.
13. Freeze conformance cases.
14. Document unsupported equivalence claims.

### Binding objective

```text
same core meaning
→ same canonical form
→ same semantic hash
```

### Required restraint

Passing the v0.4 suite will prove implementation-level canonical stability over the tested language subset.

It will not prove that two arbitrary human concepts have the same meaning.
