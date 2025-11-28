from src.economia import Moeda


def test_moeda_from_gp_sp_cp() -> None:
    """Converte ouro/prata/bronze em um único valor de bronze."""
    moeda = Moeda.from_gp_sp_cp(ouro=1, prata=2, bronze=3)
    assert moeda.valor_bronze == 1 * 100 + 2 * 10 + 3


def test_moeda_formatar() -> None:
    """Formata sempre exibindo ouro, prata e bronze."""
    moeda = Moeda(123)
    assert moeda.formatar() == "1 Ouro, 2 Prata, 3 Bronze"


def test_moeda_formatar_mostra_zeros() -> None:
    """Mesmo sem todas as casas, a string continua completa."""
    moeda = Moeda(70)
    assert moeda.formatar() == "0 Ouro, 7 Prata, 0 Bronze"


def test_moeda_to_from_dict() -> None:
    """Serializa e desserializa mantendo o valor."""
    moeda = Moeda(57)
    restored = Moeda.from_dict(moeda.to_dict())
    assert restored.valor_bronze == 57


def test_moeda_receber_gastar_tem() -> None:
    """Receber, gastar e verificar saldo usam regras coerentes."""
    bolsa = Moeda()
    bolsa.receber(25)
    assert bolsa.valor_bronze == 25
    assert bolsa.tem(10)
    assert bolsa.gastar(10) is True
    assert bolsa.valor_bronze == 15
    assert bolsa.gastar(30) is False
    assert not bolsa.tem(40)
