"""
Calculadora de cubagem Stone — interface de linha de comando.

Orquestra o fluxo completo:
    1. usuário escolhe categoria e subcategoria;
    2. o produto é identificado (nome digitado, descrição ou imagem);
    3. a LLM busca as dimensões cruas do produto;
    4. as dimensões são embaladas conforme a estratégia da categoria;
    5. encontra-se a menor caixa dos Correios e o peso faturável.
"""
import sys

import arte
import caixa
import embalagem
import llm
from catalogo import CATEGORIAS

OPCAO_SAIR = "Sair"


# ---------------------------------------------------------------------------
# Entrada de dados validada
# ---------------------------------------------------------------------------
def pergunta_inteiro(mensagem, minimo, maximo):
    """Lê um inteiro entre `minimo` e `maximo`, repetindo até ser válido."""
    while True:
        resposta = input(mensagem).strip()
        if resposta.isdigit() and minimo <= int(resposta) <= maximo:
            return int(resposta)
        print(f"Digite um número entre {minimo} e {maximo}.")


# ---------------------------------------------------------------------------
# Seleção de categoria e subcategoria
# ---------------------------------------------------------------------------
def seleciona_categoria():
    """Exibe as categorias e devolve a escolhida, ou None se o usuário sair."""
    for indice, categoria in enumerate(CATEGORIAS, start=1):
        print(f"  {indice}. {categoria['nome']}")
    opcao_sair = len(CATEGORIAS) + 1
    print(f"  {opcao_sair}. {OPCAO_SAIR}")

    escolha = pergunta_inteiro("Selecione a categoria do produto: ", 1, opcao_sair)
    if escolha == opcao_sair:
        return None
    return CATEGORIAS[escolha - 1]


def seleciona_subcategoria(categoria):
    """Exibe as subcategorias da categoria e devolve a escolhida."""
    subcategorias = categoria["subcategorias"]
    for subcategoria in subcategorias:
        print(f"  {subcategoria['id']}. {subcategoria['nome']}  ({subcategoria['exemplos']})")
    escolha = pergunta_inteiro("Selecione a subcategoria: ", 1, len(subcategorias))
    return subcategorias[escolha - 1]


# ---------------------------------------------------------------------------
# Identificação do produto
# ---------------------------------------------------------------------------
def identifica_por_descricao(categoria, subcategoria):
    descricao = input("Descreva o produto: ").strip()
    return llm.identifica_produto(categoria["nome"], subcategoria, descricao=descricao)


def identifica_por_imagem(categoria, subcategoria):
    caminho = input("Caminho da imagem (ex: C:/Users/foto.jpg): ").strip()
    try:
        imagem = llm.carrega_imagem(caminho)
    except FileNotFoundError:
        print("Arquivo de imagem não encontrado.")
        return None
    return llm.identifica_produto(categoria["nome"], subcategoria, imagem=imagem)


def obtem_nome_produto(categoria, subcategoria):
    """
    Decide como obter o nome do produto: digitado pelo usuário, ou
    identificado pela LLM por descrição ou por imagem.
    """
    sabe_nome = input("Sabe o nome do produto? (S - sim; N - não): ").strip().lower()
    if sabe_nome == "s":
        return input("Digite o nome do produto: ").strip()

    print("\nComo deseja identificar o produto?")
    print("  1. Descrição em texto")
    print("  2. Imagem (caminho do arquivo)")
    modo = pergunta_inteiro("Escolha (1 ou 2): ", 1, 2)

    if modo == 1:
        identificacao = identifica_por_descricao(categoria, subcategoria)
    else:
        identificacao = identifica_por_imagem(categoria, subcategoria)

    if identificacao is None:
        return None
    exibe_identificacao(identificacao)
    return identificacao["nome_produto"]


# ---------------------------------------------------------------------------
# Apresentação dos resultados
# ---------------------------------------------------------------------------
def exibe_identificacao(identificacao):
    print(f"\nProduto identificado : {identificacao['nome_produto']}")
    if identificacao.get("observacao"):
        print(f"Observação           : {identificacao['observacao']}")


