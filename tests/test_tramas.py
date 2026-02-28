from __future__ import annotations

from src import config
from src.gerador_mapa import gerar_mapa
from src.historias import carregar_historias
from src.tramas import TramaAtiva, carregar_tramas, gerar_pista_trama, sortear_trama_para_motivacao


def test_carregar_tramas_retorna_catalogo_valido() -> None:
    """Catálogo de tramas deve carregar entradas válidas."""
    tramas = carregar_tramas()
    assert tramas
    for trama in tramas:
        assert trama.andar_min >= 1
        assert trama.andar_max >= trama.andar_min
        assert trama.pistas
        assert trama.desfechos
        assert trama.consequencias


def test_sortear_trama_para_motivacao_retorna_trama_ativa() -> None:
    """Sorteio deve criar trama ativa coerente para uma motivação."""
    trama = sortear_trama_para_motivacao("guerreiro_vinganca_mentor")
    assert trama is not None
    assert trama.id
    assert trama.nome
    assert trama.andar_alvo >= 1
    assert trama.desfecho in {"vivo", "morto", "corrompido"}


def test_gerar_pista_trama_interpola_variaveis() -> None:
    """Pistas devem interpolar variáveis de contexto sem erro."""
    trama = TramaAtiva(
        id="teste",
        nome="Trama Teste",
        tema="mistério",
        motivacao_id="m1",
        andar_alvo=4,
        desfecho="morto",
        desfecho_texto="texto",
        sala_nome="Sala",
        sala_descricao="Desc",
        pistas=("Suba até {andar_alvo}; você está no {nivel_atual}.",),
    )
    pista = gerar_pista_trama(trama, 2)
    assert "4" in pista
    assert "2" in pista


def test_gerar_mapa_injeta_sala_de_trama_no_andar_alvo() -> None:
    """No andar-alvo, o mapa deve conter a sala especial de trama."""
    trama = TramaAtiva(
        id="trama_alvo",
        nome="Trama Alvo",
        tema="resgate",
        motivacao_id="m1",
        andar_alvo=1,
        desfecho="morto",
        desfecho_texto="Desfecho narrativo",
        sala_nome="Sala Narrativa",
        sala_descricao="Descrição narrativa",
        pistas=("pista",),
    )

    mapa = gerar_mapa(1, config.DIFICULDADES["normal"], trama_ativa=trama)
    salas_trama = [s for linha in mapa for s in linha if s.trama_id == "trama_alvo"]

    assert len(salas_trama) == 1
    sala = salas_trama[0]
    assert sala.tipo == "trama"
    assert sala.nome == "Sala Narrativa"
    assert sala.trama_desfecho == "morto"


def test_motivacoes_de_tramas_existem_no_catalogo() -> None:
    """IDs de motivação em tramas devem existir em historias_personagem ou ser '*'."""
    ids_motivacao = {historia.id for historia in carregar_historias()}
    tramas = carregar_tramas()
    for trama in tramas:
        for motivacao in trama.motivacoes:
            assert motivacao == "*" or motivacao in ids_motivacao


def test_tramas_tem_consequencias_para_desfechos() -> None:
    """Cada desfecho de trama deve possuir pelo menos uma consequência registrada."""
    for trama in carregar_tramas():
        for desfecho in trama.desfechos:
            assert desfecho in trama.consequencias
            assert trama.consequencias[desfecho]
