"""Generation stage: retrieve context chunks, then call Groq LLM for a grounded answer.

Pipeline stage (from planning.md architecture):
    Retrieval  ->  [ Generation ]  ->  Interface

Grounding design (two-layer enforcement):
  1. System prompt hard-constrains the model: it may only use the numbered
     passages provided and must say it doesn't know if the answer isn't there.
     This is an instruction, not a suggestion — the word "only" appears twice
     and the fallback response is specified explicitly.
  2. Source attribution is PROGRAMMATIC: Python collects source filenames from
     the retrieved chunks and appends them to every response. The LLM is never
     asked to produce citations — it cannot hallucinate them.

Usage:
  python generate.py                 # run the 5 eval questions
  from generate import answer        # call answer(query) in app.py
"""

import os

from dotenv import load_dotenv
from groq import Groq

import embed

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

_client = Groq(api_key=os.environ["GROQ_API_KEY"])

# ── System prompt ──────────────────────────────────────────────────────────────
# "Only" appears twice; fallback wording is specified so the model can't invent
# a polite non-answer that still sounds authoritative.
SYSTEM_PROMPT = """\
You are an assistant that helps prospective and current RPI students.
You may only answer using the numbered passages provided in the user message.
Do not use any knowledge from your training data. Do not guess or infer details
that are not explicitly stated in the passages.
If the passages do not contain enough information to answer the question,
respond with exactly: "I don't have enough information in my sources to answer that."
Keep your answer concise and direct.\
"""


def answer(query: str, top_k: int = embed.TOP_K) -> dict:
    """Return a grounded answer for query.

    Returns:
        {
            "answer": str,          # LLM response, grounded to retrieved chunks
            "sources": list[str],   # filenames — set programmatically, not by LLM
            "chunks": list[dict],   # full hit list from retrieve() for inspection
        }
    """
    hits = embed.retrieve(query, top_k=top_k)

    # Build numbered context block — explicit numbering helps the model reference
    # passages and makes it clear that this is all the evidence it has.
    context_lines = []
    for i, hit in enumerate(hits, 1):
        context_lines.append(f"[{i}] (source: {hit['source']})\n{hit['text']}")
    context_block = "\n\n".join(context_lines)

    user_message = (
        f"Question: {query}\n\n"
        f"Passages:\n{context_block}"
    )

    response = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,   # low temperature for factual grounded answers
        max_tokens=512,
    )

    llm_answer = response.choices[0].message.content.strip()

    # Source attribution: derived from retrieved chunks in Python, not from LLM output.
    sources = list(dict.fromkeys(h["source"] for h in hits))  # deduplicated, ordered

    return {"answer": llm_answer, "sources": sources, "chunks": hits}


# ── Eval smoke test ────────────────────────────────────────────────────────────
EVAL_QUESTIONS = [
    "What do students say about VCC North and VCC South?",
    "Does RPI have a supercomputer cluster?",
    "What do people say about the Fall rush for Greek life?",
    "What do students say about the website QUACS?",
    "What do students say about the sq ft in Sharp dorm?",
]


def main():
    for q in EVAL_QUESTIONS:
        print(f"\nQ: {q}")
        result = answer(q)
        print(f"A: {result['answer']}")
        print(f"Sources: {', '.join(result['sources'])}")
        print("-" * 60)


if __name__ == "__main__":
    main()
