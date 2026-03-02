"""Carrega dados de chefes e sorteia o mais apropriado para o andar."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from src.catalogos import carregar_json_catalogo
from src.erros import ErroDadosError


@dataclass
class ChefeConfig:
    """Configuração básica para selecionar chefes por andar."""

    id: str
    tipo: str
    descricao: str
    titulo: str
    historia: str
    andar_min: int
    andar_max: int
    nome: str
    historias_por_classe: dict[str, dict[str, str]] = field(default_factory=dict)


_CACHE: list[ChefeConfig] | None = None


def _normalizar_nome(identificador: str) -> str:
    """Gera um nome apresentável a partir de um identificador."""
    return identificador.replace("_", " ").title()


def carregar_chefes() -> list[ChefeConfig]:
    """Lê o JSON de chefes com cache em memória."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    dados = carregar_json_catalogo("chefes.json", tipo_esperado=list)
    chefes: list[ChefeConfig] = []
    for item in dados:
        if not all(chave in item for chave in ("id", "tipo", "andar_min", "andar_max")):
            raise ErroDadosError("Entrada de chefe incompleta em 'chefes.json'.")
        historias_cls = item.get("historias_por_classe") or {}
        if not isinstance(historias_cls, dict):
            historias_cls = {}
        chefes.append(
            ChefeConfig(
                id=item["id"],
                tipo=item["tipo"],
                descricao=item.get("descricao", ""),
                titulo=item.get("titulo", item.get("nome", item["id"].title())),
                historia=item.get("historia", ""),
                andar_min=int(item["andar_min"]),
                andar_max=int(item["andar_max"]),
                nome=item.get("nome") or _normalizar_nome(item["id"]),
                historias_por_classe={str(k).lower(): v for k, v in historias_cls.items()},
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


def sortear_chefe_para_andar(andar: int, rng: random.Random | None = None) -> ChefeConfig | None:
    """Retorna um chefe apropriado para o andar informado."""
    rng = rng or random
    chefes = [c for c in carregar_chefes() if c.andar_min <= andar <= c.andar_max]
    if not chefes:
        return None
    return rng.choice(chefes)
