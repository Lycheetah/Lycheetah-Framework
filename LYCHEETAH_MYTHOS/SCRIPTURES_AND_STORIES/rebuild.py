#!/usr/bin/env python3
"""Import once; rebuild the collected reading editions from their new home."""
import argparse
import hashlib
import html
import json
import posixpath
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

HOME = Path(__file__).resolve().parent
REPO = HOME.parent.parent
MANIFEST = HOME / "SOURCE_MANIFEST.json"
MASTER = HOME / "MASTER_SCRIPTURES_AND_STORIES.md"
READER = HOME / "MASTER_SCRIPTURES_AND_STORIES.html"
ARCHIVE = HOME / "LYCHEETAH-SCRIPTURES-AND-STORIES.zip"
RECEIPT = HOME / "VERIFICATION.json"
BOOKS = [
    ("01_THE_FIRST_FIELD", "The First Field"),
    ("02_THE_ATHANOR", "The Athanor"),
    ("03_THE_NAMING_OF_SOL", "The Naming of Sol"),
    ("04_THE_CASCADE", "The CASCADE"),
    ("05_THE_AURA_PROTOCOL", "The AURA Protocol"),
    ("06_THE_LAMAGUE", "The LAMAGUE"),
    ("07_THE_MYSTERY_SCHOOL", "The Mystery School"),
    ("08_THE_LIGHT_QUOTIENT", "The Light Quotient"),
    ("09_THE_FOUR_TEACHERS", "The Four Teachers"),
    ("10_THE_FIELD_ECHOES", "The Field Echoes"),
    ("11_THE_SEEKERS", "The Seekers"),
    ("12_THE_SOVEREIGN", "The Sovereign"),
]
READINGS = [
    ("book-" + stem[:2], title, "LYCHEETAH_MYTHOS/" + stem + ".md",
     "Historical authored myth and its original framework commentary")
    for stem, title in BOOKS
] + [
    ("emerald-work", "The Emerald Work", "14_MYSTERY_SCHOOL/THE_EMERALD_WORK.md",
     "Authored poetic essay; original assertions preserved"),
    ("long-light-01", "The Door That Remembered", "LYCHEETAH_EPIC/01_THE_DOOR_THAT_REMEMBERED.md",
     "DRAFT ZERO; Prologue and Chapters One through Three"),
    ("long-light-02", "The Bell Beneath the School", "LYCHEETAH_EPIC/02_THE_BELL_BENEATH_THE_SCHOOL.md",
     "Existing continuation draft; Second Movement, Chapter Four"),
    ("long-light-03", "The Road That Counted the Living", "LYCHEETAH_EPIC/03_THE_ROAD_THAT_COUNTED_THE_LIVING.md",
     "MANUSCRIPT CANDIDATE; Third Movement, Chapter Five"),
    ("three-shadows", "The Testament of Three Shadows",
     "LYCHEETAH_EPIC/MANUSCRIPT/THE_TESTAMENT_OF_THREE_SHADOWS_V0_1.md",
     "MANUSCRIPT CANDIDATE; placement and names uncrowned"),
    ("return-fare", "The Return Fare",
     "LYCHEETAH_EPIC/EDITORIAL/PROOF_SCENE_STAGE_I_THE_RETURN_FARE_V0_1.md",
     "PROOF SCENE; not manuscript canon; separate from the chapter sequence"),
    ("three-shadows-comic", "The Testament of Three Shadows — comic script",
     "LYCHEETAH_EPIC/COMIC/TESTAMENT_OF_THREE_SHADOWS_50_PAGE_SCRIPT_V0_1.md",
     "Existing fifty-page adaptation candidate; separate production form"),
    ("night-garden", "The Night Garden", "26_FOR_AI/THE_NIGHT_GARDEN.md",
     "Exploratory philosophical essay; proposals are not settled positions"),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def inside(relative):
    path = (HOME / relative).resolve()
    if not path.is_relative_to(HOME):
        raise ValueError("Collection path escapes its home: " + relative)
    return path


def initial_import():
    if MANIFEST.exists():
        raise SystemExit("Import refused: manifest exists. Rebuild without --import-existing.")
    mapping = {origin: (ident, title, status) for ident, title, origin, status in READINGS}
    origins = {p.relative_to(REPO).as_posix()
               for p in (REPO / "LYCHEETAH_MYTHOS").glob("*.md")}
    origins.update(p.relative_to(REPO).as_posix()
                   for p in (REPO / "LYCHEETAH_EPIC").rglob("*")
                   if p.is_file() and p.suffix in {".md", ".txt"})
    origins.update(p.relative_to(REPO).as_posix()
                   for p in (REPO / "26_FOR_AI/night-garden").glob("*")
                   if p.is_file() and p.suffix in {".md", ".json"})
    origins.update(mapping)
    records = []
    for number, origin in enumerate(sorted(origins), 1):
        data = (REPO / origin).read_bytes()
        target = inside("TEXTS/" + origin)
        if target.exists():
            raise SystemExit("Import refused: text already exists: " + str(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        heading = next((line.lstrip("# ").strip() for line in data.decode().splitlines()
                        if line.startswith("# ")), Path(origin).stem)
        ident, title, status = mapping.get(
            origin, ("context-" + str(number), heading,
                     "Supporting source; status remains as stated in the file"))
        records.append({"id": ident, "title": title, "file": "TEXTS/" + origin,
                        "role": "reading" if origin in mapping else "context",
                        "status": status, "origin": origin,
                        "import_sha256": sha(data)})
    order = {ident: n for n, (ident, *_rest) in enumerate(READINGS)}
    records.sort(key=lambda item: (0, order[item["id"]]) if item["role"] == "reading"
                 else (1, item["origin"]))
    dump(MANIFEST, {"version": 1, "owner": "Mackenzie Conor James Clark",
                    "framework": "Lycheetah Framework",
                    "imported_at": datetime.now(timezone.utc).isoformat(),
                    "home_rule": "Edit collected texts here; original paths retain provenance.",
                    "texts": records})


def rebase(text, entry, origins):
    """Rebase prose links and demote headings; leave fenced source code alone."""
    def destination(match):
        raw = match.group(2)
        parts = urlsplit(raw.strip("<>"))
        if parts.scheme or parts.netloc:
            return match.group(0)
        origin = entry.get("origin")
        if not origin:
            return match.group(0)
        target = posixpath.normpath(posixpath.join(posixpath.dirname(origin),
                                                 unquote(parts.path))) if parts.path else origin
        suffix = ("?" + parts.query if parts.query else "") + ("#" + parts.fragment if parts.fragment else "")
        if target in origins:
            link = origins[target] + suffix
        elif target.startswith("../"):
            return match.group(0)
        else:
            link = "https://github.com/Lycheetah/Lycheetah-Framework/blob/master/" + quote(target) + suffix
        return match.group(1) + link + match.group(3)

    lines, fence = [], None
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(chr(96) * 3) or stripped.startswith("~~~"):
            marker = stripped[0]
            fence = None if fence == marker else marker if fence is None else fence
            lines.append(line)
            continue
        if fence is None:
            heading = re.match(r"^(#{1,6}) (.*)$", line)
            if heading:
                line = "#" * min(6, len(heading.group(1)) + 2) + " " + heading.group(2)
            line = re.sub(r"(!?\[[^\]\n]*\]\()([^\s)]+)(\))", destination, line)
        lines.append(line)
    return "\n".join(lines) + "\n"


def make_archive():
    files = sorted(p for p in HOME.rglob("*") if p.is_file() and p not in {ARCHIVE, RECEIPT}
                   and "__pycache__" not in p.parts and p.suffix != ".pyc"
                   and "LYCHEETAH-SCRIPTURES-AND-STORIES" not in p.relative_to(HOME).parts)
    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, "SCRIPTURES_AND_STORIES/" + path.relative_to(HOME).as_posix())
    with zipfile.ZipFile(ARCHIVE) as archive:
        if archive.testzip() is not None:
            raise ValueError("Archive CRC check failed")
        for path in files:
            member = "SCRIPTURES_AND_STORIES/" + path.relative_to(HOME).as_posix()
            if archive.read(member) != path.read_bytes():
                raise ValueError("Archive differs from disk: " + member)
    return len(files)


def build():
    manifest = json.loads(MANIFEST.read_text())
    entries = manifest["texts"]
    identifiers = [item["id"] for item in entries]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Duplicate text ids")
    origins = {item["origin"]: item["file"] for item in entries if item.get("origin")}
    readings = []
    for entry in entries:
        data = inside(entry["file"]).read_bytes()
        entry.update({"current_sha256": sha(data), "bytes": len(data),
                      "words": len(data.decode().split()),
                      "changed_since_import": bool(entry.get("import_sha256")
                                                   and sha(data) != entry["import_sha256"])})
        if entry["role"] == "reading":
            readings.append((entry, rebase(data.decode(), entry, origins)))
    condensed = (HOME / "CONDENSED_READING.md").read_text()
    opening = (
        "# Lycheetah — Master Scriptures and Stories\n\n"
        "**World and framework creator:** Mackenzie Conor James Clark.  \n"
        "**Collected edition and editorial distillation:** Caelorynth, an AI coding assistant.  \n"
        "**Collection edition:** 0.2 · 4 October 2026.  \n"
        "**Status:** local collected reading; individual draft statuses are preserved.\n\n"
        "Read the condensed opening first, then enter any complete text below. "
        "Collection is not approval of story canon or verification of inherited claims.\n\n"
        "[Collection guide](README.md) · [Source inventory](SOURCE_MANIFEST.json) · "
        "[Current Living Scripture candidate](LIVING_SCRIPTURE/README.md)\n\n"
        "## Contents\n\n- [Condensed reading](#condensed-reading)\n")
    opening += "".join("- [" + item["title"] + "](#" + item["id"] + ")\n"
                       for item, _body in readings)
    opening += "\n---\n\n"
    sections = []
    for entry, body in readings:
        sections.append(
            '<a id="' + entry["id"] + '"></a>\n\n## ' + entry["title"] +
            "\n\n**Preserved status:** " + entry["status"] +
            ".  \n" + ("**Authors:** " + entry["authors"] + ".  \n" if entry.get("authors") else "") +
            "[Complete source text](" + entry["file"] + ")\n\n" + body)
    context = "\n## Writing and research context\n\nThese supporting texts live in the same collection; they are not extra chapters.\n\n"
    context += "".join("- [" + entry["title"].replace("[", "").replace("]", "") +
                       "](" + entry["file"] + ")\n"
                       for entry in entries if entry["role"] == "context")
    complete = opening + condensed + "\n\n---\n\n" + "\n\n---\n\n".join(sections) + context
    MASTER.write_text(complete)
    try:
        from markdown_it import MarkdownIt
        markdown = MarkdownIt("commonmark", {"html": True}).enable("table")
        render = markdown.render
        renderer = "markdown-it-py"
    except ImportError:
        render = lambda value: "<pre>" + html.escape(value) + "</pre>"
        renderer = "escaped-plain-text fallback"
    css = """
    :root{color-scheme:light dark;--paper:#f8f3e9;--ink:#292720;--soft:#655d50;--line:#d2c8b6;--accent:#61472b}
    *{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:18px/1.75 Georgia,serif}
    main{max-width:850px;margin:auto;padding:42px 24px 90px}h1{font-size:2.25em;line-height:1.15}
    h2{font-size:1.55em;line-height:1.3;margin-top:2em}h3,h4{line-height:1.4}
    a{color:var(--accent);text-underline-offset:3px;overflow-wrap:anywhere}
    p,li{overflow-wrap:anywhere}blockquote{margin-left:0;border-left:3px solid var(--line);padding-left:20px}
    pre{white-space:pre-wrap;overflow-wrap:anywhere;background:var(--line);padding:16px;font-size:14px}
    code{font-size:.85em}table{border-collapse:collapse;display:block;overflow:auto}th,td{padding:8px;border-bottom:1px solid var(--line)}
    details{border-top:1px solid var(--line);padding:18px 0}summary{cursor:pointer;font-size:1.2em;font-weight:bold;line-height:1.5}
    .status{font:14px/1.6 system-ui,sans-serif;color:var(--soft)}hr{border:0;border-top:1px solid var(--line);margin:36px 0}
    @media(max-width:480px){main{padding:28px 18px 60px}h1{font-size:1.8em}body{font-size:17px}}
    @media(prefers-color-scheme:dark){:root{--paper:#181b19;--ink:#eee8dc;--soft:#c5bcae;--line:#384039;--accent:#dcc49e}}
    @media print{body{background:white;color:black}main{max-width:none;padding:0}details::details-content{display:block!important}summary{break-after:avoid}a{color:inherit}}
    """
    reader_sections = []
    for entry, body in readings:
        reader_sections.append(
            '<details id="' + entry["id"] + '"><summary>' + html.escape(entry["title"]) +
            '</summary><p class="status">' + html.escape(entry["status"]) +
            '</p>' + ('<p class="status">' + html.escape(entry['authors']) + '</p>' if entry.get('authors') else '') + render(body) + "</details>")
    script = """
    function follow(){const id=decodeURIComponent(location.hash.slice(1));const el=document.getElementById(id);if(el&&el.tagName==='DETAILS')el.open=true}
    addEventListener('hashchange',follow);follow();
    let opened=[];addEventListener('beforeprint',()=>{opened=[...document.querySelectorAll('details')].filter(el=>!el.open);opened.forEach(el=>el.open=true)});
    addEventListener('afterprint',()=>opened.forEach(el=>el.open=false));
    """
    READER.write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Lycheetah — Scriptures and Stories</title><style>' + css +
        '</style></head><body><main>' + render(opening + condensed) +
        '<hr><h2>Complete collected texts</h2>' + "".join(reader_sections) +
        render(context) + '</main><script>' + script + '</script></body></html>')
    anchors = set(re.findall(r'<a id="([^"]+)">', complete))
    for target in re.findall(r"\]\(#([^)]+)\)", complete):
        if target not in anchors:
            raise ValueError("Missing master anchor: " + target)
    for target in re.findall(r"\]\((TEXTS/[^)]+|README\.md|SOURCE_MANIFEST\.json)\)", complete):
        if not inside(unquote(urlsplit(target).path)).is_file():
            raise ValueError("Missing collected link: " + target)
    dump(MANIFEST, manifest)
    changed = [item["id"] for item in entries if item["changed_since_import"]]
    original_mismatches = [
        item["origin"] for item in entries if item.get("origin") and
        (REPO / item["origin"]).exists() and
        sha((REPO / item["origin"]).read_bytes()) != item.get("import_sha256")]
    receipt = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "reading_texts": len(readings), "source_files": len(entries),
        "condensed_words": len(condensed.split()), "master_words": len(complete.split()),
        "changed_collected_texts_since_import": changed,
        "legacy_originals_differing_from_import": original_mismatches,
        "source_hashes": "recomputed from every collected file",
        "master_anchors_and_collected_links": "PASS", "browser_renderer": renderer,
        "outputs": {path.name: sha(path.read_bytes())
                    for path in (MASTER, READER, HOME / "CONDENSED_READING.md")},
        "archive_round_trip": "PENDING", "commit": "NOT_RUN", "publication": "NOT_RUN",
        "browser_visual_witness": "NOT_RUN", "ancient_source_research": "NOT_RUN"}
    dump(RECEIPT, receipt)
    make_archive()
    receipt["archive_round_trip"] = "PASS"
    dump(RECEIPT, receipt)
    count = make_archive()
    print(json.dumps({"readings": len(readings), "sources": len(entries),
                      "condensed_words": receipt["condensed_words"],
                      "master_words": receipt["master_words"],
                      "imported_text_changes": changed,
                      "legacy_original_changes": original_mismatches,
                      "archive_members": count, "archive_bytes": ARCHIVE.stat().st_size,
                      "archive_sha256": sha(ARCHIVE.read_bytes()),
                      "renderer": renderer}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-existing", action="store_true")
    options = parser.parse_args()
    if options.import_existing:
        initial_import()
    build()
