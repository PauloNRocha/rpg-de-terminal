import random
import time
from collections.abc import Callable

from src.entidades import Inimigo, Personagem
from src.ui import desenhar_tela_combate


def calcular_dano(ataque: int, defesa: int) -> int:
    """Calcula o dano de um ataque, com um fator de aleatoriedade."""
    variacao = random.uniform(0.8, 1.2)
    dano_bruto = ataque * variacao
    dano_final = max(0, dano_bruto - defesa)
    if dano_final <= 0 and ataque > 0:
        # Garante progresso no combate, evitando lutas infinitas por defesa alta.
        return 1
    return int(dano_final)


def iniciar_combate(
    jogador: Personagem, inimigo: Inimigo, usar_item_callback: Callable[[Personagem], bool]
) -> tuple[bool, Inimigo]:
    """Inicia e gerencia um loop de combate por turnos com a nova UI."""
    log_combate = [f"Um {inimigo.nome} selvagem aparece!"]

    while jogador.esta_vivo() and inimigo.esta_vivo():
        escolha = desenhar_tela_combate(jogador, inimigo, log_combate)

        if escolha == "1":
            # Turno do Jogador
            dano_causado = calcular_dano(jogador.ataque, inimigo.defesa)
            inimigo.hp -= dano_causado
            log_combate.append(f"Você ataca o {inimigo.nome} e causa {dano_causado} de dano!")

            if not inimigo.esta_vivo():
                log_combate.append(f"Você derrotou o {inimigo.nome}!")
                break

            # Turno do Inimigo
            dano_recebido = calcular_dano(inimigo.ataque, jogador.defesa)
            jogador.hp -= dano_recebido
            log_combate.append(f"O {inimigo.nome} ataca e causa {dano_recebido} de dano em você!")

            if not jogador.esta_vivo():
                log_combate.append("Você foi derrotado...")
                break

        elif escolha == "2":
            if usar_item_callback(jogador):
                log_combate.append("Você usou um item e recuperou vida!")
                # Turno do Inimigo após usar item
                dano_recebido = calcular_dano(inimigo.ataque, jogador.defesa)
                jogador.hp -= dano_recebido
                mensagem_ataque = (
                    f"O {inimigo.nome} ataca enquanto você se curava e "
                    f"causa {dano_recebido} de dano!"
                )
                log_combate.append(mensagem_ataque)
            else:
                log_combate.append("Você não tem itens consumíveis ou decidiu não usar.")
                continue

        elif escolha == "3":
            chance_de_fuga = 0.5
            if random.random() < chance_de_fuga:
                log_combate.append("Você conseguiu fugir!")
                desenhar_tela_combate(jogador, inimigo, log_combate)
                time.sleep(2)
                return False, inimigo
            log_combate.append("Você tentou fugir, mas falhou!")
            # Turno do Inimigo após falha na fuga
            dano_recebido = calcular_dano(inimigo.ataque, jogador.defesa)
            jogador.hp -= dano_recebido
            log_combate.append(f"O {inimigo.nome} ataca e causa {dano_recebido} de dano!")

        else:
            log_combate.append("Opção inválida! Tente novamente.")
            time.sleep(1)

    return jogador.esta_vivo(), inimigo
