"""
Catálogo de categorias e subcategorias de produtos.

Este módulo contém apenas DADOS: cada categoria conhece o seu nome, a
estratégia de embalagem que se aplica a ela e a lista de subcategorias com
os parâmetros usados pelos algoritmos de redimensionamento (ver embalagem.py).

As estratégias disponíveis são:

    "dobravel"        Itens têxteis que são dobrados e comprimidos.
                      Parâmetros: div_c, div_l, comp.
    "calcado"         Pares de calçado acomodados lado a lado.
                      Parâmetros: fator_l, folga_c, folga_a.
    "multiplicativo"  Eletrônicos: folga proporcional ao tamanho do produto.
                      Parâmetros: fc, fl, fa.
    "aditivo"         Demais itens rígidos: folga fixa em centímetros por eixo.
                      Parâmetros: folga_c, folga_l, folga_a.
"""


# ---------------------------------------------------------------------------
# Estratégia "dobravel" — div_c/div_l dobram comprimento e largura e definem
# o número de camadas empilhadas (div_c × div_l). comp é a densidade de
# compactação: a fração do volume solto que sobra depois de compactar a peça.
# Itens fofos (edredom, almofada) compactam muito (comp baixo); tecidos finos
# (lençol, toalha) compactam pouco. Subcategoria sem divisores (ex.: almofada)
# é apenas comprimida de forma isotrópica, sem dobrar.
# ---------------------------------------------------------------------------
VESTUARIO = [
    {"id": 1, "nome": "Roupa Leve",          "exemplos": "Camiseta, calça",  "div_c": 2, "div_l": 2, "comp": 0.55},
    {"id": 2, "nome": "Roupa Grossa",        "exemplos": "Moletom, jaqueta", "div_c": 3, "div_l": 2, "comp": 0.50},
    {"id": 3, "nome": "Roupa Íntima & Meia", "exemplos": "Sutiã, meia",      "div_c": 4, "div_l": 2, "comp": 0.45},
]

CASA_E_BANHO = [
    {"id": 1, "nome": "Lençol/Fronha",    "exemplos": "Casal, solteiro",     "div_c": 6, "div_l": 4, "comp": 0.22},
    {"id": 2, "nome": "Cobertor/Edredom", "exemplos": "King, casal",         "div_c": 7, "div_l": 4, "comp": 0.13},
    {"id": 3, "nome": "Almofada",         "exemplos": "Travesseiro, pelúcia", "div_c": None, "div_l": None, "comp": 0.43},
    {"id": 4, "nome": "Toalha",           "exemplos": "Banho, rosto",        "div_c": 5, "div_l": 3, "comp": 0.40},
]

# ---------------------------------------------------------------------------
# Estratégia "calcado" — fator_l acomoda o par lado a lado na largura;
# folga_c e folga_a somam a folga de comprimento e altura (cano + proteção).
# ---------------------------------------------------------------------------
CALCADOS = [
    {"id": 1, "nome": "Chinelo/Sandália",                       "exemplos": "Havaiana, rasteirinha", "fator_l": 1.8, "folga_c": 2, "folga_a": 2},
    {"id": 2, "nome": "Tênis cano baixo/Sapatilha/Sapato",      "exemplos": "Scarpin, All Star",     "fator_l": 2.0, "folga_c": 2, "folga_a": 2},
    {"id": 3, "nome": "Tênis cano médio/Bota cano médio",       "exemplos": "Coturno, Air Jordan",   "fator_l": 2.1, "folga_c": 2, "folga_a": 3},
    {"id": 4, "nome": "Tênis cano alto/Bota cano alto",         "exemplos": "Montaria",              "fator_l": 2.2, "folga_c": 2, "folga_a": 4},
]

# ---------------------------------------------------------------------------
# Estratégia "multiplicativo" — folga proporcional: cada eixo do produto é
# multiplicado pelo seu fator (fc/fl/fa) para reservar espaço de proteção.
# ---------------------------------------------------------------------------
ELETRONICOS = [
    {"id": 1,  "nome": "Smartphone",      "exemplos": "iPhone, Galaxy",   "fc": 1.10, "fl": 1.15, "fa": 4.00},
    {"id": 2,  "nome": "Tablet",          "exemplos": "iPad, Galaxy Tab", "fc": 1.08, "fl": 1.10, "fa": 2.50},
    {"id": 3,  "nome": "Notebook",        "exemplos": "MacBook, Dell",    "fc": 1.07, "fl": 1.07, "fa": 1.80},
    {"id": 4,  "nome": "Fone de ouvido",  "exemplos": "AirPods, JBL",     "fc": 1.30, "fl": 1.30, "fa": 1.50},
    {"id": 5,  "nome": "Headphone",       "exemplos": "Sony WH, Bose",    "fc": 1.20, "fl": 1.20, "fa": 1.30},
    {"id": 6,  "nome": "Carregador/Cabo", "exemplos": "USB-C, tomada",    "fc": 1.40, "fl": 1.40, "fa": 1.50},
    {"id": 7,  "nome": "Smartwatch",      "exemplos": "Apple Watch",      "fc": 1.20, "fl": 1.20, "fa": 2.50},
    {"id": 8,  "nome": "Console",         "exemplos": "PS5, Xbox",        "fc": 1.12, "fl": 1.12, "fa": 1.25},
    {"id": 9,  "nome": "Câmera",          "exemplos": "DSLR, GoPro",      "fc": 1.15, "fl": 1.15, "fa": 1.50},
    {"id": 10, "nome": "Monitor",         "exemplos": '24", 27"',         "fc": 1.15, "fl": 1.15, "fa": 1.40},
]

