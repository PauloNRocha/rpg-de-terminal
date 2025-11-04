import os
import time
import sys
from src.combate import iniciar_combate
from src.gerador_itens import gerar_item_aleatorio
from src.gerador_inimigos import gerar_inimigo
from src.gerador_mapa import gerar_mapa # Importa o novo gerador de mapas
from src.personagem import criar_personagem as criar_personagem_logica, CLASSES
from src.ui import (
    desenhar_hud_exploracao,
    desenhar_tela_inventario,
    desenhar_tela_evento,
    desenhar_tela_equipar,
    desenhar_menu_principal,
    desenhar_tela_input,
    desenhar_tela_escolha_classe,
    desenhar_tela_resumo_personagem,
    limpar_tela, # Importa a função limpar_tela
    tela_game_over, # Importa a função tela_game_over
)

def verificar_level_up(jogador):
    """Verifica se o jogador tem XP suficiente para subir de nível e aplica as mudanças."""
    subiu_de_nivel = False
    while jogador["xp_atual"] >= jogador["xp_para_proximo_nivel"]:
        subiu_de_nivel = True
        jogador["nivel"] += 1
        xp_excedente = jogador["xp_atual"] - jogador["xp_para_proximo_nivel"]
        jogador["xp_atual"] = xp_excedente
        jogador["xp_para_proximo_nivel"] = int(jogador["xp_para_proximo_nivel"] * 1.5)

        hp_ganho = 10
        ataque_ganho = 2
        defesa_ganho = 1
        
        jogador["hp_max"] += hp_ganho
        jogador["hp"] = jogador["hp_max"]
        jogador["ataque_base"] += ataque_ganho
        jogador["defesa_base"] += defesa_ganho
        
        titulo = f"🌟 VOCÊ SUBIU PARA O NÍVEL {jogador['nivel']}! 🌟"
        mensagem = (
            f"HP Máximo: +{hp_ganho}\n"
            f"Ataque Base: +{ataque_ganho}\n"
            f"Defesa Base: +{defesa_ganho}\n\n"
            "Seu HP foi totalmente restaurado!"
        )
        desenhar_tela_evento(titulo, mensagem)
    
    if subiu_de_nivel:
        aplicar_bonus_equipamento(jogador)

# Função auxiliar para aplicar bônus de equipamento
def aplicar_bonus_equipamento(jogador):
    # Reseta para os valores base antes de aplicar bônus
    jogador["ataque"] = jogador.get("ataque_base", jogador["ataque"])
    jogador["defesa"] = jogador.get("defesa_base", jogador["defesa"])

    if jogador["equipamento"]["arma"]:
        bonus_ataque = jogador["equipamento"]["arma"]["bonus"].get("ataque", 0)
        jogador["ataque"] += bonus_ataque

    if jogador["equipamento"]["escudo"]:
        bonus_defesa = jogador["equipamento"]["escudo"]["bonus"].get("defesa", 0)
        jogador["defesa"] += bonus_defesa


def gerenciar_inventario(jogador):
    """Cria um loop para gerenciar as ações do inventário."""
    while True:
        escolha = desenhar_tela_inventario(jogador)
        if escolha == "1":
            usar_item(jogador)
        elif escolha == "2":
            equipar_item(jogador)
        elif escolha == "3":
            break # Volta para o mapa
        else:
            desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")


def usar_item(jogador):
    """Gerencia a lógica de usar um item consumível usando a nova UI."""
    while True:
        itens_consumiveis = [item for item in jogador["inventario"] if item["tipo"] == "consumivel"]
        
        opcoes_itens = [f"{i+1}. {item['nome']} ({item['descricao']})" for i, item in enumerate(itens_consumiveis)]
        opcoes_itens.append(f"{len(itens_consumiveis) + 1}. Voltar")

        escolha_str = desenhar_tela_input(
            "USAR ITEM",
            "Seus itens consumíveis:\n" + "\n".join(opcoes_itens) + "\n\nEscolha um item para usar ou 'Voltar': "
        )

        try:
            escolha = int(escolha_str)
            if escolha == len(itens_consumiveis) + 1:
                return False
            if not (1 <= escolha <= len(itens_consumiveis)):
                raise ValueError

            item_escolhido = itens_consumiveis[escolha - 1]

            if "hp" in item_escolhido["efeito"]:
                cura = item_escolhido["efeito"]["hp"]
                jogador["hp"] = min(jogador["hp_max"], jogador["hp"] + cura)
                desenhar_tela_evento("ITEM USADO", f"Você usou {item_escolhido['nome']} e restaurou {cura} de HP.")
                jogador["inventario"].remove(item_escolhido)
                return True
        except (ValueError, IndexError):
            desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")

def equipar_item(jogador):
    """Gerencia a lógica de equipar um item usando a nova UI."""
    while True:
        itens_equipaveis = [item for item in jogador["inventario"] if item["tipo"] in ["arma", "escudo"]]
        
        escolha_str = desenhar_tela_equipar(jogador, itens_equipaveis)
        
        try:
            if not escolha_str.isdigit():
                raise ValueError

            escolha = int(escolha_str)
            
            if escolha == len(itens_equipaveis) + 1: # Opção "Voltar"
                return

            if not (1 <= escolha <= len(itens_equipaveis)):
                raise ValueError

            item_escolhido = itens_equipaveis[escolha - 1]
            tipo_item = item_escolhido["tipo"]

            # Desequipa o item atual (se houver) e o devolve ao inventário
            if jogador["equipamento"][tipo_item]:
                item_desequipado = jogador["equipamento"][tipo_item]
                jogador["inventario"].append(item_desequipado)

            # Equipa o novo item
            jogador["equipamento"][tipo_item] = item_escolhido
            jogador["inventario"].remove(item_escolhido)
            
            aplicar_bonus_equipamento(jogador) # Recalcula os bônus

        except (ValueError, IndexError):
            # TODO: Adicionar mensagem de feedback na UI para erro
            time.sleep(1)


def iniciar_aventura(jogador, mapa):
    """Loop principal da exploração do mapa com menu de ações numérico."""
    
    # Encontra a posição inicial do jogador na "Entrada da Masmorra"
    start_x, start_y = 0, 0
    for y_idx, linha in enumerate(mapa):
        for x_idx, sala in enumerate(linha):
            if sala.get("nome") == "Entrada da Masmorra":
                start_x, start_y = x_idx, y_idx
                break
        else:
            continue
        break
    
    jogador["x"], jogador["y"] = start_x, start_y
    posicao_anterior = None

    # Inicializa os atributos base para aplicar bônus de equipamento
    jogador["ataque_base"] = jogador["ataque"]
    jogador["defesa_base"] = jogador["defesa"]

    while True:
        x, y = jogador["x"], jogador["y"]
        sala_atual = mapa[y][x]
        
        # Gera um inimigo dinamicamente se a sala permitir
        if sala_atual.get("pode_ter_inimigo") and not sala_atual.get("inimigo_derrotado"):
            inimigo = sala_atual.get("inimigo_atual")
            if inimigo is None:
                nivel_inimigo = sala_atual.get("nivel_area", 1)
                
                # Verifica se a sala é de um chefe
                if sala_atual.get("chefe"):
                    inimigo = gerar_inimigo(nivel_inimigo, tipo_inimigo="chefe_orc")
                else:
                    inimigo = gerar_inimigo(nivel_inimigo)
                sala_atual["inimigo_atual"] = inimigo # Armazena o inimigo na sala
            
            desenhar_tela_evento("ENCONTRO!", f"CUIDADO! Um {inimigo['nome']} está na sala!")
            
            resultado_combate, inimigo_atualizado = iniciar_combate(jogador, inimigo, usar_item)
            sala_atual["inimigo_atual"] = inimigo_atualizado # Atualiza o inimigo na sala
            
            if resultado_combate: # Vitória
                xp_ganho = inimigo_atualizado["xp_recompensa"]
                desenhar_tela_evento("VITÓRIA!", f"Você derrotou o {inimigo['nome']} e ganhou {xp_ganho} de XP!")
                jogador["xp_atual"] += xp_ganho
                
                if inimigo_atualizado.get("drop_raridade"):
                    item_dropado = gerar_item_aleatorio(inimigo_atualizado["drop_raridade"])
                    if item_dropado:
                        jogador["inventario"].append(item_dropado)
                        desenhar_tela_evento("ITEM DROPADO!", f"O inimigo dropou: {item_dropado['nome']}!")
                
                sala_atual["inimigo_derrotado"] = True
                sala_atual["inimigo_atual"] = None # Remove o inimigo da sala após a derrota
                verificar_level_up(jogador)
            else: # Derrota ou fuga
                if jogador["hp"] <= 0:
                    tela_game_over()
                    return
                else: # Fuga
                    desenhar_tela_evento("FUGA!", "Você recua para a sala anterior.")
                    if posicao_anterior:
                        jogador["x"], jogador["y"] = posicao_anterior
                    continue

        # Define as opções de ação
        opcoes = []
        if y > 0: opcoes.append("Ir para o Norte")
        if y < len(mapa) - 1: opcoes.append("Ir para o Sul")
        if x < len(mapa[0]) - 1: opcoes.append("Ir para o Leste")
        if x > 0: opcoes.append("Ir para o Oeste")
        if posicao_anterior is not None: opcoes.append("Voltar por onde veio")
        opcoes.append("Ver Inventário")
        opcoes.append("Usar Item")
        opcoes.append("Equipar Item")
        opcoes.append("Sair da masmorra")

        # Desenha a UI e captura a entrada do jogador
        escolha_str = desenhar_hud_exploracao(jogador, sala_atual, opcoes)

        try:
            escolha = int(escolha_str)
            if not (1 <= escolha <= len(opcoes)):
                raise ValueError

            acao_escolhida = opcoes[escolha - 1]
            
            posicao_atual = (x, y)

            if acao_escolhida == "Ir para o Norte":
                jogador["y"] -= 1
            elif acao_escolhida == "Ir para o Sul":
                jogador["y"] += 1
            elif acao_escolhida == "Ir para o Leste":
                jogador["x"] += 1
            elif acao_escolhida == "Ir para o Oeste":
                jogador["x"] -= 1
            elif acao_escolhida == "Voltar por onde veio":
                jogador["x"], jogador["y"] = posicao_anterior
            elif acao_escolhida == "Ver Inventário":
                gerenciar_inventario(jogador)
                continue
            elif acao_escolhida == "Usar Item":
                usar_item(jogador)
                continue
            elif acao_escolhida == "Equipar Item":
                equipar_item(jogador)
                continue
            elif acao_escolhida == "Sair da masmorra":
                desenhar_tela_evento("FIM DE JOGO", "Você saiu da masmorra.\n\nObrigado por jogar!")
                break
            
            posicao_anterior = posicao_atual

        except (ValueError, IndexError):
            desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")

def processo_criacao_personagem():
    """Orquestra o processo de criação de personagem usando a UI."""
    nome = ""
    while not nome:
        nome = desenhar_tela_input("CRIAÇÃO DE PERSONAGEM", "Qual é o nome do seu herói?")
    
    classe_escolhida = ""
    classes_lista = list(CLASSES.keys())
    while not classe_escolhida:
        escolha = desenhar_tela_escolha_classe(CLASSES)
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(classes_lista):
                classe_escolhida = classes_lista[idx]
        except (ValueError, IndexError):
            desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")
            
    jogador = criar_personagem_logica(nome, classe_escolhida)
    desenhar_tela_resumo_personagem(jogador)
    return jogador

def main():
    """Função principal do jogo."""
    try:
        while True:
            escolha = desenhar_menu_principal()
            
            if escolha == "1":
                jogador = processo_criacao_personagem()
                mapa_gerado = gerar_mapa() # Gera um novo mapa a cada aventura
                iniciar_aventura(jogador, mapa_gerado)
            
            elif escolha == "2":
                desenhar_tela_evento("DESPEDIDA", "Obrigado por jogar!\n\nAté a próxima.")
                break
            else:
                desenhar_tela_evento("ERRO", "Opção inválida! Tente novamente.")
    except KeyboardInterrupt:
        desenhar_tela_evento("ATÉ LOGO!", "O jogo foi interrompido.\n\nEsperamos você para a próxima aventura!")
        sys.exit(0)

if __name__ == "__main__":
    main()