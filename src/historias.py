"""Carregamento e sorteio de motivações para o personagem."""

from __future__ import annotations

import json
import random
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from src.entidades import Motivacao
from src.erros import ErroDadosError

_CAMINHO = Path(__file__).parent / "data" / "historias_personagem.json"


@dataclass(frozen=True)
class HistoriaBruta:
    """Entrada bruta de motivação carregada do JSON."""

    id: str
    titulo: str
    descricao: str
    classes: tuple[str, ...]
    tom: str | None = None


_CACHE: list[HistoriaBruta] | None = None


def carregar_historias() -> list[HistoriaBruta]:
    """Carrega o arquivo JSON de histórias, com cache."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    try:
        dados = json.loads(_CAMINHO.read_text(encoding="utf-8"))
    except FileNotFoundError as erro:
        raise ErroDadosError(
            "Arquivo 'historias_personagem.json' não encontrado em src/data/."
        ) from erro
    except json.JSONDecodeError as erro:
        raise ErroDadosError(
            "Arquivo 'historias_personagem.json' inválido (JSON malformado)."
        ) from erro
    if not isinstance(dados, list) or not dados:
        raise ErroDadosError(
            "Arquivo 'historias_personagem.json' deve ser uma lista com entradas válidas."
        )
    historias: list[HistoriaBruta] = []
    for item in dados:
        if not isinstance(item, dict) or "id" not in item or "descricao" not in item:
            raise ErroDadosError("Entrada inválida em 'historias_personagem.json'.")
        classes_raw = item.get("classes", [])
        if classes_raw is None:
            classes_raw = []
        if not isinstance(classes_raw, Iterable):
            classes_raw = []
        classes_tuple = tuple(str(c).lower() for c in classes_raw)
        historias.append(
            HistoriaBruta(
                id=str(item["id"]),
                titulo=str(item.get("titulo", item["id"].title())),
                descricao=str(item.get("descricao", "")),
                classes=classes_tuple,
                tom=str(item.get("tom")) if item.get("tom") is not None else None,
            )
        )
    _CACHE = historias
    return historias


def sortear_motivacao(classe: str) -> Motivacao:
    """Sorteia uma motivação apropriada para a classe (ou genérica se não houver)."""
    classe = classe.lower()
    historias = carregar_historias()
    elegiveis = [h for h in historias if not h.classes or classe in h.classes]
    if not elegiveis:
        elegiveis = historias
    escolhida = random.choice(elegiveis)
    return Motivacao(id=escolhida.id, titulo=escolhida.titulo, descricao=escolhida.descricao)
