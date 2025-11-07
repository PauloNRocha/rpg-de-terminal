import copy
import json
import random
from pathlib import Path
from typing import Any

from src.entidades import Inimigo

TemplatesInimigos = dict[str, dict[str, Any]]

# Carrega os templates de inimigos do arquivo JSON
try:
    caminho_json: Path = Path(__file__).parent / "data" / "inimigos.json"
    with open(caminho_json, encoding="utf-8") as f:
        INIMIGO_TEMPLATES: TemplatesInimigos = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    # Fallback para o caso de o arquivo não ser encontrado ou for inválido
    INIMIGO_TEMPLATES = {}


def gerar_inimigo(nivel: int, tipo_inimigo: str | None = None) -> Inimigo:
    """Gera um inimigo com atributos escalados para um nível específico."""
    if not INIMIGO_TEMPLATES:
        raise RuntimeError("Não foi possível carregar os templates de inimigos do arquivo JSON.")

    # Escolhe um tipo de inimigo
    if tipo_inimigo and tipo_inimigo in INIMIGO_TEMPLATES:
        tipo_escolhido = tipo_inimigo
    else:
        # Exclui o chefe da geração aleatória normal
        tipos_disponiveis: list[str] = [k for k in INIMIGO_TEMPLATES if k != "chefe_orc"]
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

    return Inimigo(
        nome=f"{template['nome']} (Nível {nivel})",
        hp=hp,
        hp_max=hp,
        ataque=ataque,
        defesa=defesa,
        xp_recompensa=xp_recompensa,
        drop_raridade=template["drop_raridade"],
    )
