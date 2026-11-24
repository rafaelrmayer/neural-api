"""Gateway authentication and compatibility with the public demonstration routes."""
import pytest
import torch
from torch import nn
from fastapi.testclient import TestClient

from app.main import app
from app.cards import FRASES, OPCOES_FIXAS


SECRET = 'fictitious-gateway-test-only'
HEADERS = {'X-RapidAPI-Proxy-Secret': SECRET}
CASES = [
    ('GET', '/health', None),
    ('GET', '/v1/models', None),
    ('POST', '/v1/predict', {'inputs': [1, 2, 3]}),
    ('POST', '/v1/cards/suggestions', {'period': 'tarde', 'last_activity': 0}),
    ('POST', '/v1/cards/random-forest/suggestions',
     {'period': 'tarde', 'last_activity': 0, 'allowed_card_ids': [0, 2]}),
]


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv('RAPIDAPI_PROXY_SECRET', SECRET)
    model = nn.Sequential(nn.Linear(9, 16), nn.ReLU(), nn.Linear(16, 5))
    path = tmp_path / 'synthetic-test.pt'
    torch.save(dict(state_dict=model.state_dict(), frases=FRASES, opcoes_fixas=OPCOES_FIXAS,
                    arquitetura=[9, 16, 5], dados_sinteticos=True), path)
    monkeypatch.setenv('CARDS_MODEL_PATH', str(path))
    with TestClient(app) as session:
        yield session


@pytest.mark.parametrize('method,path,payload', CASES)
def test_gateway_requires_secret_and_preserves_each_contract(client, method, path, payload):
    assert client.request(method, '/rapidapi' + path, json=payload).status_code == 403
    assert client.request(method, '/rapidapi' + path, json=payload,
                          headers={'X-RapidAPI-Proxy-Secret': 'wrong'}).status_code == 403
    public = client.request(method, path, json=payload)
    gateway = client.request(method, '/rapidapi' + path, json=payload, headers=HEADERS)
    assert gateway.status_code == public.status_code == 200
    assert gateway.json() == public.json()
    assert SECRET not in gateway.text


@pytest.mark.parametrize('value', [None, '', '   '])
def test_missing_configuration_fails_closed_but_public_api_works(client, monkeypatch, value):
    if value is None:
        monkeypatch.delenv('RAPIDAPI_PROXY_SECRET')
    else:
        monkeypatch.setenv('RAPIDAPI_PROXY_SECRET', value)
    response = client.get('/rapidapi/health', headers=HEADERS)
    assert response.status_code == 503
    assert response.json() == {'error': 'gateway_not_configured'}
    assert client.get('/health').status_code == 200


@pytest.mark.parametrize('path', ['/rapidapi', '/rapidapi/', '/rapidapi/docs',
                                '/rapidapi/openapi.json', '/rapidapi/admin',
                                '/rapidapi/health/', '/rapidapi/unknown'])
def test_gateway_does_not_forward_other_paths(client, path):
    assert client.get(path, headers=HEADERS).status_code == 404


@pytest.mark.parametrize('method,path', [('POST', '/health'), ('GET', '/v1/predict'),
                                      ('DELETE', '/v1/models'), ('OPTIONS', '/health')])
def test_gateway_methods_are_restricted(client, method, path):
    assert client.request(method, '/rapidapi' + path, headers=HEADERS).status_code == 405


def test_duplicate_or_invalid_secret_never_authenticates(client):
    assert client.get('/rapidapi/health', headers=[
        ('X-RapidAPI-Proxy-Secret', SECRET),
        ('X-RapidAPI-Proxy-Secret', SECRET),
    ]).status_code == 403
    assert client.get('/rapidapi/health', headers={
        'X-RapidAPI-Proxy-Secret': SECRET + ' ',
    }).status_code == 403


def test_validation_and_unavailable_model_are_preserved(client):
    response = client.post('/rapidapi/v1/cards/random-forest/suggestions',
                           json={'period': 'invalid'}, headers=HEADERS)
    assert response.status_code == 422
    app.state.card_engine = None
    response = client.post('/rapidapi/v1/cards/suggestions',
                           json={'period': 'tarde'}, headers=HEADERS)
    assert response.status_code == 503
    assert response.json() == {'detail': 'Modelo de cartões indisponível.'}


def test_original_documentation_remains_available_without_gateway_credentials(client):
    assert client.get('/docs').status_code == 200
    schema = client.get('/openapi.json').json()
    assert len(schema['paths']) == 5
    assert not any(path.startswith('/rapidapi') for path in schema['paths'])
    assert 'RAPIDAPI_PROXY_SECRET' not in str(schema)
