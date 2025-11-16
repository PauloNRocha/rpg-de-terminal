import random
import unicodedata
from collections.abc import Sequence
from typing import Any

from rich import box
from rich.bar import Bar
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.config import DificuldadePerfil
from src.entidades import Inimigo, Personagem, Sala

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


def desenhar_hud_exploracao(
    jogador: Personagem,
    sala_atual: Sala,
    opcoes: list[str],
    nivel_masmorra: int,
    dificuldade_nome: str,
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
        grid_jogador, title=Text("Jogador", style="bold blue"), border_style="blue", width=75
    )

    texto_local = Text()
    texto_local.append(f"🗺️  Local: {sala_atual.nome}\n", style="bold magenta")
    texto_local.append(sala_atual.descricao, style="white")

    titulo_local = Text(f"Localização — Masmorra Nível {nivel_masmorra}", style="bold blue")

    hud_sala = Panel(
        texto_local,
        title=titulo_local,
        border_style="blue",
        width=75,
    )

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
    """Desenha uma tela de evento com título e mensagem."""
    limpar_tela()
    desenhar_caixa(titulo, mensagem)
    console.input("[bold yellow]Pressione Enter para continuar... [/]")


def desenhar_tela_saida(titulo: str, mensagem: str) -> None:
    """Desenha uma tela de evento final sem esperar por input."""
    limpar_tela()
    desenhar_caixa(titulo, mensagem)


def desenhar_tela_equipar(jogador: Personagem, grupos_itens: list[dict[str, Any]]) -> str:
    """Desenha a tela de equipar itens, com agrupamento e resumo de quantidades."""
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

    arma_equipada = jogador.equipamento.get("arma")
    escudo_equipado = jogador.equipamento.get("escudo")

    tabela_equipamento.add_row(
        "Arma:",
        arma_equipada.nome if arma_equipada else "Nenhuma",
        ", ".join([f"{k}: {v}" for k, v in arma_equipada.bonus.items()]) if arma_equipada else "",
    )
    tabela_equipamento.add_row(
        "Escudo:",
        escudo_equipado.nome if escudo_equipado else "Nenhum",
        ", ".join([f"{k}: {v}" for k, v in escudo_equipado.bonus.items()])
        if escudo_equipado
        else "",
    )
    console.print(tabela_equipamento)

    if grupos_itens:
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
        tabela_disponiveis.add_column("Qtd", style="yellow", width=5)

        for i, grupo in enumerate(grupos_itens):
            item = grupo["item"]
            bonus_str = ", ".join([f"{k}: {v}" for k, v in item.bonus.items()]) or "-"
            quantidade = grupo["quantidade"]
            tabela_disponiveis.add_row(
                str(i + 1),
                item.nome,
                item.tipo,
                bonus_str,
                f"x{quantidade}",
            )
        console.print(tabela_disponiveis)
    else:
        console.print(
            Panel(
                Text("Você não tem itens equipáveis no inventário.", justify="center"),
                width=75,
                border_style="blue",
            )
        )
        console.input("[bold yellow]Pressione Enter para voltar... [/]")
        return "voltar"

    texto_opcoes = (
        f"Escolha um item (1-{len(grupos_itens)}) ou {len(grupos_itens) + 1} para Voltar."
    )
    opcoes_panel = Panel(
        Text(texto_opcoes, justify="center"),
        width=75,
    )
    console.print(opcoes_panel)
    return console.input("[bold yellow]> [/]")


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
        menu_texto.append("3. Sair\n", style="bold red")
    else:
        menu_texto.append("2. Sair\n", style="bold red")

    footer_text = f"v{versao} - Desenvolvido por Paulo N. Rocha"
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


