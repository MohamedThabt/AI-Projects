import gradio as gr
import httpx

from config.settings import settings


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
        
        with gr.Row():
            check_btn = gr.Button("Check Health Status", variant="primary")
        
        with gr.Row():
            output = gr.Textbox(label="Result", lines=3)
        
        check_btn.click(fn=check_health, outputs=output)
    
    return demo
