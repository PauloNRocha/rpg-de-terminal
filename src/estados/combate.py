"""Estado responsável pelo combate."""

from collections.abc import Callable
from contextlib import suppress
from enum import Enum
from typing import Protocol

from src.entidades import Inimigo, Item, Personagem, Sala
from src.gerador_itens import obter_item_por_nome
from src.ui import desenhar_tela_evento, tela_game_over


class ContextoCombate(Protocol):
    """Interface mínima esperada pelo estado de combate."""

    jogador: Personagem | None
    sala_em_combate: Sala | None
    inimigo_em_combate: Inimigo | None

    def limpar_combate(self) -> None:
        """Remove referências ao combate atual."""
        ...

    def restaurar_posicao_anterior(self) -> None:
        """Recoloca o jogador na sala anterior."""
        ...

    def resetar_jogo(self) -> None:
        """Limpa todo o contexto da partida."""
        ...


def executar_estado_combate(
    contexto: ContextoCombate,
    iniciar_combate: Callable[
        [Personagem, Inimigo, Callable[[Personagem], bool | None]],
        tuple[bool, Inimigo],
    ],
    usar_item_fn: Callable[[Personagem], bool | None],
    gerar_item_aleatorio: Callable[[str], Item | None],
    verificar_level_up: Callable[[Personagem], None],
    atualizar_status_temporarios: Callable[[Personagem], None],
    estado_menu: Enum,
    estado_exploracao: Enum,
    on_trama_corrompida_vencida: Callable[[Sala], None] | None = None,
) -> Enum:
    """Resolve o combate e retorna o próximo estado do loop principal."""
    jogador = contexto.jogador
    sala = contexto.sala_em_combate
    inimigo = contexto.inimigo_em_combate
    if jogador is None or sala is None or inimigo is None:
        return estado_exploracao

    resultado, inimigo_atualizado = iniciar_combate(jogador, inimigo, usar_item_fn)
    sala.inimigo_atual = inimigo_atualizado

    if resultado:
        xp_ganho = inimigo_atualizado.xp_recompensa
        mensagem_vitoria = f"Você derrotou o {inimigo.nome} e ganhou {xp_ganho} de XP!"
        desenhar_tela_evento("VITÓRIA!", mensagem_vitoria)
        jogador.xp_atual += xp_ganho
        contexto.registrar_inimigo_derrotado()
        if sala.chefe and (
            not getattr(contexto, "chefe_mais_profundo_nivel", 0)
            or contexto.nivel_masmorra >= contexto.chefe_mais_profundo_nivel
        ):
            contexto.chefe_mais_profundo_nivel = contexto.nivel_masmorra
            contexto.chefe_mais_profundo_nome = sala.chefe_nome or inimigo.nome
        item_dropado: Item | None = None
        if getattr(inimigo_atualizado, "drop_item_nome", None):
            item_dropado = obter_item_por_nome(inimigo_atualizado.drop_item_nome or "")
        if item_dropado is None and inimigo_atualizado.drop_raridade:
            item_dropado = gerar_item_aleatorio(inimigo_atualizado.drop_raridade)
        if item_dropado:
            jogador.inventario.append(item_dropado)
            mensagem_item = f"O inimigo dropou: {item_dropado.nome}!"
            desenhar_tela_evento("ITEM ENCONTRADO!", mensagem_item)
            contexto.registrar_item_obtido()
        if sala.trama_id and sala.trama_desfecho == "corrompido":
            sala.trama_resolvida = True
            if (
                hasattr(contexto, "trama_ativa")
                and contexto.trama_ativa
                and getattr(contexto.trama_ativa, "id", None) == sala.trama_id
            ):
                contexto.trama_ativa.concluida = True
            if on_trama_corrompida_vencida is not None:
                on_trama_corrompida_vencida(sala)
            else:
                desenhar_tela_evento(
                    "TRAMA CONCLUÍDA",
                    "Ao vencer a forma corrompida, "
                    "você finalmente encerra este capítulo da jornada.",
                )
        sala.inimigo_derrotado = True
        sala.inimigo_atual = None
        contexto.limpar_combate()
        verificar_level_up(jogador)
        atualizar_status_temporarios(jogador)
        return estado_exploracao

    if not jogador.esta_vivo():
        contexto.inimigo_causa_morte = inimigo.nome
        tela_game_over()
        if hasattr(contexto, "exibir_resumo_final"):
            with suppress(Exception):
                contexto.exibir_resumo_final("morte")
        contexto.resetar_jogo()
        return estado_menu

    desenhar_tela_evento("FUGA!", "Você recua para a sala anterior.")
    if hasattr(contexto, "tutorial"):
        with suppress(Exception):
            contexto.tutorial.mostrar(
                "dica_fuga",
                "Dica: Fuga",
                "Fugir consome o turno atual. Ao retornar, o inimigo pode não estar mais lá,\n"
                "mas a sala ainda pode ter novos perigos. Use para sobreviver, não para farmar.",
            )
    contexto.restaurar_posicao_anterior()
    contexto.limpar_combate()
    atualizar_status_temporarios(jogador)
    return estado_exploracao
