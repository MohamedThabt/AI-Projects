import gradio as gr
import httpx

from config.settings import settings
from ui.pages.project1 import create_project1_page


def check_health() -> str:
    """Call the FastAPI health endpoint."""
    try:
        response = httpx.get("http://localhost:8000/api/health")
        if response.status_code == 200:
            data = response.json()
            return f"✅ Health Check: {data}"
        else:
            return f"❌ Health check failed with status {response.status_code}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def create_gradio_interface() -> gr.Blocks:
    """Create the main Gradio interface."""
    with gr.Blocks(title=settings.app_name) as demo:
        gr.Markdown(f"# {settings.app_name}")
        gr.Markdown(f"**Version:** {settings.app_version} | **Environment:** {settings.app_env}")

        # --- Home Page ---
        with gr.Column(visible=True) as home_page:
            gr.Markdown("## Home")
            with gr.Row():
                health_btn = gr.Button("Check Health Status", variant="primary")
                project1_btn = gr.Button("Go to Project 1 →", variant="secondary")
            with gr.Row():
                health_output = gr.Textbox(label="Health Result", lines=3)

        # --- Project 1 Page ---
        project1_page, back_btn = create_project1_page()

        # --- Wire up events ---
        health_btn.click(fn=check_health, outputs=health_output)

        project1_btn.click(
            fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
            outputs=[home_page, project1_page],
        )
        back_btn.click(
            fn=lambda: (gr.update(visible=True), gr.update(visible=False)),
            outputs=[home_page, project1_page],
        )

    return demo
