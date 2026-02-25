"""Project 1 controller — AI Website Brochure Generator.

Thin layer that handles request/response shaping and delegates all business
logic to the brochure_generator service.
"""

from collections.abc import AsyncGenerator

from app.models.project1_models import BrochureRequest
from app.services.brochure_generator import run_pipeline_stream


async def handle_generate_stream(request: BrochureRequest) -> AsyncGenerator[str, None]:
    """Return an async generator that streams brochure generation output."""
    async for chunk in run_pipeline_stream(str(request.url)):
        yield chunk
