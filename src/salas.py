"""Catálogo data-driven de salas."""

from __future__ import annotations

import json
import random
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from src import config
from src.erros import ErroDadosError

_CAMINHO_SALAS = Path(__file__).parent / "data" / "salas.json"


@dataclass(frozen=True)
class SalaTemplate:
    """Representa o texto base de uma sala."""

    nome: str
    descricao: str
    tags: tuple[str, ...] = ()


_CATALOGO: dict[str, list[SalaTemplate]] | None = None


def carregar_salas() -> dict[str, list[SalaTemplate]]:
    """Carrega e valida o arquivo JSON contendo as salas."""
    global _CATALOGO
    if _CATALOGO is not None:
        return _CATALOGO
    try:
        dados = json.loads(_CAMINHO_SALAS.read_text(encoding="utf-8"))
    except FileNotFoundError as erro:
        raise ErroDadosError("Arquivo 'salas.json' não encontrado em src/data/.") from erro
    except json.JSONDecodeError as erro:
        raise ErroDadosError("Arquivo 'salas.json' inválido (JSON malformado).") from erro
    if not isinstance(dados, dict) or not dados:
        raise ErroDadosError("Arquivo 'salas.json' deve ser um objeto com listas de salas.")
    catalogo: dict[str, list[SalaTemplate]] = {}
    for categoria, lista in dados.items():
        if not isinstance(lista, list) or not lista:
            raise ErroDadosError(f"Categoria de salas '{categoria}' está vazia ou inválida.")
        templates: list[SalaTemplate] = []
        for item in lista:
            if not isinstance(item, dict):
                raise ErroDadosError(f"Entrada inválida na categoria '{categoria}'.")
            nome = item.get("nome")
            descricao = item.get("descricao")
            if not isinstance(nome, str) or not isinstance(descricao, str):
                raise ErroDadosError(
                    f"Sala da categoria '{categoria}' está sem 'nome' ou 'descricao' válidos."
                )
            tags_raw = item.get("tags", [])
            if not isinstance(tags_raw, list):
                tags_raw = []
            tags = tuple(_normalizar_tag(str(tag)) for tag in tags_raw if str(tag).strip())
            templates.append(SalaTemplate(nome=nome, descricao=descricao, tags=tags))
        catalogo[categoria] = templates
    _CATALOGO = catalogo
    return catalogo


def sortear_sala_template(
    categoria: str,
    usadas_por_categoria: dict[str, set[str]],
    tema: str | None = None,
) -> SalaTemplate:
    """Retorna um template de sala evitando repetição até que a lista se esgote."""
    catalogo = carregar_salas()
    if categoria not in catalogo:
        categoria = "caminho"
    candidatos = catalogo.get(categoria, [])
    if not candidatos:
        raise ErroDadosError(f"Categoria de sala '{categoria}' não possui entradas disponíveis.")
    usadas = usadas_por_categoria.setdefault(categoria, set())
    pool = [template for template in candidatos if template.nome not in usadas]
    if not pool:
        usadas.clear()
        pool = candidatos
    escolhido = _sortear_template_ponderado(pool, tema)
    usadas.add(escolhido.nome)
    return escolhido


def _sortear_template_ponderado(templates: list[SalaTemplate], tema: str | None) -> SalaTemplate:
    """Sorteia um template com peso maior para tags alinhadas ao tema da trama."""
    if not tema:
        return random.choice(templates)
    tema_norm = _normalizar_tag(tema)
    pesos = [
        config.TEMA_PESO_SALA_COMPATIVEL if tema_norm in template.tags else 1.0
        for template in templates
    ]
    if all(peso == 1.0 for peso in pesos):
        return random.choice(templates)
    return random.choices(templates, weights=pesos, k=1)[0]


def _normalizar_tag(tag: str) -> str:
    """Normaliza tags removendo acentos e padronizando caixa."""
    texto = unicodedata.normalize("NFKD", tag.strip().lower())
    return "".join(ch for ch in texto if not unicodedata.combining(ch))
