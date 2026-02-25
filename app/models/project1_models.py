from pydantic import BaseModel, HttpUrl


class BrochureRequest(BaseModel):
    url: HttpUrl


class BrochureTaskResponse(BaseModel):
    task_id: str
    status: str


class BrochureStatusResponse(BaseModel):
    task_id: str
    status: str
    result: str | None = None
    error: str | None = None
