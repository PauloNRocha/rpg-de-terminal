import time
from src.utils import limpar_tela

CLASSES = {
    "guerreiro": {"hp": 25, "ataque": 6, "defesa": 4},
    "mago": {"hp": 15, "ataque": 8, "defesa": 2},
    "arqueiro": {"hp": 20, "ataque": 7, "defesa": 3},
}

def criar_personagem(nome, classe_escolhida):
    """
    Cria e retorna um dicionário de personagem com base no nome e na classe.
    A lógica de UI (input/print) foi movida para o loop principal do jogo.
    """
    stats = CLASSES[classe_escolhida]
    
    jogador = {
        "nome": nome,
        "classe": classe_escolhida.capitalize(),
        "hp": stats["hp"],
        "hp_max": stats["hp"],
        "ataque": stats["ataque"],
        "defesa": stats["defesa"],
        "x": 0, "y": 0,
        "inventario": [],
        "equipamento": {"arma": None, "escudo": None},
        "nivel": 1,
        "xp_atual": 0,
        "xp_para_proximo_nivel": 100,
    }
    return jogador
