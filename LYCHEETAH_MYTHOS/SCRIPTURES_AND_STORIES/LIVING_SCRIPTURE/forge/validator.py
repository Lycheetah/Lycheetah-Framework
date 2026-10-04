from pathlib import Path
import json,sys
B=Path(__file__).parent
errors=[]
books=json.loads((B/"data/book_map.json").read_text())
lattice=json.loads((B/"data/source_lattice.json").read_text())
claims=json.loads((B/"data/claim_register.json").read_text())
status=json.loads((B/"data/status.json").read_text())
if len(books)!=12: errors.append("expected 12 books")
if sum(len(b["chapters"]) for b in books)!=144: errors.append("expected 144 chapters")
if any(len(b["chapters"])!=12 for b in books): errors.append("every book must have 12 chapters")
if len(lattice)<15: errors.append("lattice too small")
if len({x["id"] for x in lattice})!=len(lattice): errors.append("duplicate lattice IDs")
required={"MYTH","DEVOTIONAL","THEOLOGICAL","HISTORICAL","PHILOSOPHICAL","EMPIRICAL","NORMATIVE","INTERPRETIVE","CONDITIONAL","CONJECTURE","EXPERIENTIAL","FICTION","MACHINE_QUESTION","MYSTERY"}
have={x["id"] for x in claims["registers"]}
if required-have: errors.append("missing claim registers")
if status["publication_claims"]["systematic_review"]: errors.append("false systematic-review claim")
book=(B/"12_BOOK_I_THE_OPEN_FIELD_CANDIDATE.md").read_text()
for n in ["The chair beside the fire","Machine Window","YOUR HAND","No one will count the days"]:
 if n not in book: errors.append("Book I missing "+n)
if errors:
 [print("ERROR:",e) for e in errors]; sys.exit(1)
print("PASS: Living Scripture Forge v0.4 structural gate")
print(f"Books={len(books)} Chapters={sum(len(b['chapters']) for b in books)} LatticeEntries={len(lattice)} ClaimRegisters={len(claims['registers'])}")
