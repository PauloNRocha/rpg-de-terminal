# Define o layout do mapa e o nível de desafio de cada sala

MAPA = [
    [
        {"nome": "Entrada da Caverna", "descricao": "A luz fraca da entrada ilumina o chão de pedra. O ar é úmido e cheira a mofo.", "nivel_area": 1, "pode_ter_inimigo": False},
        {"nome": "Corredor Estreito", "descricao": "Um corredor apertado com teias de aranha no teto. O som de gotas d'água ecoa.", "nivel_area": 1, "pode_ter_inimigo": True},
        {"nome": "Câmara com Ossos", "descricao": "Uma pequena câmara com uma pilha de ossos roídos em um canto. Algo esteve aqui.", "nivel_area": 2, "pode_ter_inimigo": False}
    ],
    [
        {"nome": "Salão Rachado", "descricao": "O chão de pedra aqui tem uma grande rachadura. Você precisa andar com cuidado.", "nivel_area": 2, "pode_ter_inimigo": True},
        {"nome": "Encruzilhada", "descricao": "O caminho se divide aqui. Corredores seguem para todas as direções.", "nivel_area": 3, "pode_ter_inimigo": True},
        {"nome": "Fonte Misteriosa", "descricao": "Uma pequena fonte de água cristalina brota do chão. A água parece brilhar.", "nivel_area": 3, "pode_ter_inimigo": False}
    ],
    [
        {"nome": "Prisão Antiga", "descricao": "Celas com barras de ferro enferrujadas se alinham na parede. Estão todas vazias.", "nivel_area": 4, "pode_ter_inimigo": True},
        {"nome": "Altar Sombrio", "descricao": "Um altar de pedra negra se ergue no centro da sala. Símbolos estranhos estão gravados nele.", "nivel_area": 4, "pode_ter_inimigo": True},
        {"nome": "Covil do Chefe", "descricao": "O ar aqui é pesado e fétido. O chão está coberto de detritos. Este é o covil de algo grande.", "nivel_area": 5, "pode_ter_inimigo": True, "chefe": True}
    ]
]