"""Execução de modelos PyTorch para inferência."""

import math

import torch
from torch import nn


class ModelNotReadyError(RuntimeError):
    """Não há modelo disponível para inferência."""


class InferenceEngine:
    def __init__(self, model: nn.Module | None = None):
        self.model = model
        if self.model is not None:
            self.model.eval()

    def is_ready(self) -> bool:
        return self.model is not None

    def predict(self, input_data: list[float]) -> float:
        if self.model is None:
            raise ModelNotReadyError("Nenhum modelo neural está carregado.")
        if len(input_data) != 3 or not all(math.isfinite(v) for v in input_data):
            raise ValueError("Informe exatamente três números finitos.")

        inputs = torch.tensor([input_data], dtype=torch.float32)
        if not torch.isfinite(inputs).all():
            raise ValueError("Os valores excedem a capacidade numérica do modelo.")
        self.model.eval()
        with torch.inference_mode():
            result = self.model(inputs).item()
        if not math.isfinite(result):
            raise ValueError("A entrada produziu um resultado não finito.")
        return result
