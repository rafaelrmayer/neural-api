from app.schemas import ModelInfo


MODEL_NAME = "simple-network"
MODELS = [
    ModelInfo(
        name=MODEL_NAME,
        version="0.1.0",
        description="Rede experimental com pesos aleatórios, sem treinamento; apenas para validar a integração.",
    ),
    ModelInfo(name="cards-rf-demo",version="1.0.0",description="Random Forest categórico com 31 árvores e dados sintéticos; votos não são probabilidades calibradas."),
]


def get_available_models() -> list[ModelInfo]:
    return [model.model_copy(deep=True) for model in MODELS]
