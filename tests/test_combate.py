import random

import pytest

from src import combate
from src.combate import calcular_dano


def test_calcular_dano() -> None:
    """Testa a função calcular_dano para garantir que o dano é calculado corretamente."""
    # Garante que o dano não seja negativo, mas mantém piso 1 para ataques positivos
    assert calcular_dano(5, 10) == 1
    assert calcular_dano(0, 0) == 0

    # Testa um cenário básico de dano
    # Como há aleatoriedade, testamos um range esperado
    random.seed(42)  # Fixa a semente para resultados reproduzíveis
    dano = calcular_dano(10, 2)
    # Dano base: 8. Variação de 0.8 a 1.2 => (10*0.8 - 2) a (10*1.2 - 2) => 6 a 10
    assert 6 <= dano <= 10

    random.seed(100)  # Outra semente
    dano = calcular_dano(15, 5)
    # Dano base: 10. Variação de 0.8 a 1.2 => (15*0.8 - 5) a (15*1.2 - 5) => 7 a 13
    assert 7 <= dano <= 13
    # Testa caso de ataque muito alto vs defesa baixa
    random.seed(1)  # Outra semente
    dano = calcular_dano(100, 1)  # Dano base esperado: 99
    # Dano base: 99. Variação de 0.8 a 1.2 => (100*0.8 - 1) a (100*1.2 - 1) => 79 a 119
    assert 79 <= dano <= 119


def test_calcular_dano_com_detalhes_exibe_breakdown(monkeypatch: pytest.MonkeyPatch) -> None:
    """Breakdown deve mostrar fórmula com ataque, defesa e resultado."""
    monkeypatch.setattr(combate.random, "uniform", lambda *_: 1.0)
    dano, detalhe = combate._calcular_dano_com_detalhes(10, 3)
    assert dano == 7
    assert "ATK 10" in detalhe
    assert "DEF 3" in detalhe
    assert "-> 7" in detalhe


def test_calcular_dano_com_detalhes_aplica_piso_minimo(monkeypatch: pytest.MonkeyPatch) -> None:
    """Quando ataque positivo não supera defesa, o piso de 1 deve ser aplicado."""
    monkeypatch.setattr(combate.random, "uniform", lambda *_: 1.0)
    dano, detalhe = combate._calcular_dano_com_detalhes(1, 10)
    assert dano == 1
    assert "piso mínimo" in detalhe
