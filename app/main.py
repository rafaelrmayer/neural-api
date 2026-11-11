
from fastapi import FastAPI

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
