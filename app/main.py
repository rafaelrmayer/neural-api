import logging
import os


from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.rapidapi import RapidAPIGateway
from app.schemas import ModelInfo, PredictionRequest, PredictionResponse
from app.model_registry import MODEL_NAME, get_available_models
from app.inference import InferenceEngine, ModelNotReadyError
from app.models.simple_network import SimpleNeuralNetwork
from app.cards import CardEngine, OPCOES_FIXAS
from app.random_forest_cards import RandomForestCards
from app.schemas import RandomForestCardRequest, RandomForestCardResponse
from app.schemas import CardSuggestionRequest, CardSuggestionResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = InferenceEngine(SimpleNeuralNetwork())
    app.state.rf_cards = RandomForestCards()
    app.state.card_engine = None
    path = os.environ.get("CARDS_MODEL_PATH")
    if path:
        try:
            app.state.card_engine = CardEngine(path)
        except Exception:
            logging.getLogger(__name__).exception("Falha ao carregar modelo de cartões")
    yield
    app.state.card_engine = None
    app.state.engine = None


app = FastAPI(
    lifespan=lifespan,
    title="Neural API",
    description="API independente para inferência de redes neurais artificiais.",
    version="0.1.0",
)

app.add_middleware(RapidAPIGateway)


# Origens explícitas para o frontend; sem credenciais ou curingas.
allowed_origins = [value.strip() for value in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if value.strip()]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["POST"],
        allow_headers=["Content-Type"],
        allow_credentials=False,
    )

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "neural-api",
        "version": "0.1.0",
    }


@app.get("/v1/models", response_model=list[ModelInfo], tags=["Models"])
def list_models():
    return get_available_models()


@app.post(
    "/v1/predict",
    response_model=PredictionResponse,
    tags=["Inference"],
    summary="Executa uma rede experimental sem treinamento",
    responses={503: {"description": "Modelo indisponível"}},
)
def predict(payload: PredictionRequest, request: Request):
    engine = getattr(request.app.state, "engine", None)
    if engine is None:
        raise HTTPException(status_code=503, detail="Nenhum modelo neural está carregado.")
    try:
        prediction = engine.predict(payload.inputs)
    except ModelNotReadyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return PredictionResponse(prediction=prediction, model=MODEL_NAME)


@app.post(
    "/v1/cards/suggestions",
    response_model=CardSuggestionResponse,
    tags=["Cards"],
    summary="Ordena todos os cartões com modelo de demonstração sintético",
    responses={503: {"description": "Modelo de cartões indisponível"}},
)
def suggest_cards(payload: CardSuggestionRequest, request: Request):
    engine = getattr(request.app.state, "card_engine", None)
    if engine is None:
        raise HTTPException(503, "Modelo de cartões indisponível.")
    try:
        cards = engine.suggest(payload.period, payload.last_activity)
    except ValueError as exc:
        raise HTTPException(503, "Modelo de cartões indisponível.") from exc
    return CardSuggestionResponse(cards=cards, fixed_options=OPCOES_FIXAS.copy())


@app.post('/v1/cards/random-forest/suggestions', response_model=RandomForestCardResponse,
          tags=['Cards'], summary='Ordenação experimental por Random Forest sintético')
def suggest_rf_cards(payload: RandomForestCardRequest, request: Request):
    engine = getattr(request.app.state, 'rf_cards', None)
    if engine is None:
        raise HTTPException(503, 'Modelo experimental indisponível.')
    return RandomForestCardResponse(
        cards=engine.suggest(payload.period, payload.last_activity, payload.allowed_card_ids),
        fixed_options=OPCOES_FIXAS.copy(),
    )
