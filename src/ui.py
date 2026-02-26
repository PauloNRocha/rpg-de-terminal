import json
import random
import unicodedata
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rich import box
from rich.bar import Bar
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src import config
from src.armazenamento import limpar_historico
from src.config import DificuldadePerfil
from src.economia import formatar_preco
from src.entidades import Inimigo, Item, Personagem, Sala

if TYPE_CHECKING:
    from src.eventos import Evento

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


def _limitar_log(mensagens: list[str], limite: int = 10) -> list[str]:
    """Retorna apenas as últimas entradas, com cabeçalho de truncamento se necessário."""
    if len(mensagens) <= limite:
        return mensagens
    ocultos = len(mensagens) - limite
    return [f"(… +{ocultos} eventos anteriores)", *mensagens[-limite:]]


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

    # Layout em colunas quando minimapa ativo
    if config.MINIMAPA_ATIVO and mapa is not None:
        minimapa = _render_minimapa(mapa, jogador)
        console.print(Columns([hud_jogador, minimapa], expand=False, equal=False, padding=(0, 1)))
    else:
        console.print(hud_jogador)

    console.print(hud_sala)
    console.print(hud_opcoes)

    return console.input("[bold yellow]> [/]")


def desenhar_tela_evento(titulo: str, mensagem: str) -> None:
    """Desenha uma tela de evento com título e mensagem."""
    limpar_tela()
    desenhar_caixa(titulo, mensagem)
    console.input("[bold yellow]Pressione Enter para continuar... [/]")


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


def desenhar_evento_interativo(evento: "Evento") -> dict[str, Any] | None:
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


def desenhar_selecao_save(
    saves: list[dict[str, str | int]],
    titulo: str,
    pode_criar_novo: bool = False,
    sugestao_novo: int | None = None,
) -> str | None:
    """Mostra tabela de saves e retorna o slot escolhido (str) ou None se cancelar."""
    limpar_tela()
    tabela = Table(title=titulo, box=box.SIMPLE, border_style="cyan")
    tabela.add_column("Opção", justify="center", style="bold yellow", width=6)
    tabela.add_column("Slot", justify="center", style="white")
    tabela.add_column("Personagem", style="bold white")
    tabela.add_column("Classe", style="white")
    tabela.add_column("Nível", justify="right", style="white")
    tabela.add_column("Andar", justify="right", style="white")
    tabela.add_column("Dificuldade", style="white")
    tabela.add_column("Salvo em", style="dim white")
    tabela.add_column("Versão", style="dim white")

    for idx, save in enumerate(saves, start=1):
        tabela.add_row(
            str(idx),
            str(save.get("slot_id")),
            str(save.get("personagem")),
            str(save.get("classe")),
            str(save.get("nivel")),
            str(save.get("andar")),
            str(save.get("dificuldade")),
            str(save.get("salvo_em")),
            str(save.get("versao")),
        )

    console.print(tabela)

    opcoes_extra = []
    if pode_criar_novo and sugestao_novo is not None:
        opcoes_extra.append(f"N. Criar novo slot (sugestão: {sugestao_novo})")
    opcoes_extra.append("C. Cancelar")
    console.print(Panel("\n".join(opcoes_extra), border_style="blue", width=75))

    escolha = console.input("[bold yellow]Escolha (número/N/C): [/]").strip().lower()
    if escolha == "c":
        return None
    if escolha == "n" and pode_criar_novo and sugestao_novo is not None:
        return str(sugestao_novo)
    try:
        idx = int(escolha)
    except ValueError:
        return None
    if 1 <= idx <= len(saves):
        return str(saves[idx - 1].get("slot_id"))
    if not saves and sugestao_novo is not None and idx == sugestao_novo:
        return str(sugestao_novo)
    return None


