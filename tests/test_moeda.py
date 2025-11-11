from src.entidades import Moeda


def test_moeda_from_gp_sp_cp() -> None:
    """Converte ouro/prata/bronze em um único valor de bronze."""
    moeda = Moeda.from_gp_sp_cp(ouro=1, prata=2, bronze=3)
    assert moeda.valor_bronze == 1 * 100 + 2 * 10 + 3


def test_moeda_formatar() -> None:
    """Formata o valor em uma string amigável."""
    moeda = Moeda(123)
    assert moeda.formatar() == "1 Ouro, 2 Prata, 3 Bronze"


def test_moeda_to_from_dict() -> None:
    """Serializa e desserializa mantendo o valor."""
    moeda = Moeda(57)
    restored = Moeda.from_dict(moeda.to_dict())
    assert restored.valor_bronze == 57
