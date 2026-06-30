"""
Banco de dados local de dimensões de produtos (SQLite).

Registra cada consulta bem-sucedida e permite buscas futuras por
similaridade textual. O banco é fonte da verdade: se um produto existe,
suas dimensões são retornadas diretamente sem consultar a LLM.

Nenhuma dependência externa: usa apenas sqlite3 e difflib (stdlib).
"""

import sqlite3
import unicodedata
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

_CAMINHO_BANCO = Path(__file__).parent / "dimensoes.db"
_SIMILARIDADE_MINIMA = 0.55


# ---------------------------------------------------------------------------
# Conexão e criação da tabela
# ---------------------------------------------------------------------------
def _conectar():
    """Abre (ou cria) o banco e garante que a tabela existe."""
    conexao = sqlite3.connect(_CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA journal_mode=WAL")
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS dimensoes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_produto    TEXT    NOT NULL,
            nome_normalizado TEXT   NOT NULL,
            categoria       TEXT    NOT NULL,
            subcategoria    TEXT    NOT NULL,
            comprimento     REAL    NOT NULL,
            largura         REAL    NOT NULL,
            altura          REAL    NOT NULL,
            peso            REAL,
            confianca       INTEGER,
            fonte           TEXT,
            observacao       TEXT,
            criado_em       TEXT    NOT NULL
        )
    """)
    conexao.execute("""
        CREATE INDEX IF NOT EXISTS idx_categoria
        ON dimensoes (categoria, subcategoria)
    """)
    conexao.commit()
    return conexao


# ---------------------------------------------------------------------------
# Normalização de texto
# ---------------------------------------------------------------------------
def _normalizar(texto):
    """Minúsculas, sem acentos, sem espaços extras."""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return " ".join(texto.split())


def _similaridade(a, b):
    return SequenceMatcher(None, a, b).ratio()


# ---------------------------------------------------------------------------
# Busca
# ---------------------------------------------------------------------------
def buscar(nome_produto, categoria, subcategoria):
    """
    Procura no banco um produto similar na mesma categoria.
    Retorna dict com dimensões ou None.
    """
    nome_norm = _normalizar(nome_produto)
    conexao = _conectar()
    cursor = conexao.execute(
        "SELECT * FROM dimensoes WHERE categoria = ?", (categoria,)
    )
    candidatos = cursor.fetchall()
    conexao.close()

    melhor, melhor_score = None, 0.0
    for reg in candidatos:
        score = _similaridade(nome_norm, reg["nome_normalizado"])
        if reg["subcategoria"] == subcategoria:
            score = min(score + 0.10, 1.0)
        if score > melhor_score:
            melhor_score = score
            melhor = reg

    if melhor is None or melhor_score < _SIMILARIDADE_MINIMA:
        return None

    return {
        "nome_encontrado": melhor["nome_produto"],
        "comprimento":     melhor["comprimento"],
        "largura":         melhor["largura"],
        "altura":          melhor["altura"],
        "peso":            melhor["peso"],
        "confianca":       melhor["confianca"],
        "fonte":           melhor["fonte"],
        "observacao":      melhor["observacao"],
        "similaridade":    round(melhor_score, 2),
    }


# ---------------------------------------------------------------------------
# Registro
# ---------------------------------------------------------------------------
def registrar(nome_produto, categoria, subcategoria, dimensoes):
    """
    Salva dimensões no banco. Se já existir registro com nome idêntico
    na mesma categoria, não faz nada (banco é fonte da verdade).
    Retorna True se inseriu, False se já existia.
    """
    nome_salvo = dimensoes.get("nome_encontrado", nome_produto)
    nome_norm = _normalizar(nome_salvo)
    conexao = _conectar()

    existente = conexao.execute(
        "SELECT id FROM dimensoes WHERE nome_normalizado = ? AND categoria = ?",
        (nome_norm, categoria),
    ).fetchone()

    if existente:
        conexao.close()
        return False

    conexao.execute("""
        INSERT INTO dimensoes
            (nome_produto, nome_normalizado, categoria, subcategoria,
             comprimento, largura, altura, peso, confianca, fonte,
             observacao, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nome_salvo,
        nome_norm, categoria, subcategoria,
        dimensoes["comprimento"], dimensoes["largura"],
        dimensoes["altura"], dimensoes.get("peso"),
        dimensoes.get("confianca"), dimensoes.get("fonte"),
        dimensoes.get("observacao"), datetime.now().isoformat(),
    ))
    conexao.commit()
    conexao.close()
    return True


# ---------------------------------------------------------------------------
# Gestão (CLI)
# ---------------------------------------------------------------------------
def total_registros():
    conexao = _conectar()
    total = conexao.execute("SELECT COUNT(*) FROM dimensoes").fetchone()[0]
    conexao.close()
    return total


def listar_todos():
    conexao = _conectar()
    cursor = conexao.execute(
        "SELECT * FROM dimensoes ORDER BY categoria, nome_produto"
    )
    registros = [dict(r) for r in cursor.fetchall()]
    conexao.close()
    return registros


def remover(nome_produto):
    """Remove registros cujo nome seja similar ou contenha o termo."""
    termo = _normalizar(nome_produto)
    conexao = _conectar()
    cursor = conexao.execute("SELECT id, nome_normalizado FROM dimensoes")
    ids_remover = [
        r["id"] for r in cursor.fetchall()
        if _similaridade(termo, r["nome_normalizado"]) >= 0.60
        or termo in r["nome_normalizado"]
        or r["nome_normalizado"] in termo
    ]
    if not ids_remover:
        conexao.close()
        return 0
    placeholders = ",".join("?" * len(ids_remover))
    conexao.execute(
        f"DELETE FROM dimensoes WHERE id IN ({placeholders})", ids_remover
    )
    conexao.commit()
    conexao.close()
    return len(ids_remover)


def adicionar_manual(nome_produto, categoria, subcategoria,
                     comprimento, largura, altura, peso):
    """Insere um registro manual."""
    dimensoes = {
        "nome_encontrado": nome_produto,
        "comprimento": comprimento,
        "largura": largura,
        "altura": altura,
        "peso": peso,
        "confianca": 100,
        "fonte": "Entrada manual",
        "observacao": None,
    }
    return registrar(nome_produto, categoria, subcategoria, dimensoes)
