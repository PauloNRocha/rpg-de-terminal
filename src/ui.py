import os
import random
from typing import Any

from rich import box
from rich.bar import Bar
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# Define tipos para facilitar a anotação
Personagem = dict[str, Any]
Sala = dict[str, Any]
ClassesConfig = dict[str, dict[str, Any]]
Item = dict[str, Any]


def limpar_tela() -> None:
    """Limpa a tela do terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def desenhar_caixa(titulo: str, conteudo: str, largura: int = 75) -> None:
    """Desenha uma caixa de texto com título e conteúdo usando rich.Panel."""
    panel = Panel(
        Text(conteudo, justify="left"),
        title=Text(titulo, justify="center", style="bold yellow"),
        width=largura,
        box=box.DOUBLE,
        border_style="blue",
    )
    console.print(panel)


def desenhar_hud_exploracao(jogador: Personagem, sala_atual: Sala, opcoes: list[str]) -> str:
    """Desenha o HUD de exploração com informações do jogador, sala e opções."""
    limpar_tela()

    # --- Seção do Jogador ---
    hp_percent = (jogador["hp"] / jogador["hp_max"]) * 100
    xp_percent = (jogador["xp_atual"] / jogador["xp_para_proximo_nivel"]) * 100

    # Usando uma tabela para organizar as informações do jogador de forma robusta
    grid_jogador = Table.grid(expand=True)
    grid_jogador.add_column()
    grid_jogador.add_row(Text(f"👤 {jogador['nome']}, o {jogador['classe']}", style="bold green"))
    grid_jogador.add_row(Text(f"🌟 Nível: {jogador['nivel']}", style="yellow"))

    # Grid para HP
    hp_grid = Table.grid(expand=True, padding=0)
    hp_grid.add_column(width=7)
    hp_grid.add_column(ratio=1)
    hp_grid.add_column(no_wrap=True, justify="right")
    hp_grid.add_row(
        "❤️  HP: ",
        Bar(100, 0, hp_percent, color="red"),
        f" {max(0, jogador['hp'])}/{jogador['hp_max']}",
    )
    grid_jogador.add_row(hp_grid)

    # Grid para XP
    xp_grid = Table.grid(expand=True, padding=0)
    xp_grid.add_column(width=7)
    xp_grid.add_column(ratio=1)
    xp_grid.add_column(no_wrap=True, justify="right")
    xp_grid.add_row(
        "⭐  XP: ",
        Bar(100, 0, xp_percent, color="cyan"),
        f" {jogador['xp_atual']}/{jogador['xp_para_proximo_nivel']}",
    )
    grid_jogador.add_row(xp_grid)

    grid_jogador.add_row(
        Text(
            f"⚔️  Ataque: {jogador['ataque']}   | 🛡️  Defesa: {jogador['defesa']}",
            style="bold white",
        )
    )

    hud_jogador = Panel(
        grid_jogador, title=Text("Jogador", style="bold blue"), border_style="blue", width=75
    )

    # --- Seção da Sala ---
    hud_sala = Panel(
        Text(f"🗺️  Local: {sala_atual['nome']}", style="bold magenta")
        + "\n"
        + Text(sala_atual["descricao"], style="white"),
        title=Text("Localização", style="bold blue"),
        border_style="blue",
        width=75,
    )

    # --- Seção de Opções ---
    opcoes_texto = Text("", style="green")
    for i, opcao in enumerate(opcoes, 1):
        opcoes_texto.append(f"{i}. {opcao}\n")

    hud_opcoes = Panel(
        opcoes_texto,
        title=Text("Ações Disponíveis", style="bold blue"),
        border_style="blue",
        width=75,
    )

    console.print(hud_jogador)
    console.print(hud_sala)
    console.print(hud_opcoes)

    return console.input("[bold yellow]> [/]")


def desenhar_tela_evento(titulo: str, mensagem: str) -> None:
    """Desenha uma tela de evento com título e mensagem usando rich.Panel."""
    limpar_tela()
    desenhar_caixa(titulo, mensagem)
    console.input("[bold yellow]Pressione Enter para continuar... [/]")


def desenhar_tela_saida(titulo: str, mensagem: str) -> None:
    """Desenha uma tela de evento final sem esperar por input do usuário."""
    limpar_tela()
    desenhar_caixa(titulo, mensagem)


def desenhar_tela_equipar(jogador: Personagem, itens_equipaveis: list[Item]) -> str:
    """Desenha a tela de equipar itens, comparando com o equipamento atual."""
    limpar_tela()

    tabela_equipamento = Table(
        title=Text("EQUIPAR ITENS", style="bold yellow"),
        box=box.DOUBLE,
        border_style="blue",
        header_style="bold cyan",
    )
    tabela_equipamento.add_column("Slot", style="dim", width=15)
    tabela_equipamento.add_column("Equipado", style="green", width=30)
    tabela_equipamento.add_column("Bônus", style="white", width=25)

    # Equipamento atual
    arma_equipada: Item | None = jogador["equipamento"]["arma"]
    escudo_equipado: Item | None = jogador["equipamento"]["escudo"]

    tabela_equipamento.add_row(
        "Arma:",
        arma_equipada["nome"] if arma_equipada else "Nenhuma",
        ", ".join([f"{k}: {v}" for k, v in arma_equipada.get("bonus", {}).items()])
        if arma_equipada
        else "",
    )
    tabela_equipamento.add_row(
        "Escudo:",
        escudo_equipado["nome"] if escudo_equipado else "Nenhum",
        ", ".join([f"{k}: {v}" for k, v in escudo_equipado.get("bonus", {}).items()])
        if escudo_equipado
        else "",
    )

    console.print(tabela_equipamento)

    if itens_equipaveis:
        tabela_disponiveis = Table(
            title=Text("ITENS DISPONÍVEIS", style="bold yellow"),
            box=box.DOUBLE,
            border_style="blue",
            header_style="bold cyan",
        )
        tabela_disponiveis.add_column("Opção", style="dim", width=5)
        tabela_disponiveis.add_column("Item", style="green", width=25)
        tabela_disponiveis.add_column("Tipo", style="magenta", width=10)
        tabela_disponiveis.add_column("Bônus", style="white", width=25)

        for i, item in enumerate(itens_equipaveis):
            bonus_str = ", ".join([f"{k}: {v}" for k, v in item.get("bonus", {}).items()])
            tabela_disponiveis.add_row(str(i + 1), item["nome"], item["tipo"], bonus_str)

        console.print(tabela_disponiveis)
    else:
        console.print(
            Panel(
                Text("Você não tem itens equipáveis no inventário.", justify="center"),
                width=75,
                border_style="blue",
            )
        )

    opcoes_panel = Panel(
        Text(
            f"Escolha um item (1-{len(itens_equipaveis)}) ou "
            f"'{len(itens_equipaveis) + 1}' para Voltar.",
            justify="center",
        ),
        width=75,
    )
    console.print(opcoes_panel)
    return console.input("[bold yellow]> [/]")


def desenhar_menu_principal(versao: str, tem_save: bool) -> str:
    """Desenha o menu principal do jogo e retorna a escolha do jogador."""
    limpar_tela()

    menu_texto = Text("", justify="center")
    menu_texto.append("1. Iniciar Nova Aventura\n", style="bold green")
    if tem_save:
        menu_texto.append("2. Continuar Aventura (Carregar Save)\n", style="bold cyan")
        menu_texto.append("3. Sair\n", style="bold red")
    else:
        menu_texto.append("2. Sair\n", style="bold red")

    footer_text = f"v{versao} - Desenvolvido por Paulo N. Rocha"

    panel = Panel(
        menu_texto,
        title=Text("AVENTURA NO TERMINAL", justify="center", style="bold yellow"),
        subtitle=Text(footer_text, justify="center", style="dim white"),
        width=75,
        box=box.DOUBLE,
        border_style="blue",
    )

    console.print(panel)

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


def desenhar_tela_escolha_classe(classes: ClassesConfig) -> str:
    """Desenha a tela de escolha de classe e retorna a escolha do jogador."""
    limpar_tela()

    tabela_classes = Table(
        title=Text("ESCOLHA SUA CLASSE", style="bold yellow"),
        box=box.DOUBLE,
        border_style="blue",
        header_style="bold cyan",
    )

    tabela_classes.add_column("Opção", style="dim", width=5)

    tabela_classes.add_column("Classe", style="green", width=15)

    tabela_classes.add_column("Descrição", style="white", width=45)

    for i, (nome_classe, detalhes) in enumerate(classes.items()):
        tabela_classes.add_row(str(i + 1), nome_classe, detalhes["descricao"])

    console.print(tabela_classes)
    return console.input("[bold yellow]Escolha sua classe: [/]")


def desenhar_tela_resumo_personagem(jogador: Personagem) -> None:
    """Desenha a tela de resumo do personagem após a criação."""
    limpar_tela()

    resumo_texto = Text("", justify="left")

    resumo_texto.append(f"Nome: {jogador['nome']}\n", style="bold green")

    resumo_texto.append(f"Classe: {jogador['classe']}\n", style="bold yellow")

    resumo_texto.append(f"HP: {jogador['hp_max']}\n", style="red")

    resumo_texto.append(f"Ataque: {jogador['ataque']}\n", style="cyan")

    resumo_texto.append(f"Defesa: {jogador['defesa']}\n", style="blue")

    resumo_texto.append(f"Nível: {jogador['nivel']}\n", style="magenta")

    panel = Panel(
        resumo_texto,
        title=Text("SEU PERSONAGEM", justify="center", style="bold white"),
        width=75,
        box=box.DOUBLE,
        border_style="green",
    )

    console.print(panel)

    console.input("[bold yellow]Pressione Enter para iniciar a aventura... [/]")


def desenhar_tela_inventario(jogador: Personagem) -> str:
    """Desenha a tela de inventário do jogador."""
    limpar_tela()

    tabela_inventario = Table(
        title=Text("INVENTÁRIO", style="bold yellow"),
        box=box.DOUBLE,
        border_style="blue",
        header_style="bold cyan",
    )
    tabela_inventario.add_column("Opção", style="dim", width=5)
    tabela_inventario.add_column("Item", style="green", width=25)
    tabela_inventario.add_column("Tipo", style="magenta", width=10)
    tabela_inventario.add_column("Efeito", style="white", width=25)

    if not jogador["inventario"]:
        console.print(
            Panel(
                Text("Seu inventário está vazio.", justify="center"),
                width=75,
                border_style="blue",
            )
        )
    else:
        for i, item in enumerate(jogador["inventario"]):
            efeitos: dict[str, Any] | None = None
            if isinstance(item.get("efeito"), dict):
                efeitos = item["efeito"]
            elif isinstance(item.get("bonus"), dict):
                efeitos = item["bonus"]

            if efeitos:
                efeito_str = ", ".join(f"{chave}: {valor}" for chave, valor in efeitos.items())
            else:
                efeito_str = "-"

            tabela_inventario.add_row(str(i + 1), item["nome"], item["tipo"], efeito_str)
        console.print(tabela_inventario)

    console.print(
        Panel(
            Text("1. Usar Item | 2. Equipar Item | 3. Voltar", justify="center"),
            width=75,
            border_style="blue",
        )
    )
    return console.input("[bold yellow]Escolha uma opção: [/]")


def desenhar_tela_combate(
    jogador: Personagem, inimigo: Personagem, mensagem: list[str] | None = None
) -> str:
    """Desenha a tela de combate com informações do jogador, inimigo e mensagens."""
    if mensagem is None:
        mensagem = []
    limpar_tela()

    # Grid do Jogador
    hp_jogador_percent = (jogador["hp"] / jogador["hp_max"]) * 100
    grid_jogador = Table.grid(expand=True, padding=0)
    grid_jogador.add_column(no_wrap=True)
    grid_jogador.add_column(ratio=1)
    grid_jogador.add_column(no_wrap=True, justify="right")
    grid_jogador.add_row(
        Text(f"👤 {jogador['nome']}", style="bold green"),
        Bar(100, 0, hp_jogador_percent, color="green"),
        Text(f" {max(0, jogador['hp'])}/{jogador['hp_max']}", style="bold green"),
    )

    # Grid do Inimigo
    hp_inimigo_percent = (inimigo["hp"] / inimigo["hp_max"]) * 100
    grid_inimigo = Table.grid(expand=True, padding=0)
    grid_inimigo.add_column(no_wrap=True)
    grid_inimigo.add_column(ratio=1)
    grid_inimigo.add_column(no_wrap=True, justify="right")
    grid_inimigo.add_row(
        Text(f"👹 {inimigo['nome']}", style="bold red"),
        Bar(100, 0, hp_inimigo_percent, color="red"),
        Text(f" {max(0, inimigo['hp'])}/{inimigo['hp_max']}", style="bold red"),
    )

    # Mensagens de Combate
    log_combate_texto = "\n".join(mensagem)
    log_combate = Text(log_combate_texto, style="white")

    # Layout da tela de combate
    grid_principal = Table.grid(expand=True)
    grid_principal.add_column()
    grid_principal.add_row(grid_jogador)
    grid_principal.add_row("")  # Espaçamento
    grid_principal.add_row(grid_inimigo)
    grid_principal.add_row("")  # Espaçamento
    grid_principal.add_row(log_combate)

    combate_panel = Panel(
        grid_principal,
        title=Text("COMBATE", justify="center", style="bold yellow"),
        width=75,
        box=box.DOUBLE,
        border_style="red",
    )
    console.print(combate_panel)

    return console.input("[bold yellow]Sua ação (1. Atacar, 2. Usar Item, 3. Fugir): [/]")


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
