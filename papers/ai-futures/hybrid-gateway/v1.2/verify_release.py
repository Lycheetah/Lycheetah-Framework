"""Verify the current release tree against its complete SHA-256 manifest."""
from pathlib import Path
import hashlib


def check(root: Path | None = None):
    root = root or Path(__file__).resolve().parent
    lines = (root / 'SHA256SUMS.txt').read_text().splitlines()
    seen = set()
    for line in lines:
        digest, name = line.split('  ', 1)
        if name in seen or name.startswith('/') or '..' in Path(name).parts:
            raise ValueError('invalid or duplicated manifest entry')
        seen.add(name)
        target = root / name
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError('release checksum mismatch: '+name)
    disk = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()
            and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts
            and p.name != 'SHA256SUMS.txt' and p.suffix not in ('.pyc',)}
    if disk != seen:
        raise ValueError('release manifest incomplete: '+repr(sorted(disk ^ seen)))
    return len(seen)


if __name__ == '__main__':
    print('VERIFIED',check(),'files')
