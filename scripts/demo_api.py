"""Demonstração com entradas sintéticas: python -m scripts.demo_api --base-url http://127.0.0.1:8000."""
import argparse
import json
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

CASES = (
    ('Disponibilidade', '/health', None),
    ('Catálogo declarado', '/v1/models', None),
    ('Rede simples — sem treinamento', '/v1/predict', {'inputs': [1.0, 2.0, 3.0]}),
    ('Rede de cartões — dados sintéticos', '/v1/cards/suggestions', {'period': 'tarde', 'last_activity': 0}),
    ('Random Forest — dados sintéticos', '/v1/cards/random-forest/suggestions', {'period': 'tarde', 'last_activity': 0}),
)


def base_url(value):
    url = urlsplit(value)
    if url.username or url.password or url.query or url.fragment or not url.netloc:
        raise argparse.ArgumentTypeError('Use uma base sem credenciais, parâmetros ou fragmentos.')
    if url.scheme != 'https' and not (url.scheme == 'http' and url.hostname in {'localhost', '127.0.0.1', '::1'}):
        raise argparse.ArgumentTypeError('Use HTTPS, ou HTTP apenas em localhost.')
    return value.rstrip('/')


def run(base, timeout):
    results = []
    for title, path, payload in CASES:
        request = Request(base + path, data=json.dumps(payload).encode() if payload else None,
                          headers={'Accept': 'application/json', **({'Content-Type': 'application/json'} if payload else {})})
        try:
            with urlopen(request, timeout=timeout) as response:
                item = dict(title=title, endpoint=path, status=response.status, request=payload,
                            response=json.load(response))
        except HTTPError as error:
            item = dict(title=title, endpoint=path, status=error.code, request=payload,
                        error='A API recusou ou não pôde atender este exemplo.')
        except (URLError, TimeoutError, ValueError):
            item = dict(title=title, endpoint=path, status=None, request=payload,
                        error='Sem resposta JSON válida no tempo definido.')
        results.append(item)
    return dict(project='Neural API', generated_at=datetime.now(timezone.utc).isoformat(),
                base_url=base, synthetic_examples=True, results=results,
                notice='Exemplos técnicos, sem dados pessoais. Resultados não têm validação clínica. Os modelos não usam o mesmo conjunto de treino; esta execução não compara sua qualidade.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', type=base_url, default='http://127.0.0.1:8000')
    parser.add_argument('--timeout', type=float, default=15)
    parser.add_argument('--output', help='Arquivo JSON opcional com as respostas reais desta execução.')
    args = parser.parse_args()
    if not 0 < args.timeout <= 60:
        parser.error('timeout deve estar entre 0 e 60 segundos')
    report = run(args.base_url, args.timeout)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(text + '\n', encoding='utf-8')
    return 0 if all(item['status'] == 200 for item in report['results']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
