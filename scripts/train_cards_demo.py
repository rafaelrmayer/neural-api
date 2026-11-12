"""Treina demonstração sintética: python -m scripts.train_cards_demo --output /content/modelo_cartoes_demo.pt."""
import argparse
import random
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F

from app.cards import FRASES, OPCOES_FIXAS, CardEngine


def train(output: Path):
    rng = random.Random(42)
    torch.manual_seed(42)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    examples = []
    for _ in range(1500):
        period, last = rng.randrange(3), rng.randrange(6)
        choice = last if last != 5 and rng.random() < 0.55 else rng.randrange(5)
        examples.append((period, last, choice))
    rng.shuffle(examples)

    def prepare(rows):
        data = torch.tensor(rows)
        x = torch.cat((F.one_hot(data[:, 0], 3), F.one_hot(data[:, 1], 6)), dim=1).float()
        return x, data[:, 2]

    x_train, y_train = prepare(examples[:1200])
    x_test, y_test = prepare(examples[1200:])
    model = nn.Sequential(nn.Linear(9, 16), nn.ReLU(), nn.Linear(16, 5))
    optimizer = torch.optim.Adam(model.parameters(), lr=0.02)
    model.train()
    for _ in range(200):
        optimizer.zero_grad()
        loss = F.cross_entropy(model(x_train), y_train)
        loss.backward()
        optimizer.step()
    model.eval()
    with torch.inference_mode():
        accuracy = (model(x_test).argmax(1) == y_test).float().mean().item()
        fallback = y_train.bincount(minlength=5).argmax().item()
        reference = torch.tensor([last if last != 5 else fallback for _, last, _ in examples[1200:]])
        baseline = (reference == y_test).float().mean().item()
    output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(dict(
        state_dict=model.state_dict(), frases=FRASES, opcoes_fixas=OPCOES_FIXAS,
        arquitetura=[9, 16, 5], dados_sinteticos=True,
        acuracia_teste=accuracy, acuracia_referencia=baseline,
        seed=42, torch_version=str(torch.__version__),
    ), output)
    restored = CardEngine(str(output))
    with torch.inference_mode():
        torch.testing.assert_close(model(x_test), restored.model(x_test), rtol=0, atol=0)
    print(f"Acerto da rede: {accuracy:.1%}; regra simples: {baseline:.1%}")
    print(f"Modelo salvo e recarregado com resultados idênticos: {output}")
    return accuracy, baseline


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    train(parser.parse_args().output)
