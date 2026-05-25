from google import genai
from google.genai import types
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()  # ← lê o .env e injeta as variáveis

# ============================================================
# CLIENTE GEMINI — instanciado uma vez (cache)
# ============================================================
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ============================================================
# PROMPT DO SISTEMA
# ============================================================
SYSTEM_PROMPT = """
Você é um especialista em identificação de produtos de e-commerce para fins logísticos.

Seu único objetivo é identificar o nome comercial completo e padronizado de um produto
a partir de uma descrição em texto ou de uma imagem fornecida pelo usuário.

## Regras obrigatórias

1. Retorne APENAS um objeto JSON, sem texto adicional, sem markdown, sem explicações.
2. O JSON deve seguir exatamente esta estrutura:
   {
     "nome_produto": "<nome comercial completo>",
     "confianca": "<alta | media | baixa>",
     "observacao": "<motivo se confiança for média ou baixa, senão null>"
   }
3. O campo "nome_produto" deve conter:
   - Marca
   - Modelo
   - Especificação relevante (capacidade, tamanho, cor se determinante)
   - Exemplo: "Samsung Galaxy S23 128GB Preto"
4. Nunca invente especificações que não estejam evidentes na descrição ou imagem.
5. Se não for possível identificar o produto com segurança, use confiança "baixa"
   e explique na observação o que está faltando.
6. Considere o contexto de categoria e subcategoria fornecidos para refinar a identificação.
7. Padronize o nome em português brasileiro.

## Exemplos de saída esperada

Entrada: "celular da samsung com tela grande, cor preta, 256gb"
Saída:
{
  "nome_produto": "Samsung Galaxy S23 Ultra 256GB Preto",
  "confianca": "media",
  "observacao": "Modelo inferido pela descrição de tela grande e 256GB, pode ser outro modelo da linha S"
}

Entrada: "airpods pro segunda geração"
Saída:
{
  "nome_produto": "Apple AirPods Pro 2ª Geração",
  "confianca": "alta",
  "observacao": null
}
"""


# ============================================================
# CHAMADA À LLM
# ============================================================
def chama_api_llm(categoria, subcategoria):
    """
    Recebe categoria e subcategoria para contextualizar a LLM.
    Pergunta ao usuário descrição em texto ou caminho de imagem.
    Retorna o nome comercial do produto identificado.
    """
    print("\nComo deseja identificar o produto?")
    print("  1. Descrição em texto")
    print("  2. Imagem (caminho do arquivo)")
    modo = input("Escolha (1 ou 2): ").strip()

    contexto = (
        f"Categoria: {categoria}\n"
        f"Subcategoria: {subcategoria['nome']}\n"
    )

    if modo == "1":
        descricao = input("Descreva o produto: ").strip()
        conteudo = contexto + f"Descrição do produto: {descricao}"

    elif modo == "2":
        caminho = input("Caminho da imagem (ex: C:/Users/foto.jpg): ").strip()
        with open(caminho, "rb") as f:
            dados_imagem = f.read()

        extensao = caminho.split(".")[-1].lower()
        media_types = {
            "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "png": "image/png",  "webp": "image/webp"
        }
        media_type = media_types.get(extensao, "image/jpeg")

        conteudo = [
            contexto + "Identifique o produto na imagem abaixo:",
            types.Part.from_bytes(data=dados_imagem, mime_type=media_type)
        ]

    else:
        print("Opção inválida.")
        return None

    # chamada à API com system prompt em cache
    resposta = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        contents=conteudo
    )
    # limpa possíveis marcadores markdown e parseia o JSON
    texto = resposta.text.strip().removeprefix("```json").removesuffix("```").strip()
    dados = json.loads(texto)

    print(f"\nProduto identificado : {dados['nome_produto']}")
    print(f"Confiança            : {dados['confianca']}")
    if dados["observacao"]:
        print(f"Observação           : {dados['observacao']}")

    return dados["nome_produto"]
