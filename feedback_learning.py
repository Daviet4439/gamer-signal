# -*- coding: utf-8 -*-

import json
from pathlib import Path


BRANDS = ("GAMER_CAVE", "DAVIET_GAMING")


def load_examples(path):
    path = Path(path)
    empty = {brand: [] for brand in BRANDS}
    if not path.exists():
        return empty
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return empty
    if not isinstance(data, dict):
        return empty
    for brand in BRANDS:
        if not isinstance(data.get(brand), list):
            data[brand] = []
    return data


def count_examples(path):
    data = load_examples(path)
    return {brand: len(data[brand]) for brand in BRANDS}


def recent_examples(path, brand, limit=3):
    data = load_examples(path)
    return data.get(brand, [])[-max(1, int(limit)):]


def save_example(path, brand, record):
    if brand not in BRANDS:
        raise ValueError(f"Marca no permitida: {brand}")
    path = Path(path)
    data = load_examples(path)
    post = str(record.get("post", "")).strip()
    if post and not any(
        isinstance(example, dict) and str(example.get("post", "")).strip() == post
        for example in data[brand]
    ):
        data[brand].append(dict(record))
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dict(record)
