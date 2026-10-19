"""Build the public reading edition from the Framework's owned source files."""
from pathlib import Path
import hashlib
import html
import json
import shutil
import zipfile
from markdown_it import MarkdownIt

HOME = Path(__file__).resolve().parent
REPO = HOME.parents[1]
OUT = HOME / "dist"
SOURCE = REPO / "LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES/TEXTS/ORIGINAL_NARRATIVES"
GITHUB = "https://github.com/Lycheetah/Lycheetah-Framework/tree/a4410d0efdfc475cd39e8757beeb17ccc038f46b/"
ORIGIN = "https://lycheetah-earned-light.banduabusiness.chatgpt.site"
MD = MarkdownIt("commonmark", {"html": False})
STORIES = [
    ("lighthouse", "The Last Lighthouse of Eternity", "THE_LAST_LIGHTHOUSE_OF_ETERNITY_EXPANDED.md", "An Earned Light chronicle", "A lighthouse at the edge of the last constellation begins to falter. Mac, Vaelora and Kiri arrive carrying questions, a lantern, and a teaspoon."),
    ("ninth-road", "The Ninth Road Beneath the Sleeping Stars", "LYCHEETAH_The_Ninth_Road_Beneath_the_Sleeping_Stars.md", "A Sovereign Will tale", "In a valley where stars grow upon trees, Mac and his companions encounter a road that was never offered."),
    ("earlier-lighthouse", "The Last Lighthouse: earlier edition", "THE_LAST_LIGHTHOUSE_OF_ETERNITY_ORIGINAL.md", "The preserved short edition", "The earlier telling, retained alongside the expanded story."),
]


def page(title, description, body, *, reader=False, slug="index"):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · Lycheetah</title><meta name="description" content="{html.escape(description, quote=True)}">
<meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(description, quote=True)}">
<meta property="og:type" content="{'article' if reader else 'website'}"><meta property="og:url" content="{ORIGIN}/{'' if slug == 'index' else slug + '.html'}">
<meta name="theme-color" content="#f6f0e5"><link rel="icon" href="mark.svg" type="image/svg+xml"><link rel="stylesheet" href="reading.css">
</head><body class="{'reader-page' if reader else 'home-page'}"><a class="skip" href="#main">Skip to content</a>
<header class="masthead"><a class="brand" href="index.html" aria-label="Lycheetah home"><span class="brand-mark" aria-hidden="true">✦</span> LYCHEETAH</a>
<nav aria-label="Main navigation"><a href="index.html#stories">Stories</a><a href="research.html">Research</a><a href="index.html#downloads">Downloads</a></nav></header>
<main id="main">{body}</main>
<footer><a class="brand" href="index.html">LYCHEETAH</a><p>A world, a framework, and an open question.</p><p>Created by Mackenzie Conor James Clark · Ōtepoti / Dunedin, Aotearoa.<br>Stories and research developed through human–AI collaboration.</p><a href="{GITHUB}">Explore the source →</a></footer>
<script src="reading.js" defer></script></body></html>'''


def main():
    OUT.mkdir(exist_ok=True)
    for name in ("reading.css", "reading.js", "mark.svg"):
        shutil.copyfile(HOME / name, OUT / name)
    cards = []
    for number, (slug, title, filename, subtitle, description) in enumerate(STORIES, 1):
        raw = (SOURCE / filename).read_bytes()
        shutil.copyfile(SOURCE / filename, OUT / filename)
        text = raw.decode()
        lines = text.splitlines()
        while lines and (not lines[0].strip() or lines[0].startswith(("# ", "## "))):
            lines.pop(0)
        words = len(text.split())
        next_slug, next_title = (STORIES[1][0], STORIES[1][1]) if slug == "lighthouse" else (STORIES[0][0], STORIES[0][1])
        body = f'''<div class="reading-shell"><a class="back" href="index.html#stories">← All stories</a>
