from __future__ import annotations

from pathlib import Path
import PyPDF2
import tiktoken
from tiktoken import encoding_for_model



# Chunking settings (token-based chunking is best for RAG)
CHUNK_TOKENS = 200
OVERLAP_TOKENS = 50
EMBED_MODEL = "text-embedding-3-small"


def get_encoding(model: str = EMBED_MODEL):
    """
    Returns a tiktoken encoding for token-based chunking.
    Falls back to `cl100k_base` if model encoding lookup fails.
    """
    try:
        return encoding_for_model(model)
    except Exception:
        try:
            return tiktoken.get_encoding("cl100k_base")
        except Exception:
            return None


def chunk_text(
    text: str,
    *,
    chunk_tokens: int = CHUNK_TOKENS,
    overlap_tokens: int = OVERLAP_TOKENS,
    model: str = EMBED_MODEL,
) -> list[str]:
    """Split text into overlapping chunks."""
    text = text or ""
    if not text.strip():
        return []

    enc = get_encoding(model)
    if enc is None:
        # Offline-safe fallback: approximate tokens by characters.
        # Rough heuristic for English: ~4 chars per token.
        chunk_chars = max(chunk_tokens * 4, 1)
        overlap_chars = max(overlap_tokens * 4, 0)
        stride = max(chunk_chars - overlap_chars, 1)
        chunks: list[str] = []
        for i in range(0, len(text), stride):
            piece = text[i : i + chunk_chars].strip()
            if piece:
                chunks.append(piece)
        return chunks

    tokens = enc.encode(text)
    if not tokens:
        return []

    stride = max(chunk_tokens - overlap_tokens, 1)
    chunks: list[str] = []
    for start in range(0, len(tokens), stride):
        window = tokens[start : start + chunk_tokens]
        piece = enc.decode(window).strip()
        if piece:
            chunks.append(piece)
    return chunks


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from a PDF file."""
    with pdf_path.open("rb") as f:
        reader = PyPDF2.PdfReader(f)
        parts: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text:
                parts.append(page_text)
        return "\n".join(parts)


def chunk_pdfs(
    pd_file_path: str,
    *,
    chunk_tokens: int = CHUNK_TOKENS,
    overlap_tokens: int = OVERLAP_TOKENS,
) -> list[str]:
    """Chunk multiple PDFs and return a flat list of chunk texts."""
    pdf_path = Path(pd_file_path)
    if not pdf_path.exists():
        return []
    full_text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(
        full_text, chunk_tokens=chunk_tokens, overlap_tokens=overlap_tokens
    )
    return chunks   

