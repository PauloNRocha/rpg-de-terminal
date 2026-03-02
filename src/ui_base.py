"""Recursos base compartilhados pelos módulos de UI."""

from __future__ import annotations

from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()
ClassesConfig = dict[str, dict[str, Any]]

CLASSE_EMOJIS = {
    "guerreiro": "⚔️",
    "mago": "✨",
    "arqueiro": "🏹",
    "ladino": "🗡️",
}

CLASSE_CORES = {
    "guerreiro": "red",
    "mago": "magenta",
    "arqueiro": "green",
    "ladino": "yellow",
}


def limpar_tela() -> None:
    """Limpa a tela do terminal."""
    console.clear()


def limitar_log(mensagens: list[str], limite: int = 10) -> list[str]:
    """Retorna apenas as últimas entradas do log, com cabeçalho de truncamento."""
    if len(mensagens) <= limite:
        return mensagens
    ocultos = len(mensagens) - limite
    return [f"(… +{ocultos} eventos anteriores)", *mensagens[-limite:]]


def desenhar_caixa(titulo: str, conteudo: str, largura: int = 75) -> None:
    """Desenha uma caixa simples de mensagem usando Rich."""
    panel = Panel(
        Text(conteudo, justify="left"),
        title=Text(titulo, justify="center", style="bold yellow"),
        width=largura,
        box=box.DOUBLE,
        border_style="blue",
    )
    console.print(panel)
