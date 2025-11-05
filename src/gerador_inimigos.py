import random
import copy
import json
from pathlib import Path

# Carrega os templates de inimigos do arquivo JSON
try:
    caminho_json = Path(__file__).parent.parent / "data" / "inimigos.json"
    with open(caminho_json, "r", encoding="utf-8") as f:
        INIMIGO_TEMPLATES = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    # Fallback para o caso de o arquivo não ser encontrado ou for inválido
    INIMIGO_TEMPLATES = {}

def gerar_inimigo(nivel, tipo_inimigo=None):
    """
    Gera um inimigo com atributos escalados para um nível específico.
    Se 'tipo_inimigo' for fornecido, gera esse tipo. Caso contrário, escolhe um aleatório.
    """
    if not INIMIGO_TEMPLATES:
        raise RuntimeError("Não foi possível carregar os templates de inimigos do arquivo JSON.")

    # Escolhe um tipo de inimigo
    if tipo_inimigo and tipo_inimigo in INIMIGO_TEMPLATES:
        tipo_escolhido = tipo_inimigo
    else:
        # Exclui o chefe da geração aleatória normal
        tipos_disponiveis = [k for k in INIMIGO_TEMPLATES.keys() if k != "chefe_orc"]
        if not tipos_disponiveis:
            raise ValueError("Nenhum inimigo (exceto chefe) disponível para geração aleatória.")
        tipo_escolhido = random.choice(tipos_disponiveis)
    
    template = copy.deepcopy(INIMIGO_TEMPLATES[tipo_escolhido])

    # Fator de escala (aumenta 15% por nível, por exemplo)
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
        "hp_max": hp, # Adiciona hp_max para consistência
        "ataque": ataque,
        "defesa": defesa,
        "xp_recompensa": xp_recompensa,
        "drop_raridade": template["drop_raridade"]
    }

    return inimigo_gerado
