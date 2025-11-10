from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

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
