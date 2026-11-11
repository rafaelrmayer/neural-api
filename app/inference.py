

from typing import Any


class InferenceEngine:
    """Motor responsável pela execução de modelos neurais."""

    def __init__(self):
        self.model = None

    def is_ready(self) -> bool:
        """Verifica se existe um modelo carregado."""
        return self.model is not None

    def predict(self, input_data: Any) -> Any:
        """Executa uma inferência utilizando o modelo carregado."""
        if not self.is_ready():
            raise RuntimeError(
                "Nenhum modelo neural está carregado."
            )

        return self.model(input_data)
