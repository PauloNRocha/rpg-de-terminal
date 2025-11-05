import copy
import json
import random
from pathlib import Path
from typing import Any

# Define um tipo para o item para facilitar a anotação
Item = dict[str, Any]
ItensPorRaridade = dict[str, list[Item]]


def carregar_itens() -> ItensPorRaridade:
    """Carrega os dados dos itens do arquivo JSON."""
    caminho_arquivo: Path = Path(__file__).parent / "data" / "itens.json"
    with open(caminho_arquivo, encoding="utf-8") as f:
        return json.load(f)


ITENS_POR_RARIDADE: ItensPorRaridade = carregar_itens()


def gerar_item_aleatorio(raridade: str = "comum") -> Item | None:
    """Gera um item aleatório com base na raridade, selecionando de uma lista.

    pré-definida carregada de um arquivo JSON.
    """
    if raridade not in ITENS_POR_RARIDADE:
        return None

    lista_itens: list[Item] = ITENS_POR_RARIDADE[raridade]
    item_escolhido: Item = random.choice(lista_itens)

    return copy.deepcopy(item_escolhido)
