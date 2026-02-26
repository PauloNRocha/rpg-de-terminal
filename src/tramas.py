"""Sistema data-driven de tramas narrativas da masmorra."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.erros import ErroDadosError

_CAMINHO_TRAMAS = Path(__file__).parent / "data" / "tramas.json"


@dataclass(frozen=True)
class TramaConfig:
    """Definição estática de uma trama carregada do JSON."""

    id: str
    nome: str
    tema: str
    motivacoes: tuple[str, ...]
    andar_min: int
    andar_max: int
    pistas: tuple[str, ...]
    sala_nome: str
    sala_descricao: str
    desfechos: dict[str, tuple[str, ...]]
    inimigo_corrompido_tipo: str | None = None


@dataclass
class TramaAtiva:
    """Estado de uma trama ativa durante a run."""

    id: str
    nome: str
    tema: str
    motivacao_id: str | None
    andar_alvo: int
    desfecho: str
    desfecho_texto: str
    sala_nome: str
    sala_descricao: str
    pistas: tuple[str, ...]
    inimigo_corrompido_tipo: str | None = None
    concluida: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serializa a trama ativa para save JSON."""
        return {
            "id": self.id,
            "nome": self.nome,
            "tema": self.tema,
            "motivacao_id": self.motivacao_id,
            "andar_alvo": self.andar_alvo,
            "desfecho": self.desfecho,
            "desfecho_texto": self.desfecho_texto,
            "sala_nome": self.sala_nome,
            "sala_descricao": self.sala_descricao,
            "pistas": list(self.pistas),
            "inimigo_corrompido_tipo": self.inimigo_corrompido_tipo,
            "concluida": self.concluida,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TramaAtiva:
        """Restaura uma trama ativa a partir do save."""
        pistas_raw = data.get("pistas")
        pistas = tuple(str(p) for p in pistas_raw) if isinstance(pistas_raw, list) else ()
        return cls(
            id=str(data.get("id", "")),
            nome=str(data.get("nome", "Trama")),
            tema=str(data.get("tema", "mistério")),
            motivacao_id=(
                str(data.get("motivacao_id")) if data.get("motivacao_id") is not None else None
            ),
            andar_alvo=max(1, int(data.get("andar_alvo", 1))),
            desfecho=str(data.get("desfecho", "morto")),
            desfecho_texto=str(data.get("desfecho_texto", "")),
            sala_nome=str(data.get("sala_nome", "Sala de Trama")),
            sala_descricao=str(data.get("sala_descricao", "")),
            pistas=pistas,
            inimigo_corrompido_tipo=(
                str(data.get("inimigo_corrompido_tipo"))
                if data.get("inimigo_corrompido_tipo") is not None
                else None
            ),
            concluida=bool(data.get("concluida", False)),
        )


_CACHE_TRAMAS: list[TramaConfig] | None = None


def carregar_tramas() -> list[TramaConfig]:
    """Carrega e valida o catálogo de tramas."""
    global _CACHE_TRAMAS
    if _CACHE_TRAMAS is not None:
        return _CACHE_TRAMAS

    try:
        dados = json.loads(_CAMINHO_TRAMAS.read_text(encoding="utf-8"))
    except FileNotFoundError as erro:
        raise ErroDadosError("Arquivo 'tramas.json' não encontrado em src/data/.") from erro
    except json.JSONDecodeError as erro:
        raise ErroDadosError("Arquivo 'tramas.json' inválido (JSON malformado).") from erro

    if not isinstance(dados, list) or not dados:
        raise ErroDadosError("Arquivo 'tramas.json' deve ser uma lista com tramas válidas.")

    tramas: list[TramaConfig] = []
    for item in dados:
        if not isinstance(item, dict) or "id" not in item or "desfechos" not in item:
            raise ErroDadosError("Entrada inválida em 'tramas.json'.")

        andar_cfg = item.get("andar_alvo", {})
        if not isinstance(andar_cfg, dict):
            raise ErroDadosError("Campo 'andar_alvo' inválido em uma trama.")
        andar_min = max(1, int(andar_cfg.get("min", 2)))
        andar_max = max(andar_min, int(andar_cfg.get("max", andar_min)))

        pistas_raw = item.get("pistas")
        if not isinstance(pistas_raw, list) or not pistas_raw:
            raise ErroDadosError("Toda trama precisa de ao menos uma pista em 'pistas'.")
        pistas = tuple(str(p) for p in pistas_raw)

        motivacoes_raw = item.get("motivacoes", ["*"])
        if not isinstance(motivacoes_raw, list) or not motivacoes_raw:
            motivacoes_raw = ["*"]
        motivacoes = tuple(str(m).lower() for m in motivacoes_raw)

        desfechos_raw = item.get("desfechos", {})
        if not isinstance(desfechos_raw, dict) or not desfechos_raw:
            raise ErroDadosError("Toda trama precisa de desfechos válidos.")

        desfechos: dict[str, tuple[str, ...]] = {}
        for chave, textos in desfechos_raw.items():
            if not isinstance(textos, list) or not textos:
                continue
            desfechos[str(chave).lower()] = tuple(str(t) for t in textos)

        if not desfechos:
            raise ErroDadosError("Nenhum desfecho válido encontrado em uma trama.")

        tramas.append(
            TramaConfig(
                id=str(item["id"]),
                nome=str(item.get("nome", item["id"])),
                tema=str(item.get("tema", "mistério")),
                motivacoes=motivacoes,
                andar_min=andar_min,
                andar_max=andar_max,
                pistas=pistas,
                sala_nome=str(item.get("sala_nome", "Sala de Trama")),
                sala_descricao=str(item.get("sala_descricao", "")),
                desfechos=desfechos,
                inimigo_corrompido_tipo=(
                    str(item.get("inimigo_corrompido_tipo"))
                    if item.get("inimigo_corrompido_tipo") is not None
                    else None
                ),
            )
        )

    _CACHE_TRAMAS = tramas
    return tramas


def sortear_trama_para_motivacao(motivacao_id: str | None) -> TramaAtiva | None:
    """Sorteia uma trama para a motivação recebida."""
    tramas = carregar_tramas()
    if not tramas:
        return None

    motivacao_norm = (motivacao_id or "").lower()
    candidatas_diretas = [t for t in tramas if motivacao_norm and motivacao_norm in t.motivacoes]
    candidatas_curinga = [t for t in tramas if "*" in t.motivacoes]
    candidatas = candidatas_diretas or candidatas_curinga or tramas

    cfg = random.choice(candidatas)
    andar_alvo = random.randint(cfg.andar_min, cfg.andar_max)
    desfechos_disponiveis = [ch for ch, textos in cfg.desfechos.items() if textos]
    desfecho = random.choice(desfechos_disponiveis)
    desfecho_texto = random.choice(cfg.desfechos[desfecho])

    return TramaAtiva(
        id=cfg.id,
        nome=cfg.nome,
        tema=cfg.tema,
        motivacao_id=motivacao_id,
        andar_alvo=andar_alvo,
        desfecho=desfecho,
        desfecho_texto=desfecho_texto,
        sala_nome=cfg.sala_nome,
        sala_descricao=cfg.sala_descricao,
        pistas=cfg.pistas,
        inimigo_corrompido_tipo=cfg.inimigo_corrompido_tipo,
    )


def gerar_pista_trama(trama: TramaAtiva, nivel_atual: int) -> str:
    """Gera uma pista textual da trama ativa para o andar atual."""
    if not trama.pistas:
        return f"Você encontra sinais de que o alvo desta jornada está no andar {trama.andar_alvo}."

    pista = random.choice(list(trama.pistas))
    return pista.format(andar_alvo=trama.andar_alvo, nivel_atual=nivel_atual)
