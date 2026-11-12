
from pydantic import BaseModel, Field, FiniteFloat


class ModelInfo(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    version: str = Field(min_length=1, max_length=30)
    description: str | None = None


class PredictionRequest(BaseModel):
    inputs: list[FiniteFloat] = Field(min_length=3, max_length=3)


class PredictionResponse(BaseModel):
    prediction: float = Field(allow_inf_nan=False)
    model: str
    experimental: bool = True
