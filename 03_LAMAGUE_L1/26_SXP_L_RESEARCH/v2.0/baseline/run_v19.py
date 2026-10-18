"""Run SXP-L v1.9 from the release directory without installing packages."""
import sys
from pathlib import Path
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here/'runtime'))
sys.path.insert(0,str(here))
from reference19 import write_bundle
import argparse
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('source');p.add_argument('--out',default='out_v19')
a=p.parse_args()
r=write_bundle(Path(a.source).read_text(encoding='utf8'),Path(a.out))
print(f'Validated {len(r["bindings"])} v1.9 scoped clarification(s); authorized actions: 0')
