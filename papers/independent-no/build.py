"""Render the canonical manuscript and protocol into static reading copies."""

from html import escape
from pathlib import Path
import json

from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
OUT = REPO / "docs" / "research"


def render(source_name: str, filename: str, title: str) -> None:
    source = (HERE / source_name).read_text(encoding="utf-8")
    parser = MarkdownIt("commonmark", {"html": False}).enable("table")
    body = parser.render(source)
    # Tables scroll within their own region on narrow screens.
    body = body.replace("<table>", '<div class="table-scroll"><table>')
    body = body.replace("</table>", "</table></div>")
    document = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="A Lycheetah Framework working paper on keeping AI research rejections binding and inspectable.">
<meta name="author" content="Mackenzie Conor James Clark">
<title>{title} · Lycheetah Framework</title>
<link rel="stylesheet" href="independent-no-paper.css">
</head>
<body>
<a class="skip-link" href="#manuscript">Skip to manuscript</a>
<nav class="reading-nav" aria-label="Reading editions">
<a href="../independent-no.html">← Research overview</a>
<a href="independent-no-paper.html">Manuscript</a>
<a href="independent-no-protocol.html">Study protocol</a>
<a href="independent-no.pdf">PDF edition</a>
</nav>
<main id="manuscript" class="manuscript">
{body}
</main>
<footer class="reading-footer">Lycheetah Framework · Working paper v0.1 · 30 September 2026</footer>
</body>
</html>
""".format(title=escape(title), body=body)
    (OUT / filename).write_text(document, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    render("PAPER.md", "independent-no-paper.html", "The Independent No")
    render("EVALUATION_PROTOCOL.md", "independent-no-protocol.html", "Matched evaluation protocol")
    (OUT / "independent-no-paper.md").write_bytes((HERE / "PAPER.md").read_bytes())
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    (OUT / "independent-no-sources.json").write_text(
        json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Generated manuscript HTML, protocol HTML, Markdown, and primary-source ledger.")


if __name__ == "__main__":
    main()
