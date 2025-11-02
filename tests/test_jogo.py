import pytest
import jogo # Importa o módulo todo para o monkeypatch
from jogo import verificar_level_up, aplicar_bonus_equipamento

# Fixture para criar um jogador base para os testes
@pytest.fixture
def jogador_base():
    return {
        "nome": "Teste",
        "classe": "Guerreiro",
        "hp": 25,
        "hp_max": 25,
        "ataque_base": 6, # Adicionando ataque_base
        "defesa_base": 4,  # Adicionando defesa_base
        "ataque": 6,
        "defesa": 4,
        "x": 0, "y": 0,
        "inventario": [],
        "equipamento": {"arma": None, "escudo": None},
        "nivel": 1,
        "xp_atual": 0,
        "xp_para_proximo_nivel": 100,
    }

# --- Testes para verificar_level_up ---

def test_level_up_unico(jogador_base, monkeypatch):
    """Testa se o jogador sobe um nível corretamente."""
    # Substitui a função de UI por uma que não faz nada para evitar o input()
    monkeypatch.setattr(jogo, "desenhar_tela_evento", lambda titulo, mensagem: None)
    
    jogador_base["xp_atual"] = 120
    verificar_level_up(jogador_base)
    assert jogador_base["nivel"] == 2
    assert jogador_base["xp_atual"] == 20
    assert jogador_base["xp_para_proximo_nivel"] == 150
    assert jogador_base["hp_max"] == 35
    assert jogador_base["ataque_base"] == 8
    assert jogador_base["defesa_base"] == 5
    assert jogador_base["hp"] == 35 # HP deve ser restaurado ao máximo

def test_level_up_multiplo(jogador_base, monkeypatch):
    """Testa se o jogador sobe múltiplos níveis de uma vez."""
    # Substitui a função de UI por uma que não faz nada para evitar o input()
    monkeypatch.setattr(jogo, "desenhar_tela_evento", lambda titulo, mensagem: None)

    # XP para nível 2: 100. XP para nível 3: 150. Total: 250
    jogador_base["xp_atual"] = 270
    verificar_level_up(jogador_base)
    assert jogador_base["nivel"] == 3
    # Sobra 20 XP (270 - 100 - 150)
    assert jogador_base["xp_atual"] == 20
    # Próximo nível (4) custará 150 * 1.5 = 225
    assert jogador_base["xp_para_proximo_nivel"] == 225
    # Stats: Nível 1 -> 2 (+10 HP, +2 ATK, +1 DEF), Nível 2 -> 3 (+10 HP, +2 ATK, +1 DEF)
    assert jogador_base["hp_max"] == 45 # 25 + 10 + 10
    assert jogador_base["ataque_base"] == 10 # 6 + 2 + 2
    assert jogador_base["defesa_base"] == 6  # 4 + 1 + 1

def test_sem_level_up(jogador_base):
    """Testa se nada acontece se o XP for insuficiente."""
    jogador_base["xp_atual"] = 50
    verificar_level_up(jogador_base)
    assert jogador_base["nivel"] == 1
    assert jogador_base["xp_atual"] == 50
    assert jogador_base["hp_max"] == 25

# --- Testes para aplicar_bonus_equipamento ---

def test_aplicar_bonus_arma(jogador_base):
    """Testa se o bônus de ataque da arma é aplicado."""
    espada = {"nome": "Espada Curta", "tipo": "arma", "bonus": {"ataque": 3}}
    jogador_base["equipamento"]["arma"] = espada
    aplicar_bonus_equipamento(jogador_base)
    assert jogador_base["ataque"] == 9 # 6 (base) + 3 (arma)
    assert jogador_base["defesa"] == 4 # Defesa inalterada

def test_aplicar_bonus_escudo(jogador_base):
    """Testa se o bônus de defesa do escudo é aplicado."""
    escudo = {"nome": "Escudo de Madeira", "tipo": "escudo", "bonus": {"defesa": 2}}
    jogador_base["equipamento"]["escudo"] = escudo
    aplicar_bonus_equipamento(jogador_base)
    assert jogador_base["ataque"] == 6 # Ataque inalterado
    assert jogador_base["defesa"] == 6 # 4 (base) + 2 (escudo)

def test_aplicar_bonus_arma_e_escudo(jogador_base):
    """Testa se os bônus de arma e escudo são aplicados simultaneamente."""
    espada = {"nome": "Espada Curta", "tipo": "arma", "bonus": {"ataque": 3}}
    escudo = {"nome": "Escudo de Madeira", "tipo": "escudo", "bonus": {"defesa": 2}}
    jogador_base["equipamento"]["arma"] = espada
    jogador_base["equipamento"]["escudo"] = escudo
    aplicar_bonus_equipamento(jogador_base)
    assert jogador_base["ataque"] == 9 # 6 + 3
    assert jogador_base["defesa"] == 6 # 4 + 2

def test_remover_equipamento(jogador_base):
    """Testa se os status voltam ao normal ao desequipar."""
    espada = {"nome": "Espada Curta", "tipo": "arma", "bonus": {"ataque": 3}}
    jogador_base["equipamento"]["arma"] = espada
    aplicar_bonus_equipamento(jogador_base)
    assert jogador_base["ataque"] == 9 # Confirma que o bônus foi aplicado

    # Desequipa
    jogador_base["equipamento"]["arma"] = None
    aplicar_bonus_equipamento(jogador_base)
    assert jogador_base["ataque"] == 6 # Volta ao valor base
