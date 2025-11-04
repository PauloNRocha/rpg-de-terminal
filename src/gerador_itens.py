import random
import copy
import json
from pathlib import Path

# Carrega os dados dos itens do arquivo JSON
def carregar_itens():
    caminho_arquivo = Path(__file__).parent / "data" / "itens.json"
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)

ITENS_POR_RARIDADE = carregar_itens()

def gerar_item_aleatorio(raridade="comum"):
    """
    Gera um item aleatório com base na raridade, selecionando de uma lista
    pré-definida carregada de um arquivo JSON.
    """
    if raridade not in ITENS_POR_RARIDADE:
        return None

    lista_itens = ITENS_POR_RARIDADE[raridade]
    item_escolhido = random.choice(lista_itens)
    
    return copy.deepcopy(item_escolhido)
