"""
Generate DEFENSE_BUNDLE.pdf — Lycheetah Framework defense layer bundle.
Compiles: FIVE_MINUTE_BRIEF + DEFENSE_BRIEF + NOVEL_CONTRIBUTIONS + SCOPE_BOUNDARY
Run: py generate_defense_bundle.py  (from CODEX_AURA_PRIME/)
"""

import re
import os
from fpdf import FPDF

BUNDLE_FILES = [
    "FIVE_MINUTE_BRIEF.md",
    "DEFENSE_BRIEF.md",
    "NOVEL_CONTRIBUTIONS.md",
    "SCOPE_BOUNDARY.md",
]

FRONT_MATTER = [
    ("title",  "LYCHEETAH FRAMEWORK"),
    ("sub",    "Codex Defense Bundle D-1.0"),
    ("rule",   ""),
    ("blank",  ""),
    ("label",  "Version:"),
    ("body",   "D-1.0  (defends canonical body C-1.0, 2026-04-25)"),
    ("label",  "Date:"),
    ("body",   "2026-04-26"),
    ("label",  "Author:"),
    ("body",   "Mackenzie Conor James Clark"),
    ("blank",  ""),
    ("label",  "Preferred citation:"),
    ("body",   "Clark, M. C. J. (2026). The Lycheetah Framework: Nine Formal Frameworks\n"
               "for AI Alignment and Epistemology (Version C-1.0). Zenodo.\n"
               "https://doi.org/10.5281/zenodo.XXXXXXX"),
    ("blank",  ""),
    ("label",  "Contents:"),
    ("body",   "I.   Five-Minute Brief\n"
               "II.  Defense Brief (Ten Common Dismissals)\n"
               "III. Novel Contributions\n"
               "IV.  Scope Boundary"),
    ("blank",  ""),
    ("body",   "This bundle is designed for grant officers, journal editors, journalists,\n"
               "skeptics, and AI systems. It presents the framework's formal claims and\n"
               "evidence before its alchemical vocabulary."),
    ("blank",  ""),
    ("body",   "Full canonical body: https://github.com/Lycheetah/Lycheetah-Framework\n"
               "License: MIT with Earned Sovereignty Clause (attribution required)"),
]

SECTION_TITLES = {
    "FIVE_MINUTE_BRIEF.md":    "I.  Five-Minute Brief",
    "DEFENSE_BRIEF.md":        "II.  Defense Brief — Ten Common Dismissals",
    "NOVEL_CONTRIBUTIONS.md":  "III. Novel Contributions",
    "SCOPE_BOUNDARY.md":       "IV.  Scope Boundary",
}

C_BLACK    = (20,  20,  20)
C_HEAD1    = (15,  60, 110)
C_HEAD2    = (30,  90, 140)
C_HEAD3    = (50, 110, 160)
C_RULE     = (180, 190, 200)
C_LABEL    = (100, 100, 100)
C_FILL     = (245, 246, 248)
C_TBLFILL  = (235, 240, 248)


