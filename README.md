
# Neural API

API independente para desenvolvimento, inferência e integração de modelos de redes neurais artificiais.

**Versão planejada:** V0.1  
**Status:** Primeira integração experimental de inferência
**Responsável:** Rafael Ricardo Mayer — Pesquisador independente

## Objetivo

Desenvolver uma API modular de inteligência artificial que permita executar modelos de redes neurais e disponibilizar seus resultados para diferentes aplicações.

O projeto terá foco em acessibilidade, comunicação personalizada e tecnologias assistivas.

## Princípios

- Arquitetura modular e independente.
- Integração por APIs REST.
- Privacidade e segurança desde o início.
- Modelos avaliados antes da utilização em aplicações reais.
- Supervisão humana em decisões sensíveis.
- Acessibilidade como prioridade.

## Arquitetura inicial proposta

- **API:** FastAPI e Python.
- **Inferência:** módulo independente para execução de modelos.
- **Modelos:** suporte inicial a redes neurais com PyTorch.
- **Validação:** contratos de entrada e saída com Pydantic.
- **Testes:** pytest.
- **Documentação:** OpenAPI e Swagger UI.

## Escopo da V0.1

1. Criar a estrutura básica do projeto.
2. Implementar o endpoint `/health`.
3. Definir os contratos de entrada e saída.
4. Implementar um primeiro modelo experimental.
5. Criar um endpoint de inferência.
6. Adicionar testes automatizados.
7. Documentar limitações e resultados.

## Integrações futuras

A Neural API poderá ser utilizada por aplicações independentes, incluindo a Jornada de Bia, mediante contratos de integração bem definidos.

## Segurança e responsabilidade

Os resultados dos modelos serão tratados como previsões ou sugestões, não como certezas.

Dados pessoais e sensíveis não serão utilizados para treinamento sem autorização e controles adequados.

## Situação atual

A API disponibiliza `/health`, `/v1/models` e `/v1/predict`, com validação e testes automatizados. O primeiro modelo é experimental e ainda não foi treinado.

## Executar e experimentar

Requer Python 3.12. Crie um ambiente virtual e execute:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse `http://127.0.0.1:8000/docs` para usar o Swagger.

```bash
curl -X POST http://127.0.0.1:8000/v1/predict \
  -H 'Content-Type: application/json' \
  -d '{"inputs": [1.0, 2.0, 3.0]}'
```

A resposta contém `prediction` (número), `model` (`simple-network`) e
`experimental` (`true`). A rede usa três entradas, oito neurônios intermediários,
ReLU e uma saída. Ela é carregada uma vez por processo na inicialização.
Os pesos são aleatórios e não treinados: o resultado não tem significado
preditivo e pode mudar ao reiniciar o servidor. Não representa uma probabilidade.

A API rejeita entradas que não tenham exatamente três números finitos (422),
incluindo valores que excedem a capacidade numérica do modelo ou produzam saída
não finita. Modelo indisponível retorna 503. `/health` informa que o serviço está
ativo; `/v1/models` lista o modelo experimental.

Execute os testes com `python -m pytest -q`.
