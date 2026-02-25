import gradio as gr
from fastapi import FastAPI

from config.settings import settings
from routes.api import api_router
from ui.gradio_app import create_gradio_interface


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.include_router(api_router)

    # Mount Gradio interface at root
    gradio_app = create_gradio_interface()
    app = gr.mount_gradio_app(app, gradio_app, path="/")

    return app


app = create_app()
