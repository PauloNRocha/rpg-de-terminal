"""Configurações centrais do jogo."""

from dataclasses import dataclass

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

# Faixas de moedas saqueadas por raridade (mínimo, máximo)
COIN_DROP_FAIXAS = {
    "comum": (5, 15),
    "incomum": (15, 35),
    "raro": (40, 80),
    "default": (5, 10),
}

COIN_DROP_ESCALONAMENTO = 0.1  # 10% extra por nível acima do primeiro

EVENTO_PROBABILIDADE = 0.2


@dataclass(frozen=True)
class DificuldadePerfil:
    """Define multiplicadores aplicados por modo de dificuldade."""

    chave: str
    nome: str
    descricao: str
    inimigo_hp_mult: float = 1.0
    inimigo_ataque_mult: float = 1.0
    inimigo_defesa_mult: float = 1.0
    xp_recompensa_mult: float = 1.0
    saque_moedas_mult: float = 1.0
    prob_inimigo_mult: float = 1.0
    drop_consumivel_bonus: float = 0.0


DIFICULDADES: dict[str, DificuldadePerfil] = {
    "facil": DificuldadePerfil(
        chave="facil",
        nome="Explorador (Fácil)",
        descricao="Para quem quer conhecer a história e explorar sem tanto risco.",
        inimigo_hp_mult=0.85,
        inimigo_ataque_mult=0.9,
        inimigo_defesa_mult=0.9,
        xp_recompensa_mult=1.15,
        saque_moedas_mult=1.2,
        prob_inimigo_mult=0.8,
        drop_consumivel_bonus=0.15,
    ),
    "normal": DificuldadePerfil(
        chave="normal",
        nome="Aventureiro (Normal)",
        descricao="Experiência equilibrada padrão: inimigos e loot neutros.",
    ),
    "dificil": DificuldadePerfil(
        chave="dificil",
        nome="Pesadelo (Difícil)",
        descricao="Desafio máximo: inimigos mais fortes e encontros frequentes.",
        inimigo_hp_mult=1.25,
        inimigo_ataque_mult=1.2,
        inimigo_defesa_mult=1.15,
        xp_recompensa_mult=0.9,
        saque_moedas_mult=0.85,
        prob_inimigo_mult=1.25,
        drop_consumivel_bonus=-0.05,
    ),
}

DIFICULDADE_ORDEM: tuple[str, ...] = ("facil", "normal", "dificil")
DIFICULDADE_PADRAO = "normal"
