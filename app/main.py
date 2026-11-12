
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from app.schemas import ModelInfo, PredictionRequest, PredictionResponse
from app.model_registry import MODEL_NAME, get_available_models
from app.inference import InferenceEngine, ModelNotReadyError
from app.models.simple_network import SimpleNeuralNetwork


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = InferenceEngine(SimpleNeuralNetwork())
    yield
    app.state.engine = None


app = FastAPI(
    lifespan=lifespan,
    title="Neural API",
    description="API independente para inferência de redes neurais artificiais.",
    version="0.1.0",
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
