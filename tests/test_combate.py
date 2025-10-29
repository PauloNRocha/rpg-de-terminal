import pytest
import random
from src.combate import calcular_dano

# Testa a função calcular_dano
def test_calcular_dano():
    # Garante que o dano não seja negativo
    assert calcular_dano(5, 10) == 0
    assert calcular_dano(0, 0) == 0

    # Testa um cenário básico de dano
    # Como há aleatoriedade, testamos um range esperado
    random.seed(42) # Fixa a semente para resultados reproduzíveis
    dano = calcular_dano(10, 2) # Dano base esperado: 8
    assert 7 <= dano <= 9 # Deve estar entre 7 e 9 (8 +/- 1)

    random.seed(100) # Outra semente
    dano = calcular_dano(15, 5) # Dano base esperado: 10
    assert 9 <= dano <= 11 # Deve estar entre 9 e 11 (10 +/- 1)

    # Testa caso de ataque muito alto vs defesa baixa
    random.seed(1) # Outra semente
    dano = calcular_dano(100, 1) # Dano base esperado: 99
    assert 98 <= dano <= 100 # Deve estar entre 98 e 100 (99 +/- 1)
