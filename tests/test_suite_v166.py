from __future__ import annotations

import pytest

import jogo
from src import config, eventos, ui
from src.economia import Moeda
from src.entidades import Personagem, Sala


@pytest.fixture
def personagem_base() -> Personagem:
    """Cria um personagem mínimo para cenários de regressão."""
    return Personagem(
        nome="Teste",
        classe="Guerreiro",
        hp=25,
        hp_max=25,
        ataque=6,
        defesa=4,
        ataque_base=6,
        defesa_base=4,
        x=1,
        y=1,
        nivel=1,
        xp_atual=0,
        xp_para_proximo_nivel=100,
        carteira=Moeda(),
    )


def _mapa_vazio(tamanho: int = 3) -> list[list[Sala]]:
    """Monta um mapa quadrado simples sem inimigos."""
    return [
        [
            Sala(
                tipo="sala",
                nome=f"Sala {x}-{y}",
                descricao="Sala de teste",
                pode_ter_inimigo=False,
            )
            for x in range(tamanho)
        ]
        for y in range(tamanho)
    ]


def test_contexto_resetar_jogo_limpa_campos_da_run(personagem_base: Personagem) -> None:
    """Reset do contexto não deve carregar estado residual entre aventuras."""
    contexto = jogo.ContextoJogo()
    contexto.jogador = personagem_base
    contexto.mapa_atual = _mapa_vazio()
    contexto.nivel_masmorra = 4
    contexto.chefe_mais_profundo_nivel = 3
    contexto.chefe_mais_profundo_nome = "Tirano"
    contexto.inimigo_causa_morte = "Necromante"
    contexto.turnos_totais = 42

    contexto.resetar_jogo()

    assert contexto.jogador is None
    assert contexto.mapa_atual is None
    assert contexto.nivel_masmorra == 1
    assert contexto.chefe_mais_profundo_nivel == 0
    assert contexto.chefe_mais_profundo_nome is None
    assert contexto.inimigo_causa_morte is None
    assert contexto.turnos_totais == 0


def test_evento_com_custo_sem_saldo_aborta_sem_efeitos(personagem_base: Personagem) -> None:
    """Eventos pagos devem abortar sem consumir HP/buffs quando falta moeda."""
    hp_antes = personagem_base.hp
    saldo_antes = personagem_base.carteira.valor_bronze

    mensagens, delta_moedas, sucesso = eventos.aplicar_efeitos(
        {"moedas": -20, "hp": -8}, personagem_base
    )

    assert sucesso is False
    assert delta_moedas == 0
    assert personagem_base.hp == hp_antes
    assert personagem_base.carteira.valor_bronze == saldo_antes
    assert "moedas suficientes" in "\n".join(mensagens).lower()


def test_evento_com_custo_aplica_e_retorna_delta_negativo(personagem_base: Personagem) -> None:
    """Quando há saldo, custo deve ser debitado e refletido no delta retornado."""
    personagem_base.carteira.receber(100)

    mensagens, delta_moedas, sucesso = eventos.aplicar_efeitos(
        {"moedas": -20, "hp": -8}, personagem_base
    )

    assert sucesso is True
    assert delta_moedas == -20
    assert personagem_base.carteira.valor_bronze == 80
    assert personagem_base.hp == 17
    assert "sacrificou" in "\n".join(mensagens).lower()


@pytest.mark.parametrize(
    ("tecla", "esperado"),
    [
        ("w", (1, 0)),
        ("s", (1, 2)),
        ("a", (0, 1)),
        ("d", (2, 1)),
        ("k", (1, 0)),
        ("j", (1, 2)),
        ("h", (0, 1)),
        ("l", (2, 1)),
    ],
)
def test_exploracao_move_com_teclas_alternativas(
    personagem_base: Personagem,
    monkeypatch: pytest.MonkeyPatch,
    tecla: str,
    esperado: tuple[int, int],
) -> None:
    """Teclas WASD/HJKL devem mapear para os mesmos movimentos numéricos."""
    contexto = jogo.ContextoJogo(jogador=personagem_base, mapa_atual=_mapa_vazio())

    monkeypatch.setattr(config, "TECLAS_ALTERNATIVAS", True)
    monkeypatch.setattr(jogo, "desenhar_hud_exploracao", lambda *args, **kwargs: tecla)
    monkeypatch.setattr(jogo, "desenhar_tela_evento", lambda *args, **kwargs: None)

    estado = jogo.executar_estado_exploracao(contexto)

    assert estado == jogo.Estado.EXPLORACAO
    assert (personagem_base.x, personagem_base.y) == esperado
    assert contexto.posicao_anterior == (1, 1)
    assert contexto.turnos_totais == 1


def test_selecao_save_aceita_numero_sugerido_sem_saves(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ao iniciar sem saves, digitar o slot sugerido deve criar novo slot."""
    monkeypatch.setattr(ui.console, "print", lambda *args, **kwargs: None)
    monkeypatch.setattr(ui.console, "input", lambda *args, **kwargs: "1")

    slot = ui.desenhar_selecao_save(
        saves=[],
        titulo="Selecione",
        pode_criar_novo=True,
        sugestao_novo=1,
    )

    assert slot == "1"


def test_minimapa_renderiza_marcadores_esperados(personagem_base: Personagem) -> None:
    """Minimapa deve mostrar jogador, sala visitada, escada e chefe vivo."""
    mapa = _mapa_vazio()
    mapa[0][1].visitada = True
    mapa[1][2].tipo = "escada"
    mapa[2][1].chefe = True
    mapa[2][1].inimigo_derrotado = False

    panel = ui._render_minimapa(mapa, personagem_base)
    texto = panel.renderable.plain

    assert "@" in texto
    assert "." in texto
    assert "E" in texto
    assert "C" in texto
    assert "[bold" not in texto
