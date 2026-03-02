"""Telas específicas de combate."""

from __future__ import annotations

from rich import box
from rich.bar import Bar
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.entidades import Inimigo, Personagem
from src.ui_base import console, limitar_log, limpar_tela


def desenhar_tela_combate(
    jogador: Personagem,
    inimigo: Inimigo,
    mensagem: list[str] | None = None,
) -> str:
    """Desenha a tela de combate com informações do jogador, inimigo e mensagens."""
    mensagem = mensagem or []
    display_log = limitar_log(mensagem)
    limpar_tela()

    hp_jogador_percent = (jogador.hp / jogador.hp_max) * 100
    grid_jogador = Table.grid(expand=True, padding=0)
    grid_jogador.add_column(no_wrap=True)
    grid_jogador.add_column(ratio=1)
    grid_jogador.add_column(no_wrap=True, justify="right")
    grid_jogador.add_row(
        Text(f"👤 {jogador.nome}", style="bold green"),
        Bar(100, 0, hp_jogador_percent, color="green"),
        Text(f" {max(0, jogador.hp)}/{jogador.hp_max}", style="bold green"),
    )

    hp_inimigo_percent = (inimigo.hp / inimigo.hp_max) * 100
    grid_inimigo = Table.grid(expand=True, padding=0)
    grid_inimigo.add_column(no_wrap=True)
    grid_inimigo.add_column(ratio=1)
    grid_inimigo.add_column(no_wrap=True, justify="right")
    grid_inimigo.add_row(
        Text(f"👹 {inimigo.nome}", style="bold red"),
        Bar(100, 0, hp_inimigo_percent, color="red"),
        Text(f" {max(0, inimigo.hp)}/{inimigo.hp_max}", style="bold red"),
    )

    log_combate = Text("\n".join(display_log), style="white")

    grid_principal = Table.grid(expand=True)
    grid_principal.add_column()
    grid_principal.add_row(grid_jogador)
    grid_principal.add_row("")
    grid_principal.add_row(grid_inimigo)
    grid_principal.add_row("")
    grid_principal.add_row(log_combate)

    combate_panel = Panel(
        grid_principal,
        title=Text("COMBATE", justify="center", style="bold yellow"),
        width=75,
        box=box.DOUBLE,
        border_style="red",
    )
    console.print(combate_panel)
    return console.input(
        "[bold yellow]Sua ação (1. Atacar, 2. Usar Item, 3. Fugir, L. Ver log): [/]"
    )


def desenhar_log_completo(log: list[str]) -> None:
    """Mostra o log completo do combate em uma tela separada."""
    limpar_tela()
    texto = "\n".join(log) if log else "Sem eventos registrados."
    panel = Panel(
        Text(texto, style="white"),
        title=Text("Log completo do combate", style="bold yellow"),
        border_style="blue",
        width=90,
    )
    console.print(panel)
    console.input("[bold yellow]Pressione Enter para voltar ao combate... [/]")