def desenhar_tela_escolha_classe(classes: ClassesConfig) -> str:
    """Mostra cartões detalhados de cada classe e normaliza a escolha do jogador."""
    limpar_tela()

    titulo = Panel(
        Text(
            "Escolha sua classe favorita para iniciar a aventura",
            justify="center",
            style="bold yellow",
        ),
        border_style="blue",
        box=box.DOUBLE,
    )
    console.print(titulo)

    mapas_escolha: dict[str, str] = {}
    cartoes: list[Panel] = []

    for indice, (nome, detalhes) in enumerate(classes.items(), start=1):
        slug = nome.lower()
        emoji = CLASSE_EMOJIS.get(slug, "✨")
        cor = CLASSE_CORES.get(slug, "cyan")

        corpo = Text(justify="left")
        corpo.append(f"{detalhes['descricao']}\n\n", style="white")
        corpo.append(f"❤️ HP Base: {detalhes['hp']}\n", style="red")
        corpo.append(f"⚔️ Ataque Base: {detalhes['ataque']}\n", style="yellow")
        corpo.append(f"🛡️ Defesa Base: {detalhes['defesa']}\n", style="cyan")

        subtitle = f"[bold]{indice}[/bold] • [bold]{slug[0].upper()}[/bold] • {slug.title()}"
        cartoes.append(
            Panel(
                corpo,
                title=f"{emoji} {slug.title()}",
                subtitle=subtitle,
                border_style=cor,
                padding=(1, 2),
            )
        )

        mapas_escolha[str(indice)] = slug
        mapas_escolha[slug] = slug
        mapas_escolha[slug[0]] = slug

    console.print(Columns(cartoes, equal=True, expand=True))

    instrucoes = Panel(
        Text(
            "Digite o número, a inicial ou o nome completo da classe.\n"
            "Exemplos: '1', 'g' ou 'guerreiro'.",
            justify="center",
            style="bold white",
        ),
        border_style="blue",
        width=80,
    )
    console.print(instrucoes)

    while True:
        resposta = console.input("[bold yellow]Escolha sua classe: [/]").strip().lower()
        if not resposta:
            continue
        escolha_normalizada = mapas_escolha.get(resposta)
        if escolha_normalizada:
            return escolha_normalizada
        console.print(
            Panel(
                Text(
                    "Opção inválida. Tente novamente usando o número, a inicial ou o nome.",
                    justify="center",
                ),
                border_style="red",
            )
        )


