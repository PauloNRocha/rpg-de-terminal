"""Utilitários para seed por run e serialização segura do estado do RNG."""

from __future__ import annotations

import random

_SEED_MAX = 2**63 - 1
type EstadoRNG = int | float | str | bool | None | list["EstadoRNG"]


def gerar_seed() -> int:
    """Gera uma seed de run usando uma fonte não determinística do sistema."""
    return random.SystemRandom().randrange(1, _SEED_MAX)


def criar_rng(seed: int | None = None) -> tuple[int, random.Random]:
    """Cria um RNG isolado para a run a partir da seed informada ou gerada."""
    seed_normalizada = _normalizar_seed(seed)
    return seed_normalizada, random.Random(seed_normalizada)


def restaurar_rng(
    seed: int | None = None,
    estado_serializado: list[EstadoRNG] | None = None,
) -> tuple[int, random.Random]:
    """Restaura um RNG a partir da seed e, se existir, do estado serializado."""
    seed_normalizada, rng = criar_rng(seed)
    if estado_serializado is not None:
        rng.setstate(_lista_para_tupla(estado_serializado))
    return seed_normalizada, rng


def serializar_estado_rng(rng: random.Random) -> list[EstadoRNG]:
    """Serializa o estado do RNG para estruturas compatíveis com JSON."""
    return _tupla_para_lista(rng.getstate())


def _normalizar_seed(seed: int | None) -> int:
    """Normaliza a seed para um inteiro positivo e estável."""
    if seed is None:
        return gerar_seed()
    try:
        seed_int = int(seed)
    except (TypeError, ValueError):
        return gerar_seed()
    if seed_int < 1:
        return gerar_seed()
    return seed_int


def _tupla_para_lista(valor: object) -> EstadoRNG:
    """Converta recursivamente tuplas em listas para serialização JSON."""
    if isinstance(valor, tuple):
        return [_tupla_para_lista(item) for item in valor]
    if isinstance(valor, list):
        return [_tupla_para_lista(item) for item in valor]
    return valor  # type: ignore[return-value]


def _lista_para_tupla(valor: object) -> object:
    """Restaure recursivamente listas serializadas para tuplas do estado RNG."""
    if isinstance(valor, list):
        return tuple(_lista_para_tupla(item) for item in valor)
    return valor
