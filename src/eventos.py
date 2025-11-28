"""Carregamento e execução de eventos de sala."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

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
        evento = Evento(
            id=item["id"],
            nome=item.get("nome", item["id"].title()),
            descricao=item.get("descricao", ""),
            efeitos=item.get("efeitos", {}),
            opcoes=item.get("opcoes", []),
        )
        _cache[evento.id] = evento
    return _cache


def sortear_evento_id() -> str | None:
    """Retorna um ID aleatório dentre os eventos disponíveis."""
    eventos = list(carregar_eventos().values())
    if not eventos:
        return None
    import random

    return random.choice(eventos).id


def disparar_evento(
    evento_id: str, jogador: Personagem, multiplicador_moedas: float = 1.0
) -> tuple[str, str]:
    """Executa o evento informado aplicando seus efeitos ao jogador."""
    evento = carregar_eventos().get(evento_id)
    if not evento:
        return ("EVENTO", "Nada acontece.")
    efeitos = evento.efeitos or {}
    mensagens, _ = aplicar_efeitos(efeitos, jogador, multiplicador_moedas)
    return evento.nome.upper(), "\n".join(mensagens)


def aplicar_efeitos(
    efeitos: dict[str, Any], jogador: Personagem, multiplicador_moedas: float = 1.0
) -> tuple[list[str], int]:
    """Aplica efeitos de evento ou opção ao jogador e retorna mensagens e moedas ganhas."""
    mensagens: list[str] = []
    hp_delta = int(efeitos.get("hp", 0))
    if hp_delta:
        jogador.hp = max(0, min(jogador.hp_max, jogador.hp + hp_delta))
        if hp_delta > 0:
            mensagens.append(f"Você recuperou {hp_delta} de HP.")
        else:
            mensagens.append(f"Você perdeu {abs(hp_delta)} de HP.")
    moedas_base = int(efeitos.get("moedas", 0))
    moedas = round(max(0, moedas_base) * max(0.0, multiplicador_moedas))
    if moedas == 0 and moedas_base > 0:
        moedas = 1
    if moedas:
        jogador.carteira.receber(moedas)
        mensagens.append(f"Você recebeu {formatar_preco(moedas)}.")
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
    return mensagens, moedas
