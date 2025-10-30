import time
import random
from src.utils import limpar_tela

def calcular_dano(atacante_ataque, defensor_defesa):
    """Calcula o dano causado, considerando ataque, defesa e um fator de aleatoriedade."""
    dano_base = max(0, atacante_ataque - defensor_defesa)
    # Se o dano base é 0, o dano real também deve ser 0.
    if dano_base == 0:
        return 0
    dano_real = random.randint(max(0, dano_base - 1), dano_base + 1)
    return max(0, dano_real) # Garante que o dano não seja negativo

def iniciar_combate(jogador, inimigo, usar_pocao_callback):
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
        print(f"Seu Ataque: {jogador['ataque']} | Sua Defesa: {jogador['defesa']}")
        print(f"Inimigo Ataque: {inimigo_atual['ataque']} | Inimigo Defesa: {inimigo_atual['defesa']}")
        print("-" * 15)
        print("O que você faz?")
        print("1. Atacar")
        print("2. Fugir")
        # Verifica se o jogador tem poções para oferecer a opção "Usar Poção"
        tem_pocao = any(item["tipo"] == "consumivel" and "hp" in item["efeito"] for item in jogador["inventario"])
        if tem_pocao:
            print("3. Usar Poção")
        
        escolha = input("> ")

        if escolha == "1": # Atacar
            # Turno do Jogador
            dano_real_jogador = calcular_dano(jogador["ataque"], inimigo_atual["defesa"])
            
            inimigo_atual["hp"] -= dano_real_jogador
            print(f"\nVocê ataca o {inimigo_atual['nome']} e causa {dano_real_jogador} de dano!")
            time.sleep(2)

            if inimigo_atual["hp"] <= 0:
                print(f"Você derrotou o {inimigo_atual['nome']}!")
                time.sleep(2)
                return True

            # Turno do Inimigo (se o inimigo ainda estiver vivo)
            dano_real_inimigo = calcular_dano(inimigo_atual["ataque"], jogador["defesa"])

            jogador["hp"] -= dano_real_inimigo
            print(f"O {inimigo_atual['nome']} ataca você e causa {dano_real_inimigo} de dano!")
            time.sleep(2)

            if jogador["hp"] <= 0:
                return False
        
        elif escolha == "2": # Fugir
            # Tenta fugir (50% de chance)
            if random.random() < 0.5:
                print("\nVocê conseguiu fugir!")
                time.sleep(2)
                return False # Consideramos fuga como uma "derrota" no contexto da sala
            else:
                print("\nA fuga falhou! Você perdeu sua vez.")
                time.sleep(2)
                # Turno do Inimigo após falha na fuga
                dano_real_inimigo = calcular_dano(inimigo_atual["ataque"], jogador["defesa"])

                jogador["hp"] -= dano_real_inimigo
                print(f"O {inimigo_atual['nome']} ataca você e causa {dano_real_inimigo} de dano!")
                time.sleep(2)

                if jogador["hp"] <= 0:
                    return False
        
        elif escolha == "3" and tem_pocao: # Usar Poção
            # Chama a função de callback para usar a poção
            # A função de callback deve retornar True se a poção foi usada, False caso contrário
            pocao_usada = usar_pocao_callback(jogador)
            if pocao_usada:
                # Se a poção foi usada, o inimigo ainda ataca
                dano_real_inimigo = calcular_dano(inimigo_atual["ataque"], jogador["defesa"])

                jogador["hp"] -= dano_real_inimigo
                print(f"O {inimigo_atual['nome']} ataca você e causa {dano_real_inimigo} de dano!")
                time.sleep(2)

                if jogador["hp"] <= 0:
                    return False
            else:
                # Se a poção não foi usada (ex: cancelou), o jogador não perde o turno
                print("Você não usou nenhuma poção.")
                time.sleep(1)
        else:
            print("\nOpção inválida! Tente novamente.")
            time.sleep(1)
    
    return False # Caso algo inesperado aconteça
