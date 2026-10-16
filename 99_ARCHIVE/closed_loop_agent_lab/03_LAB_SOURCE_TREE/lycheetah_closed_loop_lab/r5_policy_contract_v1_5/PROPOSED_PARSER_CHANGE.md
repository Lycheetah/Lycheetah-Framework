# Proposed parser change — policy TextRule wire types

Apply in `lycheetah/assurance/policy.py`, inside `TextRule.from_dict`, immediately after the required-field check and before `phases` is parsed:

```python
        if not isinstance(data["id"], str) or not isinstance(data["pattern"], str):
            raise PolicyError("text rule id and pattern must be strings")
        for field_name in ("title", "description", "status_basis"):
            if field_name in data and not isinstance(data[field_name], str):
                raise PolicyError(f"text rule {field_name} must be a string")
```

Then replace the coercing constructor arguments:

```python
            rule_id=data["id"],
            pattern=data["pattern"],
            title=data.get("title", data["id"]),
            description=data.get("description", "Policy text rule matched"),
            # Keep the existing enum, Boolean, and phase conversions/validation.
            status_basis=data.get("status_basis", ""),
```

Do not remove the current regex compilation, 4096-character limit, active-rule evidence-basis check, unique-rule-id check, or numeric/Boolean validation. Those are semantic safeguards and should remain active after wire-type validation.

## Schema changes

Candidate file: `policy.schema.strict-candidate.json`.

- `$defs/stringArray.items`: add `minLength: 1`.
- `$defs/textRule.properties.pattern`: add `maxLength: 4096`.
- `$defs/textRule`: add a conditional requiring a non-blank `status_basis` when `claim_status` is `ACTIVE`.

The schema alone does not replace parser-level regular-expression compilation or cross-item unique-id checks.
