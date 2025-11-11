import pytest

import jogo  # Importa o módulo todo para o monkeypatch
from jogo import (
    agrupar_itens_equipaveis,
    aplicar_bonus_equipamento,
    aplicar_efeitos_consumiveis,
    hidratar_mapa,
    remover_item_por_chave,
    serializar_mapa,
    verificar_level_up,
)
from src.economia import Moeda
from src.entidades import Inimigo, Item, Personagem, Sala


# Fixture para criar um jogador base para os testes
@pytest.fixture
def jogador_base() -> Personagem:
    """Cria uma instância de Personagem base para ser usada nos testes."""
    return Personagem(
        nome="Teste",
        classe="Guerreiro",
        hp=25,
        hp_max=25,
        ataque_base=6,
        defesa_base=4,
        ataque=6,
        defesa=4,
        x=0,
        y=0,
        inventario=[],
        equipamento={"arma": None, "escudo": None},
        nivel=1,
        xp_atual=0,
        xp_para_proximo_nivel=100,
        carteira=Moeda.from_gp_sp_cp(),
    )


# Fixture para criar itens para os testes de equipamento
@pytest.fixture
def espada_curta() -> Item:
    """Cria uma instância de Item para uma espada curta."""
    return Item(nome="Espada Curta", tipo="arma", descricao="", bonus={"ataque": 3})


@pytest.fixture
def escudo_madeira() -> Item:
    """Cria uma instância de Item para um escudo de madeira."""
    return Item(nome="Escudo de Madeira", tipo="escudo", descricao="", bonus={"defesa": 2})


# --- Testes para verificar_level_up ---


def test_level_up_unico(jogador_base: Personagem, monkeypatch: pytest.MonkeyPatch) -> None:
    """Testa se o jogador sobe um nível corretamente."""
    # Substitui a função de UI por uma que não faz nada para evitar o input()
    monkeypatch.setattr(jogo, "desenhar_tela_evento", lambda titulo, mensagem: None)

    jogador_base.xp_atual = 120
    verificar_level_up(jogador_base)
    assert jogador_base.nivel == 2
    assert jogador_base.xp_atual == 20
    assert jogador_base.xp_para_proximo_nivel == 150
    assert jogador_base.hp_max == 35
    assert jogador_base.ataque_base == 8
    assert jogador_base.defesa_base == 5
    assert jogador_base.hp == 35  # HP deve ser restaurado ao máximo


def test_level_up_multiplo(jogador_base: Personagem, monkeypatch: pytest.MonkeyPatch) -> None:
    """Testa se o jogador sobe múltiplos níveis de uma vez."""
    # Substitui a função de UI por uma que não faz nada para evitar o input()
    monkeypatch.setattr(jogo, "desenhar_tela_evento", lambda titulo, mensagem: None)

    # XP para nível 2: 100. XP para nível 3: 150. Total: 250
    jogador_base.xp_atual = 270
    verificar_level_up(jogador_base)
    assert jogador_base.nivel == 3
    # Sobra 20 XP (270 - 100 - 150)
    assert jogador_base.xp_atual == 20
    # Próximo nível (4) custará 150 * 1.5 = 225
    assert jogador_base.xp_para_proximo_nivel == 225
    # Stats: Nível 1 -> 2 (+10 HP, +2 ATK, +1 DEF), Nível 2 -> 3 (+10 HP, +2 ATK, +1 DEF)
    assert jogador_base.hp_max == 45  # 25 + 10 + 10
    assert jogador_base.ataque_base == 10  # 6 + 2 + 2
    assert jogador_base.defesa_base == 6  # 4 + 1 + 1


def test_sem_level_up(jogador_base: Personagem) -> None:
    """Testa se nada acontece se o XP for insuficiente."""
    jogador_base.xp_atual = 50
    verificar_level_up(jogador_base)
    assert jogador_base.nivel == 1
    assert jogador_base.xp_atual == 50
    assert jogador_base.hp_max == 25


# --- Testes para aplicar_bonus_equipamento ---


def test_aplicar_bonus_arma(jogador_base: Personagem, espada_curta: Item) -> None:
    """Testa se o bônus de ataque da arma é aplicado."""
    jogador_base.equipamento["arma"] = espada_curta
    aplicar_bonus_equipamento(jogador_base)
    assert jogador_base.ataque == 9  # 6 (base) + 3 (arma)
    assert jogador_base.defesa == 4  # Defesa inalterada


def test_aplicar_bonus_escudo(jogador_base: Personagem, escudo_madeira: Item) -> None:
    """Testa se o bônus de defesa do escudo é aplicado."""
    jogador_base.equipamento["escudo"] = escudo_madeira
    aplicar_bonus_equipamento(jogador_base)
    assert jogador_base.ataque == 6  # Ataque inalterado
    assert jogador_base.defesa == 6  # 4 (base) + 2 (escudo)


def test_aplicar_bonus_arma_e_escudo(
    jogador_base: Personagem, espada_curta: Item, escudo_madeira: Item
) -> None:
    """Testa se os bônus de arma e escudo são aplicados simultaneamente."""
    jogador_base.equipamento["arma"] = espada_curta
    jogador_base.equipamento["escudo"] = escudo_madeira
    aplicar_bonus_equipamento(jogador_base)
    assert jogador_base.ataque == 9  # 6 + 3
    assert jogador_base.defesa == 6  # 4 + 2


def test_remover_equipamento(jogador_base: Personagem, espada_curta: Item) -> None:
    """Testa se os status voltam ao normal ao desequipar."""
    jogador_base.equipamento["arma"] = espada_curta
    aplicar_bonus_equipamento(jogador_base)
    assert jogador_base.ataque == 9  # Confirma que o bônus foi aplicado

    # Desequipa
    jogador_base.equipamento["arma"] = None
    aplicar_bonus_equipamento(jogador_base)
    assert jogador_base.ataque == 6  # Volta ao valor base


def test_serializar_e_hidratar_mapa() -> None:
    """Garante que inimigos ativos são serializados e reconstruídos corretamente."""
    inimigo = Inimigo(
        nome="Goblin",
        hp=10,
        hp_max=10,
        ataque=3,
        defesa=1,
        xp_recompensa=5,
        drop_raridade="comum",
    )
    mapa = [
        [
            Sala(
                tipo="sala",
                nome="Sala Teste",
                descricao="",
                pode_ter_inimigo=True,
                inimigo_atual=inimigo,
            )
        ]
    ]
    serializado = serializar_mapa(mapa)
    assert isinstance(serializado[0][0]["inimigo_atual"], dict)

    hidratado = hidratar_mapa(serializado)
    assert isinstance(hidratado[0][0].inimigo_atual, Inimigo)


def test_aplicar_efeitos_consumiveis_altera_atributos(jogador_base: Personagem) -> None:
    """Consumíveis com múltiplos efeitos devem aplicar todos os handlers registrados."""
    jogador_base.hp = 10
    poção = Item(
        nome="Poção Maior",
        tipo="consumivel",
        descricao="",
        efeito={"hp": 10, "xp": 20},
    )
    mensagens = aplicar_efeitos_consumiveis(jogador_base, poção)
    assert "recuperou" in mensagens[0]
    assert "XP" in mensagens[1]
    assert jogador_base.hp == 20
    assert jogador_base.xp_atual == 20


def test_agrupar_itens_equipaveis(jogador_base: Personagem, espada_curta: Item) -> None:
    """Itens iguais devem ser agrupados com quantidade correta."""
    outra_espada = Item(nome="Espada Curta", tipo="arma", descricao="", bonus={"ataque": 3})
    escudo = Item(nome="Escudo de Madeira", tipo="escudo", descricao="", bonus={"defesa": 2})
    jogador_base.inventario = [espada_curta, escudo, outra_espada]

    grupos = agrupar_itens_equipaveis(jogador_base.inventario)
    assert len(grupos) == 2
    assert grupos[0]["item"].nome == "Espada Curta"
    assert grupos[0]["quantidade"] == 2
    assert grupos[1]["item"].nome == "Escudo de Madeira"
    assert grupos[1]["quantidade"] == 1


def test_remover_item_por_chave(jogador_base: Personagem, espada_curta: Item) -> None:
    """Remover item por chave deve retirar apenas uma instância do agrupamento."""
    outra_espada = Item(nome="Espada Curta", tipo="arma", descricao="", bonus={"ataque": 3})
    jogador_base.inventario = [espada_curta, outra_espada]
    chave = (
        espada_curta.nome,
        espada_curta.tipo,
        tuple(sorted(espada_curta.bonus.items())),
        (),
    )

    removido = remover_item_por_chave(jogador_base.inventario, chave)
    assert removido.nome == "Espada Curta"
    assert len(jogador_base.inventario) == 1
