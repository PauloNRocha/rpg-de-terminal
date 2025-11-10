"""Estado e utilidades relacionados ao inventário."""

from collections.abc import Callable, Iterable
from typing import Any

from src.entidades import Item, Personagem
from src.ui import (
    desenhar_tela_equipar,
    desenhar_tela_evento,
    desenhar_tela_input,
    desenhar_tela_inventario,
)

TIPO_ORDENACAO = {"arma": 0, "escudo": 1}


def agrupar_itens_equipaveis(itens: Iterable[Item]) -> list[dict[str, Any]]:
    """Agrupa itens equipáveis por atributos para facilitar a listagem."""
    grupos: dict[tuple, dict[str, Any]] = {}
    for item in itens:
        if item.tipo not in {"arma", "escudo"}:
            continue
        chave = _chave_item(item)
        if chave not in grupos:
            grupos[chave] = {"item": item, "quantidade": 0, "chave": chave}
        grupos[chave]["quantidade"] += 1
    return sorted(
        grupos.values(),
        key=lambda grupo: (
            TIPO_ORDENACAO.get(grupo["item"].tipo, 99),
            grupo["item"].nome,
        ),
    )


def _chave_item(item: Item) -> tuple:
    bonus = tuple(sorted(item.bonus.items()))
    efeito = tuple(sorted(item.efeito.items()))
    return (item.nome, item.tipo, bonus, efeito)


def remover_item_por_chave(inventario: list[Item], chave: tuple) -> Item:
    """Remove e retorna o item correspondente à chave de agrupamento."""
    for idx, item in enumerate(inventario):
        if _chave_item(item) == chave:
            return inventario.pop(idx)
    raise ValueError("Item não encontrado no inventário para a chave informada.")


def aplicar_efeitos_consumiveis(
    jogador: Personagem,
    item: Item,
    handlers: dict[str, Callable[[Personagem, int], str]],
) -> list[str]:
    """Aplica os efeitos configurados do item e retorna mensagens de feedback."""
    mensagens: list[str] = []
    efeitos = item.efeito or {}
    for nome, valor in efeitos.items():
        handler = handlers.get(nome)
        if handler:
            mensagens.append(handler(jogador, int(valor)))
        else:
            mensagens.append(f"Efeito '{nome}' ainda não é suportado e foi ignorado.")
    return mensagens


def gerenciar_inventario(
    jogador: Personagem,
    usar_item_fn: Callable[[Personagem], bool | None],
    equipar_item_fn: Callable[[Personagem], None],
) -> None:
    """Loop principal para o menu de inventário."""
    while True:
        escolha = desenhar_tela_inventario(jogador)
        if escolha == "1":
            usar_item_fn(jogador)
        elif escolha == "2":
            equipar_item_fn(jogador)
        elif escolha == "3":
            break
        else:
            desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")


def usar_item(
    jogador: Personagem,
    handlers: dict[str, Callable[[Personagem, int], str]],
) -> list[str] | bool | None:
    """Permite selecionar um consumível e retorna as mensagens de efeito aplicadas."""
    while True:
        itens_consumiveis = [item for item in jogador.inventario if item.tipo == "consumivel"]
        opcoes_itens = [
            f"{i + 1}. {item.nome} ({item.descricao})" for i, item in enumerate(itens_consumiveis)
        ]
        opcoes_itens.append(f"{len(itens_consumiveis) + 1}. Voltar")
        prompt = (
            "Seus itens consumíveis:\n"
            + "\n".join(opcoes_itens)
            + "\n\nEscolha um item para usar ou 'Voltar': "
        )
        escolha_str = desenhar_tela_input("USAR ITEM", prompt)
        try:
            escolha = int(escolha_str)
            if escolha == len(itens_consumiveis) + 1:
                return False
            if not (1 <= escolha <= len(itens_consumiveis)):
                raise ValueError
            item_escolhido = itens_consumiveis[escolha - 1]
            if not item_escolhido.efeito:
                desenhar_tela_evento(
                    "ITEM SEM EFEITO",
                    "Este item não possui efeitos consumíveis configurados.",
                )
                continue
            mensagens = aplicar_efeitos_consumiveis(jogador, item_escolhido, handlers)
            jogador.inventario.remove(item_escolhido)
            return mensagens
        except (ValueError, IndexError):
            desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")
    return None


def equipar_item(jogador: Personagem) -> None:
    """Processa a seleção de armas/escudos e atualiza o equipamento."""
    grupos = agrupar_itens_equipaveis(jogador.inventario)
    escolha_str = desenhar_tela_equipar(jogador, grupos)
    try:
        if escolha_str == "voltar":
            return
        if not escolha_str.isdigit():
            raise ValueError
        escolha = int(escolha_str)
        if escolha == len(grupos) + 1:
            return
        if not (1 <= escolha <= len(grupos)):
            raise ValueError
        grupo = grupos[escolha - 1]
        item_escolhido = remover_item_por_chave(jogador.inventario, grupo["chave"])
        tipo_item = item_escolhido.tipo
        if jogador.equipamento[tipo_item]:
            jogador.inventario.append(jogador.equipamento[tipo_item])
        jogador.equipamento[tipo_item] = item_escolhido
    except (ValueError, IndexError):
        desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")
