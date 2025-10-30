import time
from src.utils import limpar_tela, tela_game_over
from src.personagem import criar_personagem
from src.mapa import MAPA
from src.combate import iniciar_combate
from src.gerador_itens import gerar_item_aleatorio # Nova importação

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
    limpar_tela()
    print("=== INVENTÁRIO ===")
    print(f"Nome: {jogador['nome']} | Classe: {jogador['classe']}")
    print(f"HP: {jogador['hp']}/{jogador['hp_max']} | Ataque: {jogador['ataque']} | Defesa: {jogador['defesa']}")
    print("-" * 30)

    print("\n--- Equipamento ---")
    arma_equipada = jogador["equipamento"]["arma"]
    escudo_equipado = jogador["equipamento"]["escudo"]
    print(f"Arma: {arma_equipada['nome'] if arma_equipada else 'Nenhuma'}")
    print(f"Escudo: {escudo_equipado['nome'] if escudo_equipado else 'Nenhum'}")

    print("\n--- Itens ---")
    if not jogador["inventario"]:
        print("Seu inventário está vazio.")
    else:
        for i, item in enumerate(jogador["inventario"], 1):
            print(f"{i}. {item['nome']} ({item.get('descricao', 'Item consumível.')})")
    
    input("\nPressione Enter para continuar...")

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
    limpar_tela()
    print("=== EQUIPAR ITEM ===")
    
    itens_equipaveis = [item for item in jogador["inventario"] if item["tipo"] in ["arma", "escudo"]]
    if not itens_equipaveis:
        print("Você não tem itens equipáveis no inventário.")
        time.sleep(2)
        return

    print("Seus itens equipáveis:")
    for i, item in enumerate(itens_equipaveis, 1):
        print(f"{i}. {item['nome']} ({item['descricao']})")
    print(f"{len(itens_equipaveis) + 1}. Voltar")

    while True:
        try:
            escolha = int(input("\nEscolha um item para equipar ou 'Voltar': "))
            if escolha == len(itens_equipaveis) + 1:
                return
            if not (1 <= escolha <= len(itens_equipaveis)):
                raise ValueError

            item_escolhido = itens_equipaveis[escolha - 1]
            tipo_item = item_escolhido["tipo"]

            # Desequipa o item atual, se houver
            if jogador["equipamento"][tipo_item]:
                item_desequipado = jogador["equipamento"][tipo_item]
                jogador["inventario"].append(item_desequipado)
                print(f"Você desequipou {item_desequipado['nome']}.")
                time.sleep(1)

            # Equipa o novo item
            jogador["equipamento"][tipo_item] = item_escolhido
            jogador["inventario"].remove(item_escolhido)
            aplicar_bonus_equipamento(jogador) # Recalcula os bônus
            print(f"Você equipou {item_escolhido['nome']}.")
            time.sleep(2)
            return

        except (ValueError, IndexError):
            print("Opção inválida! Tente novamente.")
            time.sleep(1)


def iniciar_aventura(jogador, mapa):
    """Loop principal da exploração do mapa com menu de ações numérico."""
    
    jogador["x"], jogador["y"] = 0, 0
    posicao_anterior = None

    # Inicializa os atributos base para aplicar bônus de equipamento
    jogador["ataque_base"] = jogador["ataque"]
    jogador["defesa_base"] = jogador["defesa"]

    while True:
        limpar_tela()
        
        x, y = jogador["x"], jogador["y"]
        sala_atual = mapa[y][x]
        
        print(f"Você está em: {sala_atual['nome']}")
        print(sala_atual['descricao'])
        print("-" * 30)
        print(f"HP: {jogador['hp']}/{jogador['hp_max']} | Ataque: {jogador['ataque']} | Defesa: {jogador['defesa']}")
        
        # Verifica se há um inimigo na sala
        if sala_atual.get("inimigo"):
            inimigo = sala_atual["inimigo"]
            print(f"\nCUIDADO! Um {inimigo['nome']} está na sala!")
            time.sleep(2)
            
            resultado_combate = iniciar_combate(jogador, inimigo, usar_item)
            
            if resultado_combate: # Vitória
                if inimigo.get("drop_raridade"): # Verifica se o inimigo dropa algo
                    item_dropado = gerar_item_aleatorio(inimigo["drop_raridade"])
                    if item_dropado:
                        jogador["inventario"].append(item_dropado)
                        print(f"O {inimigo['nome']} dropou: {item_dropado['nome']}!")
                sala_atual["inimigo"] = None # Remove o inimigo do mapa
                print("\nVocê continua sua jornada...")
                time.sleep(2)
            else: # Derrota ou fuga
                if jogador["hp"] <= 0:
                    tela_game_over()
                    return # Retorna para o menu principal
                else: # Fuga
                    print("\nVocê recua para a sala anterior.")
                    if posicao_anterior:
                        jogador["x"], jogador["y"] = posicao_anterior
                    time.sleep(2)
                    continue # Reinicia o loop na sala anterior

        print("\nO que você faz?")
        
        # Gera a lista de ações dinamicamente
        opcoes = []
        if y > 0: opcoes.append("Ir para o Norte")
        if y < len(mapa) - 1: opcoes.append("Ir para o Sul")
        if x < len(mapa[0]) - 1: opcoes.append("Ir para o Leste")
        if x > 0: opcoes.append("Ir para o Oeste")
        if posicao_anterior is not None: opcoes.append("Voltar por onde veio")
        opcoes.append("Ver Inventário") # Nova opção
        opcoes.append("Usar Item")      # Nova opção
        opcoes.append("Equipar Item")   # Nova opção
        opcoes.append("Sair da masmorra")

        # Mostra o menu numerado
        for i, opcao in enumerate(opcoes, 1):
            print(f"{i}. {opcao}")

        try:
            escolha = int(input("> "))
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
                continue # Continua o loop para mostrar o menu novamente
            elif acao_escolhida == "Usar Item":
                usar_item(jogador)
                continue # Continua o loop para mostrar o menu novamente
            elif acao_escolhida == "Equipar Item":
                equipar_item(jogador)
                continue # Continua o loop para mostrar o menu novamente
            elif acao_escolhida == "Sair da masmorra":
                print("\nVocê saiu da masmorra.")
                time.sleep(2)
                break
            
            posicao_anterior = posicao_atual

        except (ValueError, IndexError):
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