import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from src import config, eventos
from src.armazenamento import (
    ErroCarregamento,
    SaveInfo,
    carregar_jogo,
    listar_saves,
    proximo_slot_disponivel,
    salvar_jogo,
)
from src.atualizador import AtualizacaoInfo, verificar_atualizacao
from src.chefes import obter_chefe_por_id
from src.combate import iniciar_combate
from src.entidades import Inimigo, Item, Personagem, Sala
from src.erros import ErroDadosError
from src.estados import (
    agrupar_itens_equipaveis as agrupar_itens_equipaveis_estado,
)
from src.estados import (
    aplicar_efeitos_consumiveis as aplicar_efeitos_consumiveis_estado,
)
from src.estados import (
    equipar_item as equipar_item_estado,
)
from src.estados import (
    executar_estado_combate as executar_estado_combate_mod,
)
from src.estados import (
    gerenciar_inventario as gerenciar_inventario_estado,
)
from src.estados import (
    remover_item_por_chave as remover_item_por_chave_estado,
)
from src.estados import (
    usar_item as usar_item_estado,
)
from src.gerador_inimigos import gerar_inimigo
from src.gerador_itens import gerar_item_aleatorio, obter_item_por_nome
from src.gerador_mapa import gerar_mapa
from src.personagem import criar_personagem, obter_classes
from src.personagem_utils import aplicar_bonus_equipamento, consumir_status_temporarios
from src.ui import (
    desenhar_evento_interativo,
    desenhar_hud_exploracao,
    desenhar_menu_principal,
    desenhar_selecao_save,
    desenhar_tela_escolha_classe,
    desenhar_tela_escolha_dificuldade,
    desenhar_tela_evento,
    desenhar_tela_ficha_personagem,
    desenhar_tela_input,
    desenhar_tela_pre_chefe,
    desenhar_tela_resumo_andar,
    desenhar_tela_resumo_personagem,
    desenhar_tela_saida,
    tela_game_over,
)
from src.ui_resumo import desenhar_tela_resumo_final
from src.version import __version__

Mapa = list[list[Sala]]
EffectHandler = Callable[[Personagem, int], str]

# Retrocompatibilidade para os testes que importam direto de jogo.py
agrupar_itens_equipaveis = agrupar_itens_equipaveis_estado
remover_item_por_chave = remover_item_por_chave_estado


class Estado(Enum):
    """Estados principais do loop do jogo."""

    MENU = auto()
    CRIACAO = auto()
    EXPLORACAO = auto()
    INVENTARIO = auto()
    COMBATE = auto()
    SAIR = auto()


def _nova_estatistica_andar() -> dict[str, int]:
    """Cria uma estrutura vazia de estatísticas por andar."""
    return {
        "inimigos_derrotados": 0,
        "itens_obtidos": 0,
        "moedas_ganhas": 0,
        "eventos_disparados": 0,
    }


def _nova_estatistica_total() -> dict[str, int]:
    """Cria uma estrutura de estatísticas acumuladas da run."""
    stats = _nova_estatistica_andar()
    stats["andares_concluidos"] = 0
    return stats


@dataclass
class ContextoJogo:
    """Armazena o estado corrente entre as transições."""

    jogador: Personagem | None = None
    mapa_atual: Mapa | None = None
    nivel_masmorra: int = 1
    sala_em_combate: Sala | None = None
    inimigo_em_combate: Inimigo | None = None
    posicao_anterior: tuple[int, int] | None = None
    slot_atual: str | None = None
    atualizacao_notificada: bool = False
    info_atualizacao: AtualizacaoInfo | None = None
    alerta_atualizacao_exibido: bool = False
    dificuldade: str = config.DIFICULDADE_PADRAO
    estatisticas_andar: dict[str, int] = field(default_factory=_nova_estatistica_andar)
    estatisticas_total: dict[str, int] = field(default_factory=_nova_estatistica_total)

    def limpar_combate(self) -> None:
        """Remove referências ao combate atual."""
        self.sala_em_combate = None
        self.inimigo_em_combate = None

    def restaurar_posicao_anterior(self) -> None:
        """Reposiciona o jogador caso uma fuga tenha ocorrido."""
        if self.posicao_anterior and self.jogador:
            self.jogador.x, self.jogador.y = self.posicao_anterior
        self.posicao_anterior = None

    def resetar_jogo(self) -> None:
        """Retorna o contexto ao estado inicial do jogo."""
        self.jogador = None
        self.mapa_atual = None
        self.nivel_masmorra = 1
        self.posicao_anterior = None
        self.info_atualizacao = None
        self.alerta_atualizacao_exibido = False
        self.limpar_combate()
        self.resetar_estatisticas()

    def obter_perfil_dificuldade(self) -> config.DificuldadePerfil:
        """Retorna a configuração completa da dificuldade atual."""
        return config.DIFICULDADES.get(
            self.dificuldade, config.DIFICULDADES[config.DIFICULDADE_PADRAO]
        )

    def definir_dificuldade(self, chave: str | None) -> None:
        """Atualiza a dificuldade respeitando o catálogo disponível."""
        if not chave:
            self.dificuldade = config.DIFICULDADE_PADRAO
            return
        chave_normalizada = chave.lower()
        if chave_normalizada not in config.DIFICULDADES:
            chave_normalizada = config.DIFICULDADE_PADRAO
        self.dificuldade = chave_normalizada

    def resetar_estatisticas(self) -> None:
        """Limpa as estatísticas acumuladas do andar atual."""
        self.estatisticas_andar = _nova_estatistica_andar()

    def registrar_inimigo_derrotado(self) -> None:
        """Incrementa o contador de inimigos derrotados no andar atual."""
        self.estatisticas_andar["inimigos_derrotados"] += 1
        self.estatisticas_total["inimigos_derrotados"] += 1

    def registrar_item_obtido(self, quantidade: int = 1) -> None:
        """Soma itens coletados (drops, recompensas) ao resumo do andar."""
        ganho = max(0, quantidade)
        self.estatisticas_andar["itens_obtidos"] += ganho
        self.estatisticas_total["itens_obtidos"] += ganho

    def registrar_moedas(self, valor: int) -> None:
        """Acumula moedas obtidas durante o andar."""
        if valor > 0:
            self.estatisticas_andar["moedas_ganhas"] += valor
            self.estatisticas_total["moedas_ganhas"] += valor

    def registrar_evento(self) -> None:
        """Marca que um evento de sala foi disparado no andar atual."""
        self.estatisticas_andar["eventos_disparados"] += 1
        self.estatisticas_total["eventos_disparados"] += 1

    def registrar_andar_concluido(self) -> None:
        """Conta que um andar foi concluído (usado no resumo final)."""
        self.estatisticas_total["andares_concluidos"] += 1

    def _estatisticas_run(self) -> dict[str, int]:
        """Combina totais com progresso parcial do andar atual."""
        combinadas = self.estatisticas_total.copy()
        for chave, valor in self.estatisticas_andar.items():
            combinadas[chave] = combinadas.get(chave, 0) + valor
        return combinadas

    def exibir_resumo_final(self, motivo: str) -> None:
        """Mostra o painel de resumo da run antes de resetar."""
        stats = self._estatisticas_run()
        desenhar_tela_resumo_final(
            motivo=motivo,
            jogador=self.jogador,
            nivel_atual=self.nivel_masmorra,
            estatisticas=stats,
        )


def selecionar_dificuldade(contexto: ContextoJogo) -> None:
    """Mostra a tela de dificuldade e aplica a escolha ao contexto."""
    perfis = [
        config.DIFICULDADES[chave]
        for chave in config.DIFICULDADE_ORDEM
        if chave in config.DIFICULDADES
    ]
    escolha = desenhar_tela_escolha_dificuldade(perfis, contexto.dificuldade)
    contexto.definir_dificuldade(escolha)
    perfil = contexto.obter_perfil_dificuldade()
    desenhar_tela_evento(
        "DIFICULDADE DEFINIDA",
        f"Você jogará no modo {perfil.nome}.\n\n{perfil.descricao}",
    )


def _posicionar_na_entrada(jogador: Personagem, mapa: Mapa) -> None:
    """Posiciona o jogador na entrada (usado ao gerar um mapa novo)."""
    for y_idx, linha in enumerate(mapa):
        for x_idx, sala in enumerate(linha):
            if sala.tipo == "entrada":
                jogador.x, jogador.y = x_idx, y_idx
                return


def _salvar_slot_contexto(contexto: ContextoJogo, slot: str | None) -> None:
    """Guarda o slot selecionado no contexto."""
    contexto.slot_atual = slot


def _formatar_saves_para_ui(saves: list[SaveInfo]) -> list[dict[str, str | int]]:
    """Converta SaveInfo em dicts simples para exibição na UI."""
    return [
        {
            "slot_id": save.slot_id,
            "personagem": save.personagem,
            "classe": save.classe,
            "nivel": save.nivel,
            "andar": save.andar,
            "dificuldade": save.dificuldade,
            "salvo_em": save.salvo_em,
            "versao": save.versao,
        }
        for save in saves
    ]


def _selecionar_slot(novo_jogo: bool, saves: list[SaveInfo]) -> str | None:
    """Abre a UI de seleção de slot para novo jogo ou carregar existente."""
    saves_ui = _formatar_saves_para_ui(saves)
    if novo_jogo:
        sugestao = proximo_slot_disponivel()
        return desenhar_selecao_save(
            saves_ui,
            "Selecione um slot para salvar a nova aventura",
            pode_criar_novo=True,
            sugestao_novo=sugestao,
        )
    if not saves:
        return None
    return desenhar_selecao_save(
        saves_ui,
        "Selecione um save para continuar",
        pode_criar_novo=False,
    )


def executar_estado_menu(contexto: ContextoJogo) -> Estado:
    """Renderiza o menu e decide o próximo estado."""
    if not contexto.atualizacao_notificada:
        info = verificar_atualizacao()
        if info:
            contexto.info_atualizacao = info
            contexto.atualizacao_notificada = True
            if not contexto.alerta_atualizacao_exibido:
                _mostrar_aviso_atualizacao(info)
                contexto.alerta_atualizacao_exibido = True
    saves_disponiveis = listar_saves()
    tem_save = bool(saves_disponiveis)
    alerta = None
    if contexto.info_atualizacao:
        alerta = (
            f"Nova versão disponível: v{contexto.info_atualizacao.versao_disponivel} "
            f"(atual v{__version__}). Escolha '0' para saber como atualizar."
        )
    escolha = desenhar_menu_principal(
        __version__,
        tem_save,
        contexto.obter_perfil_dificuldade().nome,
        alerta_atualizacao=alerta,
    )
    escolha = escolha.strip()
    if escolha == "0":
        info_manual = verificar_atualizacao(forcar=True)
        if info_manual:
            contexto.info_atualizacao = info_manual
            contexto.atualizacao_notificada = True
            _mostrar_aviso_atualizacao(info_manual)
            contexto.alerta_atualizacao_exibido = True
        else:
            contexto.info_atualizacao = None
            contexto.alerta_atualizacao_exibido = False
            desenhar_tela_evento(
                "ATUALIZAÇÕES",
                "Você já está na versão mais recente disponível.",
            )
        return Estado.MENU
    if escolha == "1":
        slot_escolhido = _selecionar_slot(True, saves_disponiveis)
        if not slot_escolhido:
            return Estado.MENU
        _salvar_slot_contexto(contexto, slot_escolhido)
        return Estado.CRIACAO
    if escolha == "2" and tem_save:
        slot_escolhido = _selecionar_slot(False, saves_disponiveis)
        if not slot_escolhido:
            return Estado.MENU
        try:
            estado_salvo = carregar_jogo(slot_escolhido)
            jogador_data = estado_salvo.get("jogador")
            mapa_salvo = estado_salvo.get("mapa")
            nivel_masmorra = estado_salvo.get("nivel_masmorra")
            if not all([jogador_data, mapa_salvo, isinstance(nivel_masmorra, int)]):
                raise ErroCarregamento("Arquivo de save inválido ou corrompido.")
            contexto.definir_dificuldade(estado_salvo.get("dificuldade", config.DIFICULDADE_PADRAO))
            contexto.jogador = Personagem.from_dict(jogador_data)
            contexto.mapa_atual = hidratar_mapa(mapa_salvo)
            contexto.nivel_masmorra = nivel_masmorra
            contexto.posicao_anterior = None
            _salvar_slot_contexto(contexto, slot_escolhido)
            desenhar_tela_evento("JOGO CARREGADO", "Seu progresso foi restaurado!")
            return Estado.EXPLORACAO
        except ErroCarregamento as erro:
            desenhar_tela_evento("ERRO AO CARREGAR", str(erro))
        return Estado.MENU
    if (tem_save and escolha == "3") or (not tem_save and escolha == "2"):
        return Estado.SAIR

    desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")
    return Estado.MENU


def executar_estado_criacao(contexto: ContextoJogo) -> Estado:
    """Cria um personagem novo e segue para exploração."""
    selecionar_dificuldade(contexto)
    jogador = processo_criacao_personagem()
    contexto.jogador = jogador
    contexto.nivel_masmorra = 1
    contexto.mapa_atual = None
    contexto.posicao_anterior = None
    return Estado.EXPLORACAO


def executar_estado_exploracao(contexto: ContextoJogo) -> Estado:
    """Executa um ciclo de exploração e retorna o próximo estado."""
    jogador = contexto.jogador
    if jogador is None:
        return Estado.MENU

    if contexto.mapa_atual is None:
        contexto.resetar_estatisticas()
        contexto.mapa_atual = gerar_mapa(
            contexto.nivel_masmorra, contexto.obter_perfil_dificuldade()
        )
        _posicionar_na_entrada(jogador, contexto.mapa_atual)

    mapa = contexto.mapa_atual
    sala_atual = mapa[jogador.y][jogador.x]

    if sala_atual.evento_id and not sala_atual.evento_resolvido:
        perfil = contexto.obter_perfil_dificuldade()
        contexto.registrar_evento()
        moedas_antes = jogador.carteira.valor_bronze
        evento = eventos.carregar_eventos().get(sala_atual.evento_id)
        if evento and evento.opcoes:
            escolha = desenhar_evento_interativo(evento)
            if escolha is None:
                return Estado.EXPLORACAO
            op_efeitos = escolha.get("efeitos", {})
            msgs, _ = eventos.aplicar_efeitos(op_efeitos, jogador, perfil.saque_moedas_mult)
            corpo = [evento.descricao, *msgs]
            desenhar_tela_evento(evento.nome.upper(), "\n".join(corpo))
        else:
            titulo, mensagem = eventos.disparar_evento(
                sala_atual.evento_id, jogador, perfil.saque_moedas_mult
            )
            desenhar_tela_evento(titulo, mensagem)
        ganho_moedas = jogador.carteira.valor_bronze - moedas_antes
        contexto.registrar_moedas(max(0, ganho_moedas))
        sala_atual.evento_resolvido = True
        if jogador.hp <= 0:
            tela_game_over()
            contexto.resetar_jogo()
            return Estado.MENU

    if sala_atual.pode_ter_inimigo and not sala_atual.inimigo_derrotado:
        inimigo = sala_atual.inimigo_atual
        if inimigo is None:
            perfil_dificuldade = contexto.obter_perfil_dificuldade()
            perfil_chefe = obter_chefe_por_id(sala_atual.chefe_id)
            tipo = None
            if sala_atual.chefe:
                if perfil_chefe:
                    tipo = perfil_chefe.tipo
                elif sala_atual.chefe_tipo:
                    tipo = sala_atual.chefe_tipo
            inimigo = gerar_inimigo(
                sala_atual.nivel_area,
                tipo_inimigo=tipo,
                dificuldade=perfil_dificuldade,
                chefe=sala_atual.chefe,
                perfil_chefe=perfil_chefe,
            )
            sala_atual.inimigo_atual = inimigo
        if sala_atual.chefe and not sala_atual.chefe_intro_exibida:
            chefe_config = obter_chefe_por_id(sala_atual.chefe_id)
            titulo_pre = sala_atual.nome
            historia_pre = sala_atual.descricao
            if chefe_config and contexto.jogador:
                classe = contexto.jogador.classe.lower()
                historias_cls = chefe_config.historias_por_classe or {}
                entrada = historias_cls.get(classe) or historias_cls.get("default", {})
                titulo_pre = entrada.get("titulo") or chefe_config.titulo or titulo_pre
                historia_pre = entrada.get("historia") or chefe_config.historia or historia_pre
            escolha_chefe = desenhar_tela_pre_chefe(titulo_pre, historia_pre)
            if escolha_chefe == "enfrentar":
                sala_atual.chefe_intro_exibida = True
            elif escolha_chefe == "inventario":
                return Estado.INVENTARIO
            else:  # recuar
                contexto.restaurar_posicao_anterior()
                sala_atual.inimigo_atual = None
                return Estado.EXPLORACAO
        contexto.sala_em_combate = sala_atual
        contexto.inimigo_em_combate = inimigo
        desenhar_tela_evento("ENCONTRO!", f"CUIDADO! Um {inimigo.nome} está na sala!")
        return Estado.COMBATE

    opcoes = []
    if jogador.y > 0 and mapa[jogador.y - 1][jogador.x].tipo != "parede":
        opcoes.append("Ir para o Norte")
    if jogador.y < len(mapa) - 1 and mapa[jogador.y + 1][jogador.x].tipo != "parede":
        opcoes.append("Ir para o Sul")
    if jogador.x < len(mapa[0]) - 1 and mapa[jogador.y][jogador.x + 1].tipo != "parede":
        opcoes.append("Ir para o Leste")
    if jogador.x > 0 and mapa[jogador.y][jogador.x - 1].tipo != "parede":
        opcoes.append("Ir para o Oeste")

    if sala_atual.tipo == "escada":
        chefe_derrotado = all(
            sala.inimigo_derrotado for linha in mapa for sala in linha if sala.tipo == "chefe"
        )
        if chefe_derrotado:
            opcoes.append("Descer para o próximo nível")
        else:
            desenhar_tela_evento(
                "AVISO",
                "A escada está bloqueada. Derrote o chefe para prosseguir.",
            )

    opcoes.extend(["Ver Ficha do Personagem", "Ver Inventário", "Salvar jogo", "Sair da masmorra"])
    escolha_str = desenhar_hud_exploracao(
        jogador,
        sala_atual,
        opcoes,
        contexto.nivel_masmorra,
        contexto.obter_perfil_dificuldade().nome,
    )

    try:
        escolha = int(escolha_str)
        if not (1 <= escolha <= len(opcoes)):
            raise ValueError
        acao_escolhida = opcoes[escolha - 1]
        posicao_atual = (jogador.x, jogador.y)

        if acao_escolhida == "Ir para o Norte":
            contexto.posicao_anterior = posicao_atual
            jogador.y -= 1
            return Estado.EXPLORACAO
        if acao_escolhida == "Ir para o Sul":
            contexto.posicao_anterior = posicao_atual
            jogador.y += 1
            return Estado.EXPLORACAO
        if acao_escolhida == "Ir para o Leste":
            contexto.posicao_anterior = posicao_atual
            jogador.x += 1
            return Estado.EXPLORACAO
        if acao_escolhida == "Ir para o Oeste":
            contexto.posicao_anterior = posicao_atual
            jogador.x -= 1
            return Estado.EXPLORACAO
        if acao_escolhida == "Descer para o próximo nível":
            nivel_atual = contexto.nivel_masmorra
            resumo = contexto.estatisticas_andar.copy()
            hp_cura = int(jogador.hp_max * config.DESCENT_HEAL_PERCENT)
            jogador.hp = min(jogador.hp_max, jogador.hp + hp_cura)
            desenhar_tela_resumo_andar(nivel_atual, resumo, hp_cura)
            contexto.registrar_andar_concluido()
            contexto.nivel_masmorra += 1
            contexto.mapa_atual = None
            contexto.posicao_anterior = None
            contexto.resetar_estatisticas()
            return Estado.EXPLORACAO
        if acao_escolhida == "Ver Ficha do Personagem":
            desenhar_tela_ficha_personagem(jogador)
            return Estado.EXPLORACAO
        if acao_escolhida == "Ver Inventário":
            return Estado.INVENTARIO
        if acao_escolhida == "Salvar jogo":
            estado = {
                "jogador": jogador.to_dict(),
                "mapa": serializar_mapa(mapa),
                "nivel_masmorra": contexto.nivel_masmorra,
                "dificuldade": contexto.dificuldade,
            }
            try:
                caminho = salvar_jogo(estado, contexto.slot_atual)
                desenhar_tela_evento("JOGO SALVO", f"Progresso salvo em {caminho}.")
            except OSError as erro:
                desenhar_tela_evento("ERRO AO SALVAR", f"Não foi possível salvar: {erro}.")
            return Estado.EXPLORACAO
        if acao_escolhida == "Sair da masmorra":
            contexto.exibir_resumo_final("saida")
            contexto.jogador = None
            contexto.mapa_atual = None
            contexto.nivel_masmorra = 1
            contexto.posicao_anterior = None
            return Estado.MENU
    except (ValueError, IndexError):
        desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")

    return Estado.EXPLORACAO


def executar_estado_inventario(contexto: ContextoJogo) -> Estado:
    """Executa o estado de inventário usando o módulo especializado."""
    jogador = contexto.jogador
    if jogador is None:
        return Estado.MENU

    gerenciar_inventario_estado(
        jogador,
        usar_item_fn=_usar_item_com_feedback,
        equipar_item_fn=_equipar_item_com_bonus,
    )
    return Estado.EXPLORACAO


def executar_estado_combate(contexto: ContextoJogo) -> Estado:
    """Repasse para o estado modular de combate."""
    return executar_estado_combate_mod(
        contexto,
        iniciar_combate,
        _usar_item_com_feedback,
        lambda raridade: _gerar_item_para_contexto(contexto, raridade),
        verificar_level_up,
        consumir_status_temporarios,
        Estado.MENU,
        Estado.EXPLORACAO,
    )


def _mostrar_aviso_atualizacao(
    info: AtualizacaoInfo, titulo: str = "ATUALIZAÇÃO DISPONÍVEL!"
) -> None:
    """Exibe um painel informando sobre uma nova versão do jogo."""
    mensagem = info.instrucoes + "\n\nVocê pode ajustar as preferências em settings.json."
    desenhar_tela_evento(titulo, mensagem)


def _efeito_hp(jogador: Personagem, valor: int) -> str:
    cura = max(0, int(valor))
    if cura <= 0:
        return "Nenhuma cura aplicada."
    hp_antes = jogador.hp
    jogador.hp = min(jogador.hp_max, jogador.hp + cura)
    ganho_real = jogador.hp - hp_antes
    return f"Você recuperou {ganho_real} de HP."


def _efeito_xp(jogador: Personagem, valor: int) -> str:
    ganho = max(0, int(valor))
    if ganho <= 0:
        return "Nenhuma experiência foi concedida."
    jogador.xp_atual += ganho
    return f"Você ganhou {ganho} de XP."


EFFECT_HANDLERS: dict[str, EffectHandler] = {
    "hp": _efeito_hp,
    "xp": _efeito_xp,
}


def aplicar_efeitos_consumiveis(jogador: Personagem, item: Item) -> list[str]:
    """Compatibiliza os testes reutilizando os handlers padrão do jogo."""
    return aplicar_efeitos_consumiveis_estado(jogador, item, EFFECT_HANDLERS)


def _usar_item_com_feedback(jogador: Personagem) -> bool | None:
    mensagens = usar_item_estado(jogador, EFFECT_HANDLERS)
    if mensagens:
        desenhar_tela_evento("ITEM USADO", "\n".join(mensagens))
        verificar_level_up(jogador)
        return True
    return mensagens


def _equipar_item_com_bonus(jogador: Personagem) -> None:
    equipar_item_estado(jogador)
    aplicar_bonus_equipamento(jogador)


def _gerar_item_para_contexto(contexto: ContextoJogo, raridade: str) -> Item | None:
    bonus = contexto.obter_perfil_dificuldade().drop_consumivel_bonus
    jogador = contexto.jogador
    # Drops guiados para andares iniciais: garantir 1 arma e 1 escudo cedo.
    if jogador and contexto.nivel_masmorra <= 2:
        possui_arma = bool(
            jogador.equipamento.get("arma")
            or any(item.tipo == "arma" for item in jogador.inventario)
        )
        possui_escudo = bool(
            jogador.equipamento.get("escudo")
            or any(item.tipo == "escudo" for item in jogador.inventario)
        )
        if not possui_arma:
            return obter_item_por_nome("Espada Afiada") or gerar_item_aleatorio(
                "comum", bonus_consumivel=bonus
            )
        if not possui_escudo:
            return obter_item_por_nome("Escudo de Madeira") or gerar_item_aleatorio(
                "comum", bonus_consumivel=bonus
            )

    return gerar_item_aleatorio(raridade, bonus_consumivel=bonus)


def serializar_mapa(mapa: Mapa) -> list[list[dict[str, Any]]]:
    """Converta o mapa em uma estrutura serializável."""
    mapa_serializado: list[list[dict[str, Any]]] = []
    for linha in mapa:
        nova_linha = [sala.to_dict() for sala in linha]
        mapa_serializado.append(nova_linha)
    return mapa_serializado


def hidratar_mapa(mapa_serializado: list[list[dict[str, Any]]]) -> Mapa:
    """Reconstrói as salas do mapa a partir dos dicionários serializados."""
    mapa_hidratado: Mapa = []
    for linha in mapa_serializado:
        nova_linha = [Sala.from_dict(sala) for sala in linha]
        mapa_hidratado.append(nova_linha)
    return mapa_hidratado


def verificar_level_up(jogador: Personagem) -> None:
    """Verifica se o jogador tem XP suficiente para subir de nível e aplica as mudanças."""
    subiu_de_nivel = False
    while jogador.xp_atual >= jogador.xp_para_proximo_nivel:
        subiu_de_nivel = True
        jogador.nivel += 1
        xp_excedente = jogador.xp_atual - jogador.xp_para_proximo_nivel
        jogador.xp_atual = xp_excedente
        jogador.xp_para_proximo_nivel = int(jogador.xp_para_proximo_nivel * 1.5)

        hp_ganho = config.LEVEL_UP_HP_GAIN
        ataque_ganho = config.LEVEL_UP_ATTACK_GAIN
        defesa_ganho = config.LEVEL_UP_DEFENSE_GAIN

        jogador.hp_max += hp_ganho
        jogador.hp = jogador.hp_max
        jogador.ataque_base += ataque_ganho
        jogador.defesa_base += defesa_ganho

        titulo = f"🌟 VOCÊ SUBIU PARA O NÍVEL {jogador.nivel}! 🌟"
        mensagem = (
            f"HP Máximo: +{hp_ganho}\n"
            f"Ataque Base: +{ataque_ganho}\n"
            f"Defesa Base: +{defesa_ganho}\n\n"
            "Seu HP foi totalmente restaurado!"
        )
        desenhar_tela_evento(titulo, mensagem)

    if subiu_de_nivel:
        aplicar_bonus_equipamento(jogador)


def processo_criacao_personagem() -> Personagem:
    """Orquestra o processo de criação de personagem."""
    nome = ""
    while not nome:
        nome = desenhar_tela_input("CRIAÇÃO DE PERSONAGEM", "Qual é o nome do seu herói?")
    classes_config = obter_classes()
    classes_lista = list(classes_config.keys())
    while True:
        escolha = desenhar_tela_escolha_classe(classes_config)
        if escolha in classes_config:
            classe_escolhida = escolha
            break
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(classes_lista):
                classe_escolhida = classes_lista[idx]
                break
        except (ValueError, IndexError):
            pass
        desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")
    jogador = criar_personagem(nome, classe_escolhida)
    desenhar_tela_resumo_personagem(jogador)
    return jogador


def main() -> None:
    """Função principal do jogo."""
    contexto = ContextoJogo()
    estado = Estado.MENU
    try:
        while True:
            if estado == Estado.MENU:
                estado = executar_estado_menu(contexto)
            elif estado == Estado.CRIACAO:
                estado = executar_estado_criacao(contexto)
            elif estado == Estado.EXPLORACAO:
                estado = executar_estado_exploracao(contexto)
            elif estado == Estado.INVENTARIO:
                estado = executar_estado_inventario(contexto)
            elif estado == Estado.COMBATE:
                estado = executar_estado_combate(contexto)
            elif estado == Estado.SAIR:
                desenhar_tela_saida("DESPEDIDA", "Obrigado por jogar!\n\nAté a próxima.")
                break
    except KeyboardInterrupt:
        mensagem_saida = "O jogo foi interrompido.\n\nEsperamos você para a próxima aventura!"
        desenhar_tela_saida("ATÉ LOGO!", mensagem_saida)
        sys.exit(0)
    except ErroDadosError as erro:
        desenhar_tela_saida("ERRO DE DADOS", str(erro))
        sys.exit(1)


if __name__ == "__main__":
    main()
