
from fastapi import FastAPI
from app.schemas import ModelInfo


app = FastAPI(
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
    return []
