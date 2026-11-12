import math

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.inference import InferenceEngine


def test_prediction():
    with TestClient(app) as client:
        response = client.post('/v1/predict', json={'inputs': [1, 2, 3]})
        assert response.status_code == 200
        data = response.json()
        assert math.isfinite(data['prediction'])
        assert data['model'] == 'simple-network'
        assert data['experimental'] is True
        assert client.post('/v1/predict', json={'inputs': [1, 2, 3]}).json() == data


@pytest.mark.parametrize('payload', [{}, {'inputs': []}, {'inputs': [1, 2]},
    {'inputs': [1, 2, 3, 4]}, {'inputs': ['abc', 2, 3]},
    {'inputs': [None, 2, 3]}, {'inputs': ['NaN', 2, 3]},
    {'inputs': ['Infinity', 2, 3]}, {'inputs': [1e100, 2, 3]}])
def test_invalid_request(payload):
    with TestClient(app) as client:
        assert client.post('/v1/predict', json=payload).status_code == 422


def test_unavailable_model():
    with TestClient(app) as client:
        app.state.engine = InferenceEngine()
        assert client.post('/v1/predict', json={'inputs': [1, 2, 3]}).status_code == 503


def test_openapi_contract():
    with TestClient(app) as client:
        schema = client.get('/openapi.json').json()
        assert '/v1/predict' in schema['paths']
        inputs = schema['components']['schemas']['PredictionRequest']['properties']['inputs']
        assert inputs['minItems'] == inputs['maxItems'] == 3
