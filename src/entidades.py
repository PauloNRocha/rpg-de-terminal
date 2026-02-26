"""Define as estruturas de dados centrais (dataclasses) do jogo."""

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from typing import Any

from src.economia import Moeda


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
    drop_item_nome: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Retorna o dicionário da instância."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Inimigo":
        """Cria uma instância de Inimigo a partir de um dicionário."""
        payload = data.copy()
        payload.setdefault("drop_item_nome", None)
        return cls(**payload)


@dataclass
class Motivacao:
    """Motivação narrativa do personagem."""

    id: str
    titulo: str
    descricao: str

    def to_dict(self) -> dict[str, Any]:
        """Serializa a motivação."""
        return asdict(self)


@dataclass
class StatusTemporario:
    """Bônus ou penalidade que dura um número limitado de combates."""

    atributo: str
    valor: int
    combates_restantes: int
    descricao: str = ""


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
    status_temporarios: list[StatusTemporario] = field(default_factory=list)
    motivacao: Motivacao | None = None

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
        data["status_temporarios"] = [
            {
                "atributo": s.atributo,
                "valor": s.valor,
                "combates_restantes": s.combates_restantes,
                "descricao": s.descricao,
            }
            for s in self.status_temporarios
        ]
        if self.motivacao:
            data["motivacao"] = self.motivacao.to_dict()
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
        status_raw = payload.pop("status_temporarios", [])
        motivacao_raw = payload.pop("motivacao", None)

        inventario: list[Item] = []
        for item_data in inventario_raw:
            item = _hidratar_item(item_data)
            if item:
                inventario.append(item)

        equipamento = {
            "arma": _hidratar_item(equipamento_raw.get("arma")),
            "escudo": _hidratar_item(equipamento_raw.get("escudo")),
        }
        status_temporarios: list[StatusTemporario] = []
        for status in status_raw:
            if isinstance(status, Mapping):
                try:
                    status_temporarios.append(
                        StatusTemporario(
                            atributo=str(status.get("atributo", "")).lower(),
                            valor=int(status.get("valor", 0)),
                            combates_restantes=int(status.get("combates_restantes", 0)),
                            descricao=str(status.get("descricao", "")),
                        )
                    )
                except ValueError:
                    continue
        motivacao_obj = None
        if isinstance(motivacao_raw, Mapping):
            try:
                motivacao_obj = Motivacao(
                    id=str(motivacao_raw.get("id", "")),
                    titulo=str(motivacao_raw.get("titulo", "")),
                    descricao=str(motivacao_raw.get("descricao", "")),
                )
            except ValueError:
                motivacao_obj = None

        return cls(
            inventario=inventario,
            equipamento=equipamento,
            carteira=Moeda.from_dict(carteira_raw),
            status_temporarios=status_temporarios,
            motivacao=motivacao_obj,
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
    chefe_id: str | None = None
    chefe_tipo: str | None = None
    chefe_nome: str | None = None
    chefe_descricao: str | None = None
    chefe_titulo: str | None = None
    chefe_historia: str | None = None
    chefe_intro_exibida: bool = False
    trama_id: str | None = None
    trama_nome: str | None = None
    trama_desfecho: str | None = None
    trama_texto: str | None = None
    trama_resolvida: bool = False
    trama_inimigo_tipo: str | None = None
    nivel_area: int = 1
    evento_id: str | None = None
    evento_resolvido: bool = False

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
        payload.setdefault("chefe_id", None)
        payload.setdefault("chefe_tipo", None)
        payload.setdefault("chefe_nome", None)
        payload.setdefault("chefe_descricao", None)
        payload.setdefault("chefe_titulo", None)
        payload.setdefault("chefe_historia", None)
        payload.setdefault("chefe_intro_exibida", False)
        payload.setdefault("trama_id", None)
        payload.setdefault("trama_nome", None)
        payload.setdefault("trama_desfecho", None)
        payload.setdefault("trama_texto", None)
        payload.setdefault("trama_resolvida", False)
        payload.setdefault("trama_inimigo_tipo", None)
        payload.setdefault("nivel_area", 1)
        payload.setdefault("evento_id", None)
        payload.setdefault("evento_resolvido", False)
        return cls(**payload)
