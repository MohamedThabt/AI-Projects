import gradio as gr
from fastapi import FastAPI

from config.exceptions import register_exception_handlers
from config.logger import setup_logging
from config.middleware import RequestLoggingMiddleware
from config.settings import settings
from routes.api import api_router
from ui.gradio_app import create_gradio_interface


def create_app() -> FastAPI:
    # ── Initialize structured logging ──
    setup_logging(level=settings.log_level)

    app = FastAPI(title=settings.app_name, version=settings.app_version)

    # ── Register middleware (runs on every request) ──
    app.add_middleware(RequestLoggingMiddleware)

    # ── Global exception handlers ──
    register_exception_handlers(app)

    app.include_router(api_router)

    # Mount Gradio interface at root
    gradio_app = create_gradio_interface()
    app = gr.mount_gradio_app(app, gradio_app, path="/")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # Only watch source directories — never generated output like logs/
        reload_dirs=["app", "config", "routes", "ui"],
        reload_excludes=["logs/*", "*.log"],
    )
