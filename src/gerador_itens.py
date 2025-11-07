import json
import random
from pathlib import Path
from typing import Any

from src.entidades import Item

ItensPorRaridade = dict[str, list[dict[str, Any]]]


def carregar_itens() -> ItensPorRaridade:
    """Carrega os dados dos itens do arquivo JSON."""
    caminho_arquivo: Path = Path(__file__).parent / "data" / "itens.json"
    with open(caminho_arquivo, encoding="utf-8") as f:
        return json.load(f)


ITENS_POR_RARIDADE: ItensPorRaridade = carregar_itens()


def gerar_item_aleatorio(raridade: str = "comum") -> Item | None:
    """Gera um item aleatório com base na raridade, retornando uma instância de Item."""
    if raridade not in ITENS_POR_RARIDADE:
        return None

    lista_itens_data: list[dict[str, Any]] = ITENS_POR_RARIDADE[raridade]
    item_data: dict[str, Any] = random.choice(lista_itens_data)

    # Garante que os campos opcionais existam antes de criar a instância
    item_data.setdefault("bonus", {})
    item_data.setdefault("efeito", {})

    return Item.from_dict(item_data)
