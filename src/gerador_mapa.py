# src/gerador_mapa.py

import random

LARGURA_MAPA = 10
ALTURA_MAPA = 10

def gerar_mapa(nivel=1):
    """
    Gera um novo mapa com um caminho principal garantido da entrada até a saída.
    A dificuldade dos inimigos e a estrutura podem variar com o nível.
    """
    # Inicializa o mapa com salas vazias (paredes)
    mapa = [[{"tipo": "parede"} for _ in range(LARGURA_MAPA)] for _ in range(ALTURA_MAPA)]

    # Define o ponto de partida e o caminho
    x, y = random.randint(1, LARGURA_MAPA - 2), 0
    caminho_principal = []

    # 1. Cria um caminho principal de cima para baixo
    while y < ALTURA_MAPA - 1:
        mapa[y][x] = _criar_sala("caminho", nivel)
        caminho_principal.append((x, y))
        
        # Movimenta o caminho aleatoriamente para os lados, mas prioriza ir para baixo
        direcao = random.choice(["esquerda", "direita", "baixo", "baixo", "baixo"])
        if direcao == "esquerda" and x > 1:
            x -= 1
        elif direcao == "direita" and x < LARGURA_MAPA - 2:
            x += 1
        else: # Para baixo
            y += 1

    # 2. Define as salas especiais no caminho principal
    entrada_x, entrada_y = caminho_principal[0]
    mapa[entrada_y][entrada_x] = _criar_sala("entrada", nivel)

    chefe_x, chefe_y = caminho_principal[-2]
    mapa[chefe_y][chefe_x] = _criar_sala("chefe", nivel)

    escada_x, escada_y = caminho_principal[-1]
    mapa[escada_y][escada_x] = _criar_sala("escada", nivel)

    # 3. Adiciona salas secundárias e becos sem saída
    for _ in range(int(LARGURA_MAPA * ALTURA_MAPA / 4)): # Adiciona um número de salas extras
        px, py = random.choice(caminho_principal)
        direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(direcoes)
        
        for dx, dy in direcoes:
            nx, ny = px + dx, py + dy
            if 0 <= nx < LARGURA_MAPA and 0 <= ny < ALTURA_MAPA and mapa[ny][nx]["tipo"] == "parede":
                mapa[ny][nx] = _criar_sala("secundaria", nivel)
                break

    return mapa

def _criar_sala(tipo, nivel):
    """Função auxiliar para criar diferentes tipos de sala."""
    sala = {
        "visitada": False,
        "inimigo_derrotado": False,
        "inimigo_atual": None,
        "nivel_area": nivel
    }
    if tipo == "entrada":
        sala.update({
            "tipo": "entrada",
            "nome": "Entrada da Masmorra",
            "descricao": "A luz da entrada desaparece atrás de você. O ar é úmido e cheira a poeira e morte.",
            "pode_ter_inimigo": False,
        })
    elif tipo == "chefe":
        sala.update({
            "tipo": "chefe",
            "nome": "Covil do Chefe",
            "descricao": "Uma aura de poder emana desta sala. Ossos espalhados pelo chão indicam que você não é o primeiro a chegar.",
            "pode_ter_inimigo": True,
            "chefe": True,
        })
    elif tipo == "escada":
        sala.update({
            "tipo": "escada",
            "nome": "Escadaria para as Profundezas",
            "descricao": "Uma escadaria de pedra desce para a escuridão. Você sente um ar ainda mais frio vindo de baixo.",
            "pode_ter_inimigo": False,
        })
    else: # Caminho principal ou sala secundária
        descricoes = [
            "Um corredor escuro e úmido. O som de gotas de água ecoa ao longe.",
            "Uma pequena câmara com teias de aranha cobrindo as paredes.",
            "Uma sala com entalhes estranhos nas paredes de pedra.",
            "Um túnel estreito que parece ter sido cavado às pressas."
        ]
        sala.update({
            "tipo": "sala",
            "nome": random.choice(["Corredor Escuro", "Câmara Poeirenta", "Túnel Apertado"]),
            "descricao": random.choice(descricoes),
            "pode_ter_inimigo": random.random() < 0.6, # 60% de chance de ter inimigo
        })
    return sala
