import json
from pathlib import Path

# Carrega os dados das classes do arquivo JSON
def carregar_classes():
    caminho_arquivo = Path(__file__).parent / "data" / "classes.json"
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)

CLASSES = carregar_classes()

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
