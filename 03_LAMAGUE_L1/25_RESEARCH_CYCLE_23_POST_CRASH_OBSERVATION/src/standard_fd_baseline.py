"""Conventional POSIX descriptor-anchored no-clobber copy, no LAMAGUE format.

This independently uses the same well-established OS primitives as Cycle10.
For parity comparisons in *disposable test folders only*.
"""
import hashlib
import os
from pathlib import Path, PurePosixPath
import secrets
import stat
from typing import Callable

O_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def _parent(rootfd: int, rel: str) -> int:
    parts = PurePosixPath(rel).parts
    if not parts or PurePosixPath(rel).is_absolute() or any(x in ('.', '..') for x in parts):
        raise ValueError('invalid relative')
    fd = os.dup(rootfd)
    try:
        for component in parts[:-1]:
            nxt = os.open(component, O_DIR, dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd
    except BaseException:
        os.close(fd)
        raise


def _same(rootfd: int, rel: str, fd: int) -> bool:
    try:
        check = _parent(rootfd, rel)
        try:
            a, b = os.fstat(check), os.fstat(fd)
            return (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)
        finally:
            os.close(check)
    except OSError:
        return False


def copy_one(src_root: Path, dst_root: Path, rel: str, expected_hash: str, expected_size: int,
             *, before_commit: Callable[[], None] | None = None) -> str:
    """Return VERIFIED or FAILED_NO_COMMIT; no independent full sandbox claim."""
    root_s = os.open(src_root, O_DIR)
    try:
        root_d = os.open(dst_root, O_DIR)
        try:
            p_s = _parent(root_s, rel)
            try:
                p_d = _parent(root_d, rel)
                try:
                    stage = '.stdlib-' + secrets.token_hex(16) + '.stage'
                    made_stage = False
                    try:
                        s = os.open(PurePosixPath(rel).name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=p_s)
                        try:
                            if not stat.S_ISREG(os.fstat(s).st_mode):
                                return 'FAILED_NO_COMMIT'
                            t = os.open(stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=p_d)
                            made_stage = True
                            try:
                                h = hashlib.sha256()
                                count = 0
                                while chunk := os.read(s, 1024 * 256):
                                    count += len(chunk)
                                    if count > expected_size:
                                        return 'FAILED_NO_COMMIT'
                                    h.update(chunk)
                                    os.write(t, chunk)
                                os.fsync(t)
                            finally:
                                os.close(t)
                            if h.hexdigest() != expected_hash or count != expected_size:
                                return 'FAILED_NO_COMMIT'
                        finally:
                            os.close(s)
                        if before_commit:
                            before_commit()
                        if not _same(root_d, rel, p_d) or not _same(root_s, rel, p_s):
                            return 'FAILED_NO_COMMIT'
                        try:
                            os.link(stage, PurePosixPath(rel).name, src_dir_fd=p_d, dst_dir_fd=p_d, follow_symlinks=False)
                        except FileExistsError:
                            return 'FAILED_NO_COMMIT'
                        # Under hostile rename after this last check, lexical confinement
                        # is not a proved property; hardlink remains attached to fd inode.
                        return 'VERIFIED' if _same(root_d, rel, p_d) else 'FAILED_POSTCOMMIT'
                    finally:
                        if made_stage:
                            os.unlink(stage, dir_fd=p_d)
                finally:
                    os.close(p_d)
            finally:
                os.close(p_s)
        finally:
            os.close(root_d)
    finally:
        os.close(root_s)