class DefensePDF(FPDF):

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font("Arial", "I", 8)
        self.set_text_color(*C_LABEL)
        self.set_x(self.l_margin)
        self.cell(self.epw / 2, 6, "Lycheetah Framework - Codex Defense Bundle D-1.0")
        self.cell(self.epw / 2, 6, f"Page {self.page_no()}", align="R",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*C_RULE)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "I", 7)
        self.set_text_color(*C_LABEL)
        self.set_x(self.l_margin)
        self.cell(self.epw, 6, "D-1.0 | C-1.0 | 2026-04-26 | Mackenzie Conor James Clark",
                  align="C")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _w(self, indent=0):
        """Effective width from current x (or from left_margin + indent)."""
        return self.w - self.r_margin - (self.l_margin + indent)

    def rule(self):
        self.set_draw_color(*C_RULE)
        self.set_x(self.l_margin)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def h1(self, text):
        self.ln(4)
        self.set_x(self.l_margin)
        self.set_font("Arial", "B", 18)
        self.set_text_color(*C_HEAD1)
        self.multi_cell(self._w(), 9, text)
        self.rule()
        self.set_text_color(*C_BLACK)

    def h2(self, text):
        self.ln(3)
        self.set_x(self.l_margin)
        self.set_font("Arial", "B", 13)
        self.set_text_color(*C_HEAD2)
        self.multi_cell(self._w(), 7, text)
        self.ln(1)
        self.set_text_color(*C_BLACK)

    def h3(self, text):
        self.ln(2)
        self.set_x(self.l_margin)
        self.set_font("Arial", "B", 11)
        self.set_text_color(*C_HEAD3)
        self.multi_cell(self._w(), 6, text)
        self.set_text_color(*C_BLACK)

    def body(self, text, indent=0):
        self.set_x(self.l_margin + indent)
        self.set_font("Arial", "", 10)
        self.set_text_color(*C_BLACK)
        self.multi_cell(self._w(indent), 5.5, text)

    def bullet(self, text, indent=8):
        self.set_x(self.l_margin + indent)
        self.set_font("Arial", "", 10)
        self.set_text_color(*C_BLACK)
        bullet_w = 4
        self.cell(bullet_w, 5.5, "\u2022")
        text_w = self._w(indent) - bullet_w
        self.multi_cell(text_w, 5.5, text)

    def code_block(self, text):
        self.ln(1)
        self.set_x(self.l_margin)
        self.set_fill_color(*C_FILL)
        self.set_font("Courier New", "", 8.5)
        self.set_text_color(50, 50, 50)
        self.multi_cell(self._w(), 4.5, text, fill=True)
        self.set_text_color(*C_BLACK)
        self.ln(1)

    def table_row(self, cells, widths, bold=False):
        style = "B" if bold else ""
        self.set_font("Arial", style, 9)
        x0 = self.l_margin
        y0 = self.get_y()
        # Compute row height
        row_h = 6
        for cell, w in zip(cells, widths):
            lines = self.multi_cell(w, 5, cell, dry_run=True, output="LINES")
            h = len(lines) * 5 + 2
            row_h = max(row_h, h)
        if y0 + row_h > self.page_break_trigger:
            self.add_page()
            y0 = self.get_y()
        cx = x0
        for i, (cell, w) in enumerate(zip(cells, widths)):
            self.set_xy(cx, y0)
            fill = bold and (i == 0)
            if fill:
                self.set_fill_color(*C_TBLFILL)
            self.set_font("Arial", style, 9)
            self.multi_cell(w, row_h / max(cell.count("\n") + 1, 1),
                            cell, border=1, fill=fill)
            cx += w
        self.set_xy(x0, y0 + row_h)


