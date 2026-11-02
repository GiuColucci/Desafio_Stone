# Desafio Stone: identificação de produto e caixa ideal de envio com LLM

> Projeto desenvolvido em equipe durante a **graduação em Inteligência Artificial na PUC-Rio**, como resposta a um desafio de logística de e-commerce.
>
> **Minha contribuição:** desenvolvimento do backend, com foco nos algoritmos de dimensionamento e de seleção de caixa, e na preparação da apresentação final.

Dada a descrição (texto ou foto) de um produto, o sistema descobre o que ele é, estima as dimensões da embalagem e indica a menor caixa padrão dos Correios em que ele cabe.

## O problema

No e-commerce, o vendedor muitas vezes não sabe as dimensões exatas do produto embalado. Isso gera frete calculado errado e caixas grandes demais. O objetivo é automatizar essa estimativa a partir de informações que o vendedor já tem: uma descrição ou uma foto.

## Como funciona

```text
Categoria e subcategoria  ─┐
Descrição ou imagem        ├─► LLM (Gemini)  ─► nome comercial padronizado + confiança
                           ┘                           │
                                                       ▼
                                          API do Mercado Livre
                                       (dimensões e peso do item)
                                                       │
                                                       ▼
                                  Ajuste por subcategoria (dobra, compressão, folgas)
                                                       │
                                                       ▼
                                    Menor caixa padrão dos Correios que comporta o item
```

1. **Menu de categoria** (`menu_seleciona_categoria_subcat.py`): vestuário, casa e banho, calçados, eletrônicos, eletrodomésticos e outros. Cada subcategoria tem parâmetros próprios de embalagem (fator de dobra, compressão, folgas).
2. **Identificação com LLM** (`busca_apis.py`): um prompt de sistema obriga o Gemini a responder apenas JSON (`nome_produto`, `confianca`, `observacao`), sem inventar especificações. Aceita texto ou imagem.
3. **Dimensões** (`busca_apis.py`): busca o produto no Mercado Livre e lê comprimento, largura, altura e peso.
4. **Algoritmos de embalagem** (`algoritmos_subcat.py`): três famílias de cálculo (dobráveis, calçados e eletrônicos, e itens rígidos com folga fixa).
5. **Caixa ótima** (`acha_caixa_otima.py`): escolhe, entre as embalagens padrão dos Correios (P, C, M, G, S e H), a menor que comporta o item.

A documentação completa e o fluxograma estão em [`docs/`](docs/).

## Tecnologias

Python, Google Gemini (`google-genai`), API do Mercado Livre, `requests`, `python-dotenv`.

## Como rodar

```bash
git clone https://github.com/GiuColucci/Desafio_Stone.git
cd Desafio_Stone
pip install -r requirements.txt
cp .env.example .env      # coloque sua GEMINI_API_KEY no .env
python menu_seleciona_categoria_subcat.py
```

A chave vem do [Google AI Studio](https://aistudio.google.com/apikey). O arquivo `.env` **nunca** deve ser commitado.

## Decisões de projeto

- **Saída estruturada com nível de confiança:** o sistema sabe e informa quando não tem certeza, em vez de inventar um modelo.
- **Heurísticas por subcategoria:** roupa dobra e comprime, calçado precisa de folga, eletrônico leva proteção. Cada uma tem seus fatores numa tabela, fácil de ajustar.
- **Caixas padronizadas:** usa o catálogo de embalagens recomendadas dos Correios, o que torna o resultado utilizável na prática.

## Próximos passos

- Testes automatizados para os algoritmos de embalagem.
- Validar as estimativas contra medidas reais.
- Tratar falhas da API de produtos e respostas fora do formato esperado do LLM.
- Interface web.
