# -*- coding: utf-8 -*-

"""Persistent feedback storage for Gamer Signal."""

BRANDS = ("GAMER_CAVE", "DAVIET_GAMING")
FEEDBACK_VALUES = ("bueno", "malo")
TABLE_NAME = "ejemplos_posts"


def create_feedback_client(url, key):
    url = str(url or "").strip()
    key = str(key or "").strip()
    if not url or not key:
        raise RuntimeError("Faltan SUPABASE_URL o SUPABASE_KEY en los Secrets de Streamlit.")

    try:
        from supabase import create_client
    except ImportError as error:
        raise RuntimeError("Falta instalar la dependencia supabase==2.31.0.") from error
    return create_client(url, key)


def _validate_brand(brand):
    if brand not in BRANDS:
        raise ValueError(f"Marca no permitida: {brand}")


def save_feedback(client, record):
    brand = str(record.get("marca", "")).strip()
    feedback = str(record.get("feedback", "")).strip().lower()
    _validate_brand(brand)
    if feedback not in FEEDBACK_VALUES:
        raise ValueError(f"Feedback no permitido: {feedback}")

    payload = {
        "marca": brand,
        "etiqueta": str(record.get("etiqueta", "")).strip(),
        "noticia_original": str(record.get("noticia_original", "")).strip(),
        "post": str(record.get("post", "")).strip(),
        "feedback": feedback,
        "fecha_creado": str(record.get("fecha_creado", "")).strip() or None,
    }
    if not payload["post"] or not payload["noticia_original"]:
        raise ValueError("El post y la noticia original son obligatorios.")
    if payload["fecha_creado"] is None:
        payload.pop("fecha_creado")

    response = client.table(TABLE_NAME).insert(payload).execute()
    rows = getattr(response, "data", None) or []
    return rows[0] if rows else payload


def recent_good_examples(client, brand, limit=3):
    _validate_brand(brand)
    response = (
        client.table(TABLE_NAME)
        .select("marca,etiqueta,noticia_original,post,fecha_creado")
        .eq("marca", brand)
        .eq("feedback", "bueno")
        .order("fecha_creado", desc=True)
        .limit(max(1, min(int(limit), 3)))
        .execute()
    )
    return list(getattr(response, "data", None) or [])


def count_good_examples(client):
    counts = {}
    for brand in BRANDS:
        response = (
            client.table(TABLE_NAME)
            .select("id", count="exact")
            .eq("marca", brand)
            .eq("feedback", "bueno")
            .execute()
        )
        exact_count = getattr(response, "count", None)
        if exact_count is None:
            exact_count = len(getattr(response, "data", None) or [])
        counts[brand] = int(exact_count)
    return counts
