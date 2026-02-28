"""Gerencia o salvamento e o carregamento do jogo em disco (agora com múltiplos slots)."""

from __future__ import annotations

import copy
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
_ARQUIVO_HISTORICO: Path = _DIRETORIO_SALVAMENTO / "history.json"
SAVE_SCHEMA_VERSION = 2


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
        "save_version": SAVE_SCHEMA_VERSION,
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

    try:
        conteudo = _normalizar_envelope_save(conteudo)
    except ValueError as erro:
        raise ErroCarregamento("Arquivo de save corrompido ou incompleto.") from erro

    conteudo_migrado, migrou = _migrar_conteudo_save(conteudo)

    versao_save = str(conteudo_migrado.get("versao") or "legacy")
    if not _versoes_compatíveis(versao_save, __version__):
        raise ErroCarregamento(
            "Versão do save "
            f"({versao_save}) incompatível com a versão atual do jogo "
            f"({__version__})."
        )

    dados = conteudo_migrado.get("dados", {})
    _validar_estado(dados)
    if migrou:
        with caminho.open("w", encoding="utf-8") as arquivo:
            json.dump(conteudo_migrado, arquivo, ensure_ascii=False, separators=(",", ":"))
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
        conteudo = _normalizar_envelope_save(conteudo)
        conteudo, _ = _migrar_conteudo_save(conteudo)
    except (OSError, json.JSONDecodeError):
        return None
    except ValueError:
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
    if versao_save in {"legacy", "0.0.0", "", "?"}:
        return True
    try:
        major_s, minor_s, *_ = versao_save.split(".")
        major_j, minor_j, *_ = versao_jogo.split(".")
        return major_s == major_j and minor_s == minor_j
    except ValueError:
        return False


def _normalizar_envelope_save(conteudo: object) -> dict[str, Any]:
    """Normalize formatos antigos para o envelope padrão sem perder dados."""
    if not isinstance(conteudo, dict):
        raise ValueError("Conteúdo de save inválido.")
    if "dados" in conteudo and "versao" in conteudo:
        return conteudo
    if {"jogador", "mapa", "nivel_masmorra"}.issubset(conteudo.keys()):
        return {
            "save_version": 1,
            "versao": "legacy",
            "salvo_em": "",
            "meta": {},
            "dados": conteudo,
        }
    raise ValueError("Formato de save não reconhecido.")


def _migrar_conteudo_save(conteudo: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """Aplica migrações de schema até a versão atual."""
    migrado = copy.deepcopy(conteudo)
    versao_atual = _coagir_save_version(migrado.get("save_version", 1))
    if versao_atual > SAVE_SCHEMA_VERSION:
        raise ErroCarregamento(
            f"Arquivo de save foi gerado por uma versão mais nova do jogo (schema {versao_atual})."
        )

    houve_migracao = False
    while versao_atual < SAVE_SCHEMA_VERSION:
        if versao_atual == 1:
            migrado = _migrar_v1_para_v2(migrado)
            versao_atual = 2
            houve_migracao = True
            continue
        raise ErroCarregamento(
            f"Não existe migrador para schema de save {versao_atual} -> {versao_atual + 1}."
        )

    migrado["save_version"] = SAVE_SCHEMA_VERSION
    return migrado, houve_migracao


def _coagir_save_version(valor: object) -> int:
    """Converta o identificador de versão do schema para inteiro válido."""
    try:
        versao = int(valor)
    except (TypeError, ValueError):
        versao = 1
    return max(1, versao)


def _migrar_v1_para_v2(conteudo: dict[str, Any]) -> dict[str, Any]:
    """Migra saves sem schema explícito para o formato v2."""
    dados = conteudo.get("dados")
    if not isinstance(dados, dict):
        dados = {}
    conteudo["dados"] = dados

    jogador = dados.get("jogador")
    if not isinstance(jogador, dict):
        jogador = {"nome": "Desconhecido"}
    dados["jogador"] = jogador

    jogador.setdefault("nome", "Desconhecido")
    jogador.setdefault("classe", "Aventureiro")
    jogador.setdefault("hp", 1)
    jogador.setdefault("hp_max", max(1, int(jogador.get("hp", 1))))
    jogador.setdefault("ataque", 1)
    jogador.setdefault("defesa", 0)
    jogador.setdefault("ataque_base", jogador.get("ataque", 1))
    jogador.setdefault("defesa_base", jogador.get("defesa", 0))
    jogador.setdefault("x", 0)
    jogador.setdefault("y", 0)
    jogador.setdefault("nivel", 1)
    jogador.setdefault("xp_atual", 0)
    jogador.setdefault("xp_para_proximo_nivel", 100)
    if not isinstance(jogador.get("inventario"), list):
        jogador["inventario"] = []
    equipamento = jogador.get("equipamento")
    if not isinstance(equipamento, dict):
        equipamento = {"arma": None, "armadura": None, "escudo": None}
    equipamento.setdefault("arma", None)
    equipamento.setdefault("armadura", None)
    equipamento.setdefault("escudo", None)
    jogador["equipamento"] = equipamento
    if not isinstance(jogador.get("carteira"), dict):
        jogador["carteira"] = {"valor_bronze": 0}
    if not isinstance(jogador.get("status_temporarios"), list):
        jogador["status_temporarios"] = []

    if not isinstance(dados.get("mapa"), list):
        dados["mapa"] = [[{"tipo": "entrada", "nome": "Entrada", "descricao": ""}]]
    dados.setdefault("nivel_masmorra", 1)
    dados.setdefault("dificuldade", config.DIFICULDADE_PADRAO)
    if not isinstance(dados.get("trama_pistas_exibidas"), list):
        dados["trama_pistas_exibidas"] = []
    dados.setdefault("trama_consequencia_resumo", None)

    meta = conteudo.get("meta")
    if not isinstance(meta, dict):
        meta = {}
    conteudo["meta"] = meta
    meta.setdefault("slot", "legacy")
    meta.setdefault("personagem", jogador.get("nome", "Desconhecido"))
    meta.setdefault("classe", jogador.get("classe", "?"))
    meta.setdefault("nivel", jogador.get("nivel", 1))
    meta.setdefault("andar", dados.get("nivel_masmorra", 1))
    meta.setdefault("dificuldade", dados.get("dificuldade", config.DIFICULDADE_PADRAO))

    conteudo.setdefault("versao", "legacy")
    conteudo["save_version"] = 2
    return conteudo


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


def registrar_historico(entry: dict[str, Any], limite: int = 50) -> None:
    """Acrescenta uma entrada de histórico de partidas (ignoradas pelo git)."""
    _DIRETORIO_SALVAMENTO.mkdir(parents=True, exist_ok=True)
    historico: list[dict[str, Any]] = []
    if _ARQUIVO_HISTORICO.exists():
        try:
            historico = json.loads(_ARQUIVO_HISTORICO.read_text(encoding="utf-8"))
            if not isinstance(historico, list):
                historico = []
        except (OSError, json.JSONDecodeError):
            historico = []
    historico.append(entry)
    if len(historico) > limite:
        historico = historico[-limite:]
    _ARQUIVO_HISTORICO.write_text(
        json.dumps(historico, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def limpar_historico() -> None:
    """Remove o arquivo de histórico, se existir."""
    if _ARQUIVO_HISTORICO.exists():
        _ARQUIVO_HISTORICO.unlink()
