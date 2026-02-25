import asyncio
from collections.abc import AsyncGenerator

import gradio as gr

from app.services.brochure_generator import run_pipeline_stream

# Stage-progress prefixes — we accumulate them separately so the final
# brochure markdown isn't polluted with status emoji lines.
_STAGE_PREFIXES = ("🔍", "🔗", "📄", "🧹", "✨")


async def _generate_brochure(url: str) -> AsyncGenerator[str, None]:
    """Async generator that streams progress + brochure tokens to Gradio."""
    if not url or not url.strip():
        yield "⚠️ Please enter a valid URL."
        return

    accumulated = ""  # running text shown in the Markdown component

    async for chunk in run_pipeline_stream(url.strip()):
        accumulated += chunk
        yield accumulated


def create_project1_page() -> tuple[gr.Column, gr.Button]:
    """Build the Project 1 page and return (column, back_button)."""
    with gr.Column(visible=False) as project1_page:
        gr.Markdown("## Project 1 — AI Website Brochure Generator")
        gr.Markdown(
            "Enter a website URL below. The system will scrape the site, "
            "discover related pages, and generate a professional brochure using AI."
        )

        with gr.Row():
            url_input = gr.Textbox(
                label="Website URL",
                placeholder="https://example.com",
                scale=4,
            )
            generate_btn = gr.Button("🚀 Generate Brochure", variant="primary", scale=1)

        brochure_output = gr.Markdown(label="Generated Brochure", value="")

        back_btn = gr.Button("← Back to Home", variant="secondary")

        # Wire events — Gradio natively streams async generators
        generate_btn.click(
            fn=_generate_brochure,
            inputs=[url_input],
            outputs=[brochure_output],
        )

    return project1_page, back_btn
