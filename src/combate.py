import time
import random
from src.utils import limpar_tela

def iniciar_combate(jogador, inimigo):
    """
    Inicia e gerencia o loop de um combate por turnos entre o jogador e um inimigo.
    Retorna True se o jogador vencer, False se o jogador perder ou fugir.
    """
    limpar_tela()
    print(f"!!! Um {inimigo['nome']} selvagem aparece! !!!")
    time.sleep(2)

    # Cria uma cópia do inimigo para não modificar o original no mapa
    inimigo_atual = inimigo.copy()
    
    while jogador["hp"] > 0 and inimigo_atual["hp"] > 0:
        limpar_tela()
        print("--- BATALHA ---")
        print(f"{jogador['nome']} (HP: {jogador['hp']}/{jogador['hp_max']}) vs {inimigo_atual['nome']} (HP: {inimigo_atual['hp']})")
        print("-" * 15)
        print("O que você faz?")
        print("1. Atacar")
        print("2. Fugir")
        
        escolha = input("> ")

        if escolha == "1":
            # Turno do Jogador
            dano_jogador = max(0, jogador["ataque"] - inimigo_atual["defesa"])
            dano_real_jogador = random.randint(dano_jogador - 1, dano_jogador + 1)
            dano_real_jogador = max(0, dano_real_jogador) # Garante que o dano não seja negativo
            
            inimigo_atual["hp"] -= dano_real_jogador
            print(f"\nVocê ataca o {inimigo_atual['nome']} e causa {dano_real_jogador} de dano!")
            time.sleep(2)

            if inimigo_atual["hp"] <= 0:
                print(f"Você derrotou o {inimigo_atual['nome']}!")
                time.sleep(2)
                return True

            # Turno do Inimigo
            dano_inimigo = max(0, inimigo_atual["ataque"] - jogador["defesa"])
            dano_real_inimigo = random.randint(dano_inimigo - 1, dano_inimigo + 1)
            dano_real_inimigo = max(0, dano_real_inimigo)

            jogador["hp"] -= dano_real_inimigo
            print(f"O {inimigo_atual['nome']} ataca você e causa {dano_real_inimigo} de dano!")
            time.sleep(2)

            if jogador["hp"] <= 0:
                return False
        
        elif escolha == "2":
            # Tenta fugir (50% de chance)
            if random.random() < 0.5:
                print("\nVocê conseguiu fugir!")
                time.sleep(2)
                return False # Consideramos fuga como uma "derrota" no contexto da sala
            else:
                print("\nA fuga falhou! Você perdeu sua vez.")
                time.sleep(2)
                # Turno do Inimigo após falha na fuga
                dano_inimigo = max(0, inimigo_atual["ataque"] - jogador["defesa"])
                dano_real_inimigo = random.randint(dano_inimigo - 1, dano_inimigo + 1)
                dano_real_inimigo = max(0, dano_real_inimigo)

                jogador["hp"] -= dano_real_inimigo
                print(f"O {inimigo_atual['nome']} ataca você e causa {dano_real_inimigo} de dano!")
                time.sleep(2)

                if jogador["hp"] <= 0:
                    return False
        else:
            print("\nOpção inválida! Tente novamente.")
            time.sleep(1)
    
    return False # Caso algo inesperado aconteça
