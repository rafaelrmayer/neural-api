import math

import pytest
import torch
from torch import nn

from app.inference import InferenceEngine, ModelNotReadyError
from app.models.simple_network import SimpleNeuralNetwork


def test_inference_without_model():
    engine = InferenceEngine()
    assert not engine.is_ready()
    with pytest.raises(ModelNotReadyError):
        engine.predict([1.0, 2.0, 3.0])


def test_real_network_inference():
    model = SimpleNeuralNetwork()
    engine = InferenceEngine(model)
    observed = []
    handle = model.register_forward_hook(
        lambda module, args, output: observed.append(
            (module.training, torch.is_inference_mode_enabled(), output.requires_grad)
        )
    )
    try:
        result = engine.predict([1.0, 2.0, 3.0])
        assert math.isfinite(result)
        assert result == engine.predict([1.0, 2.0, 3.0])
        assert observed == [(False, True, False)] * 2
    finally:
        handle.remove()


def test_known_weights():
    model = nn.Linear(3, 1)
    with torch.no_grad():
        model.weight.fill_(2)
        model.bias.fill_(1)
    assert InferenceEngine(model).predict([1.0, 2.0, 3.0]) == 13.0


@pytest.mark.parametrize('values', [[1.0], [1.0, float('nan'), 3.0], [1e100, 2.0, 3.0]])
def test_invalid_engine_input(values):
    with pytest.raises(ValueError):
        InferenceEngine(SimpleNeuralNetwork()).predict(values)
