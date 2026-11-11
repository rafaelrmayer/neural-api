
import pytest

from app.inference import InferenceEngine


def test_inference_engine_without_model():
    engine = InferenceEngine()

    assert engine.is_ready() is False


def test_inference_without_model_raises_error():
    engine = InferenceEngine()

    with pytest.raises(
        RuntimeError,
        match="Nenhum modelo neural está carregado."
    ):
        engine.predict([1.0, 2.0, 3.0])


def test_inference_with_model():
    engine = InferenceEngine()

    engine.model = lambda values: sum(values)

    assert engine.is_ready() is True
    assert engine.predict([1.0, 2.0, 3.0]) == 6.0

