CAIXAS_PADRAO = [
    # Padrão RPC – Embalagens Recomendadas pelos Correios
    ## Categoria P (Pequena)
    {"nome": "P04", "c": 16, "l": 12, "a":  4},
    ## Categoria C (Comprida)
    {"nome": "C08", "c": 32, "l": 12, "a":  8},
    {"nome": "C12", "c": 32, "l": 12, "a": 12},
    ## Categoria M (Média)
    {"nome": "M08", "c": 24, "l": 16, "a":  8},
    {"nome": "M12", "c": 24, "l": 16, "a": 12},
    ## Categoria G (Grande)
    {"nome": "G08", "c": 32, "l": 24, "a":  8},
    {"nome": "G12", "c": 32, "l": 24, "a": 12},
    {"nome": "G16", "c": 32, "l": 24, "a": 16},
    {"nome": "G20", "c": 32, "l": 24, "a": 20},
    ## Categoria S (Super)
    {"nome": "S04", "c": 48, "l": 32, "a":  4},
    {"nome": "S08", "c": 48, "l": 32, "a":  8},
    {"nome": "S12", "c": 48, "l": 32, "a": 12},
    {"nome": "S16", "c": 48, "l": 32, "a": 16},
    {"nome": "S20", "c": 48, "l": 32, "a": 20},
    {"nome": "S24", "c": 48, "l": 32, "a": 24},
    {"nome": "S28", "c": 48, "l": 32, "a": 28},
    ##Categoria H (Hiper)
    {"nome": "H12", "c": 64, "l": 48, "a": 12},
    {"nome": "H20", "c": 64, "l": 48, "a": 20},
    {"nome": "H28", "c": 64, "l": 48, "a": 28},
    {"nome": "H32", "c": 64, "l": 48, "a": 32},
    {"nome": "H48", "c": 64, "l": 48, "a": 48},
]
def acha_caixa(dimensoes):
    """
    Recebe um dicionário com as dimensões do produto embalado.
    Retorna a menor caixa que comporta o produto.
    """
    c = dimensoes["comprimento"]
    l = dimensoes["largura"]
    a = dimensoes["altura"]

    caixas_validas = []

    for caixa in CAIXAS_PADRAO:
        # testa as 3 orientações possíveis do produto dentro da caixa
        orientacoes = [
            (c, l, a),
            (c, a, l),
            (l, c, a),
            (l, a, c),
            (a, c, l),
            (a, l, c),
        ]
        for pc, pl, pa in orientacoes:
            if pc <= caixa["c"] and pl <= caixa["l"] and pa <= caixa["a"]:
                volume = caixa["c"] * caixa["l"] * caixa["a"]
                caixas_validas.append((volume, caixa))
                break  # já encontrou uma orientação válida, não precisa testar as outras

    if not caixas_validas:
        print("Nenhuma caixa comporta o produto.")
        return None

    # ordena por volume e pega a menor
    caixas_validas.sort(key=lambda x: x[0])
    melhor = caixas_validas[0][1]

    print(f"\nMelhor caixa         : {melhor['nome']}")
    print(f"Dimensões da caixa   : {melhor['c']} x {melhor['l']} x {melhor['a']} cm")

    return melhor