# ---------------------------------------------------------------------------
# Estratégia "aditivo" — folga fixa em cm somada a cada eixo (folga_c/l/a).
# ---------------------------------------------------------------------------
ELETRODOMESTICOS = [
    {"id": 1, "nome": "Pequeno Porte", "exemplos": "Liquidificador, torradeira, ferro",  "folga_c": 3, "folga_l": 3, "folga_a": 3},
    {"id": 2, "nome": "Médio Porte",   "exemplos": "Airfryer, cafeteira, batedeira",     "folga_c": 4, "folga_l": 4, "folga_a": 3},
    {"id": 3, "nome": "Grande Porte",  "exemplos": "Micro-ondas, aspirador, purificador", "folga_c": 5, "folga_l": 5, "folga_a": 4},
    {"id": 4, "nome": "Linha Branca",  "exemplos": "Geladeira, fogão",                   "folga_c": 8, "folga_l": 8, "folga_a": 10},
]

LIVROS_E_MIDIAS = [
    {"id": 1, "nome": "Livro Único",          "exemplos": "O Pequeno Príncipe, Vidas Secas", "folga_c": 1,   "folga_l": 1,   "folga_a": 1},
    {"id": 2, "nome": "Revistas e Catálogos", "exemplos": "Mangás, Revista Veja",            "folga_c": 1,   "folga_l": 1,   "folga_a": 0.5},
    {"id": 3, "nome": "DVD/Blu-ray",          "exemplos": "Álbum, coletânea",                "folga_c": 0.5, "folga_l": 0.5, "folga_a": 0.5},
    {"id": 4, "nome": "Jogo de Vídeo-game",   "exemplos": "Mario Kart, Sonic",               "folga_c": 0.5, "folga_l": 0.5, "folga_a": 0.5},
    {"id": 5, "nome": "Box de Livros",        "exemplos": "Box Harry Potter, Jogos Vorazes", "folga_c": 2,   "folga_l": 2,   "folga_a": 2},
]

JOGOS_E_BRINQUEDOS = [
    {"id": 1, "nome": "Jogo de Tabuleiro", "exemplos": "Monopoly, Banco Imobiliário",    "folga_c": 1.5, "folga_l": 1.5, "folga_a": 1.5},
    {"id": 2, "nome": "Card Game",         "exemplos": "Coup, Uno",                      "folga_c": 0.5, "folga_l": 0.5, "folga_a": 0.5},
    {"id": 3, "nome": "Brinquedo Rígido",  "exemplos": "Barbie, carrinho Hot Wheels",    "folga_c": 3,   "folga_l": 3,   "folga_a": 3},
    {"id": 4, "nome": "Pelúcia",           "exemplos": "Sansão - Turma da Mônica",       "folga_c": 2,   "folga_l": 2,   "folga_a": 2},
]

MOVEIS = [
    {"id": 1, "nome": "Estante/Prateleira",   "exemplos": "Estante de livros, prateleira",   "folga_c": 6, "folga_l": 6, "folga_a": 4},
    {"id": 2, "nome": "Cadeira Desmontada",   "exemplos": "Cadeira de escritório, banqueta", "folga_c": 4, "folga_l": 4, "folga_a": 4},
    {"id": 3, "nome": "Mesa Flatpack",        "exemplos": "Mesa de jantar, escrivaninha",    "folga_c": 5, "folga_l": 5, "folga_a": 3},
    {"id": 4, "nome": "Armário/Guarda-roupa", "exemplos": "Guarda-roupa, armário de cozinha", "folga_c": 6, "folga_l": 6, "folga_a": 5},
    {"id": 5, "nome": "Organizador/Sapateira", "exemplos": "Sapateira, organizador",         "folga_c": 4, "folga_l": 4, "folga_a": 4},
]

ALIMENTOS_E_BEBIDAS = [
    {"id": 1, "nome": "Garrafa/Líquido",   "exemplos": "Vinho, refrigerante, azeite", "folga_c": 4,   "folga_l": 4,   "folga_a": 4},
    {"id": 2, "nome": "Embalagem Seca",    "exemplos": "Arroz, biscoito, café",       "folga_c": 2,   "folga_l": 2,   "folga_a": 2},
    {"id": 3, "nome": "Enlatado/Conserva", "exemplos": "Atum, milho, sardinha",       "folga_c": 1.5, "folga_l": 1.5, "folga_a": 1.5},
    {"id": 4, "nome": "Kit/Cesta",         "exemplos": "Cesta de café, kit gourmet",  "folga_c": 4,   "folga_l": 4,   "folga_a": 4},
]

