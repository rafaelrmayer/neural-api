# Integração da Neural API com o RapidAPI

A [Neural API está pública no RapidAPI](https://rapidapi.com/RafaelMayer/api/neural-api), conforme confirmação do responsável em **24/11/2026**. O Basic está configurado a **US$ 0/mês**, com **1.000 chamadas/mês (Hard Limit)** e **10 chamadas/minuto**. A taxa de banda da plataforma, se aplicável, é separada da assinatura; conferir as condições atuais na conta.

As cinco operações foram testadas no gateway; após o deploy da proteção, o responsável confirmou novamente o health check e os dois POSTs de cartões com 200, além da recusa do acesso direto sem segredo. A descrição foi revisada e a visibilidade pública confirmada pelo responsável. Os testes não comprovam aplicação das cotas a uma conta consumidora nem disponibilidade contínua.

## Origem e caminhos

- Serviço público: `https://neural-api-s064.onrender.com`
- Base URL configurada no RapidAPI: `https://neural-api-s064.onrender.com/rapidapi`
- Painel de administração do Render não é a Base URL.

O namespace `/rapidapi` permite somente:

| Método | Caminho do endpoint na listagem |
| --- | --- |
| GET | `/health` |
| GET | `/v1/models` |
| POST | `/v1/predict` |
| POST | `/v1/cards/suggestions` |
| POST | `/v1/cards/random-forest/suggestions` |

O gateway acrescenta `X-RapidAPI-Proxy-Secret` em cada requisição. O middleware compara esse valor com a variável de ambiente `RAPIDAPI_PROXY_SECRET`, usando comparação em tempo constante. O consumidor continua usando sua chave RapidAPI; não deve receber o Proxy Secret.

## Configuração e manutenção pelo navegador

1. Fazer merge do PR e aguardar a conclusão do deploy da Neural API no Render. Se o serviço não tiver deploy automático, iniciar o deploy da versão revisada no painel.
2. Em RapidAPI → Hub Listing → Gateway → Firewall Settings, copiar **X-RapidAPI-Proxy-Secret** sem revelar ou publicar seu valor. Não usar a chave `X-RapidAPI-Key` do consumidor.
3. Em Render → serviço Neural API → **Environment**, adicionar a variável **`RAPIDAPI_PROXY_SECRET`** com o valor copiado. Usar a opção de salvar e aplicar/reimplantar oferecida pelo painel. Não colocar o segredo em código, GitHub, Dockerfile, Body, mensagens ou screenshots. Não alterar `CARDS_MODEL_PATH` nem `CORS_ALLOWED_ORIGINS`.
4. No RapidAPI → Hub Listing → General → **Base URL**, substituir o endereço atual por `https://neural-api-s064.onrender.com/rapidapi` e salvar.
5. Manter os caminhos das cinco operações como estão. Não adicionar `/rapidapi` em cada endpoint, pois o prefixo já está na Base URL. Não é necessário recriar ou reimportar os endpoints.
6. Testar as cinco operações novamente pelo RapidAPI, com os mesmos corpos sintéticos já validados; todas devem retornar 200. As duas rotas de cartões têm contratos diferentes: apenas Random Forest aceita `allowed_card_ids`.
7. Abrir `/rapidapi/health` diretamente no navegador, sem cabeçalho: deve retornar **403**. Abrir `/health` diretamente deve continuar retornando **200**.
8. Em uma nova listagem, manter privada até finalizar os testes e revisar a descrição e as condições do plano. A listagem atual foi publicada pelo responsável após essa revisão.

Não é necessário instalar pacotes novos, criar banco ou enviar arquivos de modelo para essa proteção. O valor não deve ser fornecido ao assistente; o responsável o cadastra diretamente no Render.

## Diagnóstico

| Resposta | Significado |
| --- | --- |
| 503 `gateway_not_configured` | O segredo não foi definido ou está vazio na instância do Render. |
| 403 `gateway_unauthorized` | Cabeçalho ausente, incorreto ou repetido; conferir os valores no Render/RapidAPI sem divulgá-los. |
| 404 `not_found` | O caminho não é uma das cinco operações do namespace; conferir Base URL e prefixo duplicado. |
| 405 `method_not_allowed` | Método incorreto; conferir GET versus POST. |
| 422 com `detail` | Validação da rota original; conferir JSON e campos permitidos. |
| 503 com `detail` de modelo | A autenticação passou, mas o modelo original está indisponível; conferir checkpoint e deploy. |

A rota de cartões exige o checkpoint sintético já configurado. O health check não testa todos os modelos. Uma chamada 200 não demonstra estabilidade sob carga, disponibilidade contínua ou que as cotas são aplicadas à conta proprietária.

## Alcance e limitações

A proteção autentica somente o namespace `/rapidapi`. As rotas públicas antigas, `/docs` e `/openapi.json` continuam disponíveis para os clientes existentes e a demonstração da Jornada. CORS não é autenticação. As cotas do RapidAPI não limitam globalmente consultas diretas ao serviço público; não anunciar exclusividade nem proteção global contra abuso por esta entrega.

`/rapidapi/docs`, `/rapidapi/openapi.json` e caminhos não autorizados não são encaminhados. O OpenAPI canônico continua descrevendo as cinco rotas originais. O middleware reutiliza a validação, os modelos e o ciclo de vida existentes; não treina ou altera previsões.

Este é um laboratório experimental com dados sintéticos. A rede simples usa pesos aleatórios não treinados. As sugestões não detectam intenção, fome ou sentimentos; votos de árvores não são probabilidades calibradas de preferência. Não enviar dados pessoais nem anunciar uso clínico. Esta alteração não modifica assinatura, cobrança ou visibilidade da listagem.
