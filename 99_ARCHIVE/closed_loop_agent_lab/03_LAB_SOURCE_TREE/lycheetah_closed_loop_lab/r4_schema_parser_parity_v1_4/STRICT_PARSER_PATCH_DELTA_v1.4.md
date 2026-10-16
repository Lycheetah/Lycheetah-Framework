# Strict parser patch delta v1.4

Apply after reviewing `strict_assurance_wire_types_v1_3.patch` against the exact upstream commit. This delta is a patch guide, not a claim that an executable unified diff was applied.

## `ControlReference.from_dict`

After confirming `data` is a `Mapping` and before reading fields, reject unknown keys:

```python
allowed = {"framework", "control_id", "title", "url"}
unknown = sorted(str(key) for key in data if key not in allowed)
if unknown:
    raise ValueError("control reference contains unknown fields: " + ", ".join(unknown))
```

## `AssuranceReceipt.from_dict`

After confirming `data["policy"]` is a mapping and before constructing the receipt, validate its embedded policy digest:

```python
policy_digest = data["policy"].get("sha256")
if not isinstance(policy_digest, str) or not re.fullmatch(r"[a-f0-9]{64}", policy_digest):
    raise ReceiptError("policy.sha256 must be 64 lowercase hexadecimal characters")
```

This requires `import re` in `receipt.py`. The proposed regression test should also assert that a self-consistent receipt created with malformed `policy.sha256` is rejected at construction. Ensure no code path assumes receipt parsing authenticates the issuer; digest-only verification still does not.
