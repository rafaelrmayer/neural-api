from app.schemas import ModelInfo


MODEL_NAME = "simple-network"
MODELS = [
    ModelInfo(
        name=MODEL_NAME,
        version="0.1.0",
        description="Rede experimental com pesos aleatórios, sem treinamento; apenas para validar a integração.",
    )
]


def get_available_models() -> list[ModelInfo]:
    return [model.model_copy(deep=True) for model in MODELS]
