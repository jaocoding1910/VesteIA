"""Comparação de tamanhos baseada somente em medidas informadas.

Nada aqui é estimado a partir de imagem. Sem medidas, a função informa a falta.
As faixas de folga são aproximações gerais e dependem de tecido e modelagem;
a mesma lógica existe em frontend/src/features/studio/sizeModel.js (exibição).
"""
from __future__ import annotations

import math

from app.studio.categories import GARMENT_FIELDS, slot_of

# Folga (cm) = circunferência da peça (plana × 2) − circunferência do corpo.
EASE_BANDS = {
    "torax": [(-math.inf, 0, "menor que o corpo (tende a apertar)"), (0, 5, "justa"), (5, 12, "regular"),
              (12, 20, "folgada"), (20, math.inf, "bem ampla")],
    "cintura": [(-math.inf, -1, "menor que o corpo (tende a apertar)"), (-1, 2, "justa"), (2, 6, "regular"),
                (6, math.inf, "folgada")],
    "quadril": [(-math.inf, 0, "menor que o corpo (tende a apertar)"), (0, 4, "justa"), (4, 10, "regular"),
                (10, 18, "folgada"), (18, math.inf, "bem ampla")],
}

BODY_FIELDS = ("torax_cm", "cintura_cm", "quadril_cm", "ombros_cm", "entreperna_cm", "altura_cm")


def _num(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and 1 <= number <= 300 else None


def clean_measures(raw: dict | None, allowed: tuple[str, ...] | list[str]) -> dict[str, float]:
    out: dict[str, float] = {}
    for key in allowed:
        number = _num((raw or {}).get(key))
        if number is not None:
            out[key] = round(number, 1)
    return out


def _band(kind: str, ease: float) -> str:
    for low, high, label in EASE_BANDS[kind]:
        if low <= ease < high:
            return label
    return "regular"


def garment_fields(category: str) -> list[str]:
    return [key for key, _ in GARMENT_FIELDS[slot_of(category)]]


def compare_size(category: str, garment: dict, body: dict) -> list[dict]:
    """Retorna observações por dimensão. Só compara o que foi informado dos dois lados."""
    slot = slot_of(category)
    notes: list[dict] = []
    pairs = []
    if slot in ("upper", "outer"):
        pairs = [("largura_cm", "torax_cm", "torax", "Tórax")]
    elif slot == "lower":
        pairs = [("cintura_cm", "cintura_cm", "cintura", "Cintura"), ("quadril_cm", "quadril_cm", "quadril", "Quadril")]
    elif slot == "full":
        pairs = [("busto_cm", "torax_cm", "torax", "Busto"), ("cintura_cm", "cintura_cm", "cintura", "Cintura"),
                 ("quadril_cm", "quadril_cm", "quadril", "Quadril")]
    for gkey, bkey, kind, label in pairs:
        if gkey in garment and bkey in body:
            ease = round(garment[gkey] * 2 - body[bkey], 1)
            notes.append({"dimensao": label, "folga_cm": ease, "leitura": _band(kind, ease)})
    if slot in ("upper", "outer") and "ombro_cm" in garment and "ombros_cm" in body:
        diff = round(garment["ombro_cm"] - body["ombros_cm"], 1)
        reading = ("ombro mais estreito que o corpo" if diff < -2 else "costura na linha do ombro" if diff <= 2
                   else "ombro levemente caído" if diff <= 6 else "ombro caído (modelagem ampla)")
        notes.append({"dimensao": "Ombros", "diferenca_cm": diff, "leitura": reading})
    if slot == "lower" and "entreperna_cm" in garment and "entreperna_cm" in body:
        diff = round(garment["entreperna_cm"] - body["entreperna_cm"], 1)
        reading = "mais curta que a perna" if diff < -3 else "na medida da perna" if diff <= 3 else "mais longa (pode sobrar na barra)"
        notes.append({"dimensao": "Entrepernas", "diferenca_cm": diff, "leitura": reading})
    return notes


def describe_for_prompt(category: str, size_label: str, garment: dict, body: dict) -> str:
    """Texto factual para orientar uma prévia ilustrativa. Não inventa números."""
    parts = [f"Size {size_label}. Garment measurements (flat, cm): " + ", ".join(f"{k.replace('_cm', '')} {v:g}" for k, v in garment.items())]
    notes = compare_size(category, garment, body)
    translate = {"menor que o corpo (tende a apertar)": "smaller than the body, tight", "justa": "close fitting",
                 "regular": "regular fit", "folgada": "loose", "bem ampla": "very loose, oversized",
                 "ombro mais estreito que o corpo": "shoulder seam inside the shoulder",
                 "costura na linha do ombro": "shoulder seam on the shoulder", "ombro levemente caído": "slightly dropped shoulder",
                 "ombro caído (modelagem ampla)": "clearly dropped shoulder", "mais curta que a perna": "shorter than the leg",
                 "na medida da perna": "ends at the ankle", "mais longa (pode sobrar na barra)": "longer than the leg, stacking at the hem"}
    if notes:
        parts.append("Expected fit from measurements: " + "; ".join(
            f"{n['dimensao']}: {translate.get(n['leitura'], n['leitura'])}" for n in notes))
    else:
        parts.append("Body measurements were not provided; scale the garment only relative to the other sizes.")
    return " ".join(parts)
