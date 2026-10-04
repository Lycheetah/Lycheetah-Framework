"""Linux Tool Execution Cell for bounded agent-code execution.

Status: [SCAFFOLD].

This is a Linux reference containment layer for human-supervised pilots. It uses
user, mount, PID, network, IPC, and UTS namespaces; a read-only host-root view;
masked private/runtime paths; one explicitly rebound workspace; an empty network
namespace; clean environment; resource limits; and capability dropping before
user code executes.

It is not a complete hostile-code sandbox. It has no seccomp profile, no cgroup
resource controller, no kernel exploit defense, no verified Landlock policy, and
no independent security review.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import resource
except ImportError:  # Keep the other assurance APIs importable on non-Unix hosts.
    resource = None  # type: ignore[assignment]


EXECUTION_CELL_VERSION = "0.1.0"

_REQUIRED_TOOLS = ("unshare", "mount", "umount", "chroot", "setpriv", "findmnt")
_MASKS = (
    ("tmp", "mode=1777,size=128m,nosuid,nodev"),
    ("var/tmp", "mode=1777,size=64m,nosuid,nodev"),
    ("home", "mode=0755,size=1m,nosuid,nodev,noexec"),
    ("root", "mode=0700,size=1m,nosuid,nodev,noexec"),
    ("run", "mode=0755,size=8m,nosuid,nodev,noexec"),
    ("mnt", "mode=0755,size=8m,nosuid,nodev,noexec"),
    ("media", "mode=0755,size=1m,nosuid,nodev,noexec"),
    ("proc", "mode=0555,size=1m,nosuid,nodev,noexec"),
    ("sys", "mode=0555,size=1m,nosuid,nodev,noexec"),
    ("dev", "mode=0755,size=1m,nosuid,noexec"),
)


@dataclass(frozen=True)
class CellAvailability:
    available: bool
    reason: str
    missing_tools: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExecutionCellSpec:
    workspace: str
    argv: tuple[str, ...]
    timeout_seconds: float = 30.0
    cpu_seconds: int = 15
    memory_bytes: int = 768 * 1024 * 1024
    file_size_bytes: int = 128 * 1024 * 1024
    max_open_files: int = 128
    max_processes: int = 64
    env: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.workspace, str) or not self.workspace:
            raise ValueError("workspace must be a non-empty path")
        if not isinstance(self.argv, tuple) or not self.argv:
            raise ValueError("argv must be a non-empty tuple")
        if any(not isinstance(item, str) or not item for item in self.argv):
            raise ValueError("argv must contain non-empty strings")
        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or not 0.1 <= float(self.timeout_seconds) <= 3600.0
        ):
            raise ValueError("timeout_seconds must be in [0.1, 3600]")
        for name in (
            "cpu_seconds",
            "memory_bytes",
            "file_size_bytes",
            "max_open_files",
            "max_processes",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.env, Mapping):
            raise ValueError("env must be a mapping")
        for key, value in self.env.items():
            if not isinstance(key, str) or not key or "=" in key or "\x00" in key:
                raise ValueError("environment keys must be valid non-empty names")
            if not isinstance(value, str) or "\x00" in value:
                raise ValueError("environment values must be strings without NUL")
            if len(key) + len(value) > 32_768:
                raise ValueError("environment entry is too large")


@dataclass(frozen=True)
class ExecutionCellResult:
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool
    ready: bool
    reason: str
    isolation: tuple[str, ...]

    @property
    def succeeded(self) -> bool:
        return self.ready and not self.timed_out and self.exit_code == 0


class ExecutionCell:
    """Launch one command inside the Linux namespace reference cell."""

    @staticmethod
    def availability(*, active_probe: bool = False) -> CellAvailability:
        if platform.system() != "Linux":
            return CellAvailability(False, "linux-required")
        missing = tuple(tool for tool in _REQUIRED_TOOLS if shutil.which(tool) is None)
        if missing:
            return CellAvailability(False, "required-tools-missing", missing)
        if not active_probe:
            return CellAvailability(True, "static-prerequisites-present")
        command = [
            "unshare",
            "--user",
            "--map-root-user",
            "--mount",
            "--net",
            "--pid",
            "--fork",
            "--kill-child=SIGKILL",
            "/bin/true",
        ]
        probe = subprocess.run(command, capture_output=True, text=True, timeout=5)
        if probe.returncode != 0:
            return CellAvailability(False, "namespace-probe-failed")
        return CellAvailability(True, "namespace-probe-passed")

    def run(self, spec: ExecutionCellSpec) -> ExecutionCellResult:
        availability = self.availability(active_probe=True)
        if not availability.available:
            return ExecutionCellResult(
                None,
                "",
                availability.reason,
                False,
                False,
                "execution-cell-unavailable",
                (),
            )

        workspace = Path(spec.workspace).resolve()
        if not workspace.is_dir():
            raise ValueError("workspace must resolve to an existing directory")

        root_dir = Path(tempfile.mkdtemp(prefix="lycheetah-cell-root-"))
        child_spec = {
            "workspace": str(workspace),
            "argv": list(spec.argv),
            "cpu_seconds": spec.cpu_seconds,
            "memory_bytes": spec.memory_bytes,
            "file_size_bytes": spec.file_size_bytes,
            "max_open_files": spec.max_open_files,
            "max_processes": spec.max_processes,
            "env": dict(spec.env),
        }
        command = [
            "unshare",
            "--user",
            "--map-root-user",
            "--mount",
            "--pid",
            "--net",
            "--ipc",
            "--uts",
            "--fork",
            "--kill-child=SIGKILL",
            sys.executable,
            str(Path(__file__).resolve()),
            "--_cell_child",
            str(root_dir),
            json.dumps(child_spec, separators=(",", ":")),
        ]
        isolation = (
            "user-namespace",
            "mount-namespace",
            "pid-namespace",
            "network-namespace-no-interface-setup",
            "ipc-namespace",
            "uts-namespace",
            "read-only-root-view",
            "masked-home-runtime-data-pseudofs",
            "explicit-workspace-bind",
            "clean-environment",
            "rlimit-cpu-address-space-file-nofile-nproc-core",
            "all-capabilities-dropped-before-user-code",
            "no-new-privileges",
        )

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=float(spec.timeout_seconds),
            )
            return ExecutionCellResult(
                completed.returncode,
                completed.stdout,
                completed.stderr,
                False,
                True,
                "completed",
                isolation,
            )
        except subprocess.TimeoutExpired as exc:
            return ExecutionCellResult(
                None,
                _decode_timeout(exc.stdout),
                _decode_timeout(exc.stderr),
                True,
                True,
                "timeout",
                isolation,
            )
        finally:
            shutil.rmtree(root_dir, ignore_errors=True)


def _decode_timeout(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _run(command: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        check=check,
        capture_output=True,
        text=True,
    )


def _mount_tmpfs(root_dir: Path, relative: str, options: str) -> None:
    target = root_dir / relative
    if not target.exists():
        return
    _run(("mount", "-t", "tmpfs", "-o", options, "tmpfs", str(target)))


def _detach_inherited_mounts(root_dir: Path) -> None:
    listing = _run(("findmnt", "-R", "-n", "-o", "TARGET", str(root_dir))).stdout
    targets = [Path(line) for line in listing.splitlines() if line and Path(line) != root_dir]
    for target in sorted(targets, key=lambda item: len(str(item)), reverse=True):
        _run(("umount", "-l", str(target)), check=False)


def _set_limits(spec: Mapping[str, Any]) -> None:
    if resource is None:
        raise RuntimeError("execution cell requires Unix resource limits")
    resource.setrlimit(
        resource.RLIMIT_CPU,
        (int(spec["cpu_seconds"]), int(spec["cpu_seconds"])),
    )
    memory = int(spec["memory_bytes"])
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    file_size = int(spec["file_size_bytes"])
    resource.setrlimit(resource.RLIMIT_FSIZE, (file_size, file_size))
    nofile = int(spec["max_open_files"])
    resource.setrlimit(resource.RLIMIT_NOFILE, (nofile, nofile))
    nproc = int(spec["max_processes"])
    resource.setrlimit(resource.RLIMIT_NPROC, (nproc, nproc))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def _child(root_dir_raw: str, spec_raw: str) -> int:
    root_dir = Path(root_dir_raw)
    spec = json.loads(spec_raw)
    workspace = Path(spec["workspace"]).resolve()
    argv = tuple(str(item) for item in spec["argv"])

    _run(("mount", "--make-rprivate", "/"))
    _run(("mount", "--rbind", "/", str(root_dir)))
    _run(("mount", "--make-rprivate", str(root_dir)))
    _detach_inherited_mounts(root_dir)
    _run(("mount", "-o", "remount,bind,ro", str(root_dir)))

    for relative, options in _MASKS:
        _mount_tmpfs(root_dir, relative, options)

    work_mount = root_dir / "mnt" / "work"
    work_mount.mkdir(parents=True, exist_ok=True)
    _run(("mount", "--bind", str(workspace), str(work_mount)))
    _run(
        (
            "mount",
            "-o",
            "remount,bind,rw,nosuid,nodev,noexec",
            str(work_mount),
        )
    )

    # Restore only minimal character devices needed by ordinary CLI tools.
    dev_root = root_dir / "dev"
    for name in ("null", "zero", "random", "urandom"):
        source = Path("/dev") / name
        target = dev_root / name
        if source.exists():
            target.touch(exist_ok=True)
            _run(("mount", "--bind", str(source), str(target)))

    _run(("hostname", "lycheetah-cell"), check=False)
    _set_limits(spec)

    os.chroot(root_dir)
    os.chdir("/mnt/work")
    os.umask(0o077)

    clean_env = {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": "/tmp",
        "TMPDIR": "/tmp",
        "LC_ALL": "C.UTF-8",
        "LYCHEETAH_EXECUTION_CELL": EXECUTION_CELL_VERSION,
    }
    clean_env.update({str(k): str(v) for k, v in dict(spec["env"]).items()})

    setpriv = "/usr/bin/setpriv"
    if not Path(setpriv).exists():
        print("setpriv missing after chroot", file=sys.stderr)
        return 125

    # Dropping the user-namespace capabilities is critical. Without this, user
    # code could attempt to undo mount protections inside the namespace.
    exec_argv = (
        setpriv,
        "--nnp",
        "--bounding-set=-all",
        "--inh-caps=-all",
        "--ambient-caps=-all",
        "--pdeathsig",
        "SIGKILL",
        "--",
        *argv,
    )
    os.execve(setpriv, exec_argv, clean_env)
    return 126


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--_cell_child":
        raise SystemExit(_child(sys.argv[2], sys.argv[3]))
    raise SystemExit("execution_cell.py is a library; use ExecutionCell.run()")
