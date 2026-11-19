
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
from pydantic import ConfigDict, field_validator


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


class RandomForestCardRequest(CardSuggestionRequest):
    allowed_card_ids: list[int] = Field(default_factory=lambda: list(range(5)), min_length=1, max_length=5)

    @field_validator('allowed_card_ids', mode='before')
    @classmethod
    def validate_allowed(cls, value):
        if not isinstance(value, list) or any(type(card) is not int or not 0 <= card < 5 for card in value) or len(set(value)) != len(value):
            raise ValueError('Use IDs únicos do catálogo de demonstração (0 a 4).')
        return value


class ScoredCard(SuggestedCard):
    score: FiniteFloat = Field(ge=0, le=1)


class RandomForestCardResponse(BaseModel):
    model: Literal['cards-rf-demo'] = 'cards-rf-demo'
    version: Literal['1.0.0'] = '1.0.0'
    experimental: Literal[True] = True
    synthetic_data: Literal[True] = True
    score_kind: Literal['tree_vote_fraction'] = 'tree_vote_fraction'
    cards: list[ScoredCard]
    fixed_options: list[str]
