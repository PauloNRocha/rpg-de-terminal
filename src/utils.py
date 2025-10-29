import os

def limpar_tela():
    """Limpa o terminal para melhorar a legibilidade."""
    os.system('cls' if os.name == 'nt' else 'clear')
