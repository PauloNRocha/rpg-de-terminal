import sys
from collections.abc import Callable
from typing import Any

from src.armazenamento import ErroCarregamento, carregar_jogo, existe_save, salvar_jogo
from src.combate import iniciar_combate
from src.entidades import Inimigo, Item, Personagem
from src.erros import ErroDadosError
from src.gerador_inimigos import gerar_inimigo
from src.gerador_itens import gerar_item_aleatorio
from src.gerador_mapa import gerar_mapa
from src.personagem import criar_personagem, obter_classes
from src.ui import (
    desenhar_hud_exploracao,
    desenhar_menu_principal,
    desenhar_tela_equipar,
    desenhar_tela_escolha_classe,
    desenhar_tela_evento,
    desenhar_tela_input,
    desenhar_tela_inventario,
    desenhar_tela_resumo_personagem,
    desenhar_tela_saida,
    tela_game_over,
)
from src.version import __version__

Mapa = list[list[dict[str, Any]]]
EffectHandler = Callable[[Personagem, int], str]


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
    """Aplica efeitos declarados no item e retorna mensagens ao jogador."""
    mensagens: list[str] = []
    efeitos = item.efeito or {}
    for nome, valor in efeitos.items():
        handler = EFFECT_HANDLERS.get(nome)
        if handler:
            mensagens.append(handler(jogador, int(valor)))
        else:
            mensagens.append(f"Efeito '{nome}' ainda não é suportado e foi ignorado.")
    return mensagens


def serializar_mapa(mapa: Mapa) -> Mapa:
    """Cria uma cópia serializável do mapa, convertendo inimigos para dict."""
    mapa_serializado: Mapa = []
    for linha in mapa:
        nova_linha: list[dict[str, Any]] = []
        for sala in linha:
            sala_copia = dict(sala)
            inimigo_atual = sala_copia.get("inimigo_atual")
            if isinstance(inimigo_atual, Inimigo):
                sala_copia["inimigo_atual"] = inimigo_atual.to_dict()
            elif not isinstance(inimigo_atual, dict):
                sala_copia["inimigo_atual"] = None
            nova_linha.append(sala_copia)
        mapa_serializado.append(nova_linha)
    return mapa_serializado


def hidratar_mapa(mapa_serializado: Mapa) -> Mapa:
    """Reconstrói instâncias de Inimigo presentes no mapa carregado."""
    mapa_hidratado: Mapa = []
    for linha in mapa_serializado:
        nova_linha: list[dict[str, Any]] = []
        for sala in linha:
            sala_copia = dict(sala)
            inimigo_atual = sala_copia.get("inimigo_atual")
            if isinstance(inimigo_atual, dict):
                sala_copia["inimigo_atual"] = Inimigo.from_dict(inimigo_atual)
            elif not isinstance(inimigo_atual, Inimigo):
                sala_copia["inimigo_atual"] = None
            nova_linha.append(sala_copia)
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

        hp_ganho = 10
        ataque_ganho = 2
        defesa_ganho = 1

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


def aplicar_bonus_equipamento(jogador: Personagem) -> None:
    """Aplica os bônus de ataque e defesa dos itens equipados."""
    jogador.ataque = jogador.ataque_base
    jogador.defesa = jogador.defesa_base

    arma = jogador.equipamento.get("arma")
    if arma:
        jogador.ataque += arma.bonus.get("ataque", 0)

    escudo = jogador.equipamento.get("escudo")
    if escudo:
        jogador.defesa += escudo.bonus.get("defesa", 0)


def gerenciar_inventario(jogador: Personagem) -> None:
    """Cria um loop para gerenciar as ações do inventário."""
    while True:
        escolha = desenhar_tela_inventario(jogador)
        if escolha == "1":
            usar_item(jogador)
        elif escolha == "2":
            equipar_item(jogador)
        elif escolha == "3":
            break
        else:
            desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")


def usar_item(jogador: Personagem) -> bool | None:
    """Gerencia a lógica de usar um item consumível."""
    while True:
        itens_consumiveis = [item for item in jogador.inventario if item.tipo == "consumivel"]

        opcoes_itens = [
            f"{i + 1}. {item.nome} ({item.descricao})" for i, item in enumerate(itens_consumiveis)
        ]
        opcoes_itens.append(f"{len(itens_consumiveis) + 1}. Voltar")

        prompt = (
            "Seus itens consumíveis:\n"
            + "\n".join(opcoes_itens)
            + "\n\nEscolha um item para usar ou 'Voltar': "
        )
        escolha_str = desenhar_tela_input("USAR ITEM", prompt)

        try:
            escolha = int(escolha_str)
            if escolha == len(itens_consumiveis) + 1:
                return False
            if not (1 <= escolha <= len(itens_consumiveis)):
                raise ValueError

            item_escolhido = itens_consumiveis[escolha - 1]

            if not item_escolhido.efeito:
                desenhar_tela_evento(
                    "ITEM SEM EFEITO",
                    "Este item não possui efeitos consumíveis configurados.",
                )
                continue

            mensagens = aplicar_efeitos_consumiveis(jogador, item_escolhido)
            jogador.inventario.remove(item_escolhido)
            verificar_level_up(jogador)
            desenhar_tela_evento("ITEM USADO", "\n".join(mensagens))
            return True
        except (ValueError, IndexError):
            desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")
    return None


