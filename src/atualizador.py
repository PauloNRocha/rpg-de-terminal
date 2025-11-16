"""Utilidades para checar novas versões do jogo via GitHub Releases."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from src.version import __version__

PROJETO_REPO = "PauloNRocha/rpg-de-terminal"
GITHUB_RELEASES_URL = f"https://api.github.com/repos/{PROJETO_REPO}/releases"
USER_AGENT = "AventuraNoTerminal/1.5"
DEFAULT_TIMEOUT = 5

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = PROJECT_ROOT / "settings.json"

DEFAULT_PREFERENCIAS = {
    "auto_update_check": True,
    "frequency": "semanal",  # "diaria", "semanal", "mensal"
    "allow_prerelease": False,
    "last_check_iso": None,
}
FREQUENCIA_DIAS = {"diaria": 1, "semanal": 7, "mensal": 30}


@dataclass
class AtualizacaoInfo:
    """Resultado de uma verificação de atualização."""

    versao_disponivel: str
    url_release: str
    nome_release: str
    eh_prerelease: bool
    modo_instalacao: str

    @property
    def instrucoes(self) -> str:
        """Retorna instruções textuais baseadas no modo de instalação."""
        base = (
            f"Nova versão disponível: v{self.versao_disponivel} (atual: v{__version__}).\n"
            f"Notas: {self.nome_release}\n"
            f"Link: {self.url_release}\n"
        )
        if self.modo_instalacao == "repo":
            return base + "Execute 'git pull origin main' e reinicie o jogo."
        if self.modo_instalacao == "pipx":
            return base + "Execute 'pipx upgrade aventura-terminal'."
        if self.modo_instalacao == "pip":
            return base + "Execute 'pip install -U aventura-terminal'."
        return base + "Baixe o ZIP da release no link acima e substitua os arquivos."


def carregar_preferencias(caminho: Path = SETTINGS_PATH) -> dict[str, Any]:
    """Lê o arquivo de preferências de atualização, criando-o com defaults se necessário."""
    if not caminho.exists():
        salvar_preferencias(DEFAULT_PREFERENCIAS.copy(), caminho)
        return DEFAULT_PREFERENCIAS.copy()
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return DEFAULT_PREFERENCIAS.copy()
    prefs = DEFAULT_PREFERENCIAS.copy()
    prefs.update({k: dados.get(k, v) for k, v in DEFAULT_PREFERENCIAS.items()})
    return prefs


def salvar_preferencias(preferencias: dict[str, Any], caminho: Path = SETTINGS_PATH) -> None:
    """Salva o dicionário de preferências em disco."""
    caminho.write_text(json.dumps(preferencias, indent=2, ensure_ascii=False), encoding="utf-8")


def _dias_de_intervalo(frequencia: str) -> int:
    return FREQUENCIA_DIAS.get(frequencia, FREQUENCIA_DIAS["semanal"])


def deve_verificar(preferencias: dict[str, Any], agora: datetime | None = None) -> bool:
    """Determina se está na hora de checar atualizações novamente."""
    if not preferencias.get("auto_update_check", True):
        return False
    ultimo = preferencias.get("last_check_iso")
    if not ultimo:
        return True
    try:
        ultima_data = datetime.fromisoformat(ultimo)
    except ValueError:
        return True
    agora = agora or datetime.now(UTC)
    intervalo = timedelta(days=_dias_de_intervalo(preferencias.get("frequency", "semanal")))
    return agora - ultima_data >= intervalo


def _fetch_releases(timeout: int = DEFAULT_TIMEOUT) -> list[dict[str, Any]]:
    request = Request(
        GITHUB_RELEASES_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
        },
    )
    with urlopen(request, timeout=timeout) as resposta:  # type: ignore[arg-type]
        return json.loads(resposta.read().decode("utf-8"))


def _normalizar_tag(tag: str) -> str:
    return tag.lstrip("vV")


def _comparar_semver(v1: str, v2: str) -> int:
    def _to_tuple(v: str) -> tuple[int, ...]:
        partes = [int(p) for p in v.split(".") if p.isdigit()]
        return tuple(partes)

    t1, t2 = _to_tuple(v1), _to_tuple(v2)
    max_len = max(len(t1), len(t2))
    t1 += (0,) * (max_len - len(t1))
    t2 += (0,) * (max_len - len(t2))
    if t1 == t2:
        return 0
    return 1 if t1 > t2 else -1


def buscar_release_mais_recente(
    allow_prerelease: bool,
    fetch_fn: Callable[[], Iterable[dict[str, Any]]] | None = None,
) -> dict[str, Any] | None:
    """Retorna o primeiro release elegível (não draft, opcionalmente sem pré-release)."""
    releases = fetch_fn() if fetch_fn else _fetch_releases()
    for release in releases:
        if release.get("draft"):
            continue
        if release.get("prerelease") and not allow_prerelease:
            continue
        if not release.get("tag_name"):
            continue
        return release
    return None


def detectar_modo_instalacao() -> str:
    """Tenta inferir como o jogo foi instalado para orientar a atualização."""
    raiz = PROJECT_ROOT
    if (raiz / ".git").exists():
        return "repo"
    caminho_modulo = Path(__file__).resolve()
    executavel = Path(sys.executable)
    if "pipx" in executavel.as_posix():
        return "pipx"
    if "site-packages" in caminho_modulo.as_posix():
        return "pip"
    if "site-packages" in executavel.as_posix():
        return "pip"
    return "standalone"


def verificar_atualizacao(
    forcar: bool = False,
    agora: datetime | None = None,
    fetch_fn: Callable[[], Iterable[dict[str, Any]]] | None = None,
) -> AtualizacaoInfo | None:
    """Checa se existe release mais recente e retorna instruções para o jogador."""
    preferencias = carregar_preferencias()
    agora = agora or datetime.now(UTC)
    if not forcar and not deve_verificar(preferencias, agora):
        return None

    try:
        release = buscar_release_mais_recente(preferencias.get("allow_prerelease", False), fetch_fn)
    except URLError:
        release = None
    except OSError:
        release = None

    preferencias["last_check_iso"] = agora.isoformat()
    salvar_preferencias(preferencias)

    if not release:
        return None

    versao_release = _normalizar_tag(str(release.get("tag_name", "")))
    if _comparar_semver(__version__, versao_release) >= 0:
        return None

    modo = detectar_modo_instalacao()
    return AtualizacaoInfo(
        versao_disponivel=versao_release,
        url_release=release.get("html_url", f"https://github.com/{PROJETO_REPO}/releases/latest"),
        nome_release=release.get("name") or release.get("body") or "Nova versão",
        eh_prerelease=bool(release.get("prerelease")),
        modo_instalacao=modo,
    )
