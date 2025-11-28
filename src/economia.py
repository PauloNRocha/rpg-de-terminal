"""Rotinas e estruturas relacionadas à economia do jogo."""

from __future__ import annotations

import random
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from src import config

if TYPE_CHECKING:
    from src.entidades import Item, Personagem

BRONZE_POR_PRATA = 10
BRONZE_POR_OURO = 100


@dataclass
class Moeda:
    """Armazena valores monetários sempre em bronze."""

    valor_bronze: int = 0

    @classmethod
    def from_gp_sp_cp(cls, ouro: int = 0, prata: int = 0, bronze: int = 0) -> Moeda:
        """Cria uma moeda a partir de valores individuais de ouro/prata/bronze."""
        total = ouro * BRONZE_POR_OURO + prata * BRONZE_POR_PRATA + bronze
        return cls(total)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | int | None) -> Moeda:
        """Reconstrói a moeda a partir do dicionário serializado."""
        if isinstance(data, Mapping):
            valor = int(data.get("valor_bronze", 0))
        elif data is None:
            valor = 0
        else:
            valor = int(data)
        return cls(valor)

    def to_dict(self) -> dict[str, int]:
        """Serializa o valor em bronze."""
        return {"valor_bronze": self.valor_bronze}

    def formatar(self) -> str:
        """Retorna o valor formatado exibindo sempre Ouro/Prata/Bronze."""
        restante = max(0, self.valor_bronze)
        ouro, restante = divmod(restante, BRONZE_POR_OURO)
        prata, bronze = divmod(restante, BRONZE_POR_PRATA)
        return f"{ouro} Ouro, {prata} Prata, {bronze} Bronze"

    def receber(self, valor: int) -> None:
        """Ganha moedas (ou corrige perdas), sem deixar o total negativo."""
        self.valor_bronze = max(0, self.valor_bronze + valor)

    def gastar(self, valor: int) -> bool:
        """Tenta gastar o valor informado; retorna True ao conseguir."""
        if valor < 0:
            raise ValueError("Valor a debitar deve ser não negativo.")
        if self.valor_bronze >= valor:
            self.valor_bronze -= valor
            return True
        return False

    def tem(self, valor: int) -> bool:
        """Informa se há moedas suficientes para a transação."""
        return self.valor_bronze >= max(0, valor)


def formatar_preco(valor_bronze: int) -> str:
    """Formata um preço independente de uma instância de Moeda."""
    return Moeda(valor_bronze).formatar()


def calcular_moedas_saque(raridade: str | None, nivel_masmorra: int) -> int:
    """Calcula o saque de moedas ao vencer um inimigo."""
    chave = (raridade or "default").lower()
    minimo, maximo = config.COIN_DROP_FAIXAS.get(chave, config.COIN_DROP_FAIXAS["default"])
    base = random.randint(minimo, maximo)
    bonus = int(base * config.COIN_DROP_ESCALONAMENTO * max(0, nivel_masmorra - 1))
    return base + bonus


def preco_item(item: Item) -> int:
    """Retorna o preço em bronze (nunca negativo)."""
    preco = getattr(item, "preco_bronze", 0)
    try:
        preco_int = int(preco)
    except (TypeError, ValueError):
        preco_int = 0
    return max(0, preco_int)


def pode_comprar(personagem: Personagem, item: Item) -> bool:
    """Indica se a carteira cobre o preço do item."""
    return personagem.carteira.tem(preco_item(item))


def comprar_item(personagem: Personagem, item: Item) -> bool:
    """Deduz o preço e adiciona o item ao inventário quando possível."""
    valor = preco_item(item)
    if not personagem.carteira.gastar(valor):
        return False
    personagem.inventario.append(item)
    return True
