"""Define as estruturas de dados centrais (dataclasses) do jogo."""

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Item:
    """Representa um item no jogo, seja equipável ou consumível."""

    nome: str
    tipo: str  # "arma", "escudo", "consumivel"
    descricao: str
    bonus: dict[str, int] = field(default_factory=dict)  # {"ataque": 5}
    efeito: dict[str, int] = field(default_factory=dict)  # {"hp": 20}

    def to_dict(self) -> dict[str, Any]:
        """Retorna o dicionário da instância."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Item":
        """Cria uma instância de Item a partir de um dicionário."""
        payload = data.copy()
        payload.setdefault("descricao", "")
        payload.setdefault("bonus", {})
        payload.setdefault("efeito", {})
        return cls(**payload)


@dataclass
class Entidade:
    """Classe base para Jogador e Inimigo."""

    nome: str
    hp: int
    hp_max: int
    ataque: int
    defesa: int

    def esta_vivo(self) -> bool:
        """Verifica se a entidade ainda tem pontos de vida."""
        return self.hp > 0


@dataclass
class Inimigo(Entidade):
    """Representa um inimigo no jogo."""

    xp_recompensa: int
    drop_raridade: str

    def to_dict(self) -> dict[str, Any]:
        """Retorna o dicionário da instância."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Inimigo":
        """Cria uma instância de Inimigo a partir de um dicionário."""
        return cls(**data)


@dataclass
class Personagem(Entidade):
    """Representa o personagem do jogador."""

    classe: str
    ataque_base: int
    defesa_base: int
    x: int
    y: int
    nivel: int
    xp_atual: int
    xp_para_proximo_nivel: int
    inventario: list[Item] = field(default_factory=list)
    equipamento: dict[str, Item | None] = field(
        default_factory=lambda: {"arma": None, "escudo": None}
    )

    def to_dict(self) -> dict[str, Any]:
        """Retorna o dicionário da instância.

        Inclui equipamento e inventário.
        """
        data = asdict(self)
        data["equipamento"]["arma"] = (
            self.equipamento["arma"].to_dict() if self.equipamento["arma"] else None
        )
        data["equipamento"]["escudo"] = (
            self.equipamento["escudo"].to_dict() if self.equipamento["escudo"] else None
        )
        data["inventario"] = [item.to_dict() for item in self.inventario]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Personagem":
        """Cria uma instância de Personagem a partir de um dicionário serializado."""

        def _hidratar_item(item_raw: Item | Mapping[str, Any] | None) -> Item | None:
            if isinstance(item_raw, Item):
                return item_raw
            if isinstance(item_raw, dict):
                return Item.from_dict(item_raw)
            return None

        payload = data.copy()
        inventario_raw = payload.pop("inventario", [])
        equipamento_raw = payload.pop("equipamento", {"arma": None, "escudo": None}) or {
            "arma": None,
            "escudo": None,
        }

        inventario: list[Item] = []
        for item_data in inventario_raw:
            item = _hidratar_item(item_data)
            if item:
                inventario.append(item)

        equipamento = {
            "arma": _hidratar_item(equipamento_raw.get("arma")),
            "escudo": _hidratar_item(equipamento_raw.get("escudo")),
        }

        return cls(
            inventario=inventario,
            equipamento=equipamento,
            **payload,
        )
