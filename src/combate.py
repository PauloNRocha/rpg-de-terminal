import random
import time
from collections.abc import Callable

from src import atualizador
from src.entidades import Inimigo, Personagem
from src.ui import desenhar_log_completo, desenhar_tela_combate


def calcular_dano(ataque: int, defesa: int) -> int:
    """Calcula o dano de um ataque, com um fator de aleatoriedade."""
    dano, _ = _calcular_dano_com_detalhes(ataque, defesa)
    return dano


def _calcular_dano_com_detalhes(ataque: int, defesa: int) -> tuple[int, str]:
    """Retorne o dano e o breakdown do cálculo para logs detalhados."""
    variacao = random.uniform(0.8, 1.2)
    dano_bruto = ataque * variacao
    dano_sem_piso = max(0, int(dano_bruto - defesa))
    piso_aplicado = dano_sem_piso <= 0 and ataque > 0
    # Garante progresso no combate, evitando lutas infinitas por defesa alta.
    dano_final = 1 if piso_aplicado else dano_sem_piso
    detalhe = f"(ATK {ataque} x {variacao:.2f} - DEF {defesa} -> {dano_final}" + (
        ", piso mínimo)" if piso_aplicado else ")"
    )
    return dano_final, detalhe


def _breakdown_ativo() -> bool:
    """Leia preferência de breakdown de dano para o log de combate."""
    try:
        preferencias = atualizador.carregar_preferencias()
    except (OSError, ValueError):
        return False
    return bool(preferencias.get("combat_log_breakdown", False))


def iniciar_combate(
    jogador: Personagem, inimigo: Inimigo, usar_item_callback: Callable[[Personagem], bool]
) -> tuple[bool, Inimigo]:
    """Inicia e gerencia um loop de combate por turnos com a nova UI."""
    log_combate = [f"Um {inimigo.nome} selvagem aparece!"]
    mostrar_breakdown = _breakdown_ativo()

    while jogador.esta_vivo() and inimigo.esta_vivo():
        escolha = desenhar_tela_combate(jogador, inimigo, log_combate)

        if escolha.lower() == "l":
            desenhar_log_completo(log_combate)
            continue

        if escolha == "1":
            # Turno do Jogador
            dano_causado, detalhe_ataque = _calcular_dano_com_detalhes(
                jogador.ataque, inimigo.defesa
            )
            inimigo.hp -= dano_causado
            msg_ataque = f"Você ataca o {inimigo.nome} e causa {dano_causado} de dano!"
            if mostrar_breakdown:
                msg_ataque = f"{msg_ataque} {detalhe_ataque}"
            log_combate.append(msg_ataque)

            if not inimigo.esta_vivo():
                log_combate.append(f"Você derrotou o {inimigo.nome}!")
                break

            # Turno do Inimigo
            dano_recebido, detalhe_defesa = _calcular_dano_com_detalhes(
                inimigo.ataque, jogador.defesa
            )
            jogador.hp -= dano_recebido
            msg_defesa = f"O {inimigo.nome} ataca e causa {dano_recebido} de dano em você!"
            if mostrar_breakdown:
                msg_defesa = f"{msg_defesa} {detalhe_defesa}"
            log_combate.append(msg_defesa)

            if not jogador.esta_vivo():
                log_combate.append("Você foi derrotado...")
                break

        elif escolha == "2":
            if usar_item_callback(jogador):
                log_combate.append("Você usou um item e recuperou vida!")
                # Turno do Inimigo após usar item
                dano_recebido, detalhe_defesa = _calcular_dano_com_detalhes(
                    inimigo.ataque, jogador.defesa
                )
                jogador.hp -= dano_recebido
                mensagem_ataque = (
                    f"O {inimigo.nome} ataca enquanto você se curava e "
                    f"causa {dano_recebido} de dano!"
                )
                if mostrar_breakdown:
                    mensagem_ataque = f"{mensagem_ataque} {detalhe_defesa}"
                log_combate.append(mensagem_ataque)
            else:
                log_combate.append("Você não tem itens consumíveis ou decidiu não usar.")
                continue

        elif escolha == "3":
            chance_de_fuga = 0.5
            if random.random() < chance_de_fuga:
                log_combate.append("Você conseguiu fugir!")
                # Não pedimos nova entrada aqui; apenas mostramos feedback rápido
                # para então retornar ao estado de exploração.
                # (Desenhar a tela de combate novamente forçava o jogador a digitar
                # outra ação mesmo após escapar.)
                time.sleep(1)
                return False, inimigo
            log_combate.append("Você tentou fugir, mas falhou!")
            # Turno do Inimigo após falha na fuga
            dano_recebido, detalhe_defesa = _calcular_dano_com_detalhes(
                inimigo.ataque, jogador.defesa
            )
            jogador.hp -= dano_recebido
            msg_fuga = f"O {inimigo.nome} ataca e causa {dano_recebido} de dano!"
            if mostrar_breakdown:
                msg_fuga = f"{msg_fuga} {detalhe_defesa}"
            log_combate.append(msg_fuga)

        else:
            log_combate.append("Opção inválida! Tente novamente.")
            time.sleep(1)

    return jogador.esta_vivo(), inimigo