UNICODE_MAP = {
    '\u2014': '--',   # em dash
    '\u2013': '-',    # en dash
    '\u2192': '->',   # right arrow
    '\u2190': '<-',   # left arrow
    '\u2194': '<->',  # left-right arrow
    '\u21d2': '=>',   # double right arrow
    '\u229a': '[*]',  # circled asterisk (Sol signature)
    '\u2234': ':.',   # therefore
    '\u2227': '^',    # logical and
    '\u2228': 'v',    # logical or
    '\u03a0': 'Pi',   # Pi
    '\u03a8': 'Psi',  # Psi
    '\u03bb': 'lambda', # lambda
    '\u03b1': 'alpha',
    '\u03b2': 'beta',
    '\u03b3': 'gamma',
    '\u03b4': 'delta',
    '\u03b5': 'epsilon',
    '\u03bc': 'mu',
    '\u03c3': 'sigma',
    '\u2248': '~',    # approximately
    '\u2260': '!=',   # not equal
    '\u2264': '<=',   # less or equal
    '\u2265': '>=',   # greater or equal
    '\u00d7': 'x',    # multiplication sign
    '\u00b7': '.',    # middle dot
    '\u2022': '*',    # bullet (handled separately but just in case)
    '\u2026': '...',  # ellipsis
    '\u201c': '"',    # left double quote
    '\u201d': '"',    # right double quote
    '\u2018': "'",    # left single quote
    '\u2019': "'",    # right single quote
    '\u00e9': 'e',    # e acute
    '\u00e8': 'e',    # e grave
    '\u2082': '2',    # subscript 2
    '\u2081': '1',    # subscript 1
    '\u2083': '3',    # subscript 3
    '\u2084': '4',    # subscript 4
    '\u00b2': '^2',   # superscript 2
    '\u00b3': '^3',   # superscript 3
    '\u00b9': '^1',   # superscript 1
    '\u2070': '^0',   # superscript 0
    '\u2074': '^4',   # superscript 4
    '\u2075': '^5',   # superscript 5
    '\u00ae': '(R)',  # registered
    '\u00a9': '(c)',  # copyright
    '\u00b0': ' deg', # degree
    '\u221e': 'inf',  # infinity
    '\u2211': 'sum',  # summation
    '\u222b': 'integral', # integral
    '\u221a': 'sqrt', # square root
    '\u2202': 'd',    # partial differential
    '\u00d7': 'x',    # times
    '\u00f7': '/',    # division
    '\u2205': '{}',   # empty set
    '\u2208': 'in',   # element of
    '\u2209': 'not in', # not element of
    '\u2282': 'subset', # subset
    '\u2283': 'superset', # superset
    '\u2229': 'intersect', # intersection
    '\u222a': 'union', # union
    '\u00a0': ' ',    # non-breaking space
}


def ascii_safe(text):
    """Transliterate Unicode to ASCII-safe equivalents for Helvetica core font."""
    out = []
    for ch in text:
        if ch in UNICODE_MAP:
            out.append(UNICODE_MAP[ch])
        elif ord(ch) > 127:
            try:
                ch.encode('latin-1')
                out.append(ch)  # latin-1 range is fine
            except UnicodeEncodeError:
                out.append('?')
        else:
            out.append(ch)
    return ''.join(out)


