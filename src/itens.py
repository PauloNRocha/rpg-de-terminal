# Templates base para os itens
ITEM_TEMPLATES = {
    "espada": {"nome": "Espada", "tipo": "arma", "bonus": {"ataque": 4}},
    "machado": {"nome": "Machado", "tipo": "arma", "bonus": {"ataque": 5}},
    "adaga": {"nome": "Adaga", "tipo": "arma", "bonus": {"ataque": 3}},
    "escudo_madeira": {"nome": "Escudo de Madeira", "tipo": "escudo", "bonus": {"defesa": 2}},
    "escudo_ferro": {"nome": "Escudo de Ferro", "tipo": "escudo", "bonus": {"defesa": 3}},
    "pocao_cura": {"nome": "Poção de Cura", "tipo": "consumivel", "efeito": {"hp": 15}, "descricao": "Restaura 15 pontos de vida."}
}

# Modificadores que podem ser aplicados aos itens
PREFIXOS = {
    "afiado": {"bonus": {"ataque": 2}, "nome": "Afiado(a)"},
    "enferrujado": {"bonus": {"ataque": -1}, "nome": "Enferrujado(a)"},
    "reforcado": {"bonus": {"defesa": 1}, "nome": "Reforçado(a)"},
    "magico": {"bonus": {"ataque": 1, "defesa": 1}, "nome": "Mágico(a)"}
}

SUFIXOS = {
    "da brutalidade": {"bonus": {"ataque": 3}, "nome": "da Brutalidade"},
    "da protecao": {"bonus": {"defesa": 2}, "nome": "da Proteção"}
}