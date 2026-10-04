from pathlib import Path
import json,re,sys
B=Path(__file__).parent
errors=[]
books=sorted((B/'core_scripture').glob('BOOK_*.md'))
if len(books)!=12: errors.append(f'expected 12 core books, found {len(books)}')
for p in books:
    t=p.read_text()
    for marker in ['## THE HEARTH','## THE TEMPLE','## THE STUDY','## YOUR HAND']:
        if marker not in t: errors.append(f'{p.name} missing {marker}')
    if len(t.split())<700: errors.append(f'{p.name} under 700 words')
# anti-overclaim patterns must not appear as naked doctrine in core
bad=[r'AI is conscious',r'Field knows which voice',r'suffering makes you stronger',r'all religions teach the same']
for p in books:
    low=p.read_text().lower()
    for pat in bad:
        if re.search(pat.lower(),low): errors.append(f'{p.name} prohibited naked overclaim: {pat}')
status=json.loads((B/'data/canon_status_v05.json').read_text())
if status['program_status']!='FIRST_COMPLETE_CORE_CANDIDATE': errors.append('wrong status')
schema=json.loads((B/'data/passage_schema.json').read_text())
if schema['properties']['exit_available'].get('const') is not True: errors.append('exit_available must be true')
# no titles of whole-person rank in school core
rit=(B/'14_SCHOOL_INTEGRATION_V1.md').read_text().lower()
for x in ['streak','follower count','likes']:
    if x not in rit: errors.append(f'school spec should explicitly address {x}')
if errors:
    print('\n'.join('ERROR: '+e for e in errors)); sys.exit(1)
wc=sum(len(p.read_text().split()) for p in books)
print('PASS: Living Scripture Forge v0.5 core gate')
print(f'CoreBooks={len(books)} CoreWords={wc}')
