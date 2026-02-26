"""Carregamento e execução de eventos de sala."""

from __future__ import annotations

import json
import random
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from src import config
from src.economia import formatar_preco
from src.erros import ErroDadosError
from src.personagem_utils import adicionar_status_temporario

if TYPE_CHECKING:
    from src.entidades import Personagem

CAMINHO_EVENTOS = Path(__file__).parent / "data" / "eventos.json"


@dataclass
class Evento:
    """Evento carregado do JSON de dados."""

    id: str
    nome: str
    descricao: str
    efeitos: dict[str, Any]
    opcoes: list[dict[str, Any]]
    tags: tuple[str, ...] = ()


_cache: dict[str, Evento] = {}


def carregar_eventos() -> dict[str, Evento]:
    """Carrega os eventos do arquivo JSON (com cache)."""
    if _cache:
        return _cache
    try:
        dados = json.loads(CAMINHO_EVENTOS.read_text(encoding="utf-8"))
    except FileNotFoundError as erro:
        raise ErroDadosError("Arquivo 'eventos.json' não encontrado.") from erro
    except json.JSONDecodeError as erro:
        raise ErroDadosError("Arquivo 'eventos.json' inválido.") from erro
    if not isinstance(dados, list):
        raise ErroDadosError("Arquivo 'eventos.json' deve ser uma lista de eventos.")
    for item in dados:
        if not isinstance(item, dict) or "id" not in item:
            raise ErroDadosError("Evento inválido em 'eventos.json'.")
        tags_raw = item.get("tags", [])
        if not isinstance(tags_raw, list):
            tags_raw = []
        evento = Evento(
            id=item["id"],
            nome=item.get("nome", item["id"].title()),
            descricao=item.get("descricao", ""),
            efeitos=item.get("efeitos", {}),
            opcoes=item.get("opcoes", []),
            tags=tuple(
                _normalizar_tag(str(tag))
                for tag in tags_raw
                if isinstance(tag, str) and tag.strip()
            ),
        )
        _cache[evento.id] = evento
    return _cache


def sortear_evento_id(tema: str | None = None) -> str | None:
    """Retorna um ID aleatório dentre os eventos disponíveis."""
    eventos = list(carregar_eventos().values())
    if not eventos:
        return None
    if not tema:
        return random.choice(eventos).id

    tema_norm = _normalizar_tag(tema)
    pesos = [
        config.TEMA_PESO_EVENTO_COMPATIVEL if tema_norm in evento.tags else 1.0
        for evento in eventos
    ]
    if all(peso == 1.0 for peso in pesos):
        return random.choice(eventos).id
    return random.choices(eventos, weights=pesos, k=1)[0].id


def disparar_evento(
    evento_id: str, jogador: Personagem, multiplicador_moedas: float = 1.0
) -> tuple[str, str]:
    """Executa o evento informado aplicando seus efeitos ao jogador."""
    evento = carregar_eventos().get(evento_id)
    if not evento:
        return ("EVENTO", "Nada acontece.")
    efeitos = evento.efeitos or {}
    mensagens, _, _ = aplicar_efeitos(efeitos, jogador, multiplicador_moedas)
    return evento.nome.upper(), "\n".join(mensagens)


def aplicar_efeitos(
    efeitos: dict[str, Any], jogador: Personagem, multiplicador_moedas: float = 1.0
) -> tuple[list[str], int, bool]:
    """Aplica efeitos de evento/ação.

    Retorna (mensagens, moedas_ganhas, sucesso). Sucesso=False indica que a
    execução foi abortada (ex.: custo em moedas não pago).
    """
    mensagens: list[str] = []
    sucesso = True

    # Moedas: valores negativos representam custo
    moedas_base = int(efeitos.get("moedas", 0))
    if moedas_base < 0:
        custo = abs(moedas_base)
        if not jogador.carteira.tem(custo):
            mensagens.append(
                "Você não tem moedas suficientes para realizar essa ação.\n"
                f"Custo: {formatar_preco(custo)} | "
                f"Seu saldo: {jogador.carteira.formatar()}"
            )
            return mensagens, 0, False
        jogador.carteira.gastar(custo)
        mensagens.append(f"Você sacrificou {formatar_preco(custo)}.")
        moedas_delta = -custo
    else:
        moedas = round(max(0, moedas_base) * max(0.0, multiplicador_moedas))
        if moedas == 0 and moedas_base > 0:
            moedas = 1
        moedas_delta = moedas
        if moedas_delta:
            jogador.carteira.receber(moedas_delta)
            mensagens.append(f"Você recebeu {formatar_preco(moedas_delta)}.")

    # HP
    hp_delta = int(efeitos.get("hp", 0))
    if hp_delta:
        jogador.hp = max(0, min(jogador.hp_max, jogador.hp + hp_delta))
        if hp_delta > 0:
            mensagens.append(f"Você recuperou {hp_delta} de HP.")
        else:
            mensagens.append(f"Você perdeu {abs(hp_delta)} de HP.")

    buffs = efeitos.get("buffs", [])
    for buff in buffs:
        atributo = str(buff.get("atributo", "")).lower()
        valor = int(buff.get("valor", 0))
        duracao = int(buff.get("duracao_combates", 0))
        descricao = buff.get("descricao")
        status = adicionar_status_temporario(jogador, atributo, valor, duracao, descricao)
        if status:
            if valor > 0:
                mensagens.append(
                    buff.get("mensagem")
                    or f"Você recebeu +{valor} de {atributo} por {duracao} combates."
                )
            else:
                mensagens.append(
                    buff.get("mensagem")
                    or f"Você sofreu {valor} em {atributo} por {duracao} combates."
                )
    return mensagens, moedas_delta, sucesso


def _normalizar_tag(tag: str) -> str:
    """Normaliza tags removendo acentos e padronizando caixa."""
    texto = unicodedata.normalize("NFKD", tag.strip().lower())
    return "".join(ch for ch in texto if not unicodedata.combining(ch))
