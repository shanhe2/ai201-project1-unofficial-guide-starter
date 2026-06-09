"""Chunk the ingested documents for embedding.

Strategy (from planning.md, refined for Reddit's structure):
  1. Each document begins with a `Title:` line and is divided into comments by
     a `=== comment ===` delimiter. We split on that delimiter FIRST so one
     person's opinion is never merged with another's.
  2. A comment that already fits within CHUNK_SIZE becomes a single chunk.
  3. A longer comment is sub-split with LangChain's RecursiveCharacterTextSplitter
     using the size and overlap below — so at worst we split one author's text,
     never fuse two authors together.
  4. The thread Title is prepended to every chunk, so a chunk that holds only
     half a review still carries its subject (mitigates planning.md Challenge #1).

Run:  python chunk.py
"""

from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Chunking parameters (planning.md: ~300-500 chars, ~50-100 char overlap) ---
CHUNK_SIZE = 400      # characters; midpoint of the 300-500 range
CHUNK_OVERLAP = 75    # characters; midpoint of the 50-100 range

DOCUMENTS_DIR = Path("documents")
COMMENT_DELIMITER = "=== comment ==="

# One splitter, reused for any comment longer than CHUNK_SIZE.
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],  # prefer paragraph, then sentence
)


def parse_document(text):
    """Return (title, [comment, ...]) for one document's raw text."""
    lines = text.splitlines()
    title = ""
    if lines and lines[0].startswith("Title:"):
        title = lines[0][len("Title:"):].strip()
        text = "\n".join(lines[1:])

    comments = [c.strip() for c in text.split(COMMENT_DELIMITER)]
    comments = [c for c in comments if c]  # drop empties (e.g. before first delim)
    return title, comments


def chunk_document(text, source):
    """Turn one document into a list of chunk dicts.

    Each chunk: {"text", "source", "title"}. The title is prepended to the
    embedded text and also kept in metadata for source attribution later.
    """
    title, comments = parse_document(text)
    prefix = f"Title: {title}\n\n" if title else ""

    chunks = []
    for comment in comments:
        # A comment short enough to stand alone stays whole; otherwise sub-split.
        pieces = [comment] if len(comment) <= CHUNK_SIZE else _splitter.split_text(comment)
        for piece in pieces:
            chunks.append({
                "text": prefix + piece,
                "source": source,
                "title": title,
            })
    return chunks


def chunk_corpus(documents_dir=DOCUMENTS_DIR):
    """Chunk every .txt file in the documents directory."""
    all_chunks = []
    for path in sorted(documents_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        all_chunks.extend(chunk_document(text, source=path.name))
    return all_chunks


def main():
    chunks = chunk_corpus()
    print(f"Chunk size: {CHUNK_SIZE} chars | overlap: {CHUNK_OVERLAP} chars")
    print(f"Total chunks across corpus: {len(chunks)}\n")

    # Per-source counts (useful for the README 'final chunk count' field).
    counts = {}
    for c in chunks:
        counts[c["source"]] = counts.get(c["source"], 0) + 1
    for source, n in sorted(counts.items()):
        print(f"  {n:3d}  {source}")

    # Show one sample chunk so you can eyeball the format.
    if chunks:
        print("\n--- sample chunk ---")
        print(chunks[0]["text"])


if __name__ == "__main__":
    main()
