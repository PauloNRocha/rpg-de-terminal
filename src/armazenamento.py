"""Gerencia o salvamento e o carregamento do jogo em disco."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src import config
from src.version import __version__

DiretorioSalvamento = Path
EstadoJogo = dict[str, Any]

_DIRETORIO_SALVAMENTO: DiretorioSalvamento = Path("saves")
_ARQUIVO_SALVAMENTO: Path = _DIRETORIO_SALVAMENTO / "save.json"


class ErroCarregamento(RuntimeError):  # noqa: N818
    """Erro específico disparado quando o arquivo de save não pode ser carregado."""


def caminho_save() -> Path:
    """Retorna o caminho padrão do arquivo de salvamento."""
    return _ARQUIVO_SALVAMENTO


def existe_save() -> bool:
    """Indica se há um save disponível no disco."""
    return caminho_save().exists()


def salvar_jogo(estado: EstadoJogo) -> Path:
    """Salva o estado atual do jogo em formato JSON."""
    _DIRETORIO_SALVAMENTO.mkdir(parents=True, exist_ok=True)

    estado_serializavel = {
        "versao": __version__,
        "salvo_em": datetime.now(UTC).isoformat(timespec="seconds"),
        "dados": estado,
    }

    with caminho_save().open("w", encoding="utf-8") as arquivo:
        json.dump(estado_serializavel, arquivo, ensure_ascii=False, separators=(",", ":"))

    return caminho_save()


def carregar_jogo() -> EstadoJogo:
    """Carrega o estado do jogo a partir do disco."""
    caminho = caminho_save()
    if not caminho.exists():
        raise ErroCarregamento("Nenhum arquivo de save encontrado.")

    try:
        with caminho.open(encoding="utf-8") as arquivo:
            conteudo = json.load(arquivo)
    except (json.JSONDecodeError, OSError) as erro:
        raise ErroCarregamento("Não foi possível ler o arquivo de save.") from erro

    if "dados" not in conteudo or "versao" not in conteudo:
        raise ErroCarregamento("Arquivo de save corrompido ou incompleto.")

    versao_save = conteudo["versao"]
    if versao_save != __version__:
        raise ErroCarregamento(
            "Versão do save "
            f"({versao_save}) incompatível com a versão atual do jogo "
            f"({__version__})."
        )

    dados = conteudo["dados"]
    _validar_estado(dados)
    return dados


def remover_save() -> None:
    """Remove o arquivo de save, caso exista."""
    caminho = caminho_save()
    if caminho.exists():
        caminho.unlink()


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