def equipar_item(jogador: Personagem) -> None:
    """Gerencia a lógica de equipar um item."""
    while True:
        itens_equipaveis = [item for item in jogador.inventario if item.tipo in ["arma", "escudo"]]
        escolha_str = desenhar_tela_equipar(jogador, itens_equipaveis)

        try:
            if escolha_str == "voltar":
                return
            if not escolha_str.isdigit():
                raise ValueError
            escolha = int(escolha_str)
            if escolha == len(itens_equipaveis) + 1:
                return
            if not (1 <= escolha <= len(itens_equipaveis)):
                raise ValueError

            item_escolhido = itens_equipaveis[escolha - 1]
            tipo_item = item_escolhido.tipo

            if jogador.equipamento[tipo_item]:
                item_desequipado = jogador.equipamento[tipo_item]
                jogador.inventario.append(item_desequipado)

            jogador.equipamento[tipo_item] = item_escolhido
            jogador.inventario.remove(item_escolhido)
            aplicar_bonus_equipamento(jogador)
        except (ValueError, IndexError):
            desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")


def iniciar_aventura(jogador: Personagem, mapa: Mapa, nivel_masmorra: int) -> bool | None:
    """Loop principal da exploração."""
    start_x, start_y = 0, 0
    for y_idx, linha in enumerate(mapa):
        for x_idx, sala in enumerate(linha):
            if sala.get("tipo") == "entrada":
                start_x, start_y = x_idx, y_idx
                break
        else:
            continue
        break

    jogador.x, jogador.y = start_x, start_y
    posicao_anterior = None

    while True:
        sala_atual = mapa[jogador.y][jogador.x]

        if sala_atual.get("pode_ter_inimigo") and not sala_atual.get("inimigo_derrotado"):
            inimigo = sala_atual.get("inimigo_atual")
            if inimigo is None:
                nivel_inimigo = sala_atual.get("nivel_area", 1)
                tipo = "chefe_orc" if sala_atual.get("chefe") else None
                inimigo = gerar_inimigo(nivel_inimigo, tipo_inimigo=tipo)
                sala_atual["inimigo_atual"] = inimigo

            desenhar_tela_evento("ENCONTRO!", f"CUIDADO! Um {inimigo.nome} está na sala!")
            resultado_combate, inimigo_atualizado = iniciar_combate(jogador, inimigo, usar_item)
            sala_atual["inimigo_atual"] = inimigo_atualizado

            if resultado_combate:
                xp_ganho = inimigo_atualizado.xp_recompensa
                mensagem_vitoria = f"Você derrotou o {inimigo.nome} e ganhou {xp_ganho} de XP!"
                desenhar_tela_evento("VITÓRIA!", mensagem_vitoria)
                jogador.xp_atual += xp_ganho

                if inimigo_atualizado.drop_raridade:
                    item_dropado = gerar_item_aleatorio(inimigo_atualizado.drop_raridade)
                    if item_dropado:
                        jogador.inventario.append(item_dropado)
                        mensagem_drop = f"O inimigo dropou: {item_dropado.nome}!"
                        desenhar_tela_evento("ITEM ENCONTRADO!", mensagem_drop)

                sala_atual["inimigo_derrotado"] = True
                sala_atual["inimigo_atual"] = None
                verificar_level_up(jogador)
            else:
                if not jogador.esta_vivo():
                    tela_game_over()
                    return False
                desenhar_tela_evento("FUGA!", "Você recua para a sala anterior.")
                if posicao_anterior:
                    jogador.x, jogador.y = posicao_anterior
                continue

        opcoes = []
        if jogador.y > 0 and mapa[jogador.y - 1][jogador.x].get("tipo") != "parede":
            opcoes.append("Ir para o Norte")
        if jogador.y < len(mapa) - 1 and mapa[jogador.y + 1][jogador.x].get("tipo") != "parede":
            opcoes.append("Ir para o Sul")
        if jogador.x < len(mapa[0]) - 1 and mapa[jogador.y][jogador.x + 1].get("tipo") != "parede":
            opcoes.append("Ir para o Leste")
        if jogador.x > 0 and mapa[jogador.y][jogador.x - 1].get("tipo") != "parede":
            opcoes.append("Ir para o Oeste")

        if sala_atual.get("tipo") == "escada":
            chefe_derrotado = all(
                sala.get("inimigo_derrotado")
                for linha in mapa
                for sala in linha
                if sala.get("tipo") == "chefe"
            )
            if chefe_derrotado:
                opcoes.append("Descer para o próximo nível")
            else:
                desenhar_tela_evento(
                    "AVISO", "A escada está bloqueada. Derrote o chefe para prosseguir."
                )

        opcoes.extend(["Ver Inventário", "Salvar jogo", "Sair da masmorra"])
        escolha_str = desenhar_hud_exploracao(jogador, sala_atual, opcoes)

        try:
            escolha = int(escolha_str)
            if not (1 <= escolha <= len(opcoes)):
                raise ValueError
            acao_escolhida = opcoes[escolha - 1]
            posicao_atual = (jogador.x, jogador.y)

            if acao_escolhida == "Ir para o Norte":
                jogador.y -= 1
            elif acao_escolhida == "Ir para o Sul":
                jogador.y += 1
            elif acao_escolhida == "Ir para o Leste":
                jogador.x += 1
            elif acao_escolhida == "Ir para o Oeste":
                jogador.x -= 1
            elif acao_escolhida == "Descer para o próximo nível":
                return True
            elif acao_escolhida == "Ver Inventário":
                gerenciar_inventario(jogador)
                continue
            elif acao_escolhida == "Salvar jogo":
                estado = {
                    "jogador": jogador.to_dict(),
                    "mapa": serializar_mapa(mapa),
                    "nivel_masmorra": nivel_masmorra,
                }
                try:
                    caminho = salvar_jogo(estado)
                    desenhar_tela_evento("JOGO SALVO", f"Progresso salvo em {caminho}.")
                except OSError as erro:
                    desenhar_tela_evento("ERRO AO SALVAR", f"Não foi possível salvar: {erro}.")
                continue
            elif acao_escolhida == "Sair da masmorra":
                desenhar_tela_evento("FIM DE JOGO", "Você saiu da masmorra.\n\nObrigado por jogar!")
                return False
            posicao_anterior = posicao_atual
        except (ValueError, IndexError):
            desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")
    return None


