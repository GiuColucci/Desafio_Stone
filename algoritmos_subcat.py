'''
Algoritmo que atende as categorias: Vestuário, Casa & Banho e Brinquedos & Jogos de Tabuleiro

'''
MIN_ALTURA_CM = 1.0
MARGEM_ALTURA_CM = 1.5
def redimensiona1(comprimento,largura,altura,subcategoria):
    comp_ajustado = comprimento / subcategoria["div_c"]
    larg_ajustada = largura     / subcategoria["div_l"]
    alt_ajustada  = (altura  * subcategoria["mult_e"]) * subcategoria["comp"]

    alt_ajustada = max(alt_ajustada, MIN_ALTURA_CM) + MARGEM_ALTURA_CM
    return {
        "Comprimento embalado": round(comp_ajustado, 2),
        "Largura embalado":round(larg_ajustada, 2),
        "Altura embalado":round(alt_ajustada,  2),
    }

def calcado(altura_cano,largura_pe,comprimento_pe,subcategoria):
    if altura_cano:
        altura_cano_ajustada = subcategoria["alt_f"]
    larg_ajustada = 2.2*largura_pe
    comp_ajustado = comprimento_pe + 2

    return {
        "Altura embalado" : round(altura_cano_ajustada,2),
        "Largura embalado": round(larg_ajustada,2),
        "Comprimento embalado": round(comp_ajustado,2)
    }

def eletronicos(altura, largura,comprimento,subcategoria):
    alt_ajustada = altura*subcategoria["fa"]
    larg_ajustada = largura*subcategoria["fl"]
    comp_ajustado = comprimento*subcategoria["fc"]

    return {
        "Altura embalado" : round(alt_ajustada,2),
        "Largura embalado": round(larg_ajustada,2),
        "Comprimento embalado": round(comp_ajustado,2)
    }

'''
Algoritmo que atende as categorias: Eletrodomésticos, Livros & Mídia e Brinquedos & Jogos de Tabuleiro
'''
def redimendiona2(altura,largura,comprimento,subcategoria):
    alt_ajustada= altura + subcategoria["fa"]
    comp_ajustado = comprimento + subcategoria["fc"]
    larg_ajustada = largura + subcategoria["fl"]

    return {
        "Altura embalado" : round(alt_ajustada,2),
        "Largura embalado": round(larg_ajustada,2),
        "Comprimento embalado": round(comp_ajustado,2)
    }


