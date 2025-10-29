import time
from src.utils import limpar_tela
from src.personagem import criar_personagem
from src.mapa import MAPA

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
    
    while True:
        limpar_tela()
        print("O que você deseja fazer?")
        print("1. Iniciar Nova Aventura")
        print("2. Sair")
        
        escolha = input("> ")
        
        if escolha == "1":
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