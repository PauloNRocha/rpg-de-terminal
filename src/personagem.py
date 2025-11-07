import json
from pathlib import Path
from typing import Any

from src.entidades import Personagem

ClassesConfig = dict[str, dict[str, Any]]


def carregar_classes() -> ClassesConfig:
    """Carrega os dados das classes de personagem do arquivo JSON."""
    caminho_arquivo: Path = Path(__file__).parent / "data" / "classes.json"
    with open(caminho_arquivo, encoding="utf-8") as f:
        return json.load(f)


CLASSES: ClassesConfig = carregar_classes()


def criar_personagem(nome: str, classe_escolhida: str) -> Personagem:
    """Cria e retorna uma instância da dataclass Personagem com base no nome e na classe."""
    stats = CLASSES[classe_escolhida]

    return Personagem(
        nome=nome,
        classe=classe_escolhida.capitalize(),
        hp=stats["hp"],
        hp_max=stats["hp"],
        ataque=stats["ataque"],
        ataque_base=stats["ataque"],
        defesa=stats["defesa"],
        defesa_base=stats["defesa"],
        x=0,
        y=0,
        nivel=1,
        xp_atual=0,
        xp_para_proximo_nivel=100,
    )
