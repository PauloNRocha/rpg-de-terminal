"""Infraestrutura comum para carregar catálogos JSON em `src/data/`."""

from __future__ import annotations

import json
from pathlib import Path

from src.erros import ErroDadosError

_DIRETORIO_DADOS = Path(__file__).parent / "data"
type CatalogoBruto = dict[str, object] | list[object]
_CACHE_BRUTO: dict[str, CatalogoBruto] = {}


def carregar_json_catalogo(
    nome_arquivo: str,
    *,
    tipo_esperado: type[dict[str, object]] | type[list[object]],
) -> CatalogoBruto:
    """Carrega um catálogo JSON com cache bruto e mensagens de erro uniformes."""
    if nome_arquivo in _CACHE_BRUTO:
        return _CACHE_BRUTO[nome_arquivo]

    caminho = _DIRETORIO_DADOS / nome_arquivo
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError as erro:
        raise ErroDadosError(f"Arquivo '{nome_arquivo}' não encontrado em src/data/.") from erro
    except json.JSONDecodeError as erro:
        raise ErroDadosError(f"Arquivo '{nome_arquivo}' inválido (JSON malformado).") from erro

    if not isinstance(dados, tipo_esperado):
        tipo_legivel = "lista" if tipo_esperado is list else "objeto"
        raise ErroDadosError(f"Arquivo '{nome_arquivo}' deve conter um {tipo_legivel} JSON válido.")

    _CACHE_BRUTO[nome_arquivo] = dados
    return dados


def limpar_cache_catalogos() -> None:
    """Esvazia o cache bruto de catálogos, útil em testes e recargas."""
    _CACHE_BRUTO.clear()
