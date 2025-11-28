"""Gerencia o salvamento e o carregamento do jogo em disco (agora com múltiplos slots)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src import config
from src.version import __version__

DiretorioSalvamento = Path
EstadoJogo = dict[str, Any]

_DIRETORIO_SALVAMENTO: DiretorioSalvamento = Path("saves")
_ARQUIVO_SALVAMENTO: Path = _DIRETORIO_SALVAMENTO / "save.json"
_PADRAO_NOME_SLOT = "save_{slot}.json"


@dataclass
class SaveInfo:
    """Representa metadados de um slot de save."""

    slot_id: str
    caminho: Path
    personagem: str
    classe: str
    nivel: int
    andar: int
    dificuldade: str
    salvo_em: str
    versao: str


class ErroCarregamento(RuntimeError):  # noqa: N818
    """Erro específico disparado quando o arquivo de save não pode ser carregado."""


def _slot_para_path(slot_id: str | int | None) -> Path:
    """Converta um identificador de slot em caminho."""
    if slot_id is None or str(slot_id) in {"legacy", "default"}:
        return _ARQUIVO_SALVAMENTO
    try:
        numero = int(slot_id)
    except (TypeError, ValueError) as exc:
        raise ErroCarregamento("Slot de save inválido.") from exc
    if numero < 1:
        raise ErroCarregamento("Slot de save precisa ser >= 1.")
    return _DIRETORIO_SALVAMENTO / _PADRAO_NOME_SLOT.format(slot=numero)


def caminho_save(slot_id: str | int | None = None) -> Path:
    """Retorna o caminho do arquivo de salvamento para um slot."""
    return _slot_para_path(slot_id)


def existe_save() -> bool:
    """Indica se há algum save disponível no disco."""
    return bool(listar_saves())


def salvar_jogo(estado: EstadoJogo, slot_id: str | int | None = None) -> Path:
    """Salva o estado atual do jogo em formato JSON no slot indicado."""
    _DIRETORIO_SALVAMENTO.mkdir(parents=True, exist_ok=True)

    jogador = estado.get("jogador", {}) or {}
    agora_utc = datetime.now(UTC)
    meta = {
        "slot": slot_id or "legacy",
        "personagem": jogador.get("nome", "Desconhecido"),
        "classe": jogador.get("classe", "?"),
        "nivel": jogador.get("nivel", 1),
        "andar": estado.get("nivel_masmorra", 1),
        "dificuldade": estado.get("dificuldade", config.DIFICULDADE_PADRAO),
        "salvo_em_utc": agora_utc.isoformat(timespec="seconds"),
    }

    estado_serializavel = {
        "versao": __version__,
        "salvo_em": agora_utc.isoformat(timespec="seconds"),
        "meta": meta,
        "dados": estado,
    }

    caminho = caminho_save(slot_id)
    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(estado_serializavel, arquivo, ensure_ascii=False, separators=(",", ":"))

    return caminho


def carregar_jogo(slot_id: str | int | None = None) -> EstadoJogo:
    """Carrega o estado do jogo a partir de um slot."""
    caminho = caminho_save(slot_id)
    if not caminho.exists():
        raise ErroCarregamento("Nenhum arquivo de save encontrado para esse slot.")

    try:
        with caminho.open(encoding="utf-8") as arquivo:
            conteudo = json.load(arquivo)
    except (json.JSONDecodeError, OSError) as erro:
        raise ErroCarregamento("Não foi possível ler o arquivo de save.") from erro

    if "dados" not in conteudo or "versao" not in conteudo:
        raise ErroCarregamento("Arquivo de save corrompido ou incompleto.")

    versao_save = conteudo["versao"]
    if not _versoes_compatíveis(versao_save, __version__):
        raise ErroCarregamento(
            "Versão do save "
            f"({versao_save}) incompatível com a versão atual do jogo "
            f"({__version__})."
        )

    dados = conteudo["dados"]
    _validar_estado(dados)
    return dados


def remover_save(slot_id: str | int | None = None) -> None:
    """Remove o arquivo de save, caso exista."""
    caminho = caminho_save(slot_id)
    if caminho.exists():
        caminho.unlink()


def _extrair_info(path: Path, slot_id: str) -> SaveInfo | None:
    """Lê metadados de um arquivo de save sem validá-lo completamente."""
    try:
        with path.open(encoding="utf-8") as arquivo:
            conteudo = json.load(arquivo)
    except (OSError, json.JSONDecodeError):
        return None

    dados = conteudo.get("dados", {}) or {}
    meta = conteudo.get("meta", {}) or {}
    jogador = dados.get("jogador", {}) or {}
    salvo_iso = str(conteudo.get("salvo_em") or meta.get("salvo_em_utc") or "")
    salvo_legivel = _formatar_data_local(salvo_iso)

    return SaveInfo(
        slot_id=slot_id,
        caminho=path,
        personagem=str(meta.get("personagem") or jogador.get("nome") or "Desconhecido"),
        classe=str(meta.get("classe") or jogador.get("classe") or "?"),
        nivel=int(meta.get("nivel") or jogador.get("nivel") or 1),
        andar=int(meta.get("andar") or dados.get("nivel_masmorra") or 1),
        dificuldade=str(
            meta.get("dificuldade") or dados.get("dificuldade") or config.DIFICULDADE_PADRAO
        ),
        salvo_em=salvo_legivel,
        versao=str(conteudo.get("versao") or "?"),
    )


def listar_saves() -> list[SaveInfo]:
    """Lista todos os saves disponíveis, inclusive o legado."""
    _DIRETORIO_SALVAMENTO.mkdir(parents=True, exist_ok=True)
    saves: list[SaveInfo] = []

    # Save legado
    if _ARQUIVO_SALVAMENTO.exists():
        info = _extrair_info(_ARQUIVO_SALVAMENTO, "legacy")
        if info:
            saves.append(info)

    # Novos slots
    for path in sorted(_DIRETORIO_SALVAMENTO.glob("save_*.json")):
        nome = path.name
        slot_num = nome.removeprefix("save_").removesuffix(".json")
        if not slot_num.isdigit():
            continue
        info = _extrair_info(path, slot_num)
        if info:
            saves.append(info)

    # Ordenar por data de modificação (mais recente primeiro)
    saves.sort(key=lambda s: s.caminho.stat().st_mtime, reverse=True)
    return saves


def proximo_slot_disponivel(max_slots: int = config.MAX_SAVE_SLOTS) -> int | None:
    """Retorna o menor slot livre (1..max_slots) ou None se todos ocupados."""
    ocupados = {int(s.slot_id) for s in listar_saves() if str(s.slot_id).isdigit()}
    for slot_num in range(1, max_slots + 1):
        if slot_num not in ocupados:
            return slot_num
    return None


def _validar_estado(estado: EstadoJogo) -> None:
    """Valida minimamente o conteúdo do estado carregado."""
    if not isinstance(estado, dict):
        raise ErroCarregamento("O save não possui a estrutura esperada.")

    jogador = estado.get("jogador")
    mapa = estado.get("mapa")
    nivel = estado.get("nivel_masmorra")
    dificuldade = estado.get("dificuldade")

    if not isinstance(jogador, dict) or "nome" not in jogador:
        raise ErroCarregamento("Dados do jogador ausentes ou inválidos no save.")

    if not isinstance(mapa, list) or not mapa:
        raise ErroCarregamento("Mapa inválido no arquivo de save.")

    for linha in mapa:
        if not isinstance(linha, list):
            raise ErroCarregamento("Mapa corrompido: linhas precisam ser listas.")
        for sala in linha:
            if not isinstance(sala, dict):
                raise ErroCarregamento("Mapa corrompido: sala inválida encontrada.")

    if not isinstance(nivel, int) or nivel < 1:
        raise ErroCarregamento("Nível da masmorra inválido no save.")
    if dificuldade is not None and dificuldade not in config.DIFICULDADES:
        raise ErroCarregamento("Dificuldade inválida no arquivo de save.")


def _versoes_compatíveis(versao_save: str, versao_jogo: str) -> bool:
    """Permite carregar saves do mesmo major.minor, mesmo com patch diferente."""
    try:
        major_s, minor_s, *_ = versao_save.split(".")
        major_j, minor_j, *_ = versao_jogo.split(".")
        return major_s == major_j and minor_s == minor_j
    except ValueError:
        return False


def _formatar_data_local(iso_str: str) -> str:
    """Formata ISO para horário local legível."""
    if not iso_str:
        return "desconhecido"
    try:
        dt = datetime.fromisoformat(iso_str)
        dt_local = dt.astimezone()
        return dt_local.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return iso_str
