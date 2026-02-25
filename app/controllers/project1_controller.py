"""Project 1 controller — AI Website Brochure Generator.

Thin layer that handles request/response shaping and delegates all business
logic to the brochure_generator service.
"""

from fastapi import HTTPException

from app.models.project1_models import (
    BrochureRequest,
    BrochureStatusResponse,
    BrochureTaskResponse,
)
from app.services.brochure_generator import get_task_status, start_generation


def handle_generate(request: BrochureRequest) -> BrochureTaskResponse:
    """Start a new brochure generation task and return the task ID."""
    task_id = start_generation(str(request.url))
    return BrochureTaskResponse(task_id=task_id, status="pending")


def handle_status(task_id: str) -> BrochureStatusResponse:
    """Return the current status of an existing generation task."""
    task = get_task_status(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return BrochureStatusResponse(
        task_id=task.task_id,
        status=task.status,
        result=task.result,
        error=task.error,
    )
