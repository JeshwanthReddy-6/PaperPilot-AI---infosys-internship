from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from textwrap import wrap
import re

def text_to_pdf(text, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # APA margins (1 inch)
    left = right = top = bottom = inch
    y = height - top

    # Fonts
    body_font = "Times-Roman"
    bold_font = "Times-Bold"

    body_size = 12
    line_height = 24  # double-spaced
    max_chars = 85

    def new_page():
        nonlocal y
        c.showPage()
        y = height - top
        c.setFont(body_font, body_size)

    c.setFont(body_font, body_size)

    is_title = True
    in_references = False

    for line in text.split("\n"):

        # Blank line
        if not line.strip():
            y -= line_height
            continue

        stripped = line.strip()

        # ---------- TITLE ----------
        if is_title and stripped.startswith("**") and stripped.endswith("**"):
            title = stripped[2:-2]

            c.setFont(bold_font, body_size)
            title_lines = wrap(title, max_chars)

            for t in title_lines:
                text_width = c.stringWidth(t, bold_font, body_size)
                c.drawString((width - text_width) / 2, y, t)
                y -= line_height

            is_title = False
            c.setFont(body_font, body_size)
            continue

        # ---------- SECTION HEADINGS ----------
        if stripped in ["**Abstract**", "**Methods**", "**Results**", "**References**"]:
            heading = stripped[2:-2]
            y -= line_height

            if y < bottom:
                new_page()

            c.setFont(bold_font, body_size)
            c.drawString(left, y, heading)
            y -= line_height
            c.setFont(body_font, body_size)

            if heading == "References":
                in_references = True

            continue

        # ---------- REFERENCES (HANGING INDENT) ----------
        if in_references:
            wrapped = wrap(stripped, max_chars)
            first = True

            for w in wrapped:
                if y < bottom:
                    new_page()

                if first:
                    c.drawString(left, y, w)
                    first = False
                else:
                    c.drawString(left + 36, y, w)  # hanging indent

                y -= line_height

            continue

        # ---------- NORMAL PARAGRAPH ----------
        wrapped = wrap(line, max_chars)
        for w in wrapped:
            if y < bottom:
                new_page()

            c.drawString(left, y, w)
            y -= line_height

    c.save()
