

import torch
from torch import nn


class SimpleNeuralNetwork(nn.Module):
    """Rede neural simples para validar inferências."""

    def __init__(self):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(3, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.network(inputs)