def processo_criacao_personagem() -> Personagem:
    """Orquestra o processo de criação de personagem."""
    nome = ""
    while not nome:
        nome = desenhar_tela_input("CRIAÇÃO DE PERSONAGEM", "Qual é o nome do seu herói?")
    classe_escolhida = ""
    classes_config = obter_classes()
    classes_lista = list(classes_config.keys())
    while not classe_escolhida:
        escolha = desenhar_tela_escolha_classe(classes_config)
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(classes_lista):
                classe_escolhida = classes_lista[idx]
        except (ValueError, IndexError):
            desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")
    jogador = criar_personagem(nome, classe_escolhida)
    desenhar_tela_resumo_personagem(jogador)
    return jogador


def executar_campanha(
    jogador: Personagem, nivel_masmorra: int, mapa_atual: Mapa | None = None
) -> None:
    """Executa o loop principal de exploração a partir de um estado inicial."""
    mapa_corrente = mapa_atual
    while True:
        if mapa_corrente is None:
            mapa_corrente = gerar_mapa(nivel_masmorra)
        aventura_continua = iniciar_aventura(jogador, mapa_corrente, nivel_masmorra)
        if aventura_continua:
            nivel_masmorra += 1
            mapa_corrente = None
            hp_cura = int(jogador.hp_max * 0.25)
            jogador.hp = min(jogador.hp_max, jogador.hp + hp_cura)
            mensagem_nivel = f"Você desce para o próximo nível.\nVocê recuperou {hp_cura} de HP."
            desenhar_tela_evento(f"NÍVEL {nivel_masmorra} ALCANÇADO!", mensagem_nivel)
        else:
            break


def main() -> None:
    """Função principal do jogo."""
    try:
        while True:
            tem_save = existe_save()
            escolha = desenhar_menu_principal(__version__, tem_save)
            if escolha == "1":
                jogador = processo_criacao_personagem()
                executar_campanha(jogador, nivel_masmorra=1)
            elif escolha == "2" and tem_save:
                try:
                    estado = carregar_jogo()
                    jogador_data = estado.get("jogador")
                    mapa_salvo = estado.get("mapa")
                    nivel_masmorra = estado.get("nivel_masmorra")
                    if not all([jogador_data, mapa_salvo, isinstance(nivel_masmorra, int)]):
                        raise ErroCarregamento("Arquivo de save inválido ou corrompido.")
                    jogador = Personagem.from_dict(jogador_data)
                    mapa_recuperado = hidratar_mapa(mapa_salvo)
                    desenhar_tela_evento("JOGO CARREGADO", "Seu progresso foi restaurado!")
                    executar_campanha(
                        jogador,
                        nivel_masmorra=nivel_masmorra,
                        mapa_atual=mapa_recuperado,
                    )
                except ErroCarregamento as erro:
                    desenhar_tela_evento("ERRO AO CARREGAR", str(erro))
            elif (tem_save and escolha == "3") or (not tem_save and escolha == "2"):
                desenhar_tela_evento("DESPEDIDA", "Obrigado por jogar!\n\nAté a próxima.")
                break
            else:
                desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")
    except KeyboardInterrupt:
        mensagem_saida = "O jogo foi interrompido.\n\nEsperamos você para a próxima aventura!"
        desenhar_tela_saida("ATÉ LOGO!", mensagem_saida)
        sys.exit(0)
    except ErroDadosError as erro:
        desenhar_tela_saida("ERRO DE DADOS", str(erro))
        sys.exit(1)


if __name__ == "__main__":
    main()
