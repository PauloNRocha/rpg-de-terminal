"""Funções utilitárias para manipular atributos do personagem."""

from __future__ import annotations

from src.entidades import Personagem, StatusTemporario


def aplicar_bonus_equipamento(jogador: Personagem) -> None:
    """Recalcula ataque e defesa com base em equipamento e status temporários."""
    jogador.ataque = jogador.ataque_base
    jogador.defesa = jogador.defesa_base

    arma = jogador.equipamento.get("arma") if jogador.equipamento else None
    if arma:
        jogador.ataque += arma.bonus.get("ataque", 0)
        jogador.defesa += arma.bonus.get("defesa", 0)

    escudo = jogador.equipamento.get("escudo") if jogador.equipamento else None
    if escudo:
        jogador.ataque += escudo.bonus.get("ataque", 0)
        jogador.defesa += escudo.bonus.get("defesa", 0)

    for status in jogador.status_temporarios:
        if status.atributo == "ataque":
            jogador.ataque += status.valor
        elif status.atributo == "defesa":
            jogador.defesa += status.valor

    jogador.ataque = max(0, jogador.ataque)
    jogador.defesa = max(0, jogador.defesa)


def adicionar_status_temporario(
    jogador: Personagem,
    atributo: str,
    valor: int,
    duracao: int,
    descricao: str | None = None,
) -> StatusTemporario | None:
    """Adiciona um status temporário válido ao personagem."""
    atributo = atributo.lower()
    if atributo not in {"ataque", "defesa"} or valor == 0 or duracao <= 0:
        return None
    status = StatusTemporario(
        atributo=atributo,
        valor=valor,
        combates_restantes=duracao,
        descricao=descricao or "",
    )
    jogador.status_temporarios.append(status)
    aplicar_bonus_equipamento(jogador)
    return status


def consumir_status_temporarios(jogador: Personagem, decremento: int = 1) -> None:
    """Reduz a duração dos status após um combate e remove expirados."""
    if decremento <= 0 or not jogador.status_temporarios:
        return
    ativos: list[StatusTemporario] = []
    for status in jogador.status_temporarios:
        status.combates_restantes = max(0, status.combates_restantes - decremento)
        if status.combates_restantes > 0:
            ativos.append(status)
    jogador.status_temporarios = ativos
    aplicar_bonus_equipamento(jogador)