def exibe_dimensoes(dimensoes):
    print(f"\nProduto encontrado   : {dimensoes['nome_encontrado']}")
    print(f"Dimensões (C x L x A): "
          f"{dimensoes['comprimento']} x {dimensoes['largura']} x {dimensoes['altura']} cm")
    print(f"Peso                 : {dimensoes['peso']} kg")
    if dimensoes.get("fonte"):
        print(f"Fonte                : {dimensoes['fonte']}")
    if dimensoes.get("observacao"):
        print(f"Observação           : {dimensoes['observacao']}")


def exibe_resultado_caixa(embalada, melhor_caixa, peso_cubado, peso_faturavel):
    print(f"\nDimensões embaladas  : "
          f"{embalada['comprimento']} x {embalada['largura']} x {embalada['altura']} cm")
    print(f"Melhor caixa         : {melhor_caixa['nome']}")
    print(f"Dimensões da caixa   : "
          f"{melhor_caixa['comprimento']} x {melhor_caixa['largura']} x {melhor_caixa['altura']} cm")
    print(f"Peso cubado          : {peso_cubado} kg")
    print(f"Peso faturável       : {peso_faturavel} kg")


def exibe_envio_transportadora(embalada, peso_real):
    """Mostra dimensões e peso de cubagem rodoviária para itens volumosos."""
    peso_cubado = caixa.calcula_peso_cubado_transportadora(embalada)
    peso_faturavel = caixa.calcula_peso_faturavel(peso_real, peso_cubado)
    print(f"\nDimensões embaladas  : "
          f"{embalada['comprimento']} x {embalada['largura']} x {embalada['altura']} cm")
    print(f"Peso cubado (rodov.) : {peso_cubado} kg")
    print(f"Peso faturável       : {peso_faturavel} kg")


def avisa_produto_sem_caixa(categoria):
    print("\nAVISO: o produto excede o tamanho das embalagens padrão dos Correios.")
    if categoria["nome"] == "Móveis":
        print("Considere o envio via transportadora ou embalagem customizada.")


# ---------------------------------------------------------------------------
# Pipeline de cálculo
# ---------------------------------------------------------------------------
def calcula_embalagem(categoria, subcategoria, nome_produto):
    """Da dimensão crua ao peso faturável; imprime cada passo do resultado."""
    dimensoes = llm.busca_dimensoes(nome_produto, categoria["nome"], subcategoria)
    if dimensoes is None:
        print("Não foi possível obter as dimensões do produto.")
        return
    exibe_dimensoes(dimensoes)

    embalada = embalagem.calcular_dimensoes_embaladas(
        categoria["estrategia"], dimensoes, subcategoria
    )
    melhor_caixa = caixa.acha_caixa(embalada)
    if melhor_caixa is None:
        exibe_envio_transportadora(embalada, dimensoes.get("peso"))
        avisa_produto_sem_caixa(categoria)
        return

    peso_cubado = caixa.calcula_peso_cubado(embalada)
    peso_faturavel = caixa.calcula_peso_faturavel(dimensoes.get("peso"), peso_cubado)
    exibe_resultado_caixa(embalada, melhor_caixa, peso_cubado, peso_faturavel)


# ---------------------------------------------------------------------------
# Laço principal
# ---------------------------------------------------------------------------
def configura_saida_utf8():
    """Garante UTF-8 na saída para exibir acentos e a arte ASCII no Windows."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def main():
    configura_saida_utf8()
    print(arte.INTRO)
    while True:
        categoria = seleciona_categoria()
        if categoria is None:
            print("Encerrando. Até logo!")
            break

        subcategoria = seleciona_subcategoria(categoria)
        nome_produto = obtem_nome_produto(categoria, subcategoria)
        if not nome_produto:
            print("Nome do produto não encontrado.")
            continue

        calcula_embalagem(categoria, subcategoria, nome_produto)


if __name__ == "__main__":
    main()
