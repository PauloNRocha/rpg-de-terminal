import random
import copy
from src.itens import ITEM_TEMPLATES, PREFIXOS, SUFIXOS

def gerar_item_aleatorio(raridade="comum"):
    """
    Gera um item aleatório com base em templates e modificadores.
    A raridade influencia a chance de obter modificadores.
    """
    # Filtra templates para não gerar poções como equipamento
    templates_equipaveis = {k: v for k, v in ITEM_TEMPLATES.items() if v["tipo"] in ["arma", "escudo"]}
    
    # Escolhe um template de item aleatoriamente
    nome_template = random.choice(list(templates_equipaveis.keys()))
    item_base = copy.deepcopy(templates_equipaveis[nome_template])

    # Define a chance de aplicar modificadores com base na raridade
    chance_prefixo = 0
    chance_sufixo = 0
    if raridade == "comum":
        chance_prefixo = 0.25
    elif raridade == "incomum":
        chance_prefixo = 0.5
        chance_sufixo = 0.2
    elif raridade == "raro":
        chance_prefixo = 0.8
        chance_sufixo = 0.5

    novo_nome = item_base["nome"]
    
    # Aplica prefixo
    if random.random() < chance_prefixo:
        nome_prefixo, prefixo = random.choice(list(PREFIXOS.items()))
        novo_nome = f"{prefixo['nome']} {novo_nome}"
        for stat, bonus in prefixo["bonus"].items():
            item_base["bonus"][stat] = item_base["bonus"].get(stat, 0) + bonus

    # Aplica sufixo
    if random.random() < chance_sufixo:
        nome_sufixo, sufixo = random.choice(list(SUFIXOS.items()))
        novo_nome = f"{novo_nome} {sufixo['nome']}"
        for stat, bonus in sufixo["bonus"].items():
            item_base["bonus"][stat] = item_base["bonus"].get(stat, 0) + bonus
    
    item_base["nome"] = novo_nome
    
    # Gera a descrição com base nos bônus finais
    bonus_desc = []
    if "ataque" in item_base["bonus"] and item_base["bonus"]["ataque"] != 0:
        bonus_desc.append(f"+{item_base['bonus']['ataque']} Ataque")
    if "defesa" in item_base["bonus"] and item_base["bonus"]["defesa"] != 0:
        bonus_desc.append(f"+{item_base['bonus']['defesa']} Defesa")
    
    item_base["descricao"] = ", ".join(bonus_desc) if bonus_desc else "Nenhum bônus especial."

    return item_base
