"""Floresta categórica pequena, determinística e treinada apenas com dados sintéticos.

Bootstrap de amostras, subconjunto aleatório de atributos por nó e voto majoritário.
Não recebe registros reais nem treina com requisições. Não possui validação clínica.
"""
from collections import Counter
from random import Random

from app.cards import FRASES

MODEL = "cards-rf-demo"
VERSION = "1.0.0"
PERIODS = ("manha", "tarde", "noite")


def synthetic_rows():
    rows = []
    for period in range(3):
        for last in range(-1, 5):
            # Regra de geração explícita; rótulos não representam preferências reais.
            label = (0 if last != 0 else 3) if period == 0 else (
                (1 if last in (-1, 0, 2) else 3) if period == 1 else
                (2 if last in (-1, 0, 1, 3) else 4)
            )
            rows.append(((period, last), label))
    return rows


class RandomForestCards:
    def __init__(self, seed=731, trees=31):
        self.random = Random(seed)
        self.rows = synthetic_rows()
        self.trees = [self._tree(self.random.choices(self.rows, k=len(self.rows)), 0)
                      for _ in range(trees)]

    def _tree(self, rows, depth):
        counts = Counter(label for _, label in rows)
        majority = min(counts, key=lambda label: (-counts[label], label))
        if len(counts) == 1 or depth >= 5 or len(rows) < 3:
            return majority
        # Uma das duas variáveis por nó: subespaço aleatório.
        feature = self.random.randrange(2)
        groups = {}
        for x, label in rows:
            groups.setdefault(x[feature], []).append((x, label))
        if len(groups) < 2:
            return majority
        return feature, majority, {value: self._tree(group, depth + 1)
                                   for value, group in groups.items()}

    @staticmethod
    def _predict(tree, x):
        while isinstance(tree, tuple):
            feature, fallback, branches = tree
            tree = branches.get(x[feature], fallback)
        return tree

    def suggest(self, period, last_activity, allowed):
        x = PERIODS.index(period), -1 if last_activity is None else last_activity
        votes = Counter(self._predict(tree, x) for tree in self.trees)
        ranked = sorted(allowed, key=lambda card: (-votes[card], card))
        return [{"id": card, "phrase": FRASES[card],
                 "score": votes[card] / len(self.trees)} for card in ranked]
