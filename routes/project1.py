"""Routes for Project 1 — AI Website Brochure Generator."""

from fastapi import APIRouter
from starlette import status

from app.controllers.project1_controller import handle_generate, handle_status
from app.models.project1_models import (
    BrochureRequest,
    BrochureStatusResponse,
    BrochureTaskResponse,
)

router = APIRouter(prefix="/project1", tags=["project1"])


@router.post(
    "/generate",
    response_model=BrochureTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start brochure generation",
    description="Submit a website URL to generate a professional brochure. "
    "Returns a task ID that can be polled for progress.",
)
async def generate_brochure(request: BrochureRequest) -> BrochureTaskResponse:
    return handle_generate(request)


@router.get(
    "/status/{task_id}",
    response_model=BrochureStatusResponse,
    summary="Check generation status",
    description="Poll the status of a brochure generation task by its ID.",
)
async def get_status(task_id: str) -> BrochureStatusResponse:
    return handle_status(task_id)
