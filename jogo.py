import time
from src.utils import limpar_tela, tela_game_over
from src.personagem import criar_personagem
from src.mapa import MAPA
from src.combate import iniciar_combate
from src.gerador_itens import gerar_item_aleatorio
from src.gerador_inimigos import gerar_inimigo
from src.ui import (
    desenhar_hud_exploracao,
    desenhar_tela_inventario,
    desenhar_tela_evento,
    desenhar_tela_equipar,
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


def mostrar_inventario(jogador):
    desenhar_tela_inventario(jogador)


def usar_item(jogador):
    limpar_tela()
    print("=== USAR ITEM ===")
    
    itens_consumiveis = [item for item in jogador["inventario"] if item["tipo"] == "consumivel"]
    if not itens_consumiveis:
        print("Você não tem itens consumíveis no inventário.")
        time.sleep(2)
        return False

    print("Seus itens consumíveis:")
    for i, item in enumerate(itens_consumiveis, 1):
        print(f"{i}. {item['nome']} ({item['descricao']})")
    print(f"{len(itens_consumiveis) + 1}. Voltar")

    while True:
        try:
            escolha = int(input("\nEscolha um item para usar ou 'Voltar': "))
            if escolha == len(itens_consumiveis) + 1:
                return False
            if not (1 <= escolha <= len(itens_consumiveis)):
                raise ValueError

            item_escolhido = itens_consumiveis[escolha - 1]

            if "hp" in item_escolhido["efeito"]:
                cura = item_escolhido["efeito"]["hp"]
                jogador["hp"] = min(jogador["hp_max"], jogador["hp"] + cura)
                print(f"Você usou {item_escolhido['nome']} e restaurou {cura} de HP.")
                jogador["inventario"].remove(item_escolhido)
                time.sleep(2)
                return True
        except (ValueError, IndexError):
            print("Opção inválida! Tente novamente.")
            time.sleep(1)

def equipar_item(jogador):
    """Gerencia a lógica de equipar um item usando a nova UI."""
    while True:
        itens_equipaveis = [item for item in jogador["inventario"] if item["tipo"] in ["arma", "escudo"]]
        
        desenhar_tela_equipar(jogador, itens_equipaveis)
        
        try:
            escolha_str = input("> ")
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
    
    jogador["x"], jogador["y"] = 0, 0
    posicao_anterior = None

    # Inicializa os atributos base para aplicar bônus de equipamento
    jogador["ataque_base"] = jogador["ataque"]
    jogador["defesa_base"] = jogador["defesa"]

    while True:
        x, y = jogador["x"], jogador["y"]
        sala_atual = mapa[y][x]
        
        # Gera um inimigo dinamicamente se a sala permitir
        if sala_atual.get("pode_ter_inimigo") and not sala_atual.get("inimigo_derrotado"):
            nivel_inimigo = sala_atual.get("nivel_area", 1)
            
            # Verifica se a sala é de um chefe
            if sala_atual.get("chefe"):
                inimigo = gerar_inimigo(nivel_inimigo, tipo_inimigo="chefe_orc")
            else:
                inimigo = gerar_inimigo(nivel_inimigo)
            
            # TODO: Melhorar a tela de início de combate
            print(f"\nCUIDADO! Um {inimigo['nome']} está na sala!")
            time.sleep(2)
            
            resultado_combate = iniciar_combate(jogador, inimigo, usar_item)
            
            if resultado_combate: # Vitória
                xp_ganho = inimigo["xp_recompensa"]
                print(f"Você ganhou {xp_ganho} de XP!")
                jogador["xp_atual"] += xp_ganho
                
                if inimigo.get("drop_raridade"):
                    item_dropado = gerar_item_aleatorio(inimigo["drop_raridade"])
                    if item_dropado:
                        jogador["inventario"].append(item_dropado)
                        print(f"O inimigo dropou: {item_dropado['nome']}!")
                
                sala_atual["inimigo_derrotado"] = True
                time.sleep(2)
                verificar_level_up(jogador)
            else: # Derrota ou fuga
                if jogador["hp"] <= 0:
                    tela_game_over()
                    return
                else: # Fuga
                    print("\nVocê recua para a sala anterior.")
                    if posicao_anterior:
                        jogador["x"], jogador["y"] = posicao_anterior
                    time.sleep(2)
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
                mostrar_inventario(jogador)
                continue
            elif acao_escolhida == "Usar Item":
                usar_item(jogador)
                continue
            elif acao_escolhida == "Equipar Item":
                equipar_item(jogador)
                continue
            elif acao_escolhida == "Sair da masmorra":
                print("\nVocê saiu da masmorra.")
                time.sleep(2)
                break
            
            posicao_anterior = posicao_atual

        except (ValueError, IndexError):
            # TODO: Adicionar mensagem de feedback na UI
            print("\nOpção inválida! Tente novamente.")
            time.sleep(1)


def main():
    """Função principal do jogo."""
    limpar_tela()
    print("========================================")
    print("=== Bem-vindo à Aventura no Terminal ===")
    print("========================================")
    print("\nPrepare-se para desbravar masmorras escuras!")
    time.sleep(3)
    
    while True:
        limpar_tela()
        print("O que você deseja fazer?")
        print("1. Iniciar Nova Aventura")
        print("2. Sair")
        
        escolha = input("> ")
        
        if escolha == "1":
            # Reseta o jogador para uma nova aventura
            jogador = criar_personagem()
            iniciar_aventura(jogador, MAPA)

        elif escolha == "2":
            print("\nObrigado por jogar! Até a próxima.")
            break
        else:
            print("\nOpção inválida! Tente novamente.")
            time.sleep(1)

if __name__ == "__main__":
    main()