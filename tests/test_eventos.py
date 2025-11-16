import pytest

from src import eventos
from src.economia import Moeda
from src.entidades import Personagem


def personagem_stub() -> Personagem:
    """Cria um personagem mínimo para testar eventos."""
    return Personagem(
        nome="Heroi",
        classe="Guerreiro",
        hp=10,
        hp_max=20,
        ataque_base=5,
        defesa_base=3,
        ataque=5,
        defesa=3,
        x=0,
        y=0,
        nivel=1,
        xp_atual=0,
        xp_para_proximo_nivel=100,
        carteira=Moeda(),
    )


def test_disparar_evento_cura(monkeypatch: pytest.MonkeyPatch) -> None:
    """Eventos de cura aumentam o HP do personagem."""
    personagem = personagem_stub()
    titulo, mensagem = eventos.disparar_evento("santuario_da_luz", personagem)
    assert "SANTUÁRIO" in titulo
    assert personagem.hp > 10
    assert "recuperou" in mensagem


def test_disparar_evento_moedas() -> None:
    """Eventos de tesouro concedem moedas."""
    personagem = personagem_stub()
    _titulo, mensagem = eventos.disparar_evento("cofre_esquecido", personagem)
    assert personagem.carteira.valor_bronze > 0
    assert "recebeu" in mensagem


def test_disparar_evento_com_multiplicador_afeta_recompensa() -> None:
    """Multiplicadores de moedas ajustam o total recebido."""
    personagem = personagem_stub()
    _titulo, _mensagem = eventos.disparar_evento(
        "cofre_esquecido", personagem, multiplicador_moedas=0.5
    )
    assert personagem.carteira.valor_bronze == 18
