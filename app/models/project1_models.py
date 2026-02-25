from pydantic import BaseModel, HttpUrl


class BrochureRequest(BaseModel):
    url: HttpUrl