def desenhar_tela_escolha_dificuldade(perfis: Sequence[DificuldadePerfil], selecionada: str) -> str:
    """Exibe cartas de dificuldade e retorna a chave escolhida."""

    def _normalizar(texto: str) -> str:
        slug = unicodedata.normalize("NFKD", texto)
        return "".join(ch for ch in slug if not unicodedata.combining(ch)).lower()

    def _formatar_percentual(multiplicador: float) -> str:
        variacao = round((multiplicador - 1) * 100)
        sinal = "+" if variacao >= 0 else ""
        return f"{sinal}{variacao}%"

    limpar_tela()
    console.print(
        Panel(
            Text(
                "Escolha o modo de dificuldade que melhor combina com a sua aventura",
                justify="center",
                style="bold yellow",
            ),
            border_style="blue",
            box=box.DOUBLE,
        )
    )

    mapa_escolha: dict[str, str] = {}
    cartoes: list[Panel] = []
    selecionada_norm = _normalizar(selecionada)

    for indice, perfil in enumerate(perfis, start=1):
        slug = perfil.chave
        atual = _normalizar(slug) == selecionada_norm
        titulo = f"{indice}. {perfil.nome}"
        corpo = Text(justify="left")
        corpo.append(f"{perfil.descricao}\n\n", style="white")
        corpo.append(
            f"👹 Inimigos: HP {_formatar_percentual(perfil.inimigo_hp_mult)} | "
            f"ATK {_formatar_percentual(perfil.inimigo_ataque_mult)} | "
            f"DEF {_formatar_percentual(perfil.inimigo_defesa_mult)}\n",
            style="yellow",
        )
        corpo.append(
            f"⭐ XP ganhos: {_formatar_percentual(perfil.xp_recompensa_mult)}\n",
            style="green",
        )
        corpo.append(
            f"💰 Saques/Eventos: {_formatar_percentual(perfil.saque_moedas_mult)}\n",
            style="bright_yellow",
        )
        corpo.append(
            f"⚔️ Encontros: {_formatar_percentual(perfil.prob_inimigo_mult)}\n",
            style="magenta",
        )
        if perfil.drop_consumivel_bonus:
            corpo.append(
                f"🧪 Consumíveis: {_formatar_percentual(1 + perfil.drop_consumivel_bonus)}\n",
                style="cyan",
            )

        subtitle = f"{slug.title()} {'(Atual)' if atual else ''}"
        cartoes.append(
            Panel(
                corpo,
                title=titulo,
                subtitle=subtitle,
                border_style="green" if atual else "blue",
                padding=(1, 2),
            )
        )

        chaves_norm = {
            str(indice),
            slug,
            slug[0],
            _normalizar(perfil.nome),
            _normalizar(slug),
        }
        for chave in chaves_norm:
            mapa_escolha[chave] = slug

    console.print(Columns(cartoes, equal=True, expand=True))
    console.print(
        Panel(
            Text(
                ("Digite o número, a inicial, o nome ou pressione Enter para manter a atual."),
                justify="center",
                style="bold white",
            ),
            border_style="blue",
            width=85,
        )
    )

    while True:
        resposta = console.input("[bold yellow]Escolha a dificuldade: [/] ").strip()
        if not resposta and selecionada:
            return selecionada
        chave_normalizada = _normalizar(resposta)
        if chave_normalizada in mapa_escolha:
            return mapa_escolha[chave_normalizada]
        if resposta.lower() in mapa_escolha:
            return mapa_escolha[resposta.lower()]
        console.print(
            Panel(
                Text(
                    (
                        "Opção inválida. Digite o número, a inicial, o nome ou "
                        "deixe em branco para manter."
                    ),
                    justify="center",
                ),
                border_style="red",
            )
        )


def desenhar_tela_resumo_personagem(jogador: Personagem) -> None:
    """Desenha a tela de resumo do personagem após a criação."""
    limpar_tela()
    resumo_texto = Text("", justify="left")
    resumo_texto.append(f"Nome: {jogador.nome}\n", style="bold green")
    resumo_texto.append(f"Classe: {jogador.classe}\n", style="bold yellow")
    resumo_texto.append(f"HP: {jogador.hp_max}\n", style="red")
    resumo_texto.append(f"Ataque: {jogador.ataque}\n", style="cyan")
    resumo_texto.append(f"Defesa: {jogador.defesa}\n", style="blue")
    resumo_texto.append(f"Nível: {jogador.nivel}\n", style="magenta")
    resumo_texto.append(f"Carteira: {jogador.carteira.formatar()}\n", style="bold yellow")
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
    tabela_inventario.add_column("Efeito/Bônus", style="white", width=25)

    if not jogador.inventario:
        console.print(
            Panel(
                Text("Seu inventário está vazio.", justify="center"),
                width=75,
                border_style="blue",
            )
        )
    else:
        for i, item in enumerate(jogador.inventario):
            efeitos = item.efeito or item.bonus
            efeito_str = ", ".join(f"{k}: {v}" for k, v in efeitos.items()) if efeitos else "-"
            tabela_inventario.add_row(str(i + 1), item.nome, item.tipo, efeito_str)
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
    jogador: Personagem, inimigo: Inimigo, mensagem: list[str] | None = None
) -> str:
    """Desenha a tela de combate com informações do jogador, inimigo e mensagens."""
    mensagem = mensagem or []
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

    log_combate_texto = "\n".join(mensagem)
    log_combate = Text(log_combate_texto, style="white")

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
