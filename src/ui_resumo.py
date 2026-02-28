"""Telas de resumo final da run (morte ou saída)."""

from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.entidades import Personagem
from src.ui import console, limpar_tela


def desenhar_tela_resumo_final(
    motivo: str,
    jogador: Personagem | None,
    nivel_atual: int,
    estatisticas: dict[str, int],
    chefe_info: tuple[int, str] | None = None,
    inimigo_causa_morte: str | None = None,
    turnos: int | None = None,
    trama_consequencia: str | None = None,
) -> None:
    """Mostra um painel com o resumo da aventura."""
    limpar_tela()
    titulo = "FIM DA AVENTURA" if motivo == "saida" else "DERROTA HEROICA"
    subtitulo = (
        "Você deixou a masmorra e vive para contar a história."
        if motivo == "saida"
        else "Sua lenda termina aqui, mas outras histórias surgirão."
    )

    nome = jogador.nome if jogador else "—"
    classe = jogador.classe if jogador else "—"
    nivel = jogador.nivel if jogador else 1
    linha_topo = Text(
        f"{nome} ({classe}) • Nível {nivel} • Andar alcançado: {nivel_atual}",
        style="bold yellow",
    )

    tabela = Table(box=box.SIMPLE, border_style="cyan", expand=False)
    tabela.add_column("Indicador", style="bold white")
    tabela.add_column("Quantidade", justify="right", style="yellow")
    tabela.add_row("Inimigos derrotados", str(estatisticas.get("inimigos_derrotados", 0)))
    tabela.add_row("Itens obtidos", str(estatisticas.get("itens_obtidos", 0)))
    tabela.add_row("Moedas ganhas", str(estatisticas.get("moedas_ganhas", 0)))
    tabela.add_row("Eventos disparados", str(estatisticas.get("eventos_disparados", 0)))
    tabela.add_row("Andares concluídos", str(estatisticas.get("andares_concluidos", 0)))
    if turnos is not None:
        tabela.add_row("Turnos/Ações", str(turnos))
    if chefe_info:
        tabela.add_row(
            "Chefe mais profundo",
            f"Andar {chefe_info[0]} — {chefe_info[1]}",
        )
    if inimigo_causa_morte and motivo != "saida":
        tabela.add_row("Causa da morte", inimigo_causa_morte)
    if trama_consequencia:
        tabela.add_row("Marca da trama", trama_consequencia)

    painel = Panel(
        tabela,
        title=Text(titulo, style="bold red" if motivo != "saida" else "bold green"),
        subtitle=subtitulo,
        border_style="blue",
        width=70,
    )

    console.print(linha_topo)
    console.print(painel)
    console.input("[bold yellow]Pressione Enter para retornar ao menu... [/]")
