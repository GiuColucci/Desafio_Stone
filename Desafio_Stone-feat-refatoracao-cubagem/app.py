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
import banco
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


def _le_float(mensagem):
    """Lê um número decimal do usuário, repetindo até ser válido."""
    while True:
        resposta = input(mensagem).strip()
        try:
            valor = float(resposta)
            if valor > 0:
                return valor
            print("O valor deve ser maior que zero.")
        except ValueError:
            print("Digite um número válido (use ponto para decimais).")


# ---------------------------------------------------------------------------
# Comandos do banco de dados (bd)
# ---------------------------------------------------------------------------
def bd_help():
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║                 COMANDOS DO BANCO DE DADOS                   ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  bd help   — Exibe esta lista de comandos                    ║")
    print("║  bd show   — Lista todos os produtos registrados             ║")
    print("║  bd add    — Adiciona um produto manualmente                 ║")
    print("║               Campos: nome, categoria, subcategoria,         ║")
    print("║               comprimento (cm), largura (cm), altura (cm),   ║")
    print("║               peso (kg)                                      ║")
    print("║  bd remove — Remove um produto pelo nome                     ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")


def bd_show():
    registros = banco.listar_todos()
    if not registros:
        print("\n  Banco de dados vazio.\n")
        return
    print(f"\n  {'='*80}")
    print(f"  BANCO DE DADOS LOCAL — {len(registros)} registro(s)")
    print(f"  {'='*80}")
    for i, r in enumerate(registros, 1):
        print(f"\n  [{i}] {r['nome_produto']}")
        print(f"      Categoria     : {r['categoria']} > {r['subcategoria']}")
        print(f"      Dimensões     : {r['comprimento']} x {r['largura']} x {r['altura']} cm")
        print(f"      Peso          : {r['peso']} kg")
        print(f"      Confiança LLM : {r['confianca']}")
        print(f"      Fonte         : {r['fonte']}")
        print(f"      Registrado em : {r['criado_em'][:19]}")
    print(f"\n  {'='*80}\n")


def bd_add():
    print("\n  Adicionar produto ao banco de dados")
    print("  -----------------------------------")
    nome = input("  Nome do produto: ").strip()
    if not nome:
        print("  Nome não pode ser vazio.")
        return
    print("\n  Categorias disponíveis:")
    for i, cat in enumerate(CATEGORIAS, 1):
        print(f"    {i}. {cat['nome']}")
    idx_cat = pergunta_inteiro("  Selecione a categoria: ", 1, len(CATEGORIAS))
    categoria = CATEGORIAS[idx_cat - 1]
    print(f"\n  Subcategorias de {categoria['nome']}:")
    for sub in categoria["subcategorias"]:
        print(f"    {sub['id']}. {sub['nome']}  ({sub['exemplos']})")
    idx_sub = pergunta_inteiro("  Selecione a subcategoria: ", 1, len(categoria["subcategorias"]))
    subcategoria = categoria["subcategorias"][idx_sub - 1]
    comprimento = _le_float("  Comprimento (cm): ")
    largura     = _le_float("  Largura (cm): ")
    altura      = _le_float("  Altura (cm): ")
    peso        = _le_float("  Peso (kg): ")
    ok = banco.adicionar_manual(
        nome, categoria["nome"], subcategoria["nome"],
        comprimento, largura, altura, peso,
    )
    if ok:
        print(f"\n  Produto '{nome}' adicionado ao banco com sucesso.\n")
    else:
        print(f"\n  Produto '{nome}' já existe no banco.\n")


def bd_remove():
    nome = input("\n  Nome do produto a remover: ").strip()
    if not nome:
        print("  Nome não pode ser vazio.")
        return
    removidos = banco.remover(nome)
    if removidos > 0:
        print(f"  {removidos} registro(s) removido(s) do banco.\n")
    else:
        print(f"  Nenhum produto encontrado com nome similar a '{nome}'.\n")


def trata_comando_bd(entrada):
    """Retorna True se a entrada era um comando 'bd' e foi tratado."""
    cmd = entrada.lower().strip()
    if cmd == "bd help":
        bd_help()
        return True
    if cmd == "bd show":
        bd_show()
        return True
    if cmd == "bd add":
        bd_add()
        return True
    if cmd == "bd remove":
        bd_remove()
        return True
    if cmd.startswith("bd"):
        print("  Comando não reconhecido. Digite 'bd help' para ver os comandos.\n")
        return True
    return False


# ---------------------------------------------------------------------------
# Seleção de categoria e subcategoria
# ---------------------------------------------------------------------------
def seleciona_categoria():
    """Exibe as categorias e devolve a escolhida, ou None se o usuário sair."""
    while True:
        for indice, categoria in enumerate(CATEGORIAS, start=1):
            print(f"  {indice}. {categoria['nome']}")
        opcao_sair = len(CATEGORIAS) + 1
        print(f"  {opcao_sair}. {OPCAO_SAIR}")
        print("  (digite 'bd help' para comandos do banco de dados)")

        entrada = input("\nSelecione a categoria do produto: ").strip()

        if trata_comando_bd(entrada):
            continue

        if entrada.isdigit() and 1 <= int(entrada) <= opcao_sair:
            escolha = int(entrada)
            if escolha == opcao_sair:
                return None
            return CATEGORIAS[escolha - 1]

        print(f"Digite um número entre 1 e {opcao_sair}.\n")


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

    # Feedback sobre origem dos dados
    if dimensoes.get("origem") == "banco":
        print("\n  [BD] Resultado recuperado do banco de dados local.")
    else:
        nome_bd = dimensoes.get("nome_encontrado", nome_produto)
        print(f"\n  [BD] Produto salvo no banco de dados local.")
        print(f"       Caso queira remover essa entrada -> bd remove")
        print(f"       Nome registrado: {nome_bd}")

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
    total = banco.total_registros()
    if total > 0:
        print(f"  Banco de dados local: {total} produto(s) registrado(s)")
    print("  Digite 'bd help' a qualquer momento para gerenciar o banco.\n")
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
