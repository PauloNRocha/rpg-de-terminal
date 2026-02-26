import json
from pathlib import Path
from typing import Any

import pytest

from src import armazenamento

EstadoJogo = dict[str, Any]


def configurar_diretorio(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redireciona o sistema de salvamento para um diretório temporário."""
    arquivo = tmp_path / "save.json"
    monkeypatch.setattr(armazenamento, "_DIRETORIO_SALVAMENTO", tmp_path)
    monkeypatch.setattr(armazenamento, "_ARQUIVO_SALVAMENTO", arquivo)
    return arquivo


def test_salvar_e_carregar_estado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Garante que o estado salvo é recuperado sem alterações."""
    arquivo_save = configurar_diretorio(tmp_path, monkeypatch)
    estado: EstadoJogo = {
        "jogador": {"nome": "Hero", "nivel": 3, "hp": 20, "inventario": []},
        "mapa": [[{"tipo": "entrada"}]],
        "nivel_masmorra": 2,
    }

    caminho = armazenamento.salvar_jogo(estado)
    assert caminho == arquivo_save
    assert caminho.exists()

    dados_brutos = json.loads(caminho.read_text(encoding="utf-8"))
    assert dados_brutos["dados"] == estado

    estado_carregado = armazenamento.carregar_jogo()
    assert estado_carregado == estado


def test_carregar_sem_arquivo_dispara_erro(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """carregar_jogo deve falhar quando não há arquivo de save."""
    configurar_diretorio(tmp_path, monkeypatch)
    with pytest.raises(armazenamento.ErroCarregamento):
        armazenamento.carregar_jogo()


def test_remover_save(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Remover o save deve excluir o arquivo sem gerar exceção."""
    arquivo = configurar_diretorio(tmp_path, monkeypatch)
    estado: EstadoJogo = {"jogador": {}, "mapa": [], "nivel_masmorra": 1}
    armazenamento.salvar_jogo(estado)
    assert arquivo.exists()

    armazenamento.remover_save()
    assert not arquivo.exists()


def test_validar_estado_detecta_mapa_invalido() -> None:
    """_validar_estado deve recusar mapas fora do formato esperado."""
    estado = {"jogador": {"nome": "Hero"}, "mapa": [{}], "nivel_masmorra": 1}
    with pytest.raises(armazenamento.ErroCarregamento):
        armazenamento._validar_estado(estado)


def test_validar_estado_aceita_estrutura_minima() -> None:
    """Estados bem formados são aceitos pela validação."""
    mapa = [[{"tipo": "entrada"}]]
    estado = {"jogador": {"nome": "Hero"}, "mapa": mapa, "nivel_masmorra": 1}
    armazenamento._validar_estado(estado)


def test_salvar_carregar_preserva_campos_de_trama(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Campos extras de trama devem ser preservados no save/load."""
    configurar_diretorio(tmp_path, monkeypatch)
    estado: EstadoJogo = {
        "jogador": {"nome": "Hero", "nivel": 2, "hp": 22, "inventario": []},
        "mapa": [[{"tipo": "entrada"}]],
        "nivel_masmorra": 2,
        "dificuldade": "normal",
        "trama_ativa": {
            "id": "resgate_perdido",
            "nome": "Ecos do Resgate",
            "tema": "resgate",
            "motivacao_id": "guerreiro_promessa",
            "andar_alvo": 3,
            "desfecho": "vivo",
            "desfecho_texto": "Texto de desfecho.",
            "sala_nome": "Câmara das Correntes",
            "sala_descricao": "desc",
            "pistas": ["p1"],
            "concluida": False,
        },
        "trama_pistas_exibidas": [1, 2],
    }

    armazenamento.salvar_jogo(estado, slot_id=1)
    estado_carregado = armazenamento.carregar_jogo(1)
    assert estado_carregado["trama_ativa"]["id"] == "resgate_perdido"
    assert estado_carregado["trama_pistas_exibidas"] == [1, 2]