# ============================================================
# PROMPT DO SISTEMA — DIMENSÕES
# ============================================================
DIMENSOES_SYSTEM_PROMPT = """
Você é um especialista em obter dimensões físicas exatas de produtos para fins logísticos.

Seu fluxo interno tem duas etapas (NÃO descreva o raciocínio na saída):

ETAPA 1 — Canonicalize o nome do produto (marca + modelo + spec relevante).
ETAPA 2 — Use a ferramenta de busca na web para localizar as dimensões oficiais.
          Priorize, nesta ordem: site do fabricante, manual/ficha técnica,
          varejistas confiáveis (Mercado Livre, Amazon, Magalu, Casas Bahia).

## Regras obrigatórias

1. Retorne APENAS um objeto JSON puro, sem markdown, sem cercas ```json```, sem texto extra.
2. O JSON deve seguir EXATAMENTE esta estrutura:
   {
     "nome_encontrado": "<nome canônico: marca + modelo + spec>",
     "comprimento": <número em cm>,
     "largura":     <número em cm>,
     "altura":      <número em cm>,
     "peso":        <número em kg>,
     "confianca":   <inteiro de 0 a 100>,
     "fonte":       "<URL ou descrição da fonte usada>",
     "observacao":  "<motivo se confianca < 70, senão null>"
   }
3. Unidades obrigatórias: dimensões em CENTÍMETROS (cm), peso em QUILOGRAMAS (kg).
   Se a fonte fornecer polegadas, mm, gramas etc., converta antes de retornar.
4. Convenção das dimensões: maior valor = comprimento, intermediário = largura,
   menor = altura. Isso garante consistência com o algoritmo de caixa ótima.
5. Use a categoria e a subcategoria para desambiguar (ex: "iPhone 15" como Smartphone
   tem dimensões totalmente diferentes de "Capa iPhone 15" como Acessório).
6. NUNCA invente dimensões. Se não encontrar dado oficial, estime por similaridade
   com produto conhecido da mesma categoria e BAIXE a confiança proporcionalmente.

## Escala de confiança

- 90-100: spec oficial do fabricante encontrada e confirmada
- 70-89:  spec consistente entre 2+ varejistas confiáveis
- 40-69:  dado parcial ou estimativa por similaridade com produto conhecido
- 10-39:  estimativa fraca (categoria + tamanho típico, sem fonte específica)
- 0-9:    nenhuma referência viável encontrada (use só em último caso)

## Exemplo

Contexto: Categoria: Eletrônicos | Subcategoria: Smartphone
Produto informado: "iphone 15 128gb preto"

Saída:
{"nome_encontrado":"Apple iPhone 15 128GB Preto","comprimento":14.76,"largura":7.15,"altura":0.78,"peso":0.171,"confianca":95,"fonte":"apple.com/br/iphone-15/specs","observacao":null}
"""


# ============================================================
# CHAMADA À LLM DIMENSOES
# ============================================================
def chama_api_llm_dimensoes(nome_produto, categoria, subcategoria):
    """
    Busca dimensões físicas de um produto via Gemini com Google Search grounding.

    Faz uma única chamada à LLM, que internamente (1) canonicaliza o nome do
    produto e (2) consulta a web pelas dimensões oficiais via Google Search.
    A categoria e a subcategoria são usadas como contexto para desambiguar
    produtos com nomes parecidos.

    Sempre retorna o dicionário com as melhores estimativas disponíveis,
    mesmo em confiança muito baixa. Retorna None apenas em falha de parsing
    ou erro de rede irrecuperável.
    """
    contexto = (
        f"Categoria: {categoria}\n"
        f"Subcategoria: {subcategoria['nome']}\n"
        f"Produto informado pelo usuário: {nome_produto}\n\n"
        "Identifique o nome canônico e busque na web as dimensões físicas "
        "oficiais deste produto. Responda apenas com o JSON especificado."
    )

    try:
        resposta = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=DIMENSOES_SYSTEM_PROMPT,
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
            contents=contexto,
        )

        texto = resposta.text.strip().removeprefix("```json").removesuffix("```").strip()
        dimensoes = json.loads(texto)

    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        print(f"\nFalha ao interpretar resposta da LLM ({type(e).__name__}): {e}")
        return None
    except Exception as e:
        print(f"\nErro na chamada à LLM de dimensões: {e}")
        return None

    print(f"\nProduto encontrado   : {dimensoes['nome_encontrado']}")
    print(f"Comprimento          : {dimensoes['comprimento']} cm")
    print(f"Largura              : {dimensoes['largura']} cm")
    print(f"Altura               : {dimensoes['altura']} cm")
    print(f"Peso                 : {dimensoes['peso']} kg")
    print(f"Confiança            : {dimensoes['confianca']}/100")
    if dimensoes.get("fonte"):
        print(f"Fonte                : {dimensoes['fonte']}")
    if dimensoes.get("observacao"):
        print(f"Observação           : {dimensoes['observacao']}")

    return dimensoes


# ============================================================
# CHAMADA À API DO MERCADO LIVRE
# ============================================================
def chama_api_ml(nome_produto):
    """
    Busca o produto no Mercado Livre pelo nome.
    Retorna altura, comprimento, largura e peso do primeiro resultado.
    """
    url = "https://api.mercadolibre.com/sites/MLB/search"
    params = {"q": nome_produto, "limit": 1}

    resposta = requests.get(url, params=params)
    resposta.raise_for_status()
    dados = resposta.json()

    resultados = dados.get("results", [])
    if not resultados:
        print("Nenhum produto encontrado no Mercado Livre.")
        return None

    item_id = resultados[0]["id"]

    # busca detalhes do item para obter dimensões
    resposta_item = requests.get(f"https://api.mercadolibre.com/items/{item_id}")
    resposta_item.raise_for_status()
    detalhes = resposta_item.json()

    shipping = detalhes.get("shipping", {})
    dims = shipping.get("dimensions") or {}

    dimensoes = {
        "nome_encontrado": detalhes.get("title"),
        "comprimento":     dims.get("length"),
        "largura":         dims.get("width"),
        "altura":          dims.get("height"),
        "peso":            dims.get("weight"),
    }

    print(f"\nProduto encontrado   : {dimensoes['nome_encontrado']}")
    print(f"Comprimento          : {dimensoes['comprimento']} cm")
    print(f"Largura              : {dimensoes['largura']} cm")
    print(f"Altura               : {dimensoes['altura']} cm")
    print(f"Peso                 : {dimensoes['peso']} kg")

    return dimensoes