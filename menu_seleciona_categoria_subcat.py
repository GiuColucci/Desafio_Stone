'''
Cliente seleciona a categoria do produto e a subcategoria
'''

## Dicionário categorias
VESTUARIO = [
    # div_l = divisor largura | div_c = divisor comprimento
    # mult_e = multiplicador de espessura para altura dobrada | comp = fator de compressão
    {"id": 1, "nome": "Roupa Leve","exemplos": "Camiseta, Calça", "div_l": 2,"div_c": 2,"mult_e": 6,"comp": 0.60},
    {"id": 2, "nome": "Roupa Grossa","exemplos": "Moletom, Jaqueta", "div_l": 2,"div_c": 3,"mult_e": 6,"comp": 0.65},
    {"id": 3, "nome": "Roupa Íntima & Meia","exemplos": "Sutiã, Meia", "div_l": 2,"div_c": 4,"mult_e": 8,"comp": 0.50},
]

CASAEBANHO = [
    {"id": 1, "nome": "Lençol/Fronha","exemplos": "Casal, Solteiro","div_l": 4,"div_c": 6,"mult_e": 16,"comp": 0.55},
    {"id": 2, "nome": "Cobertor/Edredom","exemplos": "King, Casal", "div_l": 4,"div_c": 7, "mult_e": 16,"comp": 0.70},
    {"id": 3, "nome": "Almofada","exemplos": "Travesseiro, Pelúcia","div_l": None, "div_c": None, "mult_e": None, "comp": 0.75},
    {"id": 4, "nome": "Toalha","exemplos": "Banho, Rosto","div_l": 3,"div_c": 5,"mult_e": 12,"comp": 0.60},
]

CALCADO = [
    # cano    = altura cano padrão (cm)
    # fator_l = multiplicador de largura_pé para largura da caixa (comporta o par)
    # folga_c = folga de comprimento (cm)
    # alt_f   = altura final da caixa (cm, antes de comprimir)
    {"id": 1, "nome": "Chinelo/Sandália","exemplos": "Havaiana, rasteirinha", "cano": 2, "fator_l": 2.2, "folga_c": 2, "alt_f": 6},
    {"id": 2, "nome": "Tênis cano baixo/Sapatilha/Sapato Social", "exemplos": "Scarpin, All Star","cano": 15, "fator_l": 2.4, "folga_c": 3, "alt_f": 10},
    {"id": 3, "nome": "Tênis cano médio/Bota cano médio","exemplos": "Coturno, Air Jordan",   "cano": 35, "fator_l": 2.6, "folga_c": 4, "alt_f": 16},
    {"id": 4, "nome": "Tênis cano alto/Bota cano alto", "exemplos": "Montaria",              "cano": 55, "fator_l": 2.8, "folga_c": 5, "alt_f": 24},
]

ELETRONICOS = [
    # fc = fator comprimento | fl = fator largura | fa = fator altura
    {"id": 1,  "nome": "Smartphone",      "exemplos": "iPhone, Galaxy",   "fc": 1.10, "fl": 1.15, "fa": 4.00},
    {"id": 2,  "nome": "Tablet",          "exemplos": "iPad, Galaxy Tab", "fc": 1.08, "fl": 1.10, "fa": 2.50},
    {"id": 3,  "nome": "Notebook",        "exemplos": "MacBook, Dell",    "fc": 1.07, "fl": 1.07, "fa": 1.80},
    {"id": 4,  "nome": "Fone de ouvido",  "exemplos": "AirPods, JBL",     "fc": 1.30, "fl": 1.30, "fa": 1.50},
    {"id": 5,  "nome": "Headphone",       "exemplos": "Sony WH, Bose",    "fc": 1.20, "fl": 1.20, "fa": 1.30},
    {"id": 6,  "nome": "Carregador/Cabo", "exemplos": "USB-C, tomada",    "fc": 1.40, "fl": 1.40, "fa": 1.50},
    {"id": 7,  "nome": "Smartwatch",      "exemplos": "Apple Watch",      "fc": 1.20, "fl": 1.20, "fa": 2.50},
    {"id": 8,  "nome": "Console",         "exemplos": "PS5, Xbox",        "fc": 1.12, "fl": 1.12, "fa": 1.25},
    {"id": 9,  "nome": "Câmera",          "exemplos": "DSLR, GoPro",      "fc": 1.15, "fl": 1.15, "fa": 1.50},
    {"id": 10, "nome": "Monitor",         "exemplos": '24", 27"',          "fc": 1.15, "fl": 1.15, "fa": 1.40},
]

ELETRODOMESTICOS = [
    # folga_c/l/a = folgas em cm adicionadas a cada dimensão
    {"id": 1, "nome": "Pequeno Porte", "exemplos": "Liquidificador, torradeira, ferro","folga_c": 3, "folga_l": 3, "folga_a": 3},
    {"id": 2, "nome": "Médio Porte",   "exemplos": "Airfryer, cafeteira, batedeira","folga_c": 4, "folga_l": 4, "folga_a": 3},
    {"id": 3, "nome": "Grande Porte",  "exemplos": "Micro-ondas, aspirador, purificador", "folga_c": 5, "folga_l": 5, "folga_a": 4},
    {"id": 4, "nome": "Linha Branca",  "exemplos": "Geladeira, fogão", "folga_c": 8, "folga_l": 8, "folga_a": 10},
]

LIVROSEMIDIAS = [
    {"id": 1, "nome": "Livro único", "exemplos": "O pequeno príncipe, Vidas Secas", "folga_c": 1, "folga_l": 1, "folga_a": 1},
    {"id": 2, "nome": "Revistas e Catálogos", "exemplos": "Mangás, Revista Veja", "folga_c": 1, "folga_l": 1, "folga_a": 0.5},
    {"id": 3, "nome": "DVD/Blue-ray", "exemplos": "Álbum, coletânia", "folga_c": 0.5, "folga_l": 0.5, "folga_a": 0.5},
    {"id": 4, "nome":"Jogo de vídeo-game", "exemplos": "Mario Kart, Sonic", "folga_c": 0.5, "folga_l": 0.5, "folga_a": 0.5},
    {"id": 5, "nome": "Box Livros", "exemplos": "Box Harry Potter, coleção Jogos Vorazes", "folga_c": 2, "folga_l": 2, "folga_a": 2}

]

JOGOSEBRINQUEDOS = [
    {"id": 1, "nome": "Jogos de Tabuleiro", "exemplos": "Monopoly, Banco Imobiliário", "folga_c": 1.5, "folga_l": 1.5, "folga_a": 1.5},
    {"id": 2, "nome": "Card Game", "exemplos": "Coup, Uno", "folga_c": 0.5, "folga_l": 0.5, "folga_a": 0.5},
    {"id": 3, "nome": "Brinquedo Rígido", "exemplos": "Barbie - três mosqueteiras, Carrinho Hotweels", "folga_c": 3, "folga_l": 3, "folga_a": 3},
    {"id": 4, "nome": "Pelúcia", "exemplos": "Sansão - turma da Mônica", "folga_c": 2, "folga_l": 2, "folga_a": 2}
]

# Piso mínimo e margem aplicados à altura da embalagem de vestuário
MIN_ALTURA_CM    = 1.0
MARGEM_ALTURA_CM = 1.5


# Construção menu das categorias e subcategorias
CATEGORIAS = {
    "Vestuário":            VESTUARIO,
    "Casa & Banho":         CASAEBANHO,
    "Calçados":             CALCADO,
    "Eletrônicos":          ELETRONICOS,
    "Eletrodomésticos":     ELETRODOMESTICOS,
    "Livros & Mídias":      LIVROSEMIDIAS,
    "Jogos & Brinquedos":   JOGOSEBRINQUEDOS,
    "Sair":                 None
}

def selecionar_categoria():
    print("=========== STONE - CALCULADORA CUBAGEM ==============")
    lista = list(CATEGORIAS.keys())
    for i, nome in enumerate(lista, 1):
        print(f"  {i}. {nome}")
    escolha = int(input("Selecione a categoria do produto: ")) - 1
    return lista[escolha], CATEGORIAS[lista[escolha]]

def selecionar_subcategoria(subcategorias):
    for item in subcategorias:
        print(f"  {item['id']}. {item['nome']}  ({item['exemplos']})")
    escolha = int(input("Selecione a subcategoria: ")) - 1
    return subcategorias[escolha]

def main():
    while True:
        categoria, subs = selecionar_categoria()

        if categoria == "Sair":
            print("Encerrando. Até logo!")
            break
        
        sub = selecionar_subcategoria(subs)

        sabe_produto = input("Sabe o nome do produto? (S - sim; N - não):")
        if sabe_produto.lower() == "s":
            nome_produto = input("Digite o nome do produto: ")
        else:
            nome_produto = chama_api_llm(categoria, sub)
        
    dimensoes = chama_api_ml(nome_produto)
    
    if dimensoes is None:
        #chama API LLM para estimar cada uma

if __name__ == "__main__":
    main()