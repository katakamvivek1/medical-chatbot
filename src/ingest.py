"""
Medical Chatbot - Day 2: load medical documents and split them into chunks.

Pipeline:  data/ folder  ->  load (PDF / TXT)  ->  clean  ->  split into chunks
Day 3 turns these chunks into embeddings and stores them in a vector store.

Run it:  python -m src.ingest
"""

import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHUNK_SIZE = 800     # max characters per chunk (~150 words, about one paragraph)
CHUNK_OVERLAP = 100  # characters repeated between neighbouring chunks
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]  # try paragraphs first, then lines...


@dataclass
class Document:
    """One page of text plus where it came from."""
    text: str
    source: str  # file name, e.g. "diabetes.pdf"
    page: int    # page number, starting at 1 (always 1 for .txt)


@dataclass
class Chunk:
    """A small piece of a Document. This is what Day 3 will embed."""
    text: str
    source: str
    page: int
    chunk_id: str  # unique id, e.g. "diabetes.pdf-p2-c0"


def clean_text(text: str) -> str:
    """Fix common PDF extraction mess before splitting."""
    text = text.replace("\x00", "")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)  # "treat-\nment" -> "treatment"
    text = re.sub(r"[ \t]+", " ", text)            # many spaces -> one space
    text = re.sub(r"\n{3,}", "\n\n", text)         # many blank lines -> one
    return text.strip()


def load_pdf(path: Path) -> list[Document]:
    """Read a PDF page by page, skipping empty pages."""
    docs = []
    for number, page in enumerate(PdfReader(path).pages, start=1):
        text = clean_text(page.extract_text() or "")
        if text:
            docs.append(Document(text=text, source=path.name, page=number))
    return docs


def load_txt(path: Path) -> list[Document]:
    """Read a plain text file as a single 'page'."""
    text = clean_text(path.read_text(encoding="utf-8", errors="ignore"))
    return [Document(text=text, source=path.name, page=1)] if text else []


LOADERS = {".pdf": load_pdf, ".txt": load_txt}


def load_documents(data_dir: Path = DATA_DIR) -> list[Document]:
    """Load every supported file in data_dir. Other files are ignored."""
    if not data_dir.exists():
        raise FileNotFoundError(f"Data folder not found: {data_dir}")
    docs = []
    for path in sorted(data_dir.iterdir()):
        loader = LOADERS.get(path.suffix.lower())
        if loader:
            docs.extend(loader(path))
    return docs


def break_text(text: str, chunk_size: int, separators: list[str]) -> list[str]:
    """Break text at the largest separator it contains until every piece fits."""
    if len(text) <= chunk_size:
        return [text]
    separator, *smaller = separators
    if not separator:  # no separator left, so cut at a fixed width
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    if separator not in text:
        return break_text(text, chunk_size, smaller)
    parts = re.split(f"(?<={re.escape(separator)})", text)  # separator stays on its part
    return [p for part in parts if part for p in break_text(part, chunk_size, smaller)]


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Merge pieces into chunks, repeating the last pieces of each in the next."""
    chunks = []
    window: list[str] = []
    for piece in break_text(text, chunk_size, SEPARATORS):
        if window and sum(map(len, window)) + len(piece) > chunk_size:
            chunks.append("".join(window).strip())
            while window and (
                sum(map(len, window)) > chunk_overlap
                or sum(map(len, window)) + len(piece) > chunk_size
            ):
                window.pop(0)
        window.append(piece)
    chunks.append("".join(window).strip())
    return [chunk for chunk in chunks if chunk]


def split_documents(
    docs: list[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    """Split each page into overlapping chunks, keeping source + page."""
    chunks = []
    for doc in docs:
        for n, piece in enumerate(split_text(doc.text, chunk_size, chunk_overlap)):
            chunks.append(Chunk(
                text=piece,
                source=doc.source,
                page=doc.page,
                chunk_id=f"{doc.source}-p{doc.page}-c{n}",
            ))
    return chunks


def main() -> None:
    docs = load_documents()
    chunks = split_documents(docs)
    files = {d.source for d in docs}
    print(f"Loaded {len(docs)} page(s) from {len(files)} file(s)")
    print(f"Created {len(chunks)} chunk(s)")
    if chunks:
        avg = sum(len(c.text) for c in chunks) // len(chunks)
        print(f"Average chunk size: {avg} characters")
        sample = chunks[0]
        print(f"\nSample chunk [{sample.chunk_id}]:\n{sample.text[:300]}...")


if __name__ == "__main__":
    main()