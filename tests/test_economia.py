from __future__ import annotations

import pytest

from src import config, economia


def test_calcular_moedas_saque_respeita_faixa(monkeypatch: pytest.MonkeyPatch) -> None:
    """Saque varia conforme a faixa da raridade e escala com o nível."""
    monkeypatch.setattr(economia.random, "randint", lambda a, b: b)
    valor = economia.calcular_moedas_saque("comum", nivel_masmorra=3)
    base = config.COIN_DROP_FAIXAS["comum"][1]
    bonus = int(base * config.COIN_DROP_ESCALONAMENTO * 2)
    assert valor == base + bonus


def test_comprar_item() -> None:
    """Compra bem sucedida deduz moedas e adiciona o item."""
    from src.economia import Moeda, comprar_item

    class DummyItem:
        preco_bronze = 30

    class DummyPersonagem:
        def __init__(self) -> None:
            self.carteira = Moeda(50)
            self.inventario = []

    personagem = DummyPersonagem()
    item = DummyItem()
    assert comprar_item(personagem, item) is True
    assert personagem.carteira.valor_bronze == 20
    assert item in personagem.inventario

    item_caro = DummyItem()
    item_caro.preco_bronze = 100
    assert comprar_item(personagem, item_caro) is False
