
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


from typing import Literal
from pydantic import ConfigDict


class CardSuggestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    period: Literal["manha", "tarde", "noite"]
    last_activity: int | None = Field(default=None, ge=0, le=4, strict=True)


class SuggestedCard(BaseModel):
    id: int
    phrase: str


class CardSuggestionResponse(BaseModel):
    model: Literal["cards-demo"] = "cards-demo"
    experimental: Literal[True] = True
    synthetic_data: Literal[True] = True
    cards: list[SuggestedCard]
    fixed_options: list[str]
