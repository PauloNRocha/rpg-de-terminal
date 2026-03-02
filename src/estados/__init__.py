"""Estados reutilizáveis do jogo."""

from .combate import executar_estado_combate
from .exploracao import (
    montar_opcoes_exploracao,
    preparar_andar_exploracao,
    preparar_encontro_sala,
    resolver_evento_sala,
    resolver_sala_trama,
)
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
    "montar_opcoes_exploracao",
    "preparar_andar_exploracao",
    "preparar_encontro_sala",
    "remover_item_por_chave",
    "resolver_evento_sala",
    "resolver_sala_trama",
    "usar_item",
]