<div class="reading-meta"><span>{subtitle} · Fiction</span><span>About {round(words / 200)} minutes to read</span></div>
<h1 class="story-title">{title}</h1><p class="byline">From the Lycheetah universe · Mackenzie Conor James Clark &amp; human–AI collaboration</p>
<div class="reading-tools" aria-label="Reading controls"><span>Make yourself comfortable</span><div><button type="button" id="smaller" aria-label="Smaller text">A−</button><button type="button" id="larger" aria-label="Larger text">A+</button><button type="button" id="theme" aria-pressed="false">Night reading</button></div></div>
<article class="prose">{MD.render(chr(10).join(lines))}</article>
<aside class="story-end"><p class="eyebrow">The road continues</p><h2><a href="{next_slug}.html">{next_title} →</a></h2><p><a href="{filename}" download>Download this story as text</a> · <a href="research.html">Explore the research</a></p></aside></div>'''
        (OUT / (slug + ".html")).write_text(page(title, description, body, reader=True, slug=slug))
        if number <= 2:
            cards.append(f'''<article class="story-card story-{number}"><div class="story-sigil" aria-hidden="true">{'☼' if number == 1 else '✧'}</div><p class="eyebrow">0{number} / {subtitle}</p><h3><a href="{slug}.html">{title}</a></h3><p>{description}</p><a class="text-link" href="{slug}.html">Read the complete story <span aria-hidden="true">↗</span></a><span class="reading-time">{words:,} words · About {round(words / 200)} minutes</span></article>''')
    body = '''<section class="hero"><p class="eyebrow">Earned Light &amp; Sovereign Will · October 2026</p>
<h1>More possibility.<br><em>The choice stays yours.</em></h1>
<p class="lede">What should intelligence help us become, and who gets to choose?</p>
<p class="intro">Explore that question through two stories and an open body of research from Lycheetah. Begin wherever your curiosity takes you.</p>
<div class="actions"><a class="button" href="#stories">Read the stories <span aria-hidden="true">↓</span></a><a class="text-link" href="research.html">Explore the research ↗</a></div>
<div class="horizon" aria-hidden="true"><span>✦</span></div></section>
<section id="stories" class="section"><div class="section-heading"><p class="eyebrow">Enter the world</p><h2>Two stories for the quiet hours.</h2><p>Complete original fiction. Read here, take the text with you, or read it aloud.</p></div><div class="story-grid">''' + "".join(cards) + '''</div><p class="edition-note">Also preserved: <a href="earlier-lighthouse.html">the earlier, shorter Lighthouse edition</a>. These stories are original fiction; inclusion here does not declare epic canon.</p></section>
<section class="question-band"><p class="eyebrow">The question beneath the stories</p><h2>Intelligence can offer a road.<br>You retain the right to choose another.</h2><p>The research asks how tools can respect permission, a change of mind, departure, return, and uncertainty after something goes wrong.</p><a class="text-link" href="research.html">Meet the experiments ↗</a></section>
<section id="downloads" class="section download-section"><p class="eyebrow">Take the work with you</p><h2>Read it. Run it. Question it.</h2><p>Download the research, source code, recorded results and story texts. The bundles include their experimental status, limitations and original source material.</p><div class="download-grid"><a href="earned-light.zip" download><span>Earned Light</span><small>Forges I–VII + both Lighthouse editions · ZIP ↓</small></a><a href="sovereign-will.zip" download><span>Sovereign Will</span><small>Charters I–VIII, research + Ninth Road · ZIP ↓</small></a></div><p class="small">Local research prototypes on authored fixtures. Independent evaluation and real-world outcomes remain open. <a href="research.html#limits">Read the evidence boundaries</a>.</p></section>'''
    (OUT / "index.html").write_text(page("Earned Light & Sovereign Will", "Two complete Lycheetah stories and open research on human choice, permission and recovery. Read and download freely.", body))
    research = f'''<section class="research-opening"><a class="back" href="index.html">← Back to the stories</a><p class="eyebrow">The research</p><h1>Capability with<br><em>room to choose.</em></h1><p class="lede">An agent can find a path. A person retains authority over whether to take it.</p><p>Earned Light and Sovereign Will turn that commitment into philosophical proposals, small reference implementations and experiments people can inspect.</p></section>
