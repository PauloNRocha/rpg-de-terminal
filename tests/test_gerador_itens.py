from __future__ import annotations

import pytest

from src import gerador_itens


def test_gerar_item_consumivel_quando_chance(monkeypatch: pytest.MonkeyPatch) -> None:
    """Força a escolha de consumíveis quando a chance configurada é 100%."""
    monkeypatch.setitem(gerador_itens.config.DROP_CONSUMIVEL_CHANCE, "comum", 1.0)
    monkeypatch.setattr(gerador_itens.random, "random", lambda: 0.0)
    item = gerador_itens.gerar_item_aleatorio("comum")
    assert item is not None
    assert item.tipo == "consumivel"


def test_gerar_item_equipo_quando_sem_consumivel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Se a chance for zero, mantém o comportamento original (equipamento)."""
    monkeypatch.setitem(gerador_itens.config.DROP_CONSUMIVEL_CHANCE, "comum", 0.0)
    item = gerador_itens.gerar_item_aleatorio("comum")
    assert item is not None
    assert item.tipo != "consumivel"


def test_bonus_consumivel_incrementa_chance(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bônus positivo força a troca para consumíveis mesmo com chance base zero."""
    monkeypatch.setitem(gerador_itens.config.DROP_CONSUMIVEL_CHANCE, "comum", 0.0)
    monkeypatch.setattr(gerador_itens.random, "random", lambda: 0.0)
    item = gerador_itens.gerar_item_aleatorio("comum", bonus_consumivel=0.5)
    assert item is not None
    assert item.tipo == "consumivel"


def test_obter_item_por_nome_encontra_independente_de_maisculas() -> None:
    """Busca por nome deve ignorar caixa e espaços extras."""
    item = gerador_itens.obter_item_por_nome("  lâmina fantasmal ")
    assert item is not None
    assert item.nome == "Lâmina Fantasmal"


def test_obter_item_por_nome_inexistente() -> None:
    """Quando não encontra, retorna None."""
    assert gerador_itens.obter_item_por_nome("Item Inventado") is None
