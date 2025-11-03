import random
import time
from src.ui import desenhar_tela_combate

def calcular_dano(ataque, defesa):
    """Calcula o dano de um ataque, com um fator de aleatoriedade."""
    variacao = random.uniform(0.8, 1.2)
    dano_bruto = ataque * variacao
    dano_final = max(0, dano_bruto - defesa)
    return int(dano_final)

def iniciar_combate(jogador, inimigo, usar_pocao_callback):
    """
    Inicia e gerencia um loop de combate por turnos com a nova UI.
    Retorna True se o jogador vencer, False se perder ou fugir.
    """
    log_combate = [f"Um {inimigo['nome']} selvagem aparece!"]
    inimigo['hp_max'] = inimigo['hp'] # Armazena o HP máximo para a barra de status

    while jogador["hp"] > 0 and inimigo["hp"] > 0:
        escolha = desenhar_tela_combate(jogador, inimigo, log_combate)

        if escolha == "1":
            # Turno do Jogador
            dano_causado = calcular_dano(jogador["ataque"], inimigo["defesa"])
            inimigo["hp"] -= dano_causado
            log_combate.append(f"Você ataca o {inimigo['nome']} e causa {dano_causado} de dano!")
            
            if inimigo["hp"] <= 0:
                log_combate.append(f"Você derrotou o {inimigo['nome']}!")
                desenhar_tela_combate(jogador, inimigo, log_combate)
                time.sleep(2)
                return True, inimigo # Retorna True e o inimigo derrotado

            # Turno do Inimigo
            dano_recebido = calcular_dano(inimigo["ataque"], jogador["defesa"])
            jogador["hp"] -= dano_recebido
            log_combate.append(f"O {inimigo['nome']} ataca e causa {dano_recebido} de dano em você!")

            if jogador["hp"] <= 0:
                log_combate.append("Você foi derrotado...")
                desenhar_tela_combate(jogador, inimigo, log_combate)
                time.sleep(2)
                return False, inimigo # Retorna False e o inimigo com HP restante

        elif escolha == "2":
            # Tenta usar uma poção
            if usar_pocao_callback(jogador):
                log_combate.append("Você usou uma poção e recuperou vida!")
                # Turno do Inimigo após usar item
                dano_recebido = calcular_dano(inimigo["ataque"], jogador["defesa"])
                jogador["hp"] -= dano_recebido
                log_combate.append(f"O {inimigo['nome']} ataca enquanto você se curava e causa {dano_recebido} de dano!")
            else:
                log_combate.append("Você não tem poções ou decidiu não usar.")
                continue # Permite que o jogador escolha outra ação

        elif escolha == "3":
            # Tenta fugir
            chance_de_fuga = 0.5
            if random.random() < chance_de_fuga:
                log_combate.append("Você conseguiu fugir!")
                desenhar_tela_combate(jogador, inimigo, log_combate)
                time.sleep(2)
                return False, inimigo # Retorna False e o inimigo com HP restante
            else:
                log_combate.append("Você tentou fugir, mas falhou!")
                # Turno do Inimigo após falha na fuga
                dano_recebido = calcular_dano(inimigo["ataque"], jogador["defesa"])
                jogador["hp"] -= dano_recebido
                log_combate.append(f"O {inimigo['nome']} ataca e causa {dano_recebido} de dano!")

        else:
            log_combate.append("Opção inválida! Tente novamente.")
            time.sleep(1)
    
    return jogador["hp"] > 0, inimigo # Retorna o resultado final e o inimigo com HP restante
