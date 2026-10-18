"""Create and verify deterministic file manifests and handoff archives (lab only)."""
from pathlib import Path
import hashlib, zipfile
ROOT=Path(__file__).resolve().parent.parent
FOLDER=ROOT/'earned_trust_cycle_006'
SKIP={'SHA256SUMS.txt'}

def export_files(folder):
    return [p for p in sorted(folder.rglob('*')) if p.is_file() and
            '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.pyo')]

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

if __name__ == '__main__':
    files=[p for p in export_files(FOLDER) if p.name not in SKIP]
    manifest=''.join(f'{digest(p)}  {p.relative_to(FOLDER)}\n' for p in files)
    (FOLDER/'SHA256SUMS.txt').write_text(manifest,encoding='utf-8')
    c6zip=ROOT/'earned_trust_cycle_006.zip'
    with zipfile.ZipFile(c6zip,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in export_files(FOLDER):
            z.write(p,p.relative_to(ROOT))
    combined=ROOT/'earned_trust_cycles_001_006_complete.zip'
    master=ROOT/'EARNED_TRUST_MASTER_HANDOFF_CYCLES_001_006.md'
    with zipfile.ZipFile(combined,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.write(master,master.name)
        for cycle in range(1,7):
            folder=ROOT/f'earned_trust_cycle_{cycle:03d}'
            for p in export_files(folder):
                z.write(p,p.relative_to(ROOT))
    for path in (c6zip,combined):
        with zipfile.ZipFile(path) as z:
            result=z.testzip()
            assert result is None, (path,result)
        print(path.name,path.stat().st_size,'bytes,',len(zipfile.ZipFile(path).namelist()),'files; zip check OK')
    print('Cycle 006 checksums:',len(files),'files',digest(FOLDER/'SHA256SUMS.txt'))
