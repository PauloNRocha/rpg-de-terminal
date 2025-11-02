# src/gerador_mapa.py

import random

def gerar_mapa(tamanho_min=5, tamanho_max=10):
    """
    Gera um mapa proceduralmente para a masmorra.
    O mapa é uma lista de listas de dicionários, onde cada dicionário representa uma sala.
    """
    tamanho = random.randint(tamanho_min, tamanho_max)
    mapa = [[None for _ in range(tamanho)] for _ in range(tamanho)]

    # Ponto de partida
    start_x, start_y = random.randint(0, tamanho - 1), random.randint(0, tamanho - 1)
    mapa[start_y][start_x] = {
        "nome": "Entrada da Masmorra",
        "descricao": "Você está na entrada de uma masmorra escura e úmida.",
        "nivel_area": 1,
        "pode_ter_inimigo": False,
        "inimigo_atual": None,
        "visitada": False,
    }

    salas_criadas = [(start_x, start_y)]
    salas_para_explorar = [(start_x, start_y)]

    # Geração do mapa usando um algoritmo de expansão
    while salas_para_explorar:
        x, y = salas_para_explorar.pop(0)

        direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)] # Sul, Norte, Leste, Oeste
        random.shuffle(direcoes)

        for dx, dy in direcoes:
            nx, ny = x + dx, y + dy

            if 0 <= nx < tamanho and 0 <= ny < tamanho and mapa[ny][nx] is None:
                # Cria uma nova sala
                nivel_area = random.randint(max(1, mapa[y][x]["nivel_area"] - 1), mapa[y][x]["nivel_area"] + 1)
                pode_ter_inimigo = random.choice([True, False])

                mapa[ny][nx] = {
                    "nome": f"Sala {len(salas_criadas) + 1}",
                    "descricao": "Uma sala escura e misteriosa.",
                    "nivel_area": nivel_area,
                    "pode_ter_inimigo": pode_ter_inimigo,
                    "inimigo_atual": None,
                    "visitada": False,
                }
                salas_criadas.append((nx, ny))
                salas_para_explorar.append((nx, ny))
    
    # Garante que o mapa seja retangular e preenche espaços vazios com salas "vazias"
    mapa_final = []
    for linha in mapa:
        nova_linha = []
        for sala in linha:
            if sala is None:
                nova_linha.append({
                    "nome": "Parede Sólida",
                    "descricao": "Não há nada aqui além de uma parede fria e sólida.",
                    "nivel_area": 0,
                    "pode_ter_inimigo": False,
                    "inimigo_atual": None,
                    "visitada": False,
                })
            else:
                nova_linha.append(sala)
        mapa_final.append(nova_linha)

    # TODO: Garantir uma sala de chefe no final do mapa
    # Por enquanto, vamos apenas retornar o mapa gerado
    return mapa_final
