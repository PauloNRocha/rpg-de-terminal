import time
from src.utils import limpar_tela
from src.personagem import criar_personagem
from src.mapa import MAPA

import time

from src.utils import limpar_tela, tela_game_over

from src.personagem import criar_personagem

from src.mapa import MAPA

from src.combate import iniciar_combate



def iniciar_aventura(jogador, mapa):

    """Loop principal da exploração do mapa com menu de ações numérico."""

    

    jogador["x"], jogador["y"] = 0, 0

    posicao_anterior = None



    while True:

        limpar_tela()

        

        x, y = jogador["x"], jogador["y"]

        sala_atual = mapa[y][x]

        

        print(f"Você está em: {sala_atual['nome']}")

        print(sala_atual['descricao'])

        print("-" * 30)

        print(f"HP: {jogador['hp']}/{jogador['hp_max']}")



        if sala_atual.get("inimigo"):

            inimigo = sala_atual["inimigo"]

            print(f"\nCUIDADO! Um {inimigo['nome']} está na sala!")

            time.sleep(2)

            

            resultado_combate = iniciar_combate(jogador, inimigo)

            

            if resultado_combate:

                sala_atual["inimigo"] = None

                print("\nVocê continua sua jornada...")

                time.sleep(2)

            else:

                if jogador["hp"] <= 0:

                    tela_game_over()

                    return

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