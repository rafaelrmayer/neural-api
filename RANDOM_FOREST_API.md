# API experimental de cartões com Random Forest

`POST /v1/cards/random-forest/suggestions` é um endpoint novo, independente da Data API da família. Reutiliza a infraestrutura FastAPI, Docker e CORS deste serviço, sem dependências novas.

## Contrato v1

```json
{"period":"tarde","last_activity":0,"allowed_card_ids":[0,1,2,3,4]}
```

- `period`: `manha`, `tarde` ou `noite`.
- `last_activity`: ID de 0 a 4, ou `null`; opcional.
- `allowed_card_ids`: lista opcional de 1 a 5 IDs únicos do catálogo de demonstração. Por padrão, os cinco. Não aceita booleanos, textos, IDs desconhecidos ou campos extras.

Resposta: `model: cards-rf-demo`, `version: 1.0.0`, `experimental: true`, `synthetic_data: true`, `score_kind: tree_vote_fraction`, cartões `{id, phrase, score}` e as duas opções fixas do catálogo existente.

Os cartões permitidos são ordenados pelos votos, com desempate pelo ID. Nenhum permitido é removido, mesmo com zero votos. A pontuação é fração de votos das árvores, não probabilidade calibrada, intenção detectada ou medida clínica. Em um subconjunto de cartões, os escores podem somar menos que um porque não são renormalizados. As opções fixas de recusa e alternativa permanecem separadas.

## Modelo e dados

Implementação categórica em Python padrão: 31 árvores, amostragem bootstrap, subconjunto aleatório de uma variável por nó, profundidade máxima 5 e semente 731. É treinada uma vez ao iniciar o processo sobre 18 contextos sintéticos (3 períodos × 6 estados do último cartão). `synthetic_rows()` contém a regra explícita que gera os rótulos.

Não recebe histórico para treinamento, não armazena as consultas e não atualiza os pesos a partir delas. O ajuste aos próprios 18 exemplos foi 18/18, **o que não mede generalização nem comprova melhoria sobre a regra que gerou esses exemplos**. A primeira versão serve para validar o contrato e a integração; não é personalização real da Bia.

O catálogo continua sendo os cinco cartões da demonstração neural existente. Esta versão não sugere frases livres, não opera símbolos personalizados e não substitui o Random Forest local da Jornada. Catálogos de outros projetos exigirão contrato/modelo próprios ou uma próxima versão explícita; não se deve reinterpretar estes IDs.

## Uso e disponibilidade

```bash
curl -X POST http://127.0.0.1:8000/v1/cards/random-forest/suggestions \
  -H 'Content-Type: application/json' \
  -d '{"period":"tarde","last_activity":null}'
```

O modelo está disponível sem `CARDS_MODEL_PATH`, porque não depende do checkpoint neural. O endpoint neural antigo e sua configuração permanecem. Indisponibilidade do modelo retorna 503.

No app, selecionar **Apoio → Mais opções → laboratório → Random Forest — API externa experimental**, informar a base HTTPS e salvar. Apenas a conta autorizada pode configurar a interface. Consultas só ocorrem ao tocar em **Atualizar cartões**. Se a API falhar, o app volta à ordenação local existente; não treina outro modelo com os dados pessoais.

## Publicação e limites de acesso

Integrar este PR e aguardar o deploy do serviço antes de testar o novo modo no app. Não exige banco, segredo ou variável nova. CORS usa a lista explícita já configurada em `CORS_ALLOWED_ORIGINS` e não permite credenciais.

O endpoint deste serviço é público, como a demonstração neural. CORS não é autenticação e a autorização do laboratório do aplicativo não restringe o endpoint a administradores. Esta entrega não deve receber dados pessoais; autenticação, limites de uso e isolamento de modelos serão necessários antes de disponibilizar treinamento ou catálogos privados.

## Testes

`python -m pytest -q`: 41 testes passaram, incluindo contratos anteriores, todos os contextos, repetibilidade, escores, filtragem por IDs, rejeição de campos extras e ausência de aprendizado por consulta. Não foi realizado teste de carga ou validação clínica.
