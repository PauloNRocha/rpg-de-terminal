"""Configurações centrais do jogo."""

from dataclasses import dataclass

MAP_WIDTH = 10
MAP_HEIGHT = 10
MAP_SIDE_ROOMS_RATIO = 0.25
MAP_ENEMY_PROBABILITY = 0.55
MAP_ENEMY_PROBABILITY_ESCALONAMENTO = 0.07
MAP_ENEMY_PROBABILITY_MIN = 0.35
MAP_ENEMY_PROBABILITY_MAX = 0.95

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

COIN_DROP_ESCALONAMENTO = 0.12  # 12% extra por nível acima do primeiro

EVENTO_PROBABILIDADE = 0.2
INIMIGO_ESCALONAMENTO_POR_NIVEL = 0.25
INIMIGO_VARIACAO_PERCENTUAL = 0.12
CHEFE_HP_EXTRA_MULT_BASE = 0.2
CHEFE_HP_EXTRA_MULT_STEP = 0.03
CHEFE_HP_EXTRA_MULT_MAX = 0.35
CHEFE_ATAQUE_EXTRA_MULT_BASE = 0.12
CHEFE_ATAQUE_EXTRA_MULT_STEP = 0.02
CHEFE_ATAQUE_EXTRA_MULT_MAX = 0.25
CHEFE_DEFESA_EXTRA_MULT_BASE = 0.12
CHEFE_DEFESA_EXTRA_MULT_STEP = 0.02
CHEFE_DEFESA_EXTRA_MULT_MAX = 0.25
CHEFE_XP_MULT_BASE = 1.7
CHEFE_XP_MULT_STEP = 0.1
CHEFE_XP_MULT_MAX = 2.2


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

# Número máximo de slots de save suportados (pode ser ajustado futuramente).
MAX_SAVE_SLOTS = 5

# Minimap e controles alternativos
MINIMAPA_ATIVO = True
MINIMAPA_TAMANHO = 7  # deve ser ímpar (7 => mostra 3 salas em cada direção)
TECLAS_ALTERNATIVAS = True  # WASD/HJKL para mover
UI_TELA_ALTERNATIVA = True  # Usa tela alternativa do terminal para evitar scroll poluído


def probabilidade_inimigo_por_nivel(nivel: int, perfil: DificuldadePerfil | None = None) -> float:
    """Escala a chance de salas terem inimigos conforme o andar/dificuldade."""
    base = MAP_ENEMY_PROBABILITY + max(0, nivel - 1) * MAP_ENEMY_PROBABILITY_ESCALONAMENTO
    base = max(MAP_ENEMY_PROBABILITY_MIN, min(MAP_ENEMY_PROBABILITY_MAX, base))
    if perfil is not None:
        base *= perfil.prob_inimigo_mult
    return max(0.0, min(1.0, base))


def fator_inimigo_por_nivel(nivel: int) -> float:
    """Retorna o multiplicador base aplicado aos inimigos por andar."""
    return 1 + max(0, nivel - 1) * INIMIGO_ESCALONAMENTO_POR_NIVEL


def _calcular_bonus_escalonado(base: float, passo: float, maximo: float, nivel: int) -> float:
    return min(maximo, base + max(0, nivel - 1) * passo)


def obter_bonus_chefe(nivel: int) -> tuple[float, float, float, float]:
    """Retorna multiplicadores adicionais para chefes conforme o andar."""
    hp_bonus = _calcular_bonus_escalonado(
        CHEFE_HP_EXTRA_MULT_BASE, CHEFE_HP_EXTRA_MULT_STEP, CHEFE_HP_EXTRA_MULT_MAX, nivel
    )
    ataque_bonus = _calcular_bonus_escalonado(
        CHEFE_ATAQUE_EXTRA_MULT_BASE,
        CHEFE_ATAQUE_EXTRA_MULT_STEP,
        CHEFE_ATAQUE_EXTRA_MULT_MAX,
        nivel,
    )
    defesa_bonus = _calcular_bonus_escalonado(
        CHEFE_DEFESA_EXTRA_MULT_BASE,
        CHEFE_DEFESA_EXTRA_MULT_STEP,
        CHEFE_DEFESA_EXTRA_MULT_MAX,
        nivel,
    )
    xp_mult = min(CHEFE_XP_MULT_MAX, CHEFE_XP_MULT_BASE + max(0, nivel - 1) * CHEFE_XP_MULT_STEP)
    return hp_bonus, ataque_bonus, defesa_bonus, xp_mult
