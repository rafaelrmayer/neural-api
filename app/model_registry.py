

from app.schemas import ModelInfo


# Registro inicial dos modelos neurais disponíveis.
# Nesta versão, ainda não há modelos carregados.
MODELS: list[ModelInfo] = []


def get_available_models() -> list[ModelInfo]:
    """Retorna os modelos registrados na Neural API."""
    return MODELS.copy()
