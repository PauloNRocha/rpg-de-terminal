"""Telas de eventos, prompts e transições narrativas."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.ui_base import console, desenhar_caixa, limpar_tela

if TYPE_CHECKING:
    from src.eventos import Evento


def desenhar_tela_evento(titulo: str, mensagem: str) -> None:
    """Desenha uma tela de evento com título e mensagem."""
    limpar_tela()
    desenhar_caixa(titulo, mensagem)
    console.input("[bold yellow]Pressione Enter para continuar... [/]")


def desenhar_tela_saida(titulo: str, mensagem: str) -> None:
    """Desenha uma tela de evento final sem esperar por input."""
    limpar_tela()
    desenhar_caixa(titulo, mensagem)


def desenhar_evento_interativo(evento: Evento) -> dict[str, Any] | None:
    """Mostra um evento com opções de escolha e retorna a opção selecionada."""
    limpar_tela()
    descricao = getattr(evento, "descricao", "") or ""
    nome = getattr(evento, "nome", "Evento")
    opcoes = getattr(evento, "opcoes", []) or []

    panel_desc = Panel(Text(descricao, justify="left"), title=Text(nome, style="bold yellow"))
    console.print(panel_desc)

    tabela = Table(box=box.SIMPLE, border_style="cyan", expand=False)
    tabela.add_column("Opção", justify="center", style="bold yellow", width=6)
    tabela.add_column("Escolha", style="bold white")
    for idx, opcao in enumerate(opcoes, start=1):
        tabela.add_row(str(idx), str(opcao.get("descricao") or opcao.get("nome") or ""))
    console.print(tabela)
    console.print(
        Panel(
            "Digite o número da opção ou pressione Enter para cancelar.",
            border_style="blue",
        )
    )

    escolha = console.input("[bold yellow]Escolha: [/]").strip()
    if not escolha:
        return None
    try:
        idx = int(escolha)
    except ValueError:
        return None
    if 1 <= idx <= len(opcoes):
        return opcoes[idx - 1]
    return None


def desenhar_tela_pre_chefe(titulo: str, historia: str) -> str:
    """Mostra a cena narrativa antes do chefe e retorna a escolha do jogador."""
    limpar_tela()
    corpo = Text(historia or "", style="white", justify="left")
    panel = Panel(
        corpo,
        title=Text(titulo, style="bold yellow"),
        border_style="red",
        width=90,
    )
    console.print(panel)
    opcoes = Text(
        "1. Enfrentar agora\n2. Recuar para se preparar\n3. Abrir Inventário",
        style="bold white",
        justify="center",
    )
    console.print(Panel(opcoes, border_style="blue", width=60))
    escolha = console.input("[bold yellow]Escolha (1/2/3): [/]").strip()
    if escolha == "1":
        return "enfrentar"
    if escolha == "3":
        return "inventario"
    return "recuar"


def tela_game_over() -> None:
    """Desenha uma tela de Game Over épica com mensagens aleatórias."""
    limpar_tela()
    mensagens_epicas = [
        "Sua lenda termina aqui, nas profundezas esquecidas...",
        "A escuridão consome sua alma. A masmorra clama mais uma vítima.",
        "Seu nome será sussurrado como um aviso para outros aventureiros.",
        "Apesar de sua bravura, o destino decretou seu fim.",
        "Os monstros celebram sua queda. A esperança se esvai.",
    ]
    mensagem_escolhida = random.choice(mensagens_epicas)
    texto_game_over = Text.assemble(
        (mensagem_escolhida, "italic red"), "\n\n", ("FIM DE JOGO", "bold white")
    )
    panel = Panel(
        texto_game_over,
        title=Text("GAME OVER", justify="center", style="bold red"),
        width=75,
        box=box.DOUBLE,
        border_style="red",
    )
    console.print(panel)
    console.input("[bold yellow]Pressione Enter para voltar ao menu principal... [/]")
