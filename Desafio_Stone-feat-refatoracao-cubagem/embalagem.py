"""
Algoritmos de redimensionamento de embalagem.

A LLM devolve as dimensões CRUAS do produto (comprimento, largura e altura
em cm). Antes de procurar a caixa ideal é preciso transformar essas medidas
nas dimensões EMBALADAS, que consideram dobras, folgas de proteção e
compressão conforme a categoria do produto.

A função pública é `calcular_dimensoes_embaladas`, que escolhe a estratégia
correta a partir do nome da estratégia declarado no catálogo.
"""


# Piso e margem de segurança aplicados à altura de itens dobráveis (cm).
ALTURA_MINIMA_CM = 1.0
MARGEM_ALTURA_CM = 1.5

# Teto para a espessura de uma peça têxtil deitada (cm). O algoritmo empilha
# essa espessura em div_c × div_l camadas; se a LLM superestima a espessura
# (ex.: devolve a peça já dobrada), o empilhamento explodiria o tamanho da
# caixa. Este limite mantém o cálculo realista para uma peça plana.
ESPESSURA_MAXIMA_TECIDO_CM = 2.0


def _dobravel(dimensoes, parametros):
    """
    Têxteis dobrados e comprimidos (vestuário, cama e banho).

    Itens com divisores definidos são dobrados: o comprimento e a largura são
    divididos, e a altura resulta das camadas dobradas (div_c × div_l) compactadas.
    Itens sem divisores (ex.: almofada) são apenas comprimidos nos três eixos.
    """
    comprimento = dimensoes["comprimento"]
    largura = dimensoes["largura"]
    altura = dimensoes["altura"]
    compressao = parametros["comp"]

    if parametros["div_c"] is None:
        comprimento_final = comprimento * compressao
        largura_final = largura * compressao
        altura_final = altura * compressao
    else:
        espessura = min(altura, ESPESSURA_MAXIMA_TECIDO_CM)
        camadas = parametros["div_c"] * parametros["div_l"]
        comprimento_final = comprimento / parametros["div_c"]
        largura_final = largura / parametros["div_l"]
        altura_final = (espessura * camadas) * compressao

    altura_final = max(altura_final, ALTURA_MINIMA_CM) + MARGEM_ALTURA_CM
    return _montar(comprimento_final, largura_final, altura_final)


def _calcado(dimensoes, parametros):
    """
    Par de calçado acomodado lado a lado dentro da caixa.

    A largura comporta o par (fator_l); comprimento e altura recebem folga
    fixa para o cano e a proteção.
    """
    comprimento_final = dimensoes["comprimento"] + parametros["folga_c"]
    largura_final = dimensoes["largura"] * parametros["fator_l"]
    altura_final = dimensoes["altura"] + parametros["folga_a"]
    return _montar(comprimento_final, largura_final, altura_final)


def _multiplicativo(dimensoes, parametros):
    """
    Eletrônicos: folga proporcional ao tamanho do produto (fc, fl, fa).
    """
    comprimento_final = dimensoes["comprimento"] * parametros["fc"]
    largura_final = dimensoes["largura"] * parametros["fl"]
    altura_final = dimensoes["altura"] * parametros["fa"]
    return _montar(comprimento_final, largura_final, altura_final)


def _aditivo(dimensoes, parametros):
    """
    Itens rígidos em geral: folga fixa em cm somada a cada eixo.
    """
    comprimento_final = dimensoes["comprimento"] + parametros["folga_c"]
    largura_final = dimensoes["largura"] + parametros["folga_l"]
    altura_final = dimensoes["altura"] + parametros["folga_a"]
    return _montar(comprimento_final, largura_final, altura_final)


# Mapeia o nome da estratégia (declarado no catálogo) para a sua função.
ESTRATEGIAS = {
    "dobravel": _dobravel,
    "calcado": _calcado,
    "multiplicativo": _multiplicativo,
    "aditivo": _aditivo,
}


def calcular_dimensoes_embaladas(estrategia, dimensoes_cruas, subcategoria):
    """
    Aplica a estratégia de embalagem da categoria às dimensões cruas.

    Recebe o nome da estratégia, as dimensões cruas vindas da LLM
    (comprimento, largura, altura em cm) e a subcategoria com os parâmetros.
    Devolve um dicionário com as dimensões embaladas, prontas para a busca
    da caixa ideal.
    """
    aplicar_estrategia = ESTRATEGIAS[estrategia]
    return aplicar_estrategia(dimensoes_cruas, subcategoria)


def _montar(comprimento, largura, altura):
    """Padroniza a saída: maior eixo = comprimento, menor = altura."""
    medidas = sorted([comprimento, largura, altura], reverse=True)
    return {
        "comprimento": round(medidas[0], 2),
        "largura": round(medidas[1], 2),
        "altura": round(medidas[2], 2),
    }
