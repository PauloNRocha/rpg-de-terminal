import copy
import json
import random
import unicodedata
from pathlib import Path
from typing import Any

from src import config
from src.chefes import ChefeConfig
from src.entidades import Inimigo
from src.erros import ErroDadosError

TemplatesInimigos = dict[str, dict[str, Any]]


def carregar_templates() -> TemplatesInimigos:
    """Carrega os templates de inimigos do arquivo JSON."""
    caminho_json: Path = Path(__file__).parent / "data" / "inimigos.json"
    try:
        with open(caminho_json, encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError as erro:
        raise ErroDadosError("Arquivo 'inimigos.json' não foi encontrado em src/data/.") from erro
    except json.JSONDecodeError as erro:
        raise ErroDadosError("Arquivo 'inimigos.json' está inválido (JSON malformado).") from erro
    if not isinstance(dados, dict) or not dados:
        raise ErroDadosError("Arquivo 'inimigos.json' está vazio ou com formato incorreto.")
    return dados


try:
    INIMIGO_TEMPLATES: TemplatesInimigos = carregar_templates()
    _ERRO_INIMIGOS: ErroDadosError | None = None
except ErroDadosError as erro:
    INIMIGO_TEMPLATES = {}
    _ERRO_INIMIGOS = erro


def obter_templates() -> TemplatesInimigos:
    """Expõe os templates carregados ou dispara um erro amigável."""
    if _ERRO_INIMIGOS is not None:
        raise _ERRO_INIMIGOS
    if not INIMIGO_TEMPLATES:
        raise ErroDadosError("Nenhum inimigo disponível em 'inimigos.json'.")
    return INIMIGO_TEMPLATES


def _aplicar_variacao(valor: int) -> int:
    """Aplica um desvio aleatório controlado ao atributo informado."""
    variacao = random.uniform(
        -config.INIMIGO_VARIACAO_PERCENTUAL,
        config.INIMIGO_VARIACAO_PERCENTUAL,
    )
    return max(1, int(valor * (1 + variacao)))


def gerar_inimigo(
    nivel: int,
    tipo_inimigo: str | None = None,
    dificuldade: config.DificuldadePerfil | None = None,
    chefe: bool = False,
    perfil_chefe: ChefeConfig | None = None,
    tema: str | None = None,
) -> Inimigo:
    """Gera um inimigo com atributos escalados para um nível específico."""
    templates = obter_templates()

    # Escolhe um tipo de inimigo
    if chefe and perfil_chefe is not None:
        tipo_escolhido = perfil_chefe.tipo
    elif tipo_inimigo and tipo_inimigo in templates:
        tipo_escolhido = tipo_inimigo
    else:
        tipos_disponiveis: list[str] = [k for k in templates if not k.startswith("chefe_")]
        if not tipos_disponiveis:
            raise ValueError("Nenhum inimigo (exceto chefe) disponível para geração aleatória.")
        tipo_escolhido = _sortear_tipo_por_tema(tipos_disponiveis, templates, tema)

    template = copy.deepcopy(templates[tipo_escolhido])

    fator_escala = config.fator_inimigo_por_nivel(nivel)

    # Escala os atributos
    hp = _aplicar_variacao(int(template["hp_base"] * fator_escala))
    ataque = _aplicar_variacao(int(template["ataque_base"] * fator_escala))
    defesa = _aplicar_variacao(int(template["defesa_base"] * fator_escala))
    xp_recompensa = max(1, int(template["xp_base"] * fator_escala))

    if chefe:
        (
            bonus_hp,
            bonus_ataque,
            bonus_defesa,
            bonus_xp,
        ) = config.obter_bonus_chefe(nivel)
        hp = int(hp * (1 + bonus_hp))
        ataque = int(ataque * (1 + bonus_ataque))
        defesa = int(defesa * (1 + bonus_defesa))
        xp_recompensa = int(xp_recompensa * bonus_xp)

    if dificuldade is not None:
        hp = max(1, int(hp * dificuldade.inimigo_hp_mult))
        ataque = max(1, int(ataque * dificuldade.inimigo_ataque_mult))
        defesa = max(0, int(defesa * dificuldade.inimigo_defesa_mult))
        xp_recompensa = max(1, int(xp_recompensa * dificuldade.xp_recompensa_mult))

    nome_base = template["nome"]
    if chefe and perfil_chefe is not None and perfil_chefe.nome:
        nome_base = perfil_chefe.nome

    return Inimigo(
        nome=f"{nome_base} (Nível {nivel})",
        hp=hp,
        hp_max=hp,
        ataque=ataque,
        defesa=defesa,
        xp_recompensa=xp_recompensa,
        drop_raridade=template["drop_raridade"],
    )


def _sortear_tipo_por_tema(
    tipos_disponiveis: list[str],
    templates: TemplatesInimigos,
    tema: str | None,
) -> str:
    """Sorteia um tipo de inimigo com peso para tags do tema narrativo."""
    if not tema:
        return random.choice(tipos_disponiveis)

    tema_norm = _normalizar_tag(tema)
    pesos = [
        config.TEMA_PESO_INIMIGO_COMPATIVEL
        if tema_norm in _tags_template(templates.get(tipo, {}))
        else 1.0
        for tipo in tipos_disponiveis
    ]
    if all(peso == 1.0 for peso in pesos):
        return random.choice(tipos_disponiveis)
    return random.choices(tipos_disponiveis, weights=pesos, k=1)[0]


def _tags_template(template: dict[str, Any]) -> set[str]:
    """Retorna as tags normalizadas de um template de inimigo."""
    tags_raw = template.get("tags", [])
    if not isinstance(tags_raw, list):
        return set()
    return {_normalizar_tag(str(tag)) for tag in tags_raw if str(tag).strip()}


def _normalizar_tag(tag: str) -> str:
    """Normaliza tags removendo acentos e padronizando caixa."""
    texto = unicodedata.normalize("NFKD", tag.strip().lower())
    return "".join(ch for ch in texto if not unicodedata.combining(ch))