def clean(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\*(.+?)\*', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'__(.+?)__', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'_(.+?)_', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)
    return ascii_safe(text.strip())


def parse_and_render(pdf, content, section_title=None):
    if section_title:
        pdf.add_page()
        pdf.h1(section_title)

    in_code = False
    code_buf = []
    table_rows = []

    lines = content.split("\n")
    i = 0

    def flush_table():
        nonlocal table_rows
        if not table_rows:
            return
        cols = max(len(r) for r in table_rows)
        avail = pdf.epw
        w = avail / cols
        widths = [w] * cols
        for j, row in enumerate(table_rows):
            cleaned = [clean(c) for c in row]
            while len(cleaned) < cols:
                cleaned.append("")
            pdf.table_row(cleaned[:cols], widths, bold=(j == 0))
        pdf.ln(2)
        table_rows = []

    while i < len(lines):
        line = lines[i]

        # Code fence
        if line.strip().startswith("```"):
            if in_code:
                pdf.code_block("\n".join(code_buf))
                code_buf = []
                in_code = False
            else:
                flush_table()
                in_code = True
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Table row
        if line.strip().startswith("|") and "|" in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.match(r'^[-:]+$', c) for c in cells if c):
                i += 1
                continue
            table_rows.append(cells)
            i += 1
            continue

        # Non-table line — flush pending table
        flush_table()

        # Headings
        if line.startswith("#### ") or line.startswith("##### "):
            pdf.h3(clean(re.sub(r'^#{4,6}\s', '', line)))
        elif line.startswith("### "):
            pdf.h3(clean(line[4:]))
        elif line.startswith("## "):
            pdf.h2(clean(line[3:]))
        elif line.startswith("# "):
            if not section_title:
                pdf.h1(clean(line[2:]))
            # else: skip — section_title already rendered

        # HR
        elif re.match(r'^-{3,}$', line.strip()):
            pdf.rule()

        # Bullet
        elif re.match(r'^[-*]\s', line):
            pdf.bullet(clean(line[2:]))
        elif re.match(r'^\s{2,4}[-*]\s', line):
            pdf.bullet(clean(re.sub(r'^\s+[-*]\s', '', line)), indent=14)
        elif re.match(r'^\d+\.\s', line):
            pdf.bullet(clean(re.sub(r'^\d+\.\s', '', line)))

        # Blank
        elif line.strip() == "":
            pdf.ln(2)

        # Body
        else:
            pdf.body(clean(line))

        i += 1

    flush_table()
    if code_buf:
        pdf.code_block("\n".join(code_buf))


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    out  = os.path.join(base, "DEFENSE_BUNDLE.pdf")

    pdf = DefensePDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(left=20, top=18, right=20)

    # Register Unicode-capable system fonts
    fonts_dir = r"C:\Windows\Fonts"
    pdf.add_font("Arial", "",  os.path.join(fonts_dir, "arial.ttf"))
    pdf.add_font("Arial", "B", os.path.join(fonts_dir, "arialbd.ttf"))
    pdf.add_font("Arial", "I", os.path.join(fonts_dir, "ariali.ttf"))
    pdf.add_font("Arial", "BI",os.path.join(fonts_dir, "arialbi.ttf"))
    pdf.add_font("Courier New", "",  os.path.join(fonts_dir, "cour.ttf"))
    pdf.add_font("Courier New", "B", os.path.join(fonts_dir, "courbd.ttf"))

    # Cover page
    pdf.add_page()
    pdf.ln(28)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Arial", "B", 26)
    pdf.set_text_color(*C_HEAD1)
    pdf.cell(pdf.epw, 13, "Lycheetah Framework", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "", 16)
    pdf.set_text_color(*C_HEAD2)
    pdf.cell(pdf.epw, 9, "Codex Defense Bundle D-1.0", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_draw_color(*C_RULE)
    pdf.line(pdf.l_margin + 20, pdf.get_y(), pdf.w - pdf.r_margin - 20, pdf.get_y())
    pdf.ln(8)

    for kind, text in FRONT_MATTER:
        pdf.set_x(pdf.l_margin)
        if kind == "title":
            pdf.set_font("Arial", "B", 14)
            pdf.set_text_color(*C_HEAD1)
            pdf.cell(pdf.epw, 7, text, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*C_BLACK)
        elif kind == "sub":
            pdf.set_font("Arial", "", 12)
            pdf.set_text_color(*C_HEAD2)
            pdf.cell(pdf.epw, 6, text, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*C_BLACK)
        elif kind == "rule":
            pdf.rule()
        elif kind == "blank":
            pdf.ln(3)
        elif kind == "label":
            pdf.set_font("Arial", "B", 10)
            pdf.set_text_color(*C_LABEL)
            pdf.cell(pdf.epw, 5.5, text, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(*C_BLACK)
        elif kind == "body":
            pdf.set_x(pdf.l_margin + 4)
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(*C_BLACK)
            pdf.multi_cell(pdf.epw - 4, 5.5, text)

    # Bundle sections
    for filename in BUNDLE_FILES:
        path = os.path.join(base, filename)
        if not os.path.exists(path):
            print(f"  WARNING: {filename} not found — skipping")
            continue
        with open(path, encoding="utf-8") as f:
            content = f.read()
        title = SECTION_TITLES.get(filename, filename)
        # Strip D-1.0 status header line
        content = re.sub(r'^#\s+D-1\.0[^\n]*\n', '', content)
        parse_and_render(pdf, content, section_title=title)
        print(f"  + {filename}")

    pdf.output(out)
    print(f"\nDEFENSE_BUNDLE.pdf written: {out}")
    print(f"Pages: {pdf.page}")


if __name__ == "__main__":
    main()
