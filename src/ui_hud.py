"""Painéis de HUD da exploração."""

from __future__ import annotations

from rich.bar import Bar
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src import config
from src.entidades import Personagem, Sala
from src.ui_base import console, limpar_tela


def desenhar_hud_exploracao(
    jogador: Personagem,
    sala_atual: Sala,
    opcoes: list[str],
    nivel_masmorra: int,
    dificuldade_nome: str,
    mapa: list[list[Sala]] | None = None,
) -> str:
    """Desenha o HUD de exploração com informações do jogador, sala e opções."""
    limpar_tela()

    hp_percent = (jogador.hp / jogador.hp_max) * 100
    xp_percent = (jogador.xp_atual / jogador.xp_para_proximo_nivel) * 100

    grid_jogador = Table.grid(expand=True)
    grid_jogador.add_column()
    grid_jogador.add_row(Text(f"👤 {jogador.nome}, o {jogador.classe}", style="bold green"))
    grid_jogador.add_row(Text(f"🌟 Nível: {jogador.nivel}", style="yellow"))
    grid_jogador.add_row(Text(f"🔥 Dificuldade: {dificuldade_nome}", style="orange3"))
    if jogador.motivacao:
        grid_jogador.add_row(Text(f"🎯 Motivação: {jogador.motivacao.titulo}", style="cyan"))

    hp_grid = Table.grid(expand=True, padding=0)
    hp_grid.add_column(width=7)
    hp_grid.add_column(ratio=1)
    hp_grid.add_column(no_wrap=True, justify="right")
    hp_grid.add_row(
        "❤️  HP: ",
        Bar(100, 0, hp_percent, color="red"),
        f" {max(0, jogador.hp)}/{jogador.hp_max}",
    )
    grid_jogador.add_row(hp_grid)

    xp_grid = Table.grid(expand=True, padding=0)
    xp_grid.add_column(width=7)
    xp_grid.add_column(ratio=1)
    xp_grid.add_column(no_wrap=True, justify="right")
    xp_grid.add_row(
        "⭐  XP: ",
        Bar(100, 0, xp_percent, color="cyan"),
        f" {jogador.xp_atual}/{jogador.xp_para_proximo_nivel}",
    )
    grid_jogador.add_row(xp_grid)

    grid_jogador.add_row(
        Text(f"⚔️  Ataque: {jogador.ataque}   | 🛡️  Defesa: {jogador.defesa}", style="bold white")
    )
    grid_jogador.add_row(Text(f"💰 Bolsa: {jogador.carteira.formatar()}", style="bold yellow"))

    hud_jogador = Panel(
        grid_jogador, title=Text("Jogador", style="bold blue"), border_style="blue", width=70
    )

    texto_local = Text()
    texto_local.append(f"🗺️  Local: {sala_atual.nome}\n", style="bold magenta")
    texto_local.append(sala_atual.descricao, style="white")
    if sala_atual.trama_id and not sala_atual.trama_resolvida:
        texto_local.append(
            f"\n📜 Ponto da trama: {sala_atual.trama_nome or 'Mistério nas profundezas'}",
            style="bold yellow",
        )
    if sala_atual.chefe:
        if sala_atual.inimigo_derrotado:
            texto_local.append("\n✅ Chefe derrotado nesta sala.", style="bold green")
        else:
            nome_chefe = (
                sala_atual.chefe_nome
                or sala_atual.chefe_id
                or sala_atual.nome
                or "Chefe Desconhecido"
            )
            texto_local.append(f"\n⚠️  Presença do chefe: {nome_chefe}", style="bold red")
            if sala_atual.chefe_descricao:
                texto_local.append(f"\n{sala_atual.chefe_descricao}", style="red")

    titulo_local = Text(f"Localização — Masmorra Nível {nivel_masmorra}", style="bold blue")
    hud_sala = Panel(texto_local, title=titulo_local, border_style="blue", width=70)

    opcoes_texto = Text("", style="green")
    for i, opcao in enumerate(opcoes, 1):
        opcoes_texto.append(f"{i}. {opcao}\n")

    hud_opcoes = Panel(
        opcoes_texto,
        title=Text("Ações Disponíveis", style="bold blue"),
        border_style="blue",
        width=110,
    )

    if config.MINIMAPA_ATIVO and mapa is not None:
        minimapa = _render_minimapa(mapa, jogador)
        console.print(Columns([hud_jogador, minimapa], expand=False, equal=False, padding=(0, 1)))
    else:
        console.print(hud_jogador)

    console.print(hud_sala)
    console.print(hud_opcoes)

    return console.input("[bold yellow]> [/]")


def _render_minimapa(mapa: list[list[Sala]], jogador: Personagem) -> Panel:
    """Gera um painel textual simples de minimapa ao redor do jogador."""
    alcance = max(1, config.MINIMAPA_TAMANHO // 2)
    linhas = []
    for y in range(jogador.y - alcance, jogador.y + alcance + 1):
        linha = []
        for x in range(jogador.x - alcance, jogador.x + alcance + 1):
            if y == jogador.y and x == jogador.x:
                linha.append("@")
                continue
            if 0 <= y < len(mapa) and 0 <= x < len(mapa[0]):
                sala = mapa[y][x]
                if sala.chefe and not sala.inimigo_derrotado:
                    linha.append("C")
                elif sala.trama_id and not sala.trama_resolvida:
                    linha.append("T")
                elif sala.tipo == "escada":
                    linha.append("E")
                elif sala.visitada:
                    linha.append(".")
                else:
                    linha.append(" ")
            else:
                linha.append(" ")
        linhas.append("".join(linha))
    corpo = Text("\n".join(linhas), justify="center", style="cyan")
    return Panel(corpo, title="Minimapa", border_style="cyan", width=24)
