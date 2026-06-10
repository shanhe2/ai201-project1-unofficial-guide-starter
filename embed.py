"""Embed chunks and store them in ChromaDB; retrieve by semantic search.

Pipeline stage (from planning.md architecture):
    Chunking  ->  [ Embedding & Vector Store ]  ->  Retrieval  ->  Generation

  - Embedding model: all-MiniLM-L6-v2 via sentence-transformers (local, fast).
  - Vector store:    ChromaDB, persisted to ./chroma_db.
  - Each chunk is stored with its source filename + thread title as metadata,
    so retrieved results can be attributed back to the document they came from.
  - Retrieval default top-k = 5 (planning.md Retrieval Approach).

Usage:
  python embed.py                 # (re)build the index, then run the eval questions
"""

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

import chunk

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "rpi_guide"
PERSIST_DIR = "chroma_db"
TOP_K = 5  # planning.md Retrieval Approach

# Load the embedding model and the persistent Chroma client once at import time.
_model = SentenceTransformer(MODEL_NAME)
_client = chromadb.PersistentClient(path=PERSIST_DIR)


def _embed(texts):
    """Embed a list of strings into vectors (returns plain Python lists)."""
    return _model.encode(texts, show_progress_bar=False).tolist()


def build_index():
    """Embed every chunk and (re)load them into a fresh Chroma collection."""
    chunks = chunk.chunk_corpus()

    # Start clean so re-running never duplicates chunks.
    try:
        _client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # collection didn't exist yet
    collection = _client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine similarity for MiniLM vectors
    )

    documents = [c["text"] for c in chunks]
    metadatas = [{"source": c["source"], "title": c["title"]} for c in chunks]
    ids = [f"{c['source']}::{i}" for i, c in enumerate(chunks)]
    embeddings = _embed(documents)

    # Add in batches (Chroma best practice; also avoids large single-insert issues).
    batch_size = 32
    for start in range(0, len(documents), batch_size):
        end = start + batch_size
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadatas[start:end],
        )

    print(f"Indexed {collection.count()} chunks into '{COLLECTION_NAME}' "
          f"(model={MODEL_NAME}).")
    return collection


def get_collection():
    """Return the existing collection (build it first if missing/empty)."""
    try:
        collection = _client.get_collection(COLLECTION_NAME)
        if collection.count() > 0:
            return collection
    except Exception:
        pass
    return build_index()


def retrieve(query, top_k=TOP_K):
    """Return the top_k chunks most similar to the query.

    Each result: {"text", "source", "title", "score"} where score is cosine
    similarity in [0, 1] (higher = more relevant).
    """
    collection = get_collection()
    results = collection.query(
        query_embeddings=_embed([query]),
        n_results=top_k,
    )
    hits = []
    for text, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "text": text,
            "source": meta["source"],
            "title": meta["title"],
            "score": 1 - distance,  # cosine distance -> similarity
        })
    return hits


# The 5 evaluation questions from planning.md, for a retrieval smoke test.
EVAL_QUESTIONS = [
    "What do students say about VCC North and VCC South?",
    "Does RPI have a supercomputer cluster?",
    "What do people say about the Fall rush for Greek life?",
    "What do students say about the website QUACS?",
    "What do students say about the sq ft in Sharp dorm?",
]


def main():
    build_index()
    print("\n=== Retrieval smoke test (top-3 per question) ===")
    for q in EVAL_QUESTIONS:
        print(f"\nQ: {q}")
        for hit in retrieve(q, top_k=3):
            preview = hit["text"].replace("\n", " ")[:140]
            print(f"  [{hit['score']:.2f}] ({hit['source']}) {preview}...")


if __name__ == "__main__":
    main()
