import time
import os

def limpar_tela():
    """Limpa o terminal para melhorar a legibilidade."""
    os.system('cls' if os.name == 'nt' else 'clear')

def criar_personagem(jogador):
    """Função para criar o personagem do jogador."""
    limpar_tela()
    print("=== Criação de Personagem ===")
    
    # Pede o nome do personagem
    while True:
        nome = input("Qual é o nome do seu herói? ")
        if nome.strip(): # Garante que o nome não seja vazio
            jogador["nome"] = nome
            break
        else:
            print("O nome não pode estar em branco.")

    # Pede para escolher a classe
    print("\nEscolha sua classe:")
    print("1. Guerreiro (HP: 25, Ataque: 6, Defesa: 4)")
    print("2. Mago      (HP: 15, Ataque: 8, Defesa: 2)")
    print("3. Arqueiro  (HP: 20, Ataque: 7, Defesa: 3)")

    while True:
        escolha_classe = input("> ")
        if escolha_classe == "1":
            jogador["classe"] = "Guerreiro"
            jogador["hp_max"] = 25
            jogador["hp"] = 25
            jogador["ataque"] = 6
            jogador["defesa"] = 4
            break
        elif escolha_classe == "2":
            jogador["classe"] = "Mago"
            jogador["hp_max"] = 15
            jogador["hp"] = 15
            jogador["ataque"] = 8
            jogador["defesa"] = 2
            break
        elif escolha_classe == "3":
            jogador["classe"] = "Arqueiro"
            jogador["hp_max"] = 20
            jogador["hp"] = 20
            jogador["ataque"] = 7
            jogador["defesa"] = 3
            break
        else:
            print("Opção inválida! Escolha 1, 2 ou 3.")
    
    limpar_tela()
    print(f"Personagem criado!")
    print("--------------------")
    print(f"Nome:   {jogador['nome']}")
    print(f"Classe: {jogador['classe']}")
    print(f"HP:     {jogador['hp']}/{jogador['hp_max']}")
    print(f"Ataque: {jogador['ataque']}")
    print(f"Defesa: {jogador['defesa']}")
    print("--------------------")
    print("\nA aventura vai começar...")
    time.sleep(4)
    return jogador


def iniciar_aventura(jogador, mapa):
    """Loop principal da exploração do mapa."""
    
    # Define a posição inicial do jogador no mapa
    jogador["x"] = 0
    jogador["y"] = 0

    while True:
        limpar_tela()
        
        # Obtém a sala atual com base nas coordenadas do jogador
        sala_atual = mapa[jogador["y"]][jogador["x"]]
        
        print(f"Você está em: {sala_atual['nome']}")
        print(sala_atual['descricao'])
        print("-" * 30)
        print(f"HP: {jogador['hp']}/{jogador['hp_max']}")
        print("\nO que você faz?")
        
        # Mostra as ações possíveis
        acoes = ["ir norte", "ir sul", "ir leste", "ir oeste", "sair"]
        print(f"Ações: {', '.join(acoes)}")
        
        comando = input("> ").lower().strip()
        
        if comando == "sair":
            print("\nVocê saiu da masmorra.")
            time.sleep(2)
            break
            
        elif comando.startswith("ir "):
            direcao = comando.split(" ")[1]
            nova_x, nova_y = jogador["x"], jogador["y"]

            if direcao == "norte":
                nova_y -= 1
            elif direcao == "sul":
                nova_y += 1
            elif direcao == "leste":
                nova_x += 1
            elif direcao == "oeste":
                nova_x -= 1
            else:
                print("\nDireção inválida.")
                time.sleep(1)
                continue

            # Verifica se o movimento é válido (dentro dos limites do mapa)
            if 0 <= nova_y < len(mapa) and 0 <= nova_x < len(mapa[0]):
                jogador["x"], jogador["y"] = nova_x, nova_y
            else:
                print("\nVocê não pode ir por esse caminho. Há uma parede.")
                time.sleep(2)
        else:
            print("\nComando desconhecido.")
            time.sleep(1)


def main():
    """Função principal do jogo."""
    limpar_tela()
    print("========================================")
    print("=== Bem-vindo à Aventura no Terminal ===")
    print("========================================")
    print("\nPrepare-se para desbravar masmorras escuras!")
    time.sleep(3)
    
    # Dicionário para guardar as informações do jogador
    jogador = {
        "nome": "", "classe": "", "hp": 0, "hp_max": 0,
        "ataque": 0, "defesa": 0, "x": 0, "y": 0,
    }

    # Define o mapa do jogo (grade 3x3)
    mapa = [
        [
            {"nome": "Entrada da Caverna", "descricao": "A luz fraca da entrada ilumina o chão de pedra. O ar é úmido e cheira a mofo."},
            {"nome": "Corredor Estreito", "descricao": "Um corredor apertado com teias de aranha no teto. O som de gotas d'água ecoa."},
            {"nome": "Câmara com Ossos", "descricao": "Uma pequena câmara com uma pilha de ossos roídos em um canto. Algo esteve aqui."}
        ],
        [
            {"nome": "Salão Rachado", "descricao": "O chão de pedra aqui tem uma grande rachadura. Você precisa andar com cuidado."},
            {"nome": "Encruzilhada", "descricao": "O caminho se divide aqui. Corredores seguem para todas as direções."},
            {"nome": "Fonte Misteriosa", "descricao": "Uma pequena fonte de água cristalina brota do chão. A água parece brilhar."}
        ],
        [
            {"nome": "Prisão Antiga", "descricao": "Celas com barras de ferro enferrujadas se alinham na parede. Estão todas vazias."},
            {"nome": "Altar Sombrio", "descricao": "Um altar de pedra negra se ergue no centro da sala. Símbolos estranhos estão gravados nele."},
            {"nome": "Covil da Besta", "descricao": "O ar aqui é pesado e fétido. O chão está coberto de detritos. Este é o covil de algo grande."}
        ]
    ]

    # Loop principal do jogo
    while True:
        limpar_tela()
        print("O que você deseja fazer?")
        print("1. Iniciar Nova Aventura")
        print("2. Sair")
        
        escolha = input("> ")
        
        if escolha == "1":
            jogador = criar_personagem(jogador)
            iniciar_aventura(jogador, mapa)

        elif escolha == "2":
            print("\nObrigado por jogar! Até a próxima.")
            break
        else:
            print("\nOpção inválida! Tente novamente.")
            time.sleep(1)

if __name__ == "__main__":
    main()
