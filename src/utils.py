import os
from src.ui import desenhar_tela_evento

def limpar_tela():
    """Limpa a tela do terminal, compatível com Windows e Linux/Mac."""
    os.system('cls' if os.name == 'nt' else 'clear')

def tela_game_over():
    """Exibe a tela de Game Over usando o novo sistema de UI."""
    titulo = "GAME OVER"
    mensagem = (
        "Você foi derrotado.\n"
        "A escuridão da caverna consome suas últimas memórias.\n\n"
        "Tente novamente."
    )
    desenhar_tela_evento(titulo, mensagem)
