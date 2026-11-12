import pytest
import torch
from torch import nn
from fastapi.testclient import TestClient
from app.cards import CardEngine, FRASES, OPCOES_FIXAS
from app.main import app


@pytest.fixture
def checkpoint(tmp_path):
    model = nn.Sequential(nn.Linear(9, 16), nn.ReLU(), nn.Linear(16, 5))
    with torch.no_grad():
        for parameter in model.parameters():
            parameter.zero_()
        model[2].bias.copy_(torch.tensor([0., 4., 1., 2., 3.]))
    data = dict(state_dict=model.state_dict(), frases=FRASES,
                opcoes_fixas=OPCOES_FIXAS, arquitetura=[9, 16, 5], dados_sinteticos=True)
    path = tmp_path / 'cards.pt'
    torch.save(data, path)
    return path, data


def test_suggestions(checkpoint, monkeypatch):
    path, _ = checkpoint
    monkeypatch.setenv('CARDS_MODEL_PATH', str(path))
    with TestClient(app) as client:
        response = client.post('/v1/cards/suggestions', json={'period': 'tarde', 'last_activity': 1})
        assert response.status_code == 200
        data = response.json()
        assert [c['id'] for c in data['cards']] == [1, 4, 3, 2, 0]
        assert {c['phrase'] for c in data['cards']} == set(FRASES)
        assert data['fixed_options'] == OPCOES_FIXAS
        assert data['synthetic_data'] is data['experimental'] is True
        assert client.post('/v1/cards/suggestions', json={'period': 'manha'}).status_code == 200


@pytest.mark.parametrize('payload', [{}, {'period':'invalid'}, {'period':'tarde','last_activity':5},
    {'period':'tarde','last_activity':True}, {'period':'tarde','last_activity':'1'}])
def test_validation(payload):
    with TestClient(app) as client:
        assert client.post('/v1/cards/suggestions', json=payload).status_code == 422


def test_absent_model(monkeypatch):
    monkeypatch.delenv('CARDS_MODEL_PATH', raising=False)
    with TestClient(app) as client:
        assert client.post('/v1/cards/suggestions', json={'period':'noite'}).status_code == 503
        assert client.get('/health').status_code == 200


def test_invalid_checkpoint(checkpoint):
    path, data = checkpoint
    data['frases'] = list(reversed(FRASES))
    torch.save(data, path)
    with pytest.raises(ValueError):
        CardEngine(str(path))


def test_missing_file(monkeypatch):
    monkeypatch.setenv('CARDS_MODEL_PATH', '/missing/cards.pt')
    with TestClient(app) as client:
        assert client.post('/v1/cards/suggestions', json={'period':'manha'}).status_code == 503
