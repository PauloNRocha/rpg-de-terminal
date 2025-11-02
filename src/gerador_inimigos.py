import random
import copy
from src.inimigos import INIMIGO_TEMPLATES

def gerar_inimigo(nivel, tipo_inimigo=None):
    """
    Gera um inimigo com atributos escalados para um nível específico.
    Se 'tipo_inimigo' for fornecido, gera esse tipo. Caso contrário, escolhe um aleatório.
    """
    # Escolhe um tipo de inimigo
    if tipo_inimigo and tipo_inimigo in INIMIGO_TEMPLATES:
        tipo_escolhido = tipo_inimigo
    else:
        # Exclui o chefe da geração aleatória normal
        tipos_disponiveis = [k for k in INIMIGO_TEMPLATES.keys() if k != "chefe_orc"]
        tipo_escolhido = random.choice(tipos_disponiveis)
    
    template = copy.deepcopy(INIMIGO_TEMPLATES[tipo_escolhido])

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
