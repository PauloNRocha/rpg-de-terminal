"""Carrega dados de chefes e sorteia o mais apropriado para o andar."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from src.erros import ErroDadosError

_CAMINHO_CHEFES = Path(__file__).parent / "data" / "chefes.json"


@dataclass
class ChefeConfig:
    """Configuração básica para selecionar chefes por andar."""

    id: str
    tipo: str
    descricao: str
    andar_min: int
    andar_max: int
    nome: str


_CACHE: list[ChefeConfig] | None = None


def _normalizar_nome(identificador: str) -> str:
    """Gera um nome apresentável a partir de um identificador."""
    return identificador.replace("_", " ").title()


def carregar_chefes() -> list[ChefeConfig]:
    """Lê o JSON de chefes com cache em memória."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    try:
        dados = json.loads(_CAMINHO_CHEFES.read_text(encoding="utf-8"))
    except FileNotFoundError as erro:
        raise ErroDadosError("Arquivo 'chefes.json' não encontrado em src/data/.") from erro
    except json.JSONDecodeError as erro:
        raise ErroDadosError("Arquivo 'chefes.json' inválido (JSON malformado).") from erro
    if not isinstance(dados, list):
        raise ErroDadosError("Arquivo 'chefes.json' deve ser uma lista.")
    chefes: list[ChefeConfig] = []
    for item in dados:
        if not all(chave in item for chave in ("id", "tipo", "andar_min", "andar_max")):
            raise ErroDadosError("Entrada de chefe incompleta em 'chefes.json'.")
        chefes.append(
            ChefeConfig(
                id=item["id"],
                tipo=item["tipo"],
                descricao=item.get("descricao", ""),
                andar_min=int(item["andar_min"]),
                andar_max=int(item["andar_max"]),
                nome=item.get("nome") or _normalizar_nome(item["id"]),
            )
        )
    _CACHE = chefes
    return chefes


def obter_chefe_por_id(chefe_id: str | None) -> ChefeConfig | None:
    """Retorna o chefe com o identificador informado, se existir."""
    if not chefe_id:
        return None
    for chefe in carregar_chefes():
        if chefe.id == chefe_id:
            return chefe
    return None


def sortear_chefe_para_andar(andar: int) -> ChefeConfig | None:
    """Retorna um chefe apropriado para o andar informado."""
    chefes = [c for c in carregar_chefes() if c.andar_min <= andar <= c.andar_max]
    if not chefes:
        return None
    return random.choice(chefes)
