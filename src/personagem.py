import time
from src.utils import limpar_tela

def criar_personagem():
    """Função para criar o personagem do jogador."""
    limpar_tela()
    print("=== Criação de Personagem ===")
    
    jogador = {
        "nome": "", "classe": "", "hp": 0, "hp_max": 0,
        "ataque": 0, "defesa": 0, "x": 0, "y": 0,
        "inventario": [], # Novo: Inventário do jogador
        "equipamento": {"arma": None, "escudo": None}, # Novo: Equipamentos
    }

    # Pede o nome do personagem
    while True:
        nome = input("Qual é o nome do seu herói? ")
        if nome.strip(): # Garante que o nome não seja vazio
            jogador["nome"] = nome
            break
        else:
            print("O nome não pode estar em branco.")

    # Pede para escolher a classe
    print("\nEscolha sua classe:")
    print("1. Guerreiro (HP: 25, Ataque: 6, Defesa: 4)")
    print("2. Mago      (HP: 15, Ataque: 8, Defesa: 2)")
    print("3. Arqueiro  (HP: 20, Ataque: 7, Defesa: 3)")

    while True:
        escolha_classe = input("> ")
        if escolha_classe == "1":
            jogador["classe"] = "Guerreiro"
            jogador["hp_max"] = 25
            jogador["hp"] = 25
            jogador["ataque"] = 6
            jogador["defesa"] = 4
            break
        elif escolha_classe == "2":
            jogador["classe"] = "Mago"
            jogador["hp_max"] = 15
            jogador["hp"] = 15
            jogador["ataque"] = 8
            jogador["defesa"] = 2
            break
        elif escolha_classe == "3":
            jogador["classe"] = "Arqueiro"
            jogador["hp_max"] = 20
            jogador["hp"] = 20
            jogador["ataque"] = 7
            jogador["defesa"] = 3
            break
        else:
            print("Opção inválida! Escolha 1, 2 ou 3.")
    
    limpar_tela()
    print(f"Personagem criado!")
    print("--------------------")
    print(f"Nome:   {jogador['nome']}")
    print(f"Classe: {jogador['classe']}")
    print(f"HP:     {jogador['hp']}/{jogador['hp_max']}")
    print(f"Ataque: {jogador['ataque']}")
    print(f"Defesa: {jogador['defesa']}")
    print("--------------------")
    print("\nA aventura vai começar...")
    time.sleep(4)
    return jogador
