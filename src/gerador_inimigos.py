import random
import copy
from src.inimigos import INIMIGO_TEMPLATES

def gerar_inimigo(nivel):
    """
    Gera um inimigo aleatório com atributos escalados para um nível específico.
    """
    # Escolhe um tipo de inimigo aleatoriamente
    tipo_inimigo = random.choice(list(INIMIGO_TEMPLATES.keys()))
    template = copy.deepcopy(INIMIGO_TEMPLATES[tipo_inimigo])

    # Fator de escala (aumenta 10% por nível, por exemplo)
    fator_escala = 1 + (nivel - 1) * 0.15

    # Escala os atributos
    hp = int(template["hp_base"] * fator_escala)
    ataque = int(template["ataque_base"] * fator_escala)
    defesa = int(template["defesa_base"] * fator_escala)
    xp_recompensa = int(template["xp_base"] * fator_escala)

    # Monta o dicionário final do inimigo
    inimigo_gerado = {
        "nome": f"{template['nome']} (Nível {nivel})",
        "hp": hp,
        "ataque": ataque,
        "defesa": defesa,
        "xp_recompensa": xp_recompensa,
        "drop_raridade": template["drop_raridade"]
    }

    return inimigo_gerado
