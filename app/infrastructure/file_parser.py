"""File parsing service for PDF and Word documents."""

import io
from pathlib import Path


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    import fitz  # PyMuPDF

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts)


def parse_docx(file_bytes: bytes) -> str:
    """Extract text from a Word document using python-docx."""
    from docx import Document

    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())


def parse_file(file_bytes: bytes, filename: str) -> str:
    """Parse a file based on its extension."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return parse_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return parse_docx(file_bytes)
    elif ext in (".txt", ".md"):
        return file_bytes.decode("utf-8", errors="replace")
    else:
        raise ValueError(f"Unsupported file format: {ext}")
