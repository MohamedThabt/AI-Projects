"""Routes for Project 1 — AI Website Brochure Generator."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.controllers.project1_controller import handle_generate_stream
from app.models.project1_models import BrochureRequest

router = APIRouter(prefix="/project1", tags=["project1"])


async def _sse_generator(request: BrochureRequest):
    """Wrap the controller generator in SSE `data:` frames."""
    async for chunk in handle_generate_stream(request):
        # SSE format: each chunk as a data frame
        yield f"data: {chunk}\n\n"
    yield "data: [DONE]\n\n"


@router.post(
    "/stream",
    summary="Stream brochure generation",
    description="Submit a website URL and receive a streamed brochure via SSE. "
    "Stage progress updates are sent first, followed by LLM token chunks.",
)
async def stream_brochure(request: BrochureRequest):
    return StreamingResponse(
        _sse_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
