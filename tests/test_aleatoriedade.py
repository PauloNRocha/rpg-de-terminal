import random

from src import config
from src.aleatoriedade import criar_rng, restaurar_rng, serializar_estado_rng
from src.gerador_mapa import gerar_mapa
from src.tramas import gerar_pista_trama, sortear_trama_para_motivacao


def _resumo_mapa(mapa: list[list[object]]) -> list[list[tuple[str, str]]]:
    """Reduz o mapa a tipo/nome para comparar determinismo sem depender de objetos."""
    return [[(sala.tipo, sala.nome) for sala in linha] for linha in mapa]


def test_criar_rng_com_seed_igual_reproduz_mesma_sequencia() -> None:
    """Seeds idênticas devem produzir a mesma sequência pseudoaleatória."""
    _, rng_1 = criar_rng(12345)
    _, rng_2 = criar_rng(12345)

    assert [rng_1.randint(1, 100) for _ in range(5)] == [rng_2.randint(1, 100) for _ in range(5)]


def test_restaurar_rng_reproduz_estado_serializado() -> None:
    """Estado serializado do RNG deve permitir retomar a sequência exatamente no mesmo ponto."""
    _, rng_original = criar_rng(98765)
    prefixo = [rng_original.random() for _ in range(3)]
    estado = serializar_estado_rng(rng_original)
    sufixo_esperado = [rng_original.random() for _ in range(4)]

    _, rng_restaurado = restaurar_rng(98765, estado)

    assert prefixo
    assert [rng_restaurado.random() for _ in range(4)] == sufixo_esperado


def test_trama_com_rng_isolado_fica_reproduzivel() -> None:
    """O sorteio de trama deve respeitar o RNG da run."""
    rng_a = random.Random(2026)
    rng_b = random.Random(2026)

    trama_a = sortear_trama_para_motivacao("guerreiro_vinganca_mentor", rng=rng_a)
    trama_b = sortear_trama_para_motivacao("guerreiro_vinganca_mentor", rng=rng_b)

    assert trama_a is not None
    assert trama_b is not None
    assert trama_a.to_dict() == trama_b.to_dict()
    assert gerar_pista_trama(trama_a, 2, rng=rng_a) == gerar_pista_trama(trama_b, 2, rng=rng_b)


def test_gerar_mapa_com_mesma_seed_reproduz_layout() -> None:
    """Gerar o mesmo andar com a mesma seed deve manter layout e salas equivalentes."""
    _, rng_a = criar_rng(424242)
    _, rng_b = criar_rng(424242)

    mapa_a = gerar_mapa(2, config.DIFICULDADES["normal"], rng=rng_a)
    mapa_b = gerar_mapa(2, config.DIFICULDADES["normal"], rng=rng_b)

    assert _resumo_mapa(mapa_a) == _resumo_mapa(mapa_b)
