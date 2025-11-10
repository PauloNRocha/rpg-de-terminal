"""Configurações centrais do jogo."""

MAP_WIDTH = 10
MAP_HEIGHT = 10
MAP_SIDE_ROOMS_RATIO = 0.25
MAP_ENEMY_PROBABILITY = 0.6

LEVEL_UP_HP_GAIN = 10
LEVEL_UP_ATTACK_GAIN = 2
LEVEL_UP_DEFENSE_GAIN = 1
DESCENT_HEAL_PERCENT = 0.25

# Probabilidade de substituir o drop normal por um consumível por raridade
DROP_CONSUMIVEL_CHANCE = {
    "comum": 0.35,
    "incomum": 0.25,
    "raro": 0.15,
}
