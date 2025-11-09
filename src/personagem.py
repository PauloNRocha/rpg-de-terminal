import json
from pathlib import Path
from typing import Any

from src.entidades import Personagem
from src.erros import ErroDadosError

ClassesConfig = dict[str, dict[str, Any]]


def carregar_classes() -> ClassesConfig:
    """Carrega os dados das classes de personagem do arquivo JSON."""
    caminho_arquivo: Path = Path(__file__).parent / "data" / "classes.json"
    try:
        with open(caminho_arquivo, encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError as erro:
        raise ErroDadosError("Arquivo 'classes.json' não foi encontrado em src/data/.") from erro
    except json.JSONDecodeError as erro:
        raise ErroDadosError("Arquivo 'classes.json' está inválido (JSON malformado).") from erro
    if not isinstance(dados, dict) or not dados:
        raise ErroDadosError("Arquivo 'classes.json' está vazio ou com formato incorreto.")
    return dados


try:
    CLASSES: ClassesConfig = carregar_classes()
    _ERRO_CLASSES: ErroDadosError | None = None
except ErroDadosError as erro:
    CLASSES = {}
    _ERRO_CLASSES = erro


def obter_classes() -> ClassesConfig:
    """Retorna as classes carregadas ou dispara um erro amigável."""
    if _ERRO_CLASSES is not None:
        raise _ERRO_CLASSES
    if not CLASSES:
        raise ErroDadosError("Nenhuma classe disponível em 'classes.json'.")
    return CLASSES


def criar_personagem(nome: str, classe_escolhida: str) -> Personagem:
    """Cria e retorna uma instância da dataclass Personagem com base no nome e na classe."""
    classes = obter_classes()
    stats = classes[classe_escolhida]

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
