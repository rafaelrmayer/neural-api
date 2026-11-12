"""Sugestões experimentais; pesos carregados somente de arquivo configurado."""
import torch
from torch import nn

FRASES = [
    "Quero comer.",
    "Quero jogar Zelda: Ocarina of Time.",
    "Quero descansar.",
    "Quero desenhar.",
    "Quero ouvir uma história.",
]
OPCOES_FIXAS = ["Quero outra coisa.", "Não quero agora."]


class CardEngine:
    def __init__(self, path: str):
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
        if (checkpoint.get("arquitetura") != [9, 16, 5]
                or checkpoint.get("frases") != FRASES
                or checkpoint.get("opcoes_fixas") != OPCOES_FIXAS
                or checkpoint.get("dados_sinteticos") is not True):
            raise ValueError("Modelo incompatível com o contrato de cartões de demonstração.")
        self.model = nn.Sequential(nn.Linear(9, 16), nn.ReLU(), nn.Linear(16, 5))
        self.model.load_state_dict(checkpoint["state_dict"], strict=True)
        if not all(torch.isfinite(p).all() for p in self.model.parameters()):
            raise ValueError("Modelo contém pesos não finitos.")
        self.model.eval()

    def suggest(self, period: str, last_activity: int | None):
        inputs = torch.zeros(1, 9)
        inputs[0, ["manha", "tarde", "noite"].index(period)] = 1
        inputs[0, 3 + (5 if last_activity is None else last_activity)] = 1
        with torch.inference_mode():
            scores = self.model(inputs)[0]
        if not torch.isfinite(scores).all():
            raise ValueError("Modelo produziu pontuações não finitas.")
        order = sorted(range(5), key=lambda i: (-scores[i].item(), i))
        return [{"id": i, "phrase": FRASES[i]} for i in order]
