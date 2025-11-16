import pytest

import jogo
from src import config, gerador_inimigos


def test_contexto_normaliza_dificuldade_invalida() -> None:
    """Chaves inválidas voltam para a dificuldade padrão."""
    contexto = jogo.ContextoJogo()
    contexto.definir_dificuldade("facil")
    assert contexto.dificuldade == "facil"
    contexto.definir_dificuldade("nao-existe")
    assert contexto.dificuldade == config.DIFICULDADE_PADRAO


def test_gerar_inimigo_respeita_perfis(monkeypatch: pytest.MonkeyPatch) -> None:
    """Diferença entre fácil e difícil deve alterar os atributos."""
    template = {
        "nome": "Eco Sombrio",
        "hp_base": 18,
        "ataque_base": 5,
        "defesa_base": 2,
        "xp_base": 12,
        "drop_raridade": "comum",
    }

    monkeypatch.setattr(gerador_inimigos, "obter_templates", lambda: {"eco": template})

    facil = gerador_inimigos.gerar_inimigo(
        1, tipo_inimigo="eco", dificuldade=config.DIFICULDADES["facil"]
    )
    dificil = gerador_inimigos.gerar_inimigo(
        1, tipo_inimigo="eco", dificuldade=config.DIFICULDADES["dificil"]
    )

    assert facil.hp < dificil.hp
    assert facil.ataque < dificil.ataque
    assert facil.defesa <= dificil.defesa
    assert facil.xp_recompensa >= dificil.xp_recompensa
