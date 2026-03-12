from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from textwrap import wrap

def text_to_pdf(text, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # APA margins (1 inch)
    left = right = top = bottom = inch
    y = height - top

    # Fonts
    body_font = "Times-Roman"
    bold_font = "Times-Bold"

    # Font sizes
    title_size = 18
    heading_size = 14
    body_size = 12
    
    # Line heights
    title_line_height = 28
    heading_line_height = 26
    body_line_height = 20
    
    max_chars = 85

    # Colors
    title_color = HexColor("#0f172a")
    heading_color = HexColor("#1e293b")
    body_color = HexColor("#334155")
    line_color = HexColor("#e5e7eb")

    def new_page():
        nonlocal y
        c.showPage()
        y = height - top
        c.setFont(body_font, body_size)
        c.setFillColor(body_color)

    def draw_horizontal_line():
        nonlocal y
        c.setStrokeColor(line_color)
        c.setLineWidth(1)
        c.line(left, y + 5, width - right, y + 5)

    c.setFont(body_font, body_size)
    c.setFillColor(body_color)

    is_title = True
    in_references = False
    section_headings = ["Abstract", "Methods", "Results", "References"]

    lines = text.split("\n")
    
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip empty lines but add spacing
        if not stripped:
            y -= body_line_height / 2
            continue

        # ---------- TITLE (First non-empty, non-heading line) ----------
        if is_title and stripped not in section_headings:
            # Draw title centered and bold
            c.setFont(bold_font, title_size)
            c.setFillColor(title_color)
            
            title_lines = wrap(stripped, 60)  # Shorter wrap for title
            
            for t in title_lines:
                if y < bottom:
                    new_page()
                    c.setFont(bold_font, title_size)
                    c.setFillColor(title_color)
                
                text_width = c.stringWidth(t, bold_font, title_size)
                c.drawString((width - text_width) / 2, y, t)
                y -= title_line_height

            y -= 20  # Extra space after title
            is_title = False
            c.setFont(body_font, body_size)
            c.setFillColor(body_color)
            continue

        # ---------- SECTION HEADINGS ----------
        if stripped in section_headings:
            y -= 15  # Space before heading

            if y < bottom + 50:  # Ensure heading doesn't start at page bottom
                new_page()

            # Draw heading
            c.setFont(bold_font, heading_size)
            c.setFillColor(heading_color)
            c.drawString(left, y, stripped)
            y -= 8
            
            # Draw underline
            draw_horizontal_line()
            y -= heading_line_height

            c.setFont(body_font, body_size)
            c.setFillColor(body_color)

            if stripped == "References":
                in_references = True
            
            is_title = False
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

                y -= body_line_height

            y -= 5  # Extra space between references
            continue

        # ---------- NORMAL PARAGRAPH ----------
        wrapped = wrap(stripped, max_chars)
        for w in wrapped:
            if y < bottom:
                new_page()

            c.drawString(left, y, w)
            y -= body_line_height

    c.save()