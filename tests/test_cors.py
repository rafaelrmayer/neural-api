"""Contrato de acesso do frontend publicado à API."""
import os
import subprocess
import sys


def test_cors_explicit_origin():
    code = '''
from fastapi.testclient import TestClient
from app.main import app
with TestClient(app) as client:
    for origin, expected in [('https://rafaelrmayer.github.io', 200), ('https://other.example', 400)]:
        response = client.options('/v1/cards/suggestions', headers={
            'Origin': origin, 'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type'})
        assert response.status_code == expected
        assert response.headers.get('access-control-allow-origin') == (origin if expected == 200 else None)
        assert response.headers.get('access-control-allow-credentials') is None
'''
    subprocess.run([sys.executable, '-c', code], check=True,
                   env={**os.environ, 'CORS_ALLOWED_ORIGINS': 'https://rafaelrmayer.github.io'})
