
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

## Sugestões de cartões (demonstração)

`POST /v1/cards/suggestions` ordena os cinco cartões, preservando seus IDs
(0: comer, 1: Zelda, 2: descansar, 3: desenhar, 4: história).
`fixed_options` sempre contém “Quero outra coisa.” e “Não quero agora.”.
O consumidor deve manter todas as opções acessíveis. As sugestões são opções de
comunicação; não inferem fome, sentimentos ou desejos.

Configure `CARDS_MODEL_PATH` com o caminho do `modelo_cartoes_demo.pt` exportado
pelo notebook. O arquivo deve conter state_dict, frases, opcoes_fixas,
arquitetura [9, 16, 5] e dados_sinteticos=true. Use apenas arquivos de origem
conhecida; o carregamento usa weights_only=True, em CPU. Os pesos não estão
incluídos no repositório e não são gerados durante a inicialização.

```bash
CARDS_MODEL_PATH=/caminho/modelo_cartoes_demo.pt uvicorn app.main:app --reload
```

Exemplo de corpo da requisição:

```json
{"period": "tarde", "last_activity": 1}
```

`period` aceita manha, tarde ou noite. `last_activity` aceita os IDs de 0 a 4,
ou null/omitido para ausência de histórico. A entrada usa one-hot do período
(três posições), seguido da última atividade (seis posições; a última significa
sem histórico). A resposta traz model=cards-demo, experimental=true,
synthetic_data=true, cards (id e phrase) e fixed_options. Não expõe pontuações
como probabilidades de preferência.

Sem arquivo válido, a rota retorna 503; contratos inválidos retornam 422.
O serviço e a rota experimental original continuam disponíveis. `/v1/models`
continua listando o modelo da rota `/v1/predict`; o modelo opcional de cartões
é identificado na própria resposta de sugestões.

O treinamento do Colab usa dados sintéticos com preferência artificial por
repetição. Na execução observada, a rede acertou 55,3% e a regra simples 57,3%:
não há evidência de vantagem do modelo nem de personalização para a Bia.
Este endpoint serve para validar a integração. Não registra escolhas ou dados
pessoais e ainda não integra a interface da Jornada de Bia.

### Gerar o modelo sem arquivo prévio

Na raiz do projeto, após instalar requirements.txt:

```bash
python -m scripts.train_cards_demo --output /content/modelo_cartoes_demo.pt
```

O script usa a semente 42, CPU e algoritmos determinísticos, gera 1.500 exemplos,
separa 1.200 para treino e 300 para teste, treina por 200 épocas e compara com a
regra simples. Exporta o checkpoint e verifica igualdade exata após recarregá-lo.
Para repetir resultados numéricos, use a mesma versão do PyTorch (registrada no
checkpoint); versões/plataformas diferentes podem produzir pequenas diferenças.
O script não lê dados da Bia nem altera o modelo da rota /v1/predict.

## Hospedagem HTTPS (contêiner)

O Dockerfile executa a API na porta 7860 com usuário sem privilégios e gera o
modelo sintético durante a construção. Não exige upload de pesos. O HTTPS deve
ser fornecido pela hospedagem na frente do contêiner; não é ativado pelo Uvicorn.

A variável CORS_ALLOWED_ORIGINS aceita origens separadas por vírgula, sem barra
final ou caminho. O contêiner permite por padrão https://rafaelrmayer.github.io.
Essa configuração permite chamadas pelo navegador da Jornada; CORS não é
autenticação. Não envie dados pessoais: este serviço é uma demonstração pública.
Sem a variável, a execução direta não permite chamadas entre origens.

No frontend, configure apenas o endereço base HTTPS publicado pelo provedor,
sem /docs ou /v1/cards/suggestions. A hospedagem pode suspender instâncias
inativas; os cartões devem continuar utilizáveis quando a API estiver indisponível.

### Publicar em Hugging Face Spaces

1. Crie um Space público com SDK Docker, template Blank e hardware CPU básico.
   Confira os custos/limites exibidos pelo provedor antes de confirmar.
2. Envie Dockerfile, requirements.txt e as pastas app e scripts a esse Space.
   Preserve o README de metadados criado pelo Hugging Face (`sdk: docker` e
   `app_port: 7860` no cabeçalho YAML). Não envie dados pessoais ou segredos.
3. Aguarde a construção. Ela instala PyTorch CPU e gera o modelo sintético.
4. Abra o endereço HTTPS direto do aplicativo, terminado em .hf.space, e teste
   /health e /docs. O endereço da página huggingface.co/spaces/... não é a URL
   base da API.
5. Na Jornada de Bia, em Configurações, salve o endereço base .hf.space e peça
   sugestões em Minha Comunicação. A origem GitHub Pages já está permitida pelo
   Dockerfile. Para outro domínio, ajuste CORS_ALLOWED_ORIGINS.

A imagem Docker e o deploy remoto precisam ser verificados na hospedagem.
Não considere o serviço publicado apenas porque o código foi integrado no GitHub.