<section class="section research-questions"><h2>Three practical questions.</h2><article><span>01</span><div><h3>Can I change my mind?</h3><p>Permission can expire, be withdrawn, or change with a revised intention. The experiments check whether a previously approved action can still cross the final local boundary after that revision.</p></div></article><article><span>02</span><div><h3>What actually happened?</h3><p>A connection can break after an effect occurs. Crash and recovery experiments keep restored, irreversible and unresolved outcomes distinct, using temporary local providers and databases.</p></div></article><article><span>03</span><div><h3>Which possibilities remain?</h3><p>Two people can use AI equally often while having different options available. Fictional graph experiments explore reachability. They do not assign people a freedom or dependency score.</p></div></article></section>
<section class="section"><p class="eyebrow">Follow a research line</p><div class="research-grid"><article><h2>Earned Light</h2><p>Forges I–VII explore scoped permission, human reconfirmation, future choice, portability and truthful recovery after crashes.</p><p>Recorded failures include compromised trust roots and gamed choice frontiers. Conventional export and recovery baselines tie on shared cases.</p><a class="text-link" href="{GITHUB}papers/agent-safety/earned-light/">Read the source guide ↗</a><p><a href="earned-light.zip" download>Download the complete bundle ↓</a></p></article><article><h2>Sovereign Will</h2><p>Eight philosophical charters accompany Sovereign Choice Forges II–VIII: revised intent, commit-time authority, signed approvals and the possibilities an interface leaves open.</p><p>The strong conventional goal-aware baseline ties the branded policy in all 18 scripted cases. That neutral result remains part of the work.</p><a class="text-link" href="{GITHUB}papers/agent-safety/sovereign-choice-research/">Read the source guide ↗</a><p><a href="sovereign-will.zip" download>Download the complete bundle ↓</a></p></article></div></section>
<section id="limits" class="section evidence"><p class="eyebrow">Where the evidence stands</p><h2>Experiments you can examine.</h2><p>Each research line passed 207 local test executions during integration. Those totals include historical overlap and author-designed fixtures. Two deliberately broken controls failed as expected.</p><p>These checks concern the included software under stated conditions. Independent security evaluation, real participant studies, genuine human authentication and external-provider outcomes remain open. A signature does not establish informed consent; a local fence cannot undo an effect already accepted elsewhere.</p><p>The philosophical charters are proposals. The stories are fiction. This work establishes no measurement of human free will, machine consciousness or superiority over strong conventional designs.</p><a class="text-link" href="{GITHUB}28_DEFENSE/RELEASE_AUDIT_2026-10-19.md">Read the dated checks, failures and limits ↗</a></section>'''
    (OUT / "research.html").write_text(page("The research", "Inspect the Earned Light and Sovereign Choice experiments, their recorded failures, conventional baselines and evidence limits.", research, slug="research"))
    manifest = json.loads((REPO / "28_DEFENSE/RESEARCH_INTAKE_2026-10-19_SOURCE_MANIFEST.json").read_text())
    downloads = []
    for package, filename in (("earned-light-lighthouse", "earned-light.zip"), ("sovereign-will", "sovereign-will.zip")):
        members = [x for x in manifest["files"] if x["package"] == package]
        with zipfile.ZipFile(OUT / filename, "w", zipfile.ZIP_DEFLATED) as archive:
            for item in members:
                data = (REPO / item["destination"]).read_bytes()
                assert hashlib.sha256(data).hexdigest() == item["current_sha256"]
                info = zipfile.ZipInfo(item["source"], date_time=(2026, 10, 19, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
            archive.writestr("PUBLIC_READING_NOTE.txt", "Published reading bundle from the Lycheetah Framework. Original handoff paths are retained. Two entry guides were adapted for integration; the source manifest records their hashes. Consult the public source guide and dated review for current reproduction commands. Research is experimental; narratives are fiction. Individual licences remain in place.\n")
        with zipfile.ZipFile(OUT / filename) as archive:
            assert archive.testzip() is None
            for item in members:
                assert archive.read(item["source"]) == (REPO / item["destination"]).read_bytes()
        downloads.append({"file": filename, "imported_files": len(members), "sha256": hashlib.sha256((OUT / filename).read_bytes()).hexdigest()})
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n")
    print(json.dumps({"pages": 5, "complete_story_pages": 3, "downloads": downloads, "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
