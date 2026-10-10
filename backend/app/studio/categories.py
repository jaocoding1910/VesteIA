"""Categorias de peça e regiões do corpo que cada uma ocupa."""
from __future__ import annotations

# slot: região substituída. Vestir uma peça de um slot substitui a peça anterior do mesmo slot.
CATEGORIES: dict[str, dict] = {
    "camiseta": {"label": "Camiseta", "slot": "upper", "en": "t-shirt"},
    "camisa": {"label": "Camisa", "slot": "upper", "en": "button-up shirt"},
    "blusa": {"label": "Blusa", "slot": "upper", "en": "blouse"},
    "regata": {"label": "Regata", "slot": "upper", "en": "tank top"},
    "moletom": {"label": "Moletom", "slot": "upper", "en": "sweatshirt"},
    "casaco": {"label": "Casaco", "slot": "outer", "en": "coat"},
    "jaqueta": {"label": "Jaqueta", "slot": "outer", "en": "jacket"},
    "calca": {"label": "Calça", "slot": "lower", "en": "trousers"},
    "short": {"label": "Short", "slot": "lower", "en": "shorts"},
    "bermuda": {"label": "Bermuda", "slot": "lower", "en": "bermuda shorts"},
    "saia": {"label": "Saia", "slot": "lower", "en": "skirt"},
    "vestido": {"label": "Vestido", "slot": "full", "en": "dress"},
    "macacao": {"label": "Macacão", "slot": "full", "en": "jumpsuit"},
}

SLOT_LABEL = {"upper": "parte de cima", "outer": "sobreposição", "lower": "parte de baixo", "full": "peça inteira"}
# Ordem de aplicação em provedores que vestem uma peça por chamada.
SLOT_ORDER = {"full": 0, "lower": 1, "upper": 2, "outer": 3}

# Medidas da peça por tipo (centímetros). "plana" = peça esticada sobre a mesa.
GARMENT_FIELDS: dict[str, list[tuple[str, str]]] = {
    "upper": [("largura_cm", "Largura do tórax (peça plana)"), ("comprimento_cm", "Comprimento"),
              ("manga_cm", "Comprimento da manga"), ("ombro_cm", "Ombro a ombro")],
    "outer": [("largura_cm", "Largura do tórax (peça plana)"), ("comprimento_cm", "Comprimento"),
              ("manga_cm", "Comprimento da manga"), ("ombro_cm", "Ombro a ombro")],
    "lower": [("cintura_cm", "Cintura (peça plana)"), ("quadril_cm", "Quadril (peça plana)"),
              ("comprimento_cm", "Comprimento lateral"), ("entreperna_cm", "Entrepernas")],
    "full": [("busto_cm", "Busto (peça plana)"), ("cintura_cm", "Cintura (peça plana)"),
             ("quadril_cm", "Quadril (peça plana)"), ("comprimento_cm", "Comprimento")],
}


def slot_of(category: str) -> str:
    try:
        return CATEGORIES[category]["slot"]
    except KeyError as error:
        raise ValueError("Categoria não suportada.") from error


def compose_look(categories_in_order: list[str]) -> list[int]:
    """Resolve conflitos de região. Recebe categorias na ordem em que foram escolhidas e
    devolve os índices que permanecem no look (a última peça de cada região vence;
    peça inteira remove parte de cima e de baixo; parte de cima/baixo remove peça inteira)."""
    kept: dict[str, int] = {}
    for index, category in enumerate(categories_in_order):
        slot = slot_of(category)
        if slot == "full":
            kept.pop("upper", None)
            kept.pop("lower", None)
        elif slot in ("upper", "lower"):
            kept.pop("full", None)
        kept[slot] = index
    return sorted(kept.values(), key=lambda i: SLOT_ORDER[slot_of(categories_in_order[i])])
