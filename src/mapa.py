# Define os tipos de inimigos que podem aparecer
INIMIGOS = {
    "goblin": {"nome": "Goblin", "hp": 10, "ataque": 4, "defesa": 1},
    "orc": {"nome": "Orc", "hp": 20, "ataque": 6, "defesa": 3},
    "chefe": {"nome": "O Terrível Orc Chefe", "hp": 40, "ataque": 8, "defesa": 4}
}

# Define o mapa do jogo, agora com inimigos
MAPA = [
    [
        {"nome": "Entrada da Caverna", "descricao": "A luz fraca da entrada ilumina o chão de pedra. O ar é úmido e cheira a mofo.", "inimigo": None},
        {"nome": "Corredor Estreito", "descricao": "Um corredor apertado com teias de aranha no teto. O som de gotas d'água ecoa.", "inimigo": INIMIGOS["goblin"]},
        {"nome": "Câmara com Ossos", "descricao": "Uma pequena câmara com uma pilha de ossos roídos em um canto. Algo esteve aqui.", "inimigo": None}
    ],
    [
        {"nome": "Salão Rachado", "descricao": "O chão de pedra aqui tem uma grande rachadura. Você precisa andar com cuidado.", "inimigo": None},
        {"nome": "Encruzilhada", "descricao": "O caminho se divide aqui. Corredores seguem para todas as direções.", "inimigo": INIMIGOS["orc"]},
        {"nome": "Fonte Misteriosa", "descricao": "Uma pequena fonte de água cristalina brota do chão. A água parece brilhar.", "inimigo": None}
    ],
    [
        {"nome": "Prisão Antiga", "descricao": "Celas com barras de ferro enferrujadas se alinham na parede. Estão todas vazias.", "inimigo": None},
        {"nome": "Altar Sombrio", "descricao": "Um altar de pedra negra se ergue no centro da sala. Símbolos estranhos estão gravados nele.", "inimigo": INIMIGOS["orc"]},
        {"nome": "Covil da Besta", "descricao": "O ar aqui é pesado e fétido. O chão está coberto de detritos. Este é o covil de algo grande.", "inimigo": INIMIGOS["chefe"]}
    ]
]