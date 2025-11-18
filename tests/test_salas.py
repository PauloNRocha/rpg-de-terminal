from collections import defaultdict

from src import salas


def test_sortear_sala_template_cobre_baralho() -> None:
    """Não repete nomes até esgotar o baralho da categoria."""
    catalogo = salas.carregar_salas()
    categoria = "caminho"
    usados: dict[str, set[str]] = defaultdict(set)
    vistos: set[str] = set()
    total = len(catalogo[categoria])
    for _ in range(total):
        template = salas.sortear_sala_template(categoria, usados)
        assert template.nome not in vistos
        vistos.add(template.nome)
    # Agora o baralho é resetado e um nome já conhecido pode voltar
    template = salas.sortear_sala_template(categoria, usados)
    assert template.nome in vistos
