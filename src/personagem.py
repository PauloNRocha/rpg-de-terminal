import json
from pathlib import Path
from typing import Any

# Define um tipo para o personagem para facilitar a anotação
Personagem = dict[str, Any]
ClassesConfig = dict[str, dict[str, Any]]


def carregar_classes() -> ClassesConfig:
    """Carrega os dados das classes de personagem do arquivo JSON."""
    caminho_arquivo: Path = Path(__file__).parent / "data" / "classes.json"
    with open(caminho_arquivo, encoding="utf-8") as f:
        return json.load(f)


CLASSES: ClassesConfig = carregar_classes()


def criar_personagem(nome: str, classe_escolhida: str) -> Personagem:
    """Cria e retorna um dicionário de personagem com base no nome e na classe.

    A lógica de UI (input/print) foi movida para o loop principal do jogo.
    """
    stats = CLASSES[classe_escolhida]

    jogador: Personagem = {
        "nome": nome,
        "classe": classe_escolhida.capitalize(),
        "hp": stats["hp"],
        "hp_max": stats["hp"],
        "ataque": stats["ataque"],
        "defesa": stats["defesa"],
        "x": 0,
        "y": 0,
        "inventario": [],
        "equipamento": {"arma": None, "escudo": None},
        "nivel": 1,
        "xp_atual": 0,
        "xp_para_proximo_nivel": 100,
    }
    return jogador
