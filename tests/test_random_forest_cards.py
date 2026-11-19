import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.random_forest_cards import RandomForestCards, synthetic_rows


def test_deterministic_and_all_contexts():
    a, b = RandomForestCards(), RandomForestCards()
    for period in ['manha', 'tarde', 'noite']:
        for last in [None, 0, 1, 2, 3, 4]:
            result = a.suggest(period, last, list(range(5)))
            assert result == b.suggest(period, last, list(range(5)))
            assert sorted(card['id'] for card in result) == list(range(5))
            assert sum(card['score'] for card in result) == pytest.approx(1)
            assert all(0 <= card['score'] <= 1 for card in result)


def test_allowed_catalog_and_contract():
    with TestClient(app) as client:
        response = client.post('/v1/cards/random-forest/suggestions', json={
            'period': 'tarde', 'last_activity': 0, 'allowed_card_ids': [1, 4]})
        assert response.status_code == 200
        data = response.json()
        assert data['model'] == 'cards-rf-demo'
        assert data['synthetic_data'] is True and data['experimental'] is True
        assert data['score_kind'] == 'tree_vote_fraction'
        assert sorted(card['id'] for card in data['cards']) == [1, 4]


@pytest.mark.parametrize('extra', [
    {'allowed_card_ids': [0, 0]}, {'allowed_card_ids': []}, {'allowed_card_ids': [99]},
    {'allowed_card_ids': [True]}, {'allowed_card_ids': ['1']},
    {'history': ['texto pessoal']}, {'period': 'invalid'}, {'last_activity': True},
])
def test_rejects_invalid_and_extra_fields(extra):
    with TestClient(app) as client:
        assert client.post('/v1/cards/random-forest/suggestions', json={'period': 'manha', **extra}).status_code == 422


def test_no_online_learning_or_model_mutation():
    with TestClient(app) as client:
        request = {'period': 'noite', 'last_activity': 2}
        before = client.post('/v1/cards/random-forest/suggestions', json=request).json()
        client.post('/v1/cards/random-forest/suggestions', json={'period': 'manha'})
        assert client.post('/v1/cards/random-forest/suggestions', json=request).json() == before
    assert len(synthetic_rows()) == 18
