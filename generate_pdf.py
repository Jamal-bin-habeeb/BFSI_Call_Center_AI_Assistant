"""Convert TECHNICAL_DOCS.md to a formatted PDF."""
import os
import re
from fpdf import FPDF


def sanitize(text):
    """Replace Unicode characters with ASCII equivalents for PDF."""
    replacements = {
        "\u2014": "-",   # em-dash
        "\u2013": "-",   # en-dash
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2026": "...", # ellipsis
        "\u2022": "*",   # bullet
        "\u25ba": ">",   # triangle
        "\u25bc": "v",   # down triangle
        "\u2502": "|",   # box drawing
        "\u250c": "+",   # box corner
        "\u2514": "+",   # box corner
        "\u2500": "-",   # box horizontal
        "\u251c": "|",   # box tee
        "\u2510": "+",   # box corner
        "\u2518": "+",   # box corner
        "\u2524": "|",   # box tee
        "\u252c": "+",   # box tee
        "\u2534": "+",   # box tee
        "\u253c": "+",   # box cross
        "\u2550": "=",   # double horizontal
        "\u2551": "||",  # double vertical
        "\u2265": ">=",  # greater or equal
        "\u2264": "<=",  # less or equal
        "\u00d7": "x",   # multiplication
        "\u00b7": ".",   # middle dot
        "\u2191": "^",   # up arrow
        "\u2192": "->",  # right arrow
        "\u2193": "v",   # down arrow
        "\u2713": "[Y]", # check mark
        "\u2717": "[X]", # cross mark
        "\u25cf": "*",   # filled circle
        "\u25cb": "o",   # empty circle
        "\u20b9": "Rs.", # rupee sign
        "\u2620": "!!",  # skull
        "\u26a0": "!!",  # warning
        "\u2728": "*",   # sparkles
        "\u2764": "<3",  # heart
        "\u2615": "",    # coffee
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    # Fallback: replace any remaining non-latin-1 chars
    return text.encode("latin-1", "replace").decode("latin-1")


class TechDocPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(130, 130, 130)
            self.cell(0, 8, "BFSI Call Center AI Assistant - Technical Documentation", align="C")
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def chapter_title(self, title, level=1):
        sizes = {1: 18, 2: 14, 3: 12}
        size = sizes.get(level, 11)
        self.set_font("Helvetica", "B", size)
        self.set_text_color(30, 60, 120)
        self.ln(4)
        self.multi_cell(0, size * 0.6, sanitize(title))
        if level <= 2:
            self.set_draw_color(30, 60, 120)
            self.line(10, self.get_y() + 1, 200, self.get_y() + 1)
            self.ln(4)
        else:
            self.ln(2)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, sanitize(text))
        self.ln(2)

    def code_block(self, code):
        self.set_font("Courier", "", 8)
        self.set_fill_color(240, 240, 245)
        self.set_text_color(50, 50, 50)
        lines = code.split("\n")
        for line in lines:
            safe = sanitize(line)
            self.cell(0, 4.5, "  " + safe, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def table_row(self, cells, is_header=False):
        col_w = (self.w - 20) / len(cells)
        self.set_font("Helvetica", "B" if is_header else "", 9)
        if is_header:
            self.set_fill_color(30, 60, 120)
            self.set_text_color(255, 255, 255)
        else:
            self.set_fill_color(245, 245, 250)
            self.set_text_color(40, 40, 40)
        for cell in cells:
            safe = sanitize(cell)
            self.cell(col_w, 7, " " + safe, border=1, fill=True)
        self.ln()

    def bullet(self, text, indent=0):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        x = 15 + indent * 5
        self.set_x(x)
        safe = sanitize(text)
        self.cell(4, 5.5, "*")
        self.multi_cell(0, 5.5, " " + safe)
        self.ln(1)


def parse_and_generate(md_path, pdf_path):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pdf = TechDocPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title page
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(30, 60, 120)
    pdf.ln(40)
    pdf.cell(0, 15, "Technical Documentation", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "BFSI Call Center AI Assistant", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 8, "Architecture, Logic & Compliance Framework", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_draw_color(30, 60, 120)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "Version 1.0 | February 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.add_page()

    in_code = False
    code_buf = []
    in_table = False
    table_rows = []
    text_buf = []

    def flush_text():
        if text_buf:
            combined = " ".join(text_buf).strip()
            if combined:
                pdf.body_text(combined)
            text_buf.clear()

    def flush_table():
        nonlocal in_table
        if table_rows:
            for i, row in enumerate(table_rows):
                pdf.table_row(row, is_header=(i == 0))
            pdf.ln(3)
        table_rows.clear()
        in_table = False

    for raw_line in lines:
        line = raw_line.rstrip()

        # Code block toggle
        if line.startswith("```"):
            if in_code:
                flush_text()
                pdf.code_block("\n".join(code_buf))
                code_buf.clear()
                in_code = False
            else:
                flush_text()
                if in_table:
                    flush_table()
                in_code = True
            continue

        if in_code:
            code_buf.append(line)
            continue

        # Table
        if "|" in line and line.strip().startswith("|"):
            # Skip separator rows
            if re.match(r"^\|[\s\-:|]+\|$", line.strip()):
                continue
            flush_text()
            if not in_table:
                in_table = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # Remove markdown bold
            cells = [re.sub(r"\*\*(.*?)\*\*", r"\1", c) for c in cells]
            table_rows.append(cells)
            continue
        else:
            if in_table:
                flush_table()

        # Horizontal rule
        if line.strip() == "---":
            flush_text()
            continue

        # Headers
        m = re.match(r"^(#{1,3})\s+(.*)", line)
        if m:
            flush_text()
            level = len(m.group(1))
            title = re.sub(r"\*\*(.*?)\*\*", r"\1", m.group(2))
            # Remove markdown links
            title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)
            pdf.chapter_title(title, level)
            continue

        # Bullets
        bm = re.match(r"^(\s*)[*\-]\s+(.*)", line)
        if bm:
            flush_text()
            indent = len(bm.group(1)) // 2
            text = re.sub(r"\*\*(.*?)\*\*", r"\1", bm.group(2))
            text = re.sub(r"`([^`]+)`", r"\1", text)
            pdf.bullet(text, indent)
            continue

        # Numbered list
        nm = re.match(r"^\s*\d+\.\s+(.*)", line)
        if nm:
            flush_text()
            text = re.sub(r"\*\*(.*?)\*\*", r"\1", nm.group(1))
            text = re.sub(r"`([^`]+)`", r"\1", text)
            pdf.bullet(text)
            continue

        # Empty line
        if not line.strip():
            flush_text()
            continue

        # Regular text - clean markdown
        clean = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        clean = re.sub(r"`([^`]+)`", r"\1", clean)
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
        text_buf.append(clean.strip())

    flush_text()
    if in_table:
        flush_table()

    pdf.output(pdf_path)
    print(f"PDF generated: {pdf_path}")
    print(f"Pages: {pdf.page_no()}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    md_path = os.path.join(script_dir, "TECHNICAL_DOCS.md")
    pdf_path = os.path.join(script_dir, "TECHNICAL_DOCS.pdf")
    parse_and_generate(md_path, pdf_path)
