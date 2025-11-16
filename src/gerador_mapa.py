# src/gerador_mapa.py

import random

from src import config, eventos
from src.entidades import Sala

Mapa = list[list[Sala]]


def gerar_mapa(nivel: int = 1, perfil_dificuldade: config.DificuldadePerfil | None = None) -> Mapa:
    """Gera um novo mapa com um caminho principal garantido da entrada até a saída."""
    prob_inimigo = config.MAP_ENEMY_PROBABILITY
    if perfil_dificuldade is not None:
        prob_inimigo *= perfil_dificuldade.prob_inimigo_mult
    prob_inimigo = min(1.0, max(0.0, prob_inimigo))

    mapa: Mapa = [
        [
            Sala(
                tipo="parede",
                nome="Parede",
                descricao="Pedra maciça bloqueando a passagem.",
                pode_ter_inimigo=False,
                nivel_area=nivel,
            )
            for _ in range(config.MAP_WIDTH)
        ]
        for _ in range(config.MAP_HEIGHT)
    ]

    x, y = random.randint(1, config.MAP_WIDTH - 2), 0
    caminho_principal: list[tuple[int, int]] = []

    while y < config.MAP_HEIGHT - 1:
        mapa[y][x] = _criar_sala("caminho", nivel, prob_inimigo)
        caminho_principal.append((x, y))

        direcao = random.choice(["esquerda", "direita", "baixo", "baixo", "baixo"])
        if direcao == "esquerda" and x > 1:
            x -= 1
        elif direcao == "direita" and x < config.MAP_WIDTH - 2:
            x += 1
        else:
            y += 1

    entrada_x, entrada_y = caminho_principal[0]
    mapa[entrada_y][entrada_x] = _criar_sala("entrada", nivel)

    chefe_x, chefe_y = caminho_principal[-2]
    mapa[chefe_y][chefe_x] = _criar_sala("chefe", nivel)

    escada_x, escada_y = caminho_principal[-1]
    mapa[escada_y][escada_x] = _criar_sala("escada", nivel)

    for _ in range(int(config.MAP_WIDTH * config.MAP_HEIGHT * config.MAP_SIDE_ROOMS_RATIO)):
        px, py = random.choice(caminho_principal)
        direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(direcoes)

        for dx, dy in direcoes:
            nx, ny = px + dx, py + dy
            if (
                0 <= nx < config.MAP_WIDTH
                and 0 <= ny < config.MAP_HEIGHT
                and mapa[ny][nx].tipo == "parede"
            ):
                mapa[ny][nx] = _criar_sala("secundaria", nivel, prob_inimigo)
                break

    return mapa


def _criar_sala(tipo: str, nivel: int, prob_inimigo: float | None = None) -> Sala:
    """Cria diferentes tipos de sala de acordo com o contexto."""
    if tipo == "entrada":
        if nivel <= 1:
            return Sala(
                tipo="entrada",
                nome="Entrada da Masmorra",
                descricao=(
                    "A luz da entrada desaparece atrás de você. O ar é úmido e "
                    "cheira a poeira e morte."
                ),
                pode_ter_inimigo=False,
                nivel_area=nivel,
            )
        return Sala(
            tipo="entrada",
            nome=f"Escadaria do Andar {nivel}",
            descricao=(
                "Você deixa para trás o andar anterior descendo uma escadaria íngreme. "
                "O ar fica mais pesado e sons distantes ecoam pelas paredes encharcadas."
            ),
            pode_ter_inimigo=False,
            nivel_area=nivel,
        )
    if tipo == "chefe":
        return Sala(
            tipo="chefe",
            nome="Covil do Chefe",
            descricao=(
                "Uma aura de poder emana desta sala. Ossos espalhados pelo chão indicam "
                "que você não é o primeiro a chegar."
            ),
            pode_ter_inimigo=True,
            chefe=True,
            nivel_area=nivel,
        )
    if tipo == "escada":
        return Sala(
            tipo="escada",
            nome="Escadaria para as Profundezas",
            descricao=(
                "Uma escadaria de pedra desce para a escuridão. Você sente um ar ainda mais "
                "frio vindo de baixo."
            ),
            pode_ter_inimigo=False,
            nivel_area=nivel,
        )

    descricoes = [
        "Um corredor escuro e úmido. O som de gotas de água ecoa ao longe.",
        "Uma pequena câmara com teias de aranha cobrindo as paredes.",
        "Uma sala com entalhes estranhos nas paredes de pedra.",
        "Um túnel estreito que parece ter sido cavado às pressas.",
    ]
    chance_inimigo = prob_inimigo if prob_inimigo is not None else config.MAP_ENEMY_PROBABILITY
    sala = Sala(
        tipo="sala",
        nome=random.choice(["Corredor Escuro", "Câmara Poeirenta", "Túnel Apertado"]),
        descricao=random.choice(descricoes),
        pode_ter_inimigo=random.random() < chance_inimigo,
        nivel_area=nivel,
    )
    _atribuir_evento_randomico(sala)
    return sala


def _atribuir_evento_randomico(sala: Sala) -> None:
    if sala.tipo != "sala":
        return
    if random.random() >= config.EVENTO_PROBABILIDADE:
        return
    evento_id = eventos.sortear_evento_id()
    if evento_id:
        sala.evento_id = evento_id
