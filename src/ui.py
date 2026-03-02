import json
import unicodedata
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rich import box
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.armazenamento import limpar_historico
from src.config import DificuldadePerfil
from src.economia import formatar_preco
from src.entidades import Item, Personagem
from src.ui_base import (
    CLASSE_CORES,
    CLASSE_EMOJIS,
    ClassesConfig,
    console,
    desenhar_caixa,
    limpar_tela,
)
from src.ui_combate import desenhar_log_completo, desenhar_tela_combate
from src.ui_eventos import (
    desenhar_evento_interativo,
    desenhar_tela_evento,
    desenhar_tela_pre_chefe,
    desenhar_tela_saida,
    tela_game_over,
)
from src.ui_hud import _render_minimapa, desenhar_hud_exploracao
from src.ui_menu import desenhar_menu_principal, desenhar_tela_input

if TYPE_CHECKING:
    pass


__all__ = [
    "CLASSE_CORES",
    "CLASSE_EMOJIS",
    "ClassesConfig",
    "_render_minimapa",
    "console",
    "desenhar_caixa",
    "desenhar_evento_interativo",
    "desenhar_historico",
    "desenhar_hud_exploracao",
    "desenhar_log_completo",
    "desenhar_menu_principal",
    "desenhar_selecao_save",
    "desenhar_tela_combate",
    "desenhar_tela_equipar",
    "desenhar_tela_escolha_classe",
    "desenhar_tela_escolha_dificuldade",
    "desenhar_tela_evento",
    "desenhar_tela_ficha_personagem",
    "desenhar_tela_input",
    "desenhar_tela_inventario",
    "desenhar_tela_pre_chefe",
    "desenhar_tela_resumo_andar",
    "desenhar_tela_resumo_personagem",
    "desenhar_tela_saida",
    "limpar_tela",
    "tela_game_over",
]


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
    armadura_equipada = jogador.equipamento.get("armadura")
    escudo_equipado = jogador.equipamento.get("escudo")

    tabela_equipamento.add_row(
        "Arma:",
        arma_equipada.nome if arma_equipada else "Nenhuma",
        ", ".join([f"{k}: {v}" for k, v in arma_equipada.bonus.items()]) if arma_equipada else "",
    )
    tabela_equipamento.add_row(
        "Armadura:",
        armadura_equipada.nome if armadura_equipada else "Nenhuma",
        ", ".join([f"{k}: {v}" for k, v in armadura_equipada.bonus.items()])
        if armadura_equipada
        else "",
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
    tabela.add_column("Marca da trama", style="white")

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
            _cut(entrada.get("trama_consequencia", "-"), 26),
        )

    if not historico:
        tabela.add_row("—", "Nenhuma run registrada", "", "", "", "", "", "", "", "")

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
    armadura = jogador.equipamento.get("armadura")
    escudo = jogador.equipamento.get("escudo")

    def _bonus_str(item: Item | None) -> str:
        if not item:
            return "-"
        dados = item.bonus or {}
        return ", ".join(f"{k}: {v}" for k, v in dados.items()) or "-"

    equip.add_row("Arma", arma.nome if arma else "Nenhuma", _bonus_str(arma))
    equip.add_row("Armadura", armadura.nome if armadura else "Nenhuma", _bonus_str(armadura))
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
