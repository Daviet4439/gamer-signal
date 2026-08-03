# -*- coding: utf-8 -*-

import re
import unicodedata
from functools import lru_cache

from deep_translator import GoogleTranslator


_SPANISH_WORDS = {
    "actualizacion", "anuncio", "con", "cuando", "de", "del", "el", "en",
    "esta", "fue", "la", "las", "lo", "los", "para", "por", "presento",
    "que", "se", "su", "una", "y",
}
_ENGLISH_WORDS = {
    "after", "announced", "before", "coming", "first", "following", "from",
    "gets", "into", "launches", "more", "new", "reveals", "the", "this",
    "update", "with", "will",
}


def _plain(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(char for char in value if not unicodedata.combining(char)).lower()


def parece_espanol(texto):
    palabras = re.findall(r"[a-z]+", _plain(texto))
    if not palabras:
        return True
    espanol = sum(palabra in _SPANISH_WORDS for palabra in palabras)
    ingles = sum(palabra in _ENGLISH_WORDS for palabra in palabras)
    if any(char in str(texto or "").lower() for char in "áéíóúñ¿¡") and espanol:
        return True
    return espanol >= 2 and espanol > ingles


def _dividir_texto(texto, limite=4000):
    texto = str(texto or "").strip()
    if len(texto) <= limite:
        return [texto] if texto else []
    partes = []
    restante = texto
    while restante:
        corte = min(limite, len(restante))
        if corte < len(restante):
            separador = max(restante.rfind("\n", 0, corte), restante.rfind(". ", 0, corte))
            if separador > limite // 2:
                corte = separador + 1
        partes.append(restante[:corte].strip())
        restante = restante[corte:].strip()
    return [parte for parte in partes if parte]


@lru_cache(maxsize=1024)
def traducir_texto_al_espanol(texto):
    texto = str(texto or "").strip()
    if not texto or parece_espanol(texto):
        return texto
    traductor = GoogleTranslator(source="auto", target="es")
    traducido = " ".join(traductor.translate(parte) for parte in _dividir_texto(texto))
    return traducido.strip() or texto


def traducir_noticia(item):
    """Translate a news item while preserving the source text for reference."""
    item = dict(item or {})
    titulo_original = str(item.get("original_title") or item.get("title") or "").strip()
    resumen_original = str(item.get("original_summary") or item.get("summary") or "").strip()
    cuerpo_original = str(
        item.get("original_body") or item.get("body") or item.get("content") or resumen_original
    ).strip()

    item["original_title"] = titulo_original
    item["original_summary"] = resumen_original
    item["original_body"] = cuerpo_original
    try:
        item["title"] = traducir_texto_al_espanol(titulo_original)
        item["summary"] = traducir_texto_al_espanol(resumen_original)
        item["body"] = traducir_texto_al_espanol(cuerpo_original)
        item["translation_status"] = "es"
    except Exception:
        item["title"] = titulo_original
        item["summary"] = resumen_original
        item["body"] = cuerpo_original
        item["translation_status"] = "fallback_original"
    return item