def desenhar_historico(limite: int = 20) -> None:
    """Mostra histórico de runs gravado em saves/history.json."""
    limpar_tela()
    historico = []
    caminho_hist = Path("saves/history.json")
    if caminho_hist.exists():
        try:
            historico = json.loads(caminho_hist.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            historico = []

    tabela = Table(box=box.SIMPLE, border_style="cyan", expand=True)
    tabela.add_column("Data/Hora", style="dim white")
    tabela.add_column("Personagem", style="bold white")
    tabela.add_column("Classe", style="white")
    tabela.add_column("Motivo", style="white")
    tabela.add_column("Andar", justify="right", style="yellow")
    tabela.add_column("Dificuldade", style="white")
    tabela.add_column("Inimigos", justify="right", style="white")
    tabela.add_column("Itens", justify="right", style="white")
    tabela.add_column("Chefe + profundo", style="white")

    historico = (historico or [])[-limite:]
    historico = list(reversed(historico))  # mais recente primeiro

    def _cut(txt: object, limite: int = 18) -> str:
        s = str(txt)
        return s if len(s) <= limite else s[: limite - 1] + "…"

    for entrada in historico:
        chefe_info = ""
        if entrada.get("chefe_mais_profundo_nivel"):
            chefe_info = (
                f"A{entrada.get('chefe_mais_profundo_nivel')} "
                f"- {entrada.get('chefe_mais_profundo_nome', '')}"
            )
        tabela.add_row(
            _cut(entrada.get("timestamp_local", "?"), 19),
            _cut(entrada.get("personagem", "?")),
            _cut(entrada.get("classe", "?")),
            _cut(entrada.get("motivo", "?")),
            str(entrada.get("andar_alcancado", "?")),
            _cut(entrada.get("dificuldade", "?"), 14),
            str(entrada.get("inimigos_derrotados", 0)),
            str(entrada.get("itens_obtidos", 0)),
            chefe_info,
        )

    if not historico:
        tabela.add_row("—", "Nenhuma run registrada", "", "", "", "", "", "")

    console.print(Panel(tabela, title="Histórico de Aventuras", border_style="blue"))
    console.print(
        Panel(
            "Enter: voltar | L: limpar histórico",
            border_style="magenta",
            width=40,
        )
    )
    escolha = console.input("[bold yellow](Enter/L): [/]").strip().lower()
    if escolha == "l":
        limpar_historico()
        console.print("[bold green]Histórico apagado.[/]")
        console.input("[bold yellow]Pressione Enter para voltar... [/]")


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

    blocos: list[Panel] = []
    blocos.append(
        Panel(
            resumo_texto,
            title=Text("SEU PERSONAGEM", justify="center", style="bold white"),
            width=75,
            box=box.DOUBLE,
            border_style="green",
        )
    )

    if jogador.motivacao:
        texto_mot = Text()
        texto_mot.append(f"{jogador.motivacao.titulo}\n", style="bold yellow")
        texto_mot.append(jogador.motivacao.descricao, style="italic white")
        blocos.append(
            Panel(
                texto_mot,
                title=Text("MOTIVAÇÃO", style="bold cyan"),
                border_style="cyan",
                width=75,
            )
        )

    for bloco in blocos:
        console.print(bloco)

    console.input("[bold yellow]Pressione Enter para iniciar a aventura... [/]")


def desenhar_tela_ficha_personagem(jogador: Personagem) -> None:
    """Exibe uma ficha completa do personagem durante a aventura."""
    limpar_tela()
    status = Table.grid(padding=(0, 1))
    status.add_column(justify="left")
    status.add_column(justify="right")
    status.add_row("👤 Nome", Text(jogador.nome, style="bold green"))
    status.add_row("🏹 Classe", Text(jogador.classe, style="cyan"))
    status.add_row("🌟 Nível", Text(str(jogador.nivel), style="yellow"))
    status.add_row(
        "⭐ XP",
        Text(f"{jogador.xp_atual}/{jogador.xp_para_proximo_nivel}", style="bright_white"),
    )
    status.add_row("❤️ HP", Text(f"{jogador.hp}/{jogador.hp_max}", style="bold red"))
    status.add_row("⚔️ Ataque Total", Text(str(jogador.ataque), style="magenta"))
    status.add_row("🛡️ Defesa Total", Text(str(jogador.defesa), style="magenta"))
    status.add_row("💰 Bolsa", Text(jogador.carteira.formatar(), style="bold yellow"))

    panel_status = Panel(status, title="Status", border_style="blue")

    atributos = Table.grid(padding=0)
    atributos.add_column(justify="left")
    atributos.add_column(justify="right")
    atributos.add_row("Ataque Base", Text(str(jogador.ataque_base)))
    atributos.add_row("Defesa Base", Text(str(jogador.defesa_base)))
    atributos.add_row("Posição", Text(f"({jogador.x}, {jogador.y})", style="dim"))

    equip = Table(
        title="Equipamento",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=True,
    )
    equip.add_column("Slot", justify="left", width=10)
    equip.add_column("Item", justify="left")
    equip.add_column("Bônus", justify="left", width=20)
    arma = jogador.equipamento.get("arma")
    escudo = jogador.equipamento.get("escudo")

    def _bonus_str(item: Item | None) -> str:
        if not item:
            return "-"
        dados = item.bonus or {}
        return ", ".join(f"{k}: {v}" for k, v in dados.items()) or "-"

    equip.add_row("Arma", arma.nome if arma else "Nenhuma", _bonus_str(arma))
    equip.add_row("Escudo", escudo.nome if escudo else "Nenhum", _bonus_str(escudo))

    painel_atributos = Panel(atributos, title="Atributos Base", border_style="green")
    painel_equip = Panel(equip, border_style="green")

    if jogador.motivacao:
        painel_motivacao = Panel(
            Text(
                f"{jogador.motivacao.titulo}\n\n{jogador.motivacao.descricao}",
                style="white",
                justify="left",
            ),
            title="🎯 Motivação",
            border_style="cyan",
            width=80,
        )
        console.print(Columns([panel_status, painel_equip], expand=True))
        console.print(painel_atributos)
        console.print(painel_motivacao)
    else:
        console.print(Columns([panel_status, painel_equip], expand=True))
        console.print(painel_atributos)

    console.input("[bold yellow]Pressione Enter para retornar... [/]")


def desenhar_tela_resumo_andar(
    nivel: int, estatisticas: dict[str, int], hp_recuperado: int
) -> None:
    """Mostra um painel com o resumo do andar após descer a escadaria."""
    limpar_tela()
    tabela = Table(box=box.DOUBLE, border_style="blue", width=75)
    tabela.add_column("Estatística", style="bold cyan")
    tabela.add_column("Valor", style="bold white", justify="right")
    tabela.add_row("Inimigos derrotados", str(estatisticas.get("inimigos_derrotados", 0)))
    tabela.add_row("Itens obtidos", str(estatisticas.get("itens_obtidos", 0)))
    tabela.add_row(
        "Moedas coletadas",
        formatar_preco(estatisticas.get("moedas_ganhas", 0)),
    )
    tabela.add_row("Eventos ativados", str(estatisticas.get("eventos_disparados", 0)))
    tabela.add_row("HP recuperado", f"+{hp_recuperado}")

    painel = Panel(
        tabela,
        title=Text(
            f"Resumo do Andar {nivel}",
            justify="center",
            style="bold yellow",
        ),
        subtitle="Prepare-se para o próximo desafio!",
        border_style="blue",
        width=80,
    )
    console.print(painel)
    console.input("[bold yellow]Pressione Enter para continuar... [/]")


def desenhar_tela_inventario(jogador: Personagem) -> str:
    """Desenha a tela de inventário do jogador."""
    limpar_tela()

    def _chave_item(item: Item) -> tuple:
        bonus = tuple(sorted((item.bonus or {}).items()))
        efeito = tuple(sorted((item.efeito or {}).items()))
        return (item.nome, item.tipo, bonus, efeito)

    def _agrupar_itens(itens: list[Item]) -> list[dict[str, Any]]:
        grupos: dict[tuple, dict[str, Any]] = {}
        for item in itens:
            chave = _chave_item(item)
            if chave not in grupos:
                grupos[chave] = {"item": item, "quantidade": 0}
            grupos[chave]["quantidade"] += 1
        return sorted(grupos.values(), key=lambda g: (g["item"].tipo, g["item"].nome))

    grupos_itens = _agrupar_itens(jogador.inventario)

    tabela_inventario = Table(
        title=Text("INVENTÁRIO", style="bold yellow"),
        box=box.DOUBLE,
        border_style="blue",
        header_style="bold cyan",
    )
    tabela_inventario.add_column("Opção", style="dim", width=5)
    tabela_inventario.add_column("Item", style="green", width=25)
    tabela_inventario.add_column("Tipo", style="magenta", width=10)
    tabela_inventario.add_column("Qtd", style="yellow", width=6)
    tabela_inventario.add_column("Efeito/Bônus", style="white", width=25)

    if not grupos_itens:
        console.print(
            Panel(
                Text("Seu inventário está vazio.", justify="center"),
                width=75,
                border_style="blue",
            )
        )
    else:
        for i, grupo in enumerate(grupos_itens):
            item = grupo["item"]
            qtd = grupo["quantidade"]
            efeitos = item.efeito or item.bonus
            efeito_str = ", ".join(f"{k}: {v}" for k, v in efeitos.items()) if efeitos else "-"
            tabela_inventario.add_row(
                str(i + 1),
                item.nome,
                item.tipo,
                f"x{qtd}",
                efeito_str,
            )
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
    display_log = _limitar_log(mensagem)
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

    log_combate_texto = "\n".join(display_log)
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
