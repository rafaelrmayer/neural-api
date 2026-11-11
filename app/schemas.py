
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    version: str = Field(min_length=1, max_length=30)
    description: str | None = None
