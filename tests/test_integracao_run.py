from __future__ import annotations

from pathlib import Path

import pytest

import jogo
from src import armazenamento
from src.entidades import Inimigo, Personagem, Sala
from src.estados import combate as estado_combate
from src.tramas import TramaAtiva


def _configurar_diretorio_saves(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Redireciona saves e histórico para um diretório temporário."""
    monkeypatch.setattr(armazenamento, "_DIRETORIO_SALVAMENTO", tmp_path)
    monkeypatch.setattr(armazenamento, "_ARQUIVO_SALVAMENTO", tmp_path / "save.json")
    monkeypatch.setattr(armazenamento, "_ARQUIVO_HISTORICO", tmp_path / "history.json")


def _hidratar_contexto_carregado(estado: dict[str, object]) -> jogo.ContextoJogo:
    """Reconstrói um contexto mínimo a partir de um save carregado."""
    contexto = jogo.ContextoJogo()
    contexto.jogador = Personagem.from_dict(estado["jogador"])  # type: ignore[arg-type]
    contexto.mapa_atual = jogo.hidratar_mapa(estado["mapa"])  # type: ignore[arg-type]
    contexto.nivel_masmorra = int(estado["nivel_masmorra"])
    contexto.definir_dificuldade(str(estado.get("dificuldade", "normal")))
    contexto.trama_pistas_exibidas = set(estado.get("trama_pistas_exibidas", []))  # type: ignore[arg-type]
    contexto.trama_consequencia_resumo = estado.get("trama_consequencia_resumo")  # type: ignore[assignment]
    contexto.slot_atual = "1"
    trama_raw = estado.get("trama_ativa")
    if isinstance(trama_raw, dict):
        contexto.trama_ativa = TramaAtiva.from_dict(trama_raw)
    contexto.inicializar_rng(
        estado.get("seed_run"),  # type: ignore[arg-type]
        estado.get("rng_state"),  # type: ignore[arg-type]
    )
    return contexto


def test_fluxo_integrado_criacao_evento_combate_save_load_continuar(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fluxo completo da run deve sobreviver a save/load sem perder estado crítico."""
    _configurar_diretorio_saves(tmp_path, monkeypatch)

    monkeypatch.setattr(jogo, "desenhar_tela_input", lambda *args, **kwargs: "Heroi")
    monkeypatch.setattr(jogo, "desenhar_tela_escolha_classe", lambda *args, **kwargs: "guerreiro")
    monkeypatch.setattr(jogo, "desenhar_tela_escolha_dificuldade", lambda *args, **kwargs: "normal")
    monkeypatch.setattr(jogo, "desenhar_tela_resumo_personagem", lambda *args, **kwargs: None)
    monkeypatch.setattr(jogo, "desenhar_tela_evento", lambda *args, **kwargs: None)
    monkeypatch.setattr(jogo, "desenhar_tela_resumo_andar", lambda *args, **kwargs: None)
    monkeypatch.setattr(jogo, "desenhar_tela_ficha_personagem", lambda *args, **kwargs: None)
    monkeypatch.setattr(jogo, "desenhar_tela_resumo_final", lambda *args, **kwargs: None)
    monkeypatch.setattr(jogo, "tela_game_over", lambda: None)
    monkeypatch.setattr(jogo, "desenhar_historico", lambda *args, **kwargs: None)
    monkeypatch.setattr(estado_combate, "desenhar_tela_evento", lambda *args, **kwargs: None)
    monkeypatch.setattr(estado_combate, "tela_game_over", lambda: None)

    contexto = jogo.ContextoJogo()
    contexto.definir_dificuldade("normal")
    contexto.slot_atual = "1"

    assert jogo.executar_estado_criacao(contexto) == jogo.Estado.EXPLORACAO
    assert contexto.jogador is not None
    assert contexto.seed_run is not None
    assert contexto.trama_ativa is not None

    sala_evento = Sala(
        tipo="sala",
        nome="Sala do Cofre",
        descricao="Uma sala com runas douradas.",
        pode_ter_inimigo=False,
        nivel_area=1,
        evento_id="cofre_esquecido",
    )
    sala_combate = Sala(
        tipo="sala",
        nome="Sala do Guardião",
        descricao="Um guarda espectral vigia a passagem.",
        pode_ter_inimigo=True,
        nivel_area=1,
        inimigo_atual=Inimigo(
            nome="Guardião de Teste",
            hp=8,
            hp_max=8,
            ataque=1,
            defesa=0,
            xp_recompensa=12,
            drop_raridade="",
        ),
    )
    contexto.mapa_atual = [[sala_evento, sala_combate]]
    contexto.jogador.x = 0
    contexto.jogador.y = 0

    monkeypatch.setattr(jogo, "desenhar_hud_exploracao", lambda *args, **kwargs: "1")
    assert jogo.executar_estado_exploracao(contexto) == jogo.Estado.EXPLORACAO
    assert contexto.jogador.x == 1
    assert contexto.jogador.carteira.valor_bronze > 0

    assert jogo.executar_estado_exploracao(contexto) == jogo.Estado.COMBATE

    monkeypatch.setattr(
        jogo,
        "iniciar_combate",
        lambda jogador, inimigo, usar_item, rng=None: (True, inimigo),
    )
    assert jogo.executar_estado_combate(contexto) == jogo.Estado.EXPLORACAO
    assert sala_combate.inimigo_derrotado is True

    monkeypatch.setattr(
        jogo,
        "desenhar_hud_exploracao",
        lambda _j, _s, opcoes, *_args: str(opcoes.index("Salvar jogo") + 1),
    )
    assert jogo.executar_estado_exploracao(contexto) == jogo.Estado.EXPLORACAO

    estado_salvo = armazenamento.carregar_jogo("1")
    assert estado_salvo["seed_run"] == contexto.seed_run
    assert estado_salvo["rng_state"]

    contexto_carregado = _hidratar_contexto_carregado(estado_salvo)
    assert contexto_carregado.seed_run == contexto.seed_run
    assert contexto.rng.random() == contexto_carregado.rng.random()

    monkeypatch.setattr(
        jogo,
        "desenhar_hud_exploracao",
        lambda _j, _s, opcoes, *_args: str(opcoes.index("Sair da masmorra") + 1),
    )
    assert jogo.executar_estado_exploracao(contexto_carregado) == jogo.Estado.MENU