COSMETICOS = [
    {"id": 1, "nome": "Frasco/Tubo",          "exemplos": "Shampoo, hidratante",        "folga_c": 2,   "folga_l": 2,   "folga_a": 2},
    {"id": 2, "nome": "Perfume/Caixa Rígida", "exemplos": "Perfume, kit cosmético",     "folga_c": 3,   "folga_l": 3,   "folga_a": 3},
    {"id": 3, "nome": "Kit/Conjunto",         "exemplos": "Kit presente, skincare",     "folga_c": 3,   "folga_l": 3,   "folga_a": 3},
    {"id": 4, "nome": "Maquiagem Item Único", "exemplos": "Batom, paleta, esmalte",     "folga_c": 1.5, "folga_l": 1.5, "folga_a": 1.5},
]

FERRAMENTAS = [
    {"id": 1, "nome": "Ferramenta Manual Pequena", "exemplos": "Martelo, chave de fenda",  "folga_c": 4, "folga_l": 4, "folga_a": 4},
    {"id": 2, "nome": "Ferramenta Elétrica",       "exemplos": "Furadeira, parafusadeira", "folga_c": 5, "folga_l": 5, "folga_a": 4},
    {"id": 3, "nome": "Ferramenta Longa",          "exemplos": "Serrote, pé de cabra",     "folga_c": 5, "folga_l": 4, "folga_a": 4},
    {"id": 4, "nome": "Hardware a Granel",         "exemplos": "Parafusos, pregos (caixa)", "folga_c": 3, "folga_l": 3, "folga_a": 3},
]

PAPELARIA = [
    {"id": 1, "nome": "Caneta/Lápis/Marcador",  "exemplos": "Caneta, marcador, lápis",   "folga_c": 1.5, "folga_l": 1.5, "folga_a": 1.5},
    {"id": 2, "nome": "Caderno/Bloco/Agenda",   "exemplos": "Caderno, agenda, bloco",    "folga_c": 1.5, "folga_l": 1.5, "folga_a": 1.5},
    {"id": 3, "nome": "Pasta/Arquivo",          "exemplos": "Pasta sanfonada, fichário", "folga_c": 2,   "folga_l": 2,   "folga_a": 1.5},
    {"id": 4, "nome": "Cartucho/Toner",         "exemplos": "Cartucho HP, toner Epson",  "folga_c": 3,   "folga_l": 3,   "folga_a": 3},
    {"id": 5, "nome": "Kit Escolar/Escritório", "exemplos": "Estojo, kit volta às aulas", "folga_c": 2,   "folga_l": 2,   "folga_a": 2},
]

ESPORTIVOS = [
    {"id": 1, "nome": "Bola",                    "exemplos": "Futebol, basquete, vôlei",   "folga_c": 2, "folga_l": 2, "folga_a": 2},
    {"id": 2, "nome": "Raquete/Taco",            "exemplos": "Raquete de tênis, taco",     "folga_c": 5, "folga_l": 3, "folga_a": 3},
    {"id": 3, "nome": "Equipamento de Academia", "exemplos": "Halter, kettlebell, colchonete", "folga_c": 8, "folga_l": 8, "folga_a": 8},
    {"id": 4, "nome": "Acessório Esportivo",     "exemplos": "Luva, garrafa, faixa",       "folga_c": 2, "folga_l": 2, "folga_a": 2},
]


# ---------------------------------------------------------------------------
# Catálogo: ordem de exibição preservada. Cada categoria aponta para a sua
# estratégia de embalagem e para a sua lista de subcategorias.
# ---------------------------------------------------------------------------
CATEGORIAS = [
    {"nome": "Vestuário & Têxteis",   "estrategia": "dobravel",       "subcategorias": VESTUARIO},
    {"nome": "Casa & Banho",          "estrategia": "dobravel",       "subcategorias": CASA_E_BANHO},
    {"nome": "Calçados",              "estrategia": "calcado",        "subcategorias": CALCADOS},
    {"nome": "Eletrônicos",           "estrategia": "multiplicativo", "subcategorias": ELETRONICOS},
    {"nome": "Eletrodomésticos",      "estrategia": "aditivo",        "subcategorias": ELETRODOMESTICOS},
    {"nome": "Livros & Mídias",       "estrategia": "aditivo",        "subcategorias": LIVROS_E_MIDIAS},
    {"nome": "Jogos & Brinquedos",    "estrategia": "aditivo",        "subcategorias": JOGOS_E_BRINQUEDOS},
    {"nome": "Móveis",                "estrategia": "aditivo",        "subcategorias": MOVEIS},
    {"nome": "Alimentos & Bebidas",   "estrategia": "aditivo",        "subcategorias": ALIMENTOS_E_BEBIDAS},
    {"nome": "Cosméticos & Higiene",  "estrategia": "aditivo",        "subcategorias": COSMETICOS},
    {"nome": "Ferramentas",           "estrategia": "aditivo",        "subcategorias": FERRAMENTAS},
    {"nome": "Papelaria",             "estrategia": "aditivo",        "subcategorias": PAPELARIA},
    {"nome": "Esportivos",            "estrategia": "aditivo",        "subcategorias": ESPORTIVOS},
]
