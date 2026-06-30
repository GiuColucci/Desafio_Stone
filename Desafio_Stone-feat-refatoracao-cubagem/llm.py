"""
Acesso à LLM (Gemini via OpenRouter) para identificar produtos e buscar dimensões.

Este módulo cuida apenas da comunicação com a API: monta o contexto, faz a
chamada e devolve dados estruturados. A interação com o usuário e a exibição
dos resultados ficam na camada de interface (app.py).

A API do OpenRouter é compatível com a do OpenAI; por isso usamos o SDK
`openai` apontando para a base do OpenRouter. A busca de dimensões precisa de
acesso à web, habilitado pelo sufixo ":online" no nome do modelo.
"""
import base64
import json
import os

import banco
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # lê o .env e injeta as variáveis de ambiente

# Cliente OpenRouter (compatível com OpenAI) instanciado uma única vez.
_cliente = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Mesmo modelo Gemini, agora servido pelo OpenRouter.
_MODELO = "google/gemini-2.5-flash"
_MODELO_COM_BUSCA = "google/gemini-2.5-flash:online"  # ":online" ativa a busca na web

# Tipos MIME aceitos para identificação por imagem.
TIPOS_IMAGEM = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg",
    "png": "image/png", "webp": "image/webp",
}


PROMPT_IDENTIFICACAO = """
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
3. O campo "nome_produto" deve conter marca, modelo e especificação relevante
   (capacidade, tamanho, cor se determinante). Exemplo: "Samsung Galaxy S23 128GB Preto".
4. Nunca invente especificações que não estejam evidentes na descrição ou imagem.
5. Se não for possível identificar o produto com segurança, use confiança "baixa"
   e explique na observação o que está faltando.
6. Considere a categoria e a subcategoria fornecidas para refinar a identificação.
7. Padronize o nome em português brasileiro.
"""


PROMPT_DIMENSOES = """
Você é um especialista em obter dimensões físicas exatas de produtos para fins logísticos.

Seu fluxo interno tem duas etapas (NÃO descreva o raciocínio na saída):
ETAPA 1 — Canonicalize o nome do produto (marca + modelo + spec relevante).
ETAPA 2 — Use a busca na web para localizar as dimensões oficiais.
          Priorize: site do fabricante, manual/ficha técnica, varejistas confiáveis.

## Regras obrigatórias

1. Retorne APENAS um objeto JSON puro, sem markdown, sem cercas, sem texto extra.
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
3. Unidades obrigatórias: dimensões em CENTÍMETROS, peso em QUILOGRAMAS.
   Converta antes de retornar se a fonte usar outra unidade.
4. Convenção: maior valor = comprimento, intermediário = largura, menor = altura.
5. Use a categoria e a subcategoria para desambiguar produtos de nomes parecidos.
6. NUNCA invente dimensões. Sem dado oficial, estime por similaridade com produto
   conhecido da mesma categoria e BAIXE a confiança proporcionalmente.
7. Para roupas e têxteis, a "altura" é a ESPESSURA do tecido com a peça deitada e
   esticada (uma camada), tipicamente 0,3 a 2 cm — NÃO a espessura da peça dobrada.
8. Para líquidos e bebidas, o "peso" é o peso BRUTO (embalagem cheia + recipiente).
   Ex.: uma garrafa de vinho de 750 ml pesa cerca de 1,2 kg, não apenas o líquido.

## Escala de confiança
- 90-100: spec oficial do fabricante confirmada
- 70-89:  spec consistente entre 2+ varejistas confiáveis
- 40-69:  dado parcial ou estimativa por similaridade
- 10-39:  estimativa fraca (categoria + tamanho típico)
- 0-9:    nenhuma referência viável (use só em último caso)
"""


def _extrai_json(resposta):
    """Remove cercas de markdown e converte a resposta da LLM em dicionário."""
    texto = resposta.choices[0].message.content.strip()
    texto = texto.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(texto)


def _conversa(modelo, prompt_sistema, conteudo_usuario):
    """Faz uma chamada de chat e devolve a resposta bruta da API."""
    return _cliente.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": conteudo_usuario},
        ],
    )


def carrega_imagem(caminho):
    """
    Lê um arquivo de imagem e devolve o bloco de conteúdo no formato esperado
    pela API (data URL em base64). Levanta FileNotFoundError se não existir.
    """
    with open(caminho, "rb") as arquivo:
        dados = arquivo.read()
    extensao = caminho.rsplit(".", 1)[-1].lower()
    mime = TIPOS_IMAGEM.get(extensao, "image/jpeg")
    base64_imagem = base64.b64encode(dados).decode("utf-8")
    return {
        "type": "image_url",
        "image_url": {"url": f"data:{mime};base64,{base64_imagem}"},
    }


def identifica_produto(categoria, subcategoria, descricao=None, imagem=None):
    """
    Identifica o nome comercial do produto a partir de uma descrição em texto
    ou de uma imagem. Devolve o dicionário da LLM com nome_produto, confianca
    e observacao, ou None em caso de falha.
    """
    contexto = f"Categoria: {categoria}\nSubcategoria: {subcategoria['nome']}\n"

    if imagem is not None:
        conteudo = [
            {"type": "text", "text": contexto + "Identifique o produto na imagem abaixo:"},
            imagem,
        ]
    else:
        conteudo = contexto + f"Descrição do produto: {descricao}"

    try:
        resposta = _conversa(_MODELO, PROMPT_IDENTIFICACAO, conteudo)
        return _extrai_json(resposta)
    except (json.JSONDecodeError, AttributeError, KeyError, IndexError) as erro:
        print(f"\nFalha ao interpretar a resposta da LLM ({type(erro).__name__}): {erro}")
        return None
    except Exception as erro:
        print(f"\nErro na chamada à LLM de identificação: {erro}")
        return None


def busca_dimensoes(nome_produto, categoria, subcategoria):
    """
    Busca as dimensões físicas do produto.

    Fluxo:
      1. Consulta o banco de dados local.
         → Achou? Retorna direto (BD é fonte da verdade).
      2. Não achou? Busca via LLM com acesso à web.
         → Salva o resultado no banco para consultas futuras.
    """
    # ----- ETAPA 1: banco local (fonte da verdade) -----
    referencia = banco.buscar(nome_produto, categoria, subcategoria["nome"])
    if referencia:
        referencia["fonte"] = f"Banco local (similaridade {referencia['similaridade']})"
        referencia["origem"] = "banco"
        return referencia

    # ----- ETAPA 2: busca via LLM (código original intocado) -----
    contexto = (
        f"Categoria: {categoria}\n"
        f"Subcategoria: {subcategoria['nome']}\n"
        f"Produto informado pelo usuário: {nome_produto}\n\n"
        "Identifique o nome canônico e busque na web as dimensões físicas "
        "oficiais deste produto. Responda apenas com o JSON especificado."
    )

    try:
        resposta = _conversa(_MODELO_COM_BUSCA, PROMPT_DIMENSOES, contexto)
        dimensoes = _extrai_json(resposta)
    except (json.JSONDecodeError, AttributeError, KeyError, IndexError) as erro:
        print(f"\nFalha ao interpretar a resposta da LLM ({type(erro).__name__}): {erro}")
        return None
    except Exception as erro:
        print(f"\nErro na chamada à LLM de dimensões: {erro}")
        return None

    # ----- ETAPA 3: salva no banco para consultas futuras -----
    if dimensoes:
        banco.registrar(nome_produto, categoria, subcategoria["nome"], dimensoes)
        dimensoes["origem"] = "web"

    return dimensoes
