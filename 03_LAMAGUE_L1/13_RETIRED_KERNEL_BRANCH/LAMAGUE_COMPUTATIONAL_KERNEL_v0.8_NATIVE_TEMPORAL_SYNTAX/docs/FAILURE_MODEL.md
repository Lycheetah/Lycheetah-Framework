# Failure Model

## FATAL

Compilation or execution is forbidden.

## RECOVERABLE

Execution may continue only through a machine-defined safe response, such as unsafe compression becoming `Z_UP`.

## ADVISORY

Execution remains valid, but a nonconstitutional improvement is available.

No fatal invariant may be downgraded to advisory.
