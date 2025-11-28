"""Funções auxiliares de UI compartilhadas."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from src.ui import desenhar_tela_evento


@dataclass
class TutorialEstado:
    """Controla dicas já exibidas para evitar repetição."""

    ativo: bool = True
    vistos: set[str] = None

    def __post_init__(self) -> None:
        if self.vistos is None:
            self.vistos = set()

    def habilitado(self) -> bool:
        """Retorna True se o tutorial deve aparecer neste terminal."""
        return self.ativo and sys.stdin.isatty()

    def mostrar(self, chave: str, titulo: str, corpo: str) -> None:
        """Exibe a dica se ainda não exibida."""
        if not self.habilitado():
            return
        if chave in self.vistos:
            return
        self.vistos.add(chave)
        desenhar_tela_evento(titulo, corpo)
