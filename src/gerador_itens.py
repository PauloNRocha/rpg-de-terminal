import json
import random
from pathlib import Path
from typing import Any

from src import config
from src.entidades import Item
from src.erros import ErroDadosError

ItensPorRaridade = dict[str, list[dict[str, Any]]]


def carregar_itens() -> ItensPorRaridade:
    """Carrega os dados dos itens do arquivo JSON."""
    caminho_arquivo: Path = Path(__file__).parent / "data" / "itens.json"
    try:
        with open(caminho_arquivo, encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError as erro:
        raise ErroDadosError("Arquivo 'itens.json' não foi encontrado em src/data/.") from erro
    except json.JSONDecodeError as erro:
        raise ErroDadosError("Arquivo 'itens.json' está inválido (JSON malformado).") from erro
    if not isinstance(dados, dict) or not dados:
        raise ErroDadosError("Arquivo 'itens.json' está vazio ou com formato incorreto.")
    return dados


try:
    ITENS_POR_RARIDADE: ItensPorRaridade = carregar_itens()
    _ERRO_ITENS: ErroDadosError | None = None
except ErroDadosError as erro:
    ITENS_POR_RARIDADE = {}
    _ERRO_ITENS = erro


def obter_itens_por_raridade() -> ItensPorRaridade:
    """Retorna o catálogo de itens pronto para uso."""
    if _ERRO_ITENS is not None:
        raise _ERRO_ITENS
    if not ITENS_POR_RARIDADE:
        raise ErroDadosError("Nenhum item disponível em 'itens.json'.")
    return ITENS_POR_RARIDADE


def gerar_item_aleatorio(raridade: str = "comum", permitir_consumivel: bool = True) -> Item | None:
    """Gera um item aleatório e pode trocar por consumíveis se configurado."""
    itens_por_raridade = obter_itens_por_raridade()
    candidatos: list[dict[str, Any]] = list(itens_por_raridade.get(raridade, []))

    if permitir_consumivel and "consumivel" in itens_por_raridade:
        chance = config.DROP_CONSUMIVEL_CHANCE.get(raridade, 0.0)
        if (candidatos and chance > 0 and random.random() < chance) or not candidatos:
            candidatos = list(itens_por_raridade["consumivel"])

    if not candidatos:
        return None

    item_data: dict[str, Any] = random.choice(candidatos).copy()

    # Garante que os campos opcionais existam antes de criar a instância
    item_data.setdefault("bonus", {})
    item_data.setdefault("efeito", {})

    return Item.from_dict(item_data)
