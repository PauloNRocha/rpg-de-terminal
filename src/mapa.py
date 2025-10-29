from src.itens import ITENS

# Define os tipos de inimigos que podem aparecer
INIMIGOS = {
    "goblin": {"nome": "Goblin", "hp": 10, "ataque": 4, "defesa": 1, "drop": None},
    "orc": {"nome": "Orc", "hp": 20, "ataque": 6, "defesa": 3, "drop": ITENS["pocao_cura_pequena"]},
    "chefe": {"nome": "O Terrível Orc Chefe", "hp": 40, "ataque": 8, "defesa": 4, "drop": ITENS["espada_longa"]}
}

# Define o mapa do jogo, agora com inimigos e itens
MAPA = [
    [
        {"nome": "Entrada da Caverna", "descricao": "A luz fraca da entrada ilumina o chão de pedra. O ar é úmido e cheira a mofo.", "inimigo": None, "item": None},
        {"nome": "Corredor Estreito", "descricao": "Um corredor apertado com teias de aranha no teto. O som de gotas d'água ecoa.", "inimigo": INIMIGOS["goblin"], "item": None},
        {"nome": "Câmara com Ossos", "descricao": "Uma pequena câmara com uma pilha de ossos roídos em um canto. Algo esteve aqui.", "inimigo": None, "item": ITENS["pocao_cura_pequena"]}
    ],
    [
        {"nome": "Salão Rachado", "descricao": "O chão de pedra aqui tem uma grande rachadura. Você precisa andar com cuidado.", "inimigo": None, "item": None},
        {"nome": "Encruzilhada", "descricao": "O caminho se divide aqui. Corredores seguem para todas as direções.", "inimigo": INIMIGOS["orc"], "item": None},
        {"nome": "Fonte Misteriosa", "descricao": "Uma pequena fonte de água cristalina brota do chão. A água parece brilhar.", "inimigo": None, "item": ITENS["escudo_aco"]}
    ],
    [
        {"nome": "Prisão Antiga", "descricao": "Celas com barras de ferro enferrujadas se alinham na parede. Estão todas vazias.", "inimigo": None, "item": None},
        {"nome": "Altar Sombrio", "descricao": "Um altar de pedra negra se ergue no centro da sala. Símbolos estranhos estão gravados nele.", "inimigo": INIMIGOS["orc"], "item": None},
        {"nome": "Covil da Besta", "descricao": "O ar aqui é pesado e fétido. O chão está coberto de detritos. Este é o covil de algo grande.", "inimigo": INIMIGOS["chefe"], "item": None}
    ]
]
