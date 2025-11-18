from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.error import URLError

import pytest

from src import atualizador


def test_deve_verificar_sem_ultimo() -> None:
    """Checa quando nunca houve verificação anterior."""
    prefs = atualizador.DEFAULT_PREFERENCIAS.copy()
    prefs["last_check_iso"] = None
    assert atualizador.deve_verificar(prefs, datetime.now(UTC)) is True


def test_deve_verificar_respeita_intervalo() -> None:
    """Garante que o intervalo configurado é respeitado."""
    agora = datetime(2025, 11, 10, tzinfo=UTC)
    prefs = atualizador.DEFAULT_PREFERENCIAS.copy()
    prefs["frequency"] = "semanal"
    prefs["last_check_iso"] = (agora - timedelta(days=3)).isoformat()
    assert atualizador.deve_verificar(prefs, agora) is False
    prefs["last_check_iso"] = (agora - timedelta(days=8)).isoformat()
    assert atualizador.deve_verificar(prefs, agora) is True


def test_deve_verificar_quando_falha_recente() -> None:
    """Mesmo sem intervalo vencido, uma falha obriga nova verificação."""
    agora = datetime(2025, 11, 10, tzinfo=UTC)
    prefs = atualizador.DEFAULT_PREFERENCIAS.copy()
    prefs["frequency"] = "mensal"
    prefs["last_check_iso"] = (agora - timedelta(days=1)).isoformat()
    prefs["ultima_falha_iso"] = agora.isoformat()
    assert atualizador.deve_verificar(prefs, agora) is True


def test_verificar_atualizacao_retorna_info(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Retorna informações quando há release mais recente."""
    fake_settings = tmp_path / "settings.json"
    monkeypatch.setattr(atualizador, "SETTINGS_PATH", fake_settings)

    def fake_fetch() -> list[dict[str, str]]:
        return [
            {
                "tag_name": "v9.9.9",
                "name": "Super Release",
                "html_url": "https://example.com/release",
                "prerelease": False,
                "draft": False,
            }
        ]

    info = atualizador.verificar_atualizacao(
        forcar=True,
        agora=datetime(2025, 11, 10, tzinfo=UTC),
        fetch_fn=fake_fetch,
    )
    assert info is not None
    assert info.versao_disponivel == "9.9.9"
    assert "Super Release" in info.instrucoes


def test_verificar_atualizacao_falha_nao_atualiza_last_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Falhas de rede não atualizam o last_check e marcam ultima_falha."""
    fake_settings = tmp_path / "settings.json"
    monkeypatch.setattr(atualizador, "SETTINGS_PATH", fake_settings)

    def fake_fetch() -> list[dict[str, str]]:
        raise URLError("sem rede")

    info = atualizador.verificar_atualizacao(
        forcar=True,
        agora=datetime(2025, 11, 10, tzinfo=UTC),
        fetch_fn=fake_fetch,
    )
    assert info is None
    prefs = atualizador.carregar_preferencias(fake_settings)
    assert prefs["last_check_iso"] is None
    assert prefs["ultima_falha_iso"] is not None


def test_verificar_atualizacao_sucesso_limpa_flag_de_falha(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Após sucesso, a flag de falha é limpa e last_check é atualizado."""
    fake_settings = tmp_path / "settings.json"
    monkeypatch.setattr(atualizador, "SETTINGS_PATH", fake_settings)
    preferencias = atualizador.DEFAULT_PREFERENCIAS.copy()
    preferencias["ultima_falha_iso"] = "2025-11-09T12:00:00+00:00"
    fake_settings.write_text(json.dumps(preferencias, ensure_ascii=False), encoding="utf-8")

    def fake_fetch() -> list[dict[str, str]]:
        return [
            {
                "tag_name": "v9.9.9",
                "name": "Super Release",
                "html_url": "https://example.com/release",
                "prerelease": False,
                "draft": False,
            }
        ]

    info = atualizador.verificar_atualizacao(
        forcar=True,
        agora=datetime(2025, 11, 10, tzinfo=UTC),
        fetch_fn=fake_fetch,
    )
    assert info is not None
    prefs = atualizador.carregar_preferencias(fake_settings)
    assert prefs["ultima_falha_iso"] is None
    assert prefs["last_check_iso"] == datetime(2025, 11, 10, tzinfo=UTC).isoformat()
