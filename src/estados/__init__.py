"""Estados reutilizáveis do jogo."""

from .combate import executar_estado_combate
from .inventario import (
    agrupar_itens_equipaveis,
    aplicar_efeitos_consumiveis,
    equipar_item,
    gerenciar_inventario,
    remover_item_por_chave,
    usar_item,
)

__all__ = [
    "agrupar_itens_equipaveis",
    "aplicar_efeitos_consumiveis",
    "equipar_item",
    "executar_estado_combate",
    "gerenciar_inventario",
    "remover_item_por_chave",
    "usar_item",
]
