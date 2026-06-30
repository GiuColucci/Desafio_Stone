"""
Seleção da caixa ideal e cálculo de peso.

A partir das dimensões já embaladas, encontra a menor caixa padrão dos
Correios que comporta o produto e calcula o peso cubado e o peso final
faturável. As funções deste módulo são puras: não imprimem nada, apenas
devolvem dados para a camada de interface.
"""


# Padrão RPC — Embalagens recomendadas pelos Correios (medidas em cm).
CAIXAS_PADRAO = [
    {"nome": "P04", "comprimento": 16, "largura": 12, "altura":  4},
    {"nome": "C08", "comprimento": 32, "largura": 12, "altura":  8},
    {"nome": "C12", "comprimento": 32, "largura": 12, "altura": 12},
    {"nome": "M08", "comprimento": 24, "largura": 16, "altura":  8},
    {"nome": "M12", "comprimento": 24, "largura": 16, "altura": 12},
    {"nome": "G08", "comprimento": 32, "largura": 24, "altura":  8},
    {"nome": "G12", "comprimento": 32, "largura": 24, "altura": 12},
    {"nome": "G16", "comprimento": 32, "largura": 24, "altura": 16},
    {"nome": "G20", "comprimento": 32, "largura": 24, "altura": 20},
    {"nome": "S04", "comprimento": 48, "largura": 32, "altura":  4},
    {"nome": "S08", "comprimento": 48, "largura": 32, "altura":  8},
    {"nome": "S12", "comprimento": 48, "largura": 32, "altura": 12},
    {"nome": "S16", "comprimento": 48, "largura": 32, "altura": 16},
    {"nome": "S20", "comprimento": 48, "largura": 32, "altura": 20},
    {"nome": "S24", "comprimento": 48, "largura": 32, "altura": 24},
    {"nome": "S28", "comprimento": 48, "largura": 32, "altura": 28},
    {"nome": "H12", "comprimento": 64, "largura": 48, "altura": 12},
    {"nome": "H20", "comprimento": 64, "largura": 48, "altura": 20},
    {"nome": "H28", "comprimento": 64, "largura": 48, "altura": 28},
    {"nome": "H32", "comprimento": 64, "largura": 48, "altura": 32},
    {"nome": "H48", "comprimento": 64, "largura": 48, "altura": 48},
]

# Fator de cubagem dos Correios para encomendas: 6000 cm³ equivalem a 1 kg.
FATOR_CUBAGEM = 6000

# Cubagem rodoviária para transportadora: 300 kg por metro cúbico. Usada
# quando o produto excede as caixas dos Correios (ex.: móveis volumosos).
FATOR_CUBAGEM_TRANSPORTADORA_KG_M3 = 300
CM3_POR_M3 = 1_000_000


def _produto_cabe_na_caixa(dimensoes, caixa):
    """Testa as seis orientações do produto contra as medidas da caixa."""
    eixos = (dimensoes["comprimento"], dimensoes["largura"], dimensoes["altura"])
    c, l, a = eixos
    orientacoes = [
        (c, l, a), (c, a, l),
        (l, c, a), (l, a, c),
        (a, c, l), (a, l, c),
    ]
    return any(
        pc <= caixa["comprimento"] and pl <= caixa["largura"] and pa <= caixa["altura"]
        for pc, pl, pa in orientacoes
    )


def _volume(caixa):
    return caixa["comprimento"] * caixa["largura"] * caixa["altura"]


def acha_caixa(dimensoes):
    """
    Devolve a menor caixa padrão que comporta o produto embalado,
    ou None se nenhuma caixa for suficiente.
    """
    caixas_validas = [
        caixa for caixa in CAIXAS_PADRAO if _produto_cabe_na_caixa(dimensoes, caixa)
    ]
    if not caixas_validas:
        return None
    return min(caixas_validas, key=_volume)


def calcula_peso_cubado(dimensoes):
    """
    Peso cubado (kg) a partir do volume do pacote já embalado.

    Usa as dimensões reais da encomenda (e não as da caixa padrão), para não
    cobrar o ar desperdiçado quando a menor caixa rígida disponível é bem maior
    que o produto — caso típico de itens leves e flexíveis, como roupas.
    """
    return round(_volume(dimensoes) / FATOR_CUBAGEM, 2)


def calcula_peso_cubado_transportadora(dimensoes):
    """Peso cubado (kg) pela tabela rodoviária, para envios via transportadora."""
    volume_m3 = _volume(dimensoes) / CM3_POR_M3
    return round(volume_m3 * FATOR_CUBAGEM_TRANSPORTADORA_KG_M3, 2)


def calcula_peso_faturavel(peso_real, peso_cubado):
    """
    Peso usado na cobrança do frete: o maior entre o peso real do produto
    e o peso cubado da caixa. Se o peso real não for conhecido, usa o cubado.
    """
    if peso_real is None:
        return peso_cubado
    return round(max(peso_real, peso_cubado), 2)
