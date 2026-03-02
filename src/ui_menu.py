"""Telas de menu e prompts gerais."""

from __future__ import annotations

from rich import box
from rich.panel import Panel
from rich.text import Text

from src.ui_base import console, limpar_tela


def desenhar_menu_principal(
    versao: str,
    tem_save: bool,
    dificuldade_nome: str,
    alerta_atualizacao: str | None = None,
) -> str:
    """Desenha o menu principal do jogo."""
    limpar_tela()
    menu_texto = Text("", justify="center")
    menu_texto.append("0. Verificar Atualizações\n", style="bold cyan")
    menu_texto.append("1. Iniciar Nova Aventura\n", style="bold green")
    if tem_save:
        menu_texto.append("2. Continuar Aventura (Carregar Save)\n", style="bold cyan")
        menu_texto.append("3. Ver Histórico de Aventuras\n", style="bold magenta")
        menu_texto.append("4. Sair\n", style="bold red")
    else:
        menu_texto.append("2. Ver Histórico de Aventuras\n", style="bold magenta")
        menu_texto.append("3. Sair\n", style="bold red")

    footer_text = f"v{versao} - Desenvolvido por Paulo Rocha e IA"
    destaque_dificuldade = Panel(
        Text(
            f"Dificuldade padrão para a próxima aventura: {dificuldade_nome}",
            justify="center",
            style="bold white",
        ),
        width=75,
        border_style="cyan",
    )
    panel = Panel(
        menu_texto,
        title=Text("AVENTURA NO TERMINAL", justify="center", style="bold yellow"),
        subtitle=Text(footer_text, justify="center", style="dim white"),
        width=75,
        box=box.DOUBLE,
        border_style="blue",
    )
    console.print(panel)
    console.print(destaque_dificuldade)
    if alerta_atualizacao:
        console.print(
            Panel(
                Text(alerta_atualizacao, justify="center", style="bold yellow"),
                border_style="yellow",
                title="Atualização disponível!",
                width=75,
            )
        )
    return console.input("[bold yellow]Escolha uma opção: [/]")


def desenhar_tela_input(titulo: str, prompt: str) -> str:
    """Desenha uma tela para entrada de texto do usuário."""
    limpar_tela()
    panel = Panel(
        Text(prompt, justify="center"),
        title=Text(titulo, justify="center", style="bold yellow"),
        width=75,
        box=box.DOUBLE,
        border_style="blue",
    )
    console.print(panel)
    return console.input("[bold yellow]> [/]")
