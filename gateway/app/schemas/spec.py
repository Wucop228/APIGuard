from pydantic import BaseModel, Field


class SpecUploadRequest(BaseModel):
    content: str = Field(
        ...,
        description="OpenAPI спецификация (JSON или YAML строкой)",
    )