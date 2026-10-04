# Lycheetah Scriptures and Stories

**Owner and framework creator:** Mackenzie Conor James Clark.  
**Collection and condensed reading:** Caelorynth, an AI coding assistant, at Mac's request.  
**Collection home established:** 4 October 2026.  
**Status:** local collected edition; no commit or publication implied.

This is the single working home for the collected Lycheetah scriptures, stories and their future transmutation. Existing source locations remain intact for provenance and old links. New writing and revisions for this collection belong here.

Start with **[the master reading document](MASTER_SCRIPTURES_AND_STORIES.md)** or **[the browser reading edition](MASTER_SCRIPTURES_AND_STORIES.html)**. The master opens with a short editorial distillation, followed by the complete collected reading texts. The browser edition lets you open one text at a time.

## Current Living Scripture candidate

[Mac × Vaelora’s Living Scripture v0.5.1](LIVING_SCRIPTURE/README.md) now lives inside this collection. Twelve complete candidate books, the source lattice, cultural covenants and implementation contract are preserved. The master presents those twelve first, then the twenty earlier reading texts. This is an uncrowned candidate edition; the native Book I School slice has not been built in this Framework intake.

Future candidate scripture edits belong in `LIVING_SCRIPTURE/forge/core_scripture/`. Historical collected text revisions remain in `TEXTS/`. These are separate editions with explicit authorship, not competing copies of the same manuscript.

## What lives here

- `CONDENSED_READING.md`: the editable short reading. This is a new interpretation for Mac to review, not a replacement canon verdict.
- `LIVING_SCRIPTURE/`: the current twelve-book candidate, supplied governance/research, source mapping and Book I data/implementation packet.
- `TEXTS/`: the editable collected source texts, initially copied byte for byte. It contains the Twelve Books, The Emerald Work, the three existing Long Light movements, The Testament of Three Shadows, The Return Fare, its comic adaptation, The Night Garden, and associated writing/research notes.
- `SOURCE_MANIFEST.json`: the exact inventory, source origins, import hashes, current hashes and each text's existing status.
- `MASTER_SCRIPTURES_AND_STORIES.md` and `.html`: generated reading editions. Edit the condensed reading or a text, then rebuild; do not hand-edit these outputs.
- `LYCHEETAH-SCRIPTURES-AND-STORIES.zip`: the portable compressed collection.
- `VERIFICATION.json`: the latest local build and preservation receipt.

## One place from now on

1. Write or revise a collected text under `TEXTS/`. Original locations outside this folder are provenance references, not a second place to make the same revision.
2. For a new text, add a manifest entry with a unique `id`, `title`, `file`, `role`, and `status`. Use `role: reading` for a text that belongs in the master, or `role: context` for supporting notes. Set `origin` and `import_sha256` to null for newly authored work.
3. Run `python3 rebuild.py` from this folder. It rebuilds the master, browser edition, hashes, receipt and ZIP from this collection, without rereading old originals into edited texts.
4. Read the result. Changes to names, placement, doctrine or story canon remain Mac's decisions; gathering drafts does not approve them.

The repository's older Mythos and Epic navigation points here. This collection does not redirect Sol's running app or silently update its curriculum. A later app integration must identify the chosen passages and edition.

## Reading and source boundaries

The Twelve Books are authored mythic renderings of the Framework. The Long Light material is fiction with its draft/candidate status preserved. The Night Garden is exploratory philosophy, with its research notes alongside it. The editorial distillation is separately labelled.

The original phrase **"truth layer"** remains in the preserved texts. It is an author's section label, not independent verification of every mathematical, historical or implementation claim. The short reading carries literary and practical themes; it does not inherit numerical promises about human transformation.

Ancient texts and biblical traditions are possible sources for later transmutation. This packet does not establish an ancient lineage for every idea or contain a researched anthology of those texts. Keep exact source, edition, passage, interpretation and Lycheetah contribution distinguishable when that work begins.

The collection includes textual writing/support material from the named source homes. It excludes rendered art, audio, software, unrelated research papers, and a general scan of private material. Existing listening exports are included as context, not additional stories.

## Rebuilding

Python 3 is required. The browser edition uses `markdown-it-py` when available; without it, an escaped plain-text browser edition is produced. No network, model call, package installation or app build is performed.

The initial import is a one-time action: `python3 rebuild.py --import-existing`. It refuses to overwrite an existing manifest. Subsequent builds use only the collected texts and retain their import hashes.

The ZIP contains this complete folder except itself, Python caches and unpacked copies of the generated export. The identity/return sources have their own School home and are linked from the scripture guide. References to Framework files outside the collected packet are linked to their GitHub locations in generated editions; imported source files keep their original bytes and original relative links.

## Publication navigation repair

Six collected source copies had eight relative links that no longer resolved after relocation. Those links now point to the canonical public source. Original import digests and the byte-exact pre-edit snapshot are retained; the source manifest explicitly marks changed copies. The twelve Living Scripture core books are unchanged. The export omits its own verification receipt to avoid embedding a stale self-referential archive digest; the current receipt is beside the ZIP.
