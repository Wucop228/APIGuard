from pydantic import BaseModel, Field


class SpecUploadRequest(BaseModel):
    content: str = Field(
        ...,
        description="OpenAPI спецификация (JSON или YAML строкой)",
    )


class SpecStatusResponse(BaseModel):
    id: str
    status: str
    error_message: str | None = None


class SpecResultResponse(BaseModel):
    agent_type: str
    content: dict


class SpecDetailResponse(BaseModel):
    id: str
    status: str
    parsed_data: dict | None = None
    results: list[SpecResultResponse] = []
    error_message: str | None = None

class AgentCallbackRequest(BaseModel):
    agent_type: str
    status: str
    content: dict | None = None
    error: str | None = None