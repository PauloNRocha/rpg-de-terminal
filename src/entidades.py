"""Define as estruturas de dados centrais (dataclasses) do jogo."""

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from typing import Any

BRONZE_POR_PRATA = 10
BRONZE_POR_OURO = 100


@dataclass
class Moeda:
    """Armazena valores em bronze e formata em Ouro/Prata/Bronze."""

    valor_bronze: int = 0

    @classmethod
    def from_gp_sp_cp(cls, ouro: int = 0, prata: int = 0, bronze: int = 0) -> "Moeda":
        """Cria uma moeda a partir de valores individuais de ouro/prata/bronze."""
        total = ouro * BRONZE_POR_OURO + prata * BRONZE_POR_PRATA + bronze
        return cls(total)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | int | None) -> "Moeda":
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
        """Retorna o valor formatado como Ouro/Prata/Bronze legível."""
        restante = max(0, self.valor_bronze)
        ouro, restante = divmod(restante, BRONZE_POR_OURO)
        prata, bronze = divmod(restante, BRONZE_POR_PRATA)
        partes: list[str] = []
        if ouro:
            partes.append(f"{ouro} Ouro")
        if prata:
            partes.append(f"{prata} Prata")
        if bronze or not partes:
            partes.append(f"{bronze} Bronze")
        return ", ".join(partes)

    def adicionar(self, valor: int) -> None:
        """Incrementa (ou decrementa) o valor em bronze, nunca abaixo de zero."""
        self.valor_bronze = max(0, self.valor_bronze + valor)


@dataclass
class Item:
    """Representa um item no jogo, seja equipável ou consumível."""

    nome: str
    tipo: str  # "arma", "escudo", "consumivel"
    descricao: str
    bonus: dict[str, int] = field(default_factory=dict)  # {"ataque": 5}
    efeito: dict[str, int] = field(default_factory=dict)  # {"hp": 20}
    preco_bronze: int = 0

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
        payload.setdefault("preco_bronze", 0)
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
    carteira: Moeda = field(default_factory=Moeda)

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
        data["carteira"] = self.carteira.to_dict()
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
        carteira_raw = payload.pop("carteira", {"valor_bronze": 0})
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
            carteira=Moeda.from_dict(carteira_raw),
            **payload,
        )


@dataclass
class Sala:
    """Representa uma sala do mapa."""

    tipo: str
    nome: str
    descricao: str
    pode_ter_inimigo: bool = False
    visitada: bool = False
    inimigo_derrotado: bool = False
    inimigo_atual: Inimigo | None = None
    chefe: bool = False
    nivel_area: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Serializa a sala para dicionário, convertendo inimigos se necessário."""
        data = asdict(self)
        if self.inimigo_atual:
            data["inimigo_atual"] = self.inimigo_atual.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Sala":
        """Restaura uma sala a partir do dicionário serializado."""
        payload = data.copy()
        inimigo_raw = payload.get("inimigo_atual")
        if isinstance(inimigo_raw, dict):
            payload["inimigo_atual"] = Inimigo.from_dict(inimigo_raw)
        else:
            payload["inimigo_atual"] = None
        payload.setdefault("visitada", False)
        payload.setdefault("inimigo_derrotado", False)
        payload.setdefault("pode_ter_inimigo", False)
        payload.setdefault("chefe", False)
        payload.setdefault("nivel_area", 1)
        return cls(**payload)
