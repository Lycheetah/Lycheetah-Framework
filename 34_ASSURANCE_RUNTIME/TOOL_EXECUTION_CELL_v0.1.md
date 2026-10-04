# Tool Execution Cell v0.1 — Linux Reference Containment

**Status:** `[SCAFFOLD]`  
**Target use:** human-supervised coding-agent pilot  
**Production claim:** none

## Purpose

The external-threat audit identified hostile/unexpected code execution as an
outright gap. Context isolation and policy receipts do not contain a process
that can read the host filesystem, use ambient credentials, or reach the
network.

`ExecutionCell` is an additive Linux reference implementation for that boundary.

## Default containment

Each run gets:

- a new user namespace;
- a new mount namespace;
- a new PID namespace;
- a new network namespace with no interfaces configured;
- new IPC and UTS namespaces;
- a read-only bind of the host root;
- inherited submounts detached;
- `/home`, `/root`, `/run`, `/mnt`, `/media`, `/proc`, `/sys`, `/dev`, `/tmp`,
  and `/var/tmp` masked by fresh tmpfs mounts;
- one explicit workspace rebound as `/mnt/work`;
- no inherited environment;
- CPU, address-space, file-size, open-file, process-count, and core limits;
- all namespace capabilities dropped before user code using `setpriv`;
- `no_new_privs`;
- parent-death SIGKILL;
- wall-clock timeout enforced by the parent.

The workspace is the only host-backed writable path intended to persist.

## Deliberate limits

This is **not yet a hardened sandbox**.

It does not currently provide:

- seccomp syscall filtering;
- cgroup-enforced CPU/memory/PID limits;
- Landlock verification;
- device-policy proof beyond the minimal reconstructed `/dev`;
- kernel exploit protection;
- nested-container defense;
- a network allowlist mode;
- signed toolchain/rootfs provenance;
- independent penetration testing.

`RLIMIT_NPROC` behavior depends on UID mapping and kernel semantics; do not treat
it as a substitute for a cgroup PID controller.

The host root is read-only and private paths are masked, but system binaries and
libraries remain visible. This is a practical pilot cell, not a minimal rootfs.

## Pilot rule

Use it only with:
- disposable branches/workspaces;
- no production credentials;
- no customer secrets;
- human final approval outside the cell;
- Assurance Runtime/finality receipts before consequential actions.

The command API takes an argv tuple, not a shell command string. A caller can
choose to execute a shell explicitly, but the cell itself performs no shell
interpolation.


## Integration boundary

Namespace containment tests require a namespace-capable Linux host. A skip is not containment evidence. Importing the rest of the assurance package remains possible where the Unix `resource` module is absent; this does not make execution cells portable. Test workspaces use disposable temporary directories rather than the source environment's `/mnt/data` path.

`ready` currently records that the launcher completed or timed out after the namespace availability probe; it is not an attestation that every isolation setup step succeeded. Inspect `exit_code`, `stderr`, `succeeded` and a reviewed host probe. Captured output is not independently bounded, RLIMITs are not cgroup quotas, and the root view can contain readable files outside the explicitly masked paths. Supply a disposable workspace with no secrets. No arbitrary-host secret containment, seccomp, malicious-kernel resistance or production sandbox claim is made.
