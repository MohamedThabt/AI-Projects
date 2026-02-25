import time

import gradio as gr
import httpx

_API_BASE = "http://localhost:8000/api/project1"
_POLL_INTERVAL = 3  # seconds


def _generate_brochure(url: str) -> str:
    """Call the backend to generate a brochure, poll until done."""
    if not url or not url.strip():
        return "⚠️ Please enter a valid URL."

    # Start the task
    try:
        resp = httpx.post(f"{_API_BASE}/generate", json={"url": url.strip()}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        task_id = data["task_id"]
    except Exception as exc:
        return f"❌ Failed to start generation: {exc}"

    # Poll for completion
    while True:
        time.sleep(_POLL_INTERVAL)
        try:
            status_resp = httpx.get(f"{_API_BASE}/status/{task_id}", timeout=15)
            status_resp.raise_for_status()
            status_data = status_resp.json()
        except Exception as exc:
            return f"❌ Error polling status: {exc}"

        status = status_data.get("status", "unknown")

        if status == "completed":
            return status_data.get("result", "No content returned.")
        if status == "failed":
            return f"❌ Generation failed: {status_data.get('error', 'Unknown error')}"
        # Still running — keep polling


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

        # Wire events
        generate_btn.click(
            fn=_generate_brochure,
            inputs=[url_input],
            outputs=[brochure_output],
        )

    return project1_page, back_btn
