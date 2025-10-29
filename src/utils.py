import os

def limpar_tela():
    """Limpa o terminal para melhorar a legibilidade."""
    os.system('cls' if os.name == 'nt' else 'clear')

def tela_game_over():
    """Exibe a tela de fim de jogo."""
    limpar_tela()
    print("=================================")
    print("===                           ===")
    print("===         GAME OVER         ===")
    print("===                           ===")
    print("=================================")
    print("\nSua jornada termina aqui, herói.")
    print("Mas a masmorra sempre aguarda uma nova tentativa.")
    input("\nPressione Enter para voltar ao menu principal...")
