"""Gradio interface for the RPI Unofficial Guide RAG system.

Pipeline: user query -> retrieve() -> LLM (Groq) -> grounded answer + sources

Run:  python app.py
"""

import gradio as gr

from generate import answer


def respond(query: str) -> tuple[str, str]:
    """Call the generation pipeline and return (answer, sources) for Gradio."""
    if not query.strip():
        return "", ""

    result = answer(query)

    # Sources are programmatically assembled — filenames stripped of .txt extension
    # and formatted as a readable list.
    source_names = [s.replace(".txt", "").replace("_", " ") for s in result["sources"]]
    sources_text = "\n".join(f"• {name}" for name in source_names)

    return result["answer"], sources_text


with gr.Blocks(title="RPI Unofficial Guide") as demo:
    gr.Markdown("## RPI Unofficial Guide\nAsk questions about RPI campus life — housing, clubs, study spots, and more. Answers are grounded in real student Reddit posts.")

    with gr.Row():
        with gr.Column(scale=3):
            query_box = gr.Textbox(
                label="Your question",
                placeholder="e.g. What do students say about Sharp dorm?",
                lines=2,
            )
            submit_btn = gr.Button("Ask", variant="primary")

        with gr.Column(scale=1):
            sources_box = gr.Textbox(label="Sources", lines=6, interactive=False)

    answer_box = gr.Textbox(label="Answer", lines=6, interactive=False)

    submit_btn.click(fn=respond, inputs=query_box, outputs=[answer_box, sources_box])
    query_box.submit(fn=respond, inputs=query_box, outputs=[answer_box, sources_box])

    gr.Examples(
        examples=[
            ["What do students say about the space in Sharp dorm?"],
            ["Does RPI have a supercomputer cluster?"],
            ["What do people say about Fall rush for Greek life?"],
            ["What do students say about the website QUACS?"],
            ["What are good study spots on and off campus?"],
        ],
        inputs=query_box,
    )


if __name__ == "__main__":
    demo.launch()
