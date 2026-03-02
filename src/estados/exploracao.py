"""Helpers do estado de exploração para reduzir acoplamento de `jogo.py`."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any, Protocol

from src import config, eventos
from src.chefes import obter_chefe_por_id
from src.entidades import Personagem, Sala
from src.gerador_inimigos import gerar_inimigo
from src.gerador_mapa import gerar_mapa
from src.tramas import gerar_pista_trama
from src.ui import (
    desenhar_evento_interativo,
    desenhar_tela_evento,
    desenhar_tela_pre_chefe,
    tela_game_over,
)


class ContextoExploracao(Protocol):
    """Interface mínima do contexto esperada pelos helpers de exploração."""

    jogador: Personagem | None
    mapa_atual: list[list[Sala]] | None
    nivel_masmorra: int
    posicao_anterior: tuple[int, int] | None
    sala_em_combate: Sala | None
    inimigo_em_combate: Any
    trama_ativa: Any
    trama_pistas_exibidas: set[int]
    rng: random.Random
    turnos_totais: int
    tutorial: Any

    def resetar_estatisticas(self) -> None:
        """Limpa estatísticas do andar atual."""
        ...

    def obter_perfil_dificuldade(self) -> config.DificuldadePerfil:
        """Retorna o perfil de dificuldade da run."""
        ...

    def registrar_evento(self) -> None:
        """Conta um evento disparado no resumo do andar."""
        ...

    def registrar_moedas(self, valor: int) -> None:
        """Acumula moedas recebidas no andar atual."""
        ...

    def resetar_jogo(self) -> None:
        """Reinicia o contexto da run."""
        ...

    def restaurar_posicao_anterior(self) -> None:
        """Retorna o jogador para a posição anterior."""
        ...


def preparar_andar_exploracao(
    contexto: ContextoExploracao,
    posicionar_na_entrada: Callable[[Personagem, list[list[Sala]]], None],
    desenhar_tela_evento_fn: Callable[[str, str], None] = desenhar_tela_evento,
) -> None:
    """Gera o mapa do andar atual e exibe tutoriais/pistas pendentes."""
    jogador = contexto.jogador
    if jogador is None or contexto.mapa_atual is not None:
        return

    contexto.resetar_estatisticas()
    contexto.mapa_atual = gerar_mapa(
        contexto.nivel_masmorra,
        contexto.obter_perfil_dificuldade(),
        trama_ativa=contexto.trama_ativa,
        rng=contexto.rng,
    )
    posicionar_na_entrada(jogador, contexto.mapa_atual)
    contexto.tutorial.mostrar(
        "exploracao_basica",
        "Dica: Exploração",
        "Use os números para se mover (N/S/L/O), abrir inventário, salvar ou sair.\n"
        "A HUD mostra HP, XP, motivação, dificuldade e andar atual.",
    )
    if (
        contexto.trama_ativa
        and not contexto.trama_ativa.concluida
        and contexto.nivel_masmorra < contexto.trama_ativa.andar_alvo
        and contexto.nivel_masmorra not in contexto.trama_pistas_exibidas
    ):
        pista = gerar_pista_trama(
            contexto.trama_ativa,
            contexto.nivel_masmorra,
            rng=contexto.rng,
        )
        desenhar_tela_evento_fn("PISTA DA TRAMA", pista)
        contexto.trama_pistas_exibidas.add(contexto.nivel_masmorra)


def resolver_sala_trama(
    contexto: ContextoExploracao,
    sala: Sala,
    aplicar_consequencia_trama: Callable[[ContextoExploracao, Sala, str], None],
    verificar_level_up: Callable[[Personagem], None],
    desenhar_tela_evento_fn: Callable[[str, str], None] = desenhar_tela_evento,
) -> None:
    """Resolve a sala narrativa da trama ativa."""
    jogador = contexto.jogador
    if jogador is None:
        return

    titulo = f"TRAMA: {sala.trama_nome or 'Mistério das Profundezas'}"
    texto_base = sala.trama_texto or "Você encontra vestígios de uma história inacabada."
    desfecho = (sala.trama_desfecho or "").lower()

    desenhar_tela_evento_fn(titulo, texto_base)
    contexto.registrar_evento()

    if desfecho == "vivo":
        recompensa = 20 + contexto.nivel_masmorra * 10
        jogador.carteira.receber(recompensa)
        contexto.registrar_moedas(recompensa)
        desenhar_tela_evento_fn(
            "DESFECHO DA TRAMA",
            f"Você garante um resgate improvável e recebe {recompensa} moedas de gratidão.",
        )
        aplicar_consequencia_trama(contexto, sala, "vivo")
        sala.trama_resolvida = True
        if contexto.trama_ativa and contexto.trama_ativa.id == sala.trama_id:
            contexto.trama_ativa.concluida = True
        return

    if desfecho == "morto":
        xp_ganho = 15 + contexto.nivel_masmorra * 12
        jogador.xp_atual += xp_ganho
        desenhar_tela_evento_fn(
            "DESFECHO DA TRAMA",
            f"Você encontra apenas memórias e jura continuar.\nGanho de XP: {xp_ganho}.",
        )
        verificar_level_up(jogador)
        aplicar_consequencia_trama(contexto, sala, "morto")
        sala.trama_resolvida = True
        if contexto.trama_ativa and contexto.trama_ativa.id == sala.trama_id:
            contexto.trama_ativa.concluida = True
        return

    if desfecho == "corrompido":
        sala.pode_ter_inimigo = True
        sala.inimigo_derrotado = False
        sala.trama_resolvida = False
        tema_trama = (
            contexto.trama_ativa.tema
            if contexto.trama_ativa is not None and not contexto.trama_ativa.concluida
            else None
        )
        if sala.inimigo_atual is None and sala.trama_inimigo_tipo:
            sala.inimigo_atual = gerar_inimigo(
                max(sala.nivel_area, contexto.nivel_masmorra + 1),
                tipo_inimigo=sala.trama_inimigo_tipo,
                dificuldade=contexto.obter_perfil_dificuldade(),
                chefe=False,
                tema=tema_trama,
                rng=contexto.rng,
            )
        desenhar_tela_evento_fn(
            "DESFECHO DA TRAMA",
            "A corrupção desperta uma criatura na sala. Prepare-se para o confronto final.",
        )
        return

    sala.trama_resolvida = True
    if contexto.trama_ativa and contexto.trama_ativa.id == sala.trama_id:
        contexto.trama_ativa.concluida = True


def resolver_evento_sala(
    contexto: ContextoExploracao,
    sala: Sala,
    desenhar_tela_evento_fn: Callable[[str, str], None] = desenhar_tela_evento,
    desenhar_evento_interativo_fn: Callable[[Any], dict[str, Any] | None] = (
        desenhar_evento_interativo
    ),
    tela_game_over_fn: Callable[[], None] = tela_game_over,
) -> str | None:
    """Resolve um evento de sala e retorna `menu` em caso de morte."""
    jogador = contexto.jogador
    if jogador is None:
        return "menu"

    perfil = contexto.obter_perfil_dificuldade()
    contexto.registrar_evento()
    moedas_antes = jogador.carteira.valor_bronze
    evento = eventos.carregar_eventos().get(sala.evento_id)
    if evento and evento.opcoes:
        escolha = desenhar_evento_interativo_fn(evento)
        if escolha is None:
            return "exploracao"
        op_efeitos = escolha.get("efeitos", {})
        msgs, _, sucesso = eventos.aplicar_efeitos(op_efeitos, jogador, perfil.saque_moedas_mult)
        corpo = [evento.descricao, *msgs]
        desenhar_tela_evento_fn(evento.nome.upper(), "\n".join(corpo))
        if not sucesso:
            return "exploracao"
    else:
        titulo, mensagem = eventos.disparar_evento(
            sala.evento_id, jogador, perfil.saque_moedas_mult
        )
        desenhar_tela_evento_fn(titulo, mensagem)

    ganho_moedas = jogador.carteira.valor_bronze - moedas_antes
    contexto.registrar_moedas(max(0, ganho_moedas))
    sala.evento_resolvido = True
    if jogador.hp <= 0:
        tela_game_over_fn()
        contexto.resetar_jogo()
        return "menu"
    return None


def preparar_encontro_sala(
    contexto: ContextoExploracao,
    sala: Sala,
    montar_cena_pre_chefe: Callable[[ContextoExploracao, Sala, str], str],
    desenhar_tela_evento_fn: Callable[[str, str], None] = desenhar_tela_evento,
    desenhar_tela_pre_chefe_fn: Callable[[str, str], str] = desenhar_tela_pre_chefe,
) -> str | None:
    """Prepara o combate da sala atual e retorna a próxima transição quando houver."""
    tema_trama = (
        contexto.trama_ativa.tema
        if contexto.trama_ativa is not None and not contexto.trama_ativa.concluida
        else None
    )
    inimigo = sala.inimigo_atual
    if inimigo is None:
        perfil_dificuldade = contexto.obter_perfil_dificuldade()
        perfil_chefe = obter_chefe_por_id(sala.chefe_id)
        tipo = None
        if sala.trama_inimigo_tipo:
            tipo = sala.trama_inimigo_tipo
        elif sala.chefe:
            if perfil_chefe:
                tipo = perfil_chefe.tipo
            elif sala.chefe_tipo:
                tipo = sala.chefe_tipo
        inimigo = gerar_inimigo(
            sala.nivel_area,
            tipo_inimigo=tipo,
            dificuldade=perfil_dificuldade,
            chefe=sala.chefe,
            perfil_chefe=perfil_chefe,
            tema=tema_trama,
            rng=contexto.rng,
        )
        sala.inimigo_atual = inimigo

    if sala.chefe and not sala.chefe_intro_exibida:
        chefe_config = obter_chefe_por_id(sala.chefe_id)
        titulo_pre = sala.nome
        historia_pre = sala.descricao
        if chefe_config and contexto.jogador:
            classe = contexto.jogador.classe.lower()
            historias_cls = chefe_config.historias_por_classe or {}
            entrada = historias_cls.get(classe) or historias_cls.get("default", {})
            titulo_pre = entrada.get("titulo") or chefe_config.titulo or titulo_pre
            historia_pre = entrada.get("historia") or chefe_config.historia or historia_pre
        historia_pre = montar_cena_pre_chefe(contexto, sala, historia_pre)
        escolha_chefe = desenhar_tela_pre_chefe_fn(titulo_pre, historia_pre)
        if escolha_chefe == "enfrentar":
            sala.chefe_intro_exibida = True
        elif escolha_chefe == "inventario":
            return "inventario"
        else:
            contexto.restaurar_posicao_anterior()
            sala.inimigo_atual = None
            return "exploracao"

    contexto.sala_em_combate = sala
    contexto.inimigo_em_combate = inimigo
    desenhar_tela_evento_fn("ENCONTRO!", f"CUIDADO! Um {inimigo.nome} está na sala!")
    contexto.turnos_totais += 1
    return "combate"


def montar_opcoes_exploracao(
    jogador: Personagem,
    mapa: list[list[Sala]],
    sala_atual: Sala,
) -> list[str]:
    """Monta a lista de ações disponíveis na exploração."""
    opcoes: list[str] = []
    if jogador.y > 0 and mapa[jogador.y - 1][jogador.x].tipo != "parede":
        opcoes.append("Ir para o Norte")
    if jogador.y < len(mapa) - 1 and mapa[jogador.y + 1][jogador.x].tipo != "parede":
        opcoes.append("Ir para o Sul")
    if jogador.x < len(mapa[0]) - 1 and mapa[jogador.y][jogador.x + 1].tipo != "parede":
        opcoes.append("Ir para o Leste")
    if jogador.x > 0 and mapa[jogador.y][jogador.x - 1].tipo != "parede":
        opcoes.append("Ir para o Oeste")
    return opcoes
