"""Validação de schema dos arquivos JSON data-driven."""

from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "src" / "data"


def _carregar_json(nome_arquivo: str) -> object:
    caminho = DATA_DIR / nome_arquivo
    return json.loads(caminho.read_text(encoding="utf-8"))


def test_schema_classes_json() -> None:
    """Valide `classes.json` com campos obrigatórios e tipos esperados."""
    dados = _carregar_json("classes.json")
    assert isinstance(dados, dict)
    assert dados

    for nome, classe in dados.items():
        assert isinstance(nome, str) and nome.strip()
        assert isinstance(classe, dict)
        assert isinstance(classe.get("descricao"), str) and classe["descricao"].strip()
        for campo in ("hp", "ataque", "defesa"):
            valor = classe.get(campo)
            assert isinstance(valor, int)
            assert valor > 0


def test_schema_itens_json() -> None:
    """Valide `itens.json` e diferencie equipáveis de consumíveis."""
    dados = _carregar_json("itens.json")
    assert isinstance(dados, dict)
    assert dados

    for raridade, itens in dados.items():
        assert isinstance(raridade, str) and raridade.strip()
        assert isinstance(itens, list)
        assert itens
        for item in itens:
            assert isinstance(item, dict)
            assert isinstance(item.get("nome"), str) and item["nome"].strip()
            assert isinstance(item.get("tipo"), str) and item["tipo"].strip()
            assert isinstance(item.get("descricao"), str)
            preco = item.get("preco_bronze")
            assert isinstance(preco, int)
            assert preco >= 0
            if item["tipo"] == "consumivel":
                assert isinstance(item.get("efeito"), dict)
            else:
                assert isinstance(item.get("bonus"), dict)


def test_schema_inimigos_json() -> None:
    """Valide `inimigos.json` para atributos base e campos opcionais."""
    dados = _carregar_json("inimigos.json")
    assert isinstance(dados, dict)
    assert dados

    for nome_template, inimigo in dados.items():
        assert isinstance(nome_template, str) and nome_template.strip()
        assert isinstance(inimigo, dict)
        assert isinstance(inimigo.get("nome"), str) and inimigo["nome"].strip()
        for campo in ("hp_base", "ataque_base", "defesa_base", "xp_base"):
            valor = inimigo.get(campo)
            assert isinstance(valor, int)
            assert valor >= 0
        assert isinstance(inimigo.get("drop_raridade"), str)
        if "drop_item_nome" in inimigo:
            valor = inimigo["drop_item_nome"]
            assert valor is None or isinstance(valor, str)
        if "tags" in inimigo:
            assert isinstance(inimigo["tags"], list)
            assert all(isinstance(tag, str) and tag.strip() for tag in inimigo["tags"])


def test_schema_eventos_json() -> None:
    """Valide `eventos.json` com estrutura de efeitos/opções."""
    dados = _carregar_json("eventos.json")
    assert isinstance(dados, list)
    assert dados

    for evento in dados:
        assert isinstance(evento, dict)
        assert isinstance(evento.get("id"), str) and evento["id"].strip()
        assert isinstance(evento.get("nome"), str) and evento["nome"].strip()
        assert isinstance(evento.get("descricao"), str)
        assert "efeitos" in evento or "opcoes" in evento
        if "efeitos" in evento:
            assert isinstance(evento["efeitos"], dict)
        if "opcoes" in evento:
            assert isinstance(evento["opcoes"], list)
            assert evento["opcoes"]
            for opcao in evento["opcoes"]:
                assert isinstance(opcao, dict)
                assert isinstance(opcao.get("descricao"), str)
                assert isinstance(opcao.get("efeitos", {}), dict)
        if "tags" in evento:
            assert isinstance(evento["tags"], list)
            assert all(isinstance(tag, str) and tag.strip() for tag in evento["tags"])


def test_schema_salas_json() -> None:
    """Valide `salas.json` com categorias e templates válidos."""
    dados = _carregar_json("salas.json")
    assert isinstance(dados, dict)
    assert dados

    for categoria, salas in dados.items():
        assert isinstance(categoria, str) and categoria.strip()
        assert isinstance(salas, list)
        assert salas
        for sala in salas:
            assert isinstance(sala, dict)
            assert isinstance(sala.get("nome"), str) and sala["nome"].strip()
            assert isinstance(sala.get("descricao"), str) and sala["descricao"].strip()
            if "tags" in sala:
                assert isinstance(sala["tags"], list)
                assert all(isinstance(tag, str) and tag.strip() for tag in sala["tags"])


def test_schema_tramas_json() -> None:
    """Valide `tramas.json` incluindo desfechos e consequências."""
    dados = _carregar_json("tramas.json")
    assert isinstance(dados, list)
    assert dados

    for trama in dados:
        assert isinstance(trama, dict)
        assert isinstance(trama.get("id"), str) and trama["id"].strip()
        assert isinstance(trama.get("nome"), str) and trama["nome"].strip()
        assert isinstance(trama.get("tema"), str) and trama["tema"].strip()
        assert isinstance(trama.get("motivacoes"), list) and trama["motivacoes"]
        assert all(isinstance(mot, str) and mot.strip() for mot in trama["motivacoes"])
        andar_alvo = trama.get("andar_alvo")
        assert isinstance(andar_alvo, dict)
        assert isinstance(andar_alvo.get("min"), int) and andar_alvo["min"] >= 1
        assert isinstance(andar_alvo.get("max"), int) and andar_alvo["max"] >= andar_alvo["min"]
        assert isinstance(trama.get("sala_nome"), str) and trama["sala_nome"].strip()
        assert isinstance(trama.get("sala_descricao"), str) and trama["sala_descricao"].strip()
        assert isinstance(trama.get("pistas"), list) and trama["pistas"]
        assert all(isinstance(pista, str) and pista.strip() for pista in trama["pistas"])

        desfechos = trama.get("desfechos")
        assert isinstance(desfechos, dict) and desfechos
        for chave, textos in desfechos.items():
            assert isinstance(chave, str) and chave.strip()
            assert isinstance(textos, list) and textos
            assert all(isinstance(texto, str) and texto.strip() for texto in textos)

        consequencias = trama.get("consequencias")
        assert isinstance(consequencias, dict) and consequencias
        for chave, lista in consequencias.items():
            assert isinstance(chave, str) and chave.strip()
            assert isinstance(lista, list) and lista
            for consequencia in lista:
                assert isinstance(consequencia, dict)
                assert isinstance(consequencia.get("tipo"), str)
