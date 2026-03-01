"""PDF generator for interview transcripts using PyMuPDF (fitz)."""

import io
from datetime import datetime

import fitz  # PyMuPDF


def generate_transcript_pdf(
    transcript: list[dict],
    title: str = "面试记录",
    session_date: datetime | None = None,
) -> bytes:
    """Generate a PDF from interview transcript data.

    Args:
        transcript: List of {"role": "ai"|"user", "content": "..."} dicts.
        title: PDF title.
        session_date: Date of the interview session.

    Returns:
        PDF file content as bytes.
    """
    doc = fitz.open()

    # Page settings
    page_width, page_height = fitz.paper_size("a4")
    margin_left = 50
    margin_right = 50
    margin_top = 60
    margin_bottom = 60
    content_width = page_width - margin_left - margin_right

    # Font settings — use built-in CJK font for Chinese support
    font_title = "china-s"  # Simplified Chinese
    font_body = "china-s"
    title_size = 18
    label_size = 11
    body_size = 10.5
    line_height = 16

    def new_page():
        page = doc.new_page(width=page_width, height=page_height)
        return page, margin_top

    page, y = new_page()

    # Title
    date_str = (session_date or datetime.now()).strftime("%Y-%m-%d %H:%M")
    title_text = f"{title} — {date_str}"
    page.insert_font(fontname="cjk", fontbuffer=None, fontfile=None, set_simple=False)
    title_rect = fitz.Rect(margin_left, y, page_width - margin_right, y + 30)
    page.insert_textbox(
        title_rect,
        title_text,
        fontsize=title_size,
        fontname="china-s",
        align=fitz.TEXT_ALIGN_CENTER,
    )
    y += 45

    # Separator line
    page.draw_line(
        fitz.Point(margin_left, y),
        fitz.Point(page_width - margin_right, y),
        color=(0.7, 0.7, 0.7),
        width=0.5,
    )
    y += 20

    def insert_wrapped_text(page, y, text, fontname, fontsize, color, indent=0):
        """Insert text with word wrapping, returning (page, new_y)."""
        available_width = content_width - indent
        # Split text into lines
        lines = text.split("\n")
        for line in lines:
            # Estimate chars per line (CJK chars are roughly 2x width)
            chars_per_line = int(available_width / (fontsize * 0.55))
            if chars_per_line < 10:
                chars_per_line = 10

            # Manual wrapping
            pos = 0
            while pos < len(line):
                segment = line[pos:pos + chars_per_line]
                if y + line_height > page_height - margin_bottom:
                    page, y = new_page()

                text_rect = fitz.Rect(
                    margin_left + indent, y,
                    page_width - margin_right, y + line_height,
                )
                page.insert_textbox(
                    text_rect,
                    segment,
                    fontsize=fontsize,
                    fontname=fontname,
                    color=color,
                )
                y += line_height
                pos += chars_per_line

            if len(line) == 0:
                y += line_height * 0.5

        return page, y

    # Render transcript entries
    for i, entry in enumerate(transcript):
        role = entry.get("role", "")
        content = entry.get("content", "")

        if role == "ai":
            label = "AI 面试官："
            label_color = (0.2, 0.4, 0.8)
            text_color = (0.1, 0.1, 0.1)
        else:
            label = "候选人："
            label_color = (0.1, 0.6, 0.3)
            text_color = (0.2, 0.2, 0.2)

        # Check page space for label
        if y + line_height > page_height - margin_bottom:
            page, y = new_page()

        # Role label
        label_rect = fitz.Rect(margin_left, y, page_width - margin_right, y + line_height + 2)
        page.insert_textbox(
            label_rect,
            label,
            fontsize=label_size,
            fontname=font_body,
            color=label_color,
        )
        y += line_height + 4

        # Content text (indented)
        page, y = insert_wrapped_text(page, y, content, font_body, body_size, text_color, indent=15)

        # Spacing between entries
        y += 10

    # Save to bytes
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()
