# -*- coding: utf-8 -*-

import json
import re
import threading
import unicodedata
import uuid
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


ALLOWED_LABELS = {
    "GAMER_CAVE": ("NOTICIA", "ANÁLISIS", "DEBATE", "HISTORIA", "EN VIVO", "COMUNIDAD"),
    "DAVIET_GAMING": ("OPINIÓN", "GAMEPLAY", "REVIEW", "NOTICIA", "EN VIVO"),
}

BRAND_HASHTAGS = {
    "GAMER_CAVE": "#elgamercave",
    "DAVIET_GAMING": "#DavietGaming",
}

_TRACKING_PARAMS = {"fbclid", "gclid", "ref", "source"}
_GENERIC_HASHTAGS = {"gaming", "videojuegos", "gamers", "geek", "geekculture"}
_STOPWORDS = {
    "about", "after", "against", "among", "before", "could", "from", "into", "more",
    "news", "official", "over", "that", "their", "this", "through", "update", "with",
    "como", "desde", "entre", "esta", "este", "estos", "para", "sobre", "tras", "nuevo",
    "nueva", "noticia", "juego", "juegos", "gaming", "gamer",
}
_HISTORY_LOCK = threading.Lock()


def normalize_brand(brand):
    value = re.sub(r"[^A-Z]", "_", str(brand or "").upper()).strip("_")
    return "DAVIET_GAMING" if value in {"DAVIET_GAMING", "DAVIETGAMING"} else "GAMER_CAVE"


def _plain(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", value).strip()


def _canonical_url(value):
    try:
        parts = urlsplit(str(value).strip())
    except ValueError:
        return ""
    if not parts.netloc:
        return ""
    query = [
        (key, val)
        for key, val in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in _TRACKING_PARAMS
    ]
    return urlunsplit((parts.scheme.lower() or "https", parts.netloc.lower(), parts.path.rstrip("/"), urlencode(query), ""))


def canonical_news_id(item):
    """Stable story ID: canonical URL first, then explicit ID/GUID, then source+title."""
    item = item if isinstance(item, dict) else {}
    for field in ("link", "url"):
        value = _canonical_url(item.get(field, ""))
        if value:
            return str(uuid.uuid5(uuid.NAMESPACE_URL, f"url:{value}"))
    for field in ("id", "guid"):
        value = str(item.get(field, "")).strip()
        if value:
            return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{field}:{value}"))
    fallback = _plain(f"{item.get('source', '')}|{item.get('title', '')}").lower()
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"fallback:{fallback}"))


def post_cache_key(item, brand):
    return f"{normalize_brand(brand)}:{canonical_news_id(item)}"


def normalize_label(label, brand):
    brand = normalize_brand(brand)
    allowed = ALLOWED_LABELS[brand]
    original = unicodedata.normalize("NFKC", str(label or "")).upper().strip()
    if original in allowed:
        return original, True
    raw = _plain(original).upper().strip()

    if brand == "GAMER_CAVE":
        mappings = {
            "NOSTALGIA": "HISTORIA", "RETRO": "HISTORIA", "HISTORY": "HISTORIA",
            "ANALISIS": "ANÁLISIS", "OPINION": "ANÁLISIS", "REVIEW": "ANÁLISIS",
            "EDITORIAL": "ANÁLISIS", "INDIE/EDITORIAL": "ANÁLISIS",
            "TECNOLOGIA": "NOTICIA", "INDIE": "NOTICIA", "ANIME": "NOTICIA",
            "GAMING": "NOTICIA", "NEWS": "NOTICIA", "LIVE": "EN VIVO",
        }
    else:
        mappings = {
            "ANALISIS": "OPINIÓN", "DEBATE": "OPINIÓN", "HISTORIA": "OPINIÓN",
            "COMUNIDAD": "OPINIÓN", "NOSTALGIA": "OPINIÓN", "EDITORIAL": "OPINIÓN",
            "INDIE/EDITORIAL": "OPINIÓN", "TECNOLOGIA": "NOTICIA", "INDIE": "NOTICIA",
            "ANIME": "NOTICIA", "GAMING": "NOTICIA", "NEWS": "NOTICIA", "LIVE": "EN VIVO",
        }
    return mappings.get(raw, "NOTICIA" if "NOTICIA" in allowed else allowed[0]), False


def appears_english(value):
    words = set(re.findall(r"[a-z]+", _plain(value).lower()))
    english = words & {
        "after", "before", "could", "first", "from", "gets", "into", "more",
        "new", "news", "reveals", "the", "this", "update", "will", "with",
    }
    spanish = words & {
        "actualizacion", "anuncia", "con", "de", "del", "el", "en", "llega",
        "nuevo", "nueva", "para", "presenta", "recibe", "sobre", "una",
    }
    return len(english) >= 2 and len(english) > len(spanish)


def translated_title_is_valid(original, translated):
    translated = str(translated or "").strip()
    if not translated:
        return False
    if appears_english(translated):
        return False
    if appears_english(original) and _plain(original).lower() == _plain(translated).lower():
        return False
    return True


def _hashtag_slug(value):
    clean = re.sub(r"[^A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ]", "", str(value or ""))
    return clean[:32]


def _topic_hashtag_candidates(item):
    text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}"
    known = [
        (r"\bdiablo\s*4\b", "Diablo4"), (r"\bzelda\b", "Zelda"),
        (r"\bmario\b", "SuperMario"), (r"\bpok[eé]mon\b", "Pokemon"),
        (r"\bnintendo\b", "Nintendo"), (r"\bplaystation\b|\bps5\b", "PlayStation"),
        (r"\bxbox\b", "Xbox"), (r"\bsteam\b", "Steam"),
        (r"\bfinal fantasy\b", "FinalFantasy"), (r"\bkingdom hearts\b", "KingdomHearts"),
        (r"\bcall of duty\b", "CallOfDuty"), (r"\bcastlevania\b", "Castlevania"),
        (r"\bthief\b", "Thief"), (r"\bpalworld\b", "Palworld"),
        (r"\banime\b", "Anime"), (r"\bmanga\b", "Manga"),
        (r"\bindie\b", "IndieGames"), (r"\bpc\b|\bpc gaming\b", "PCGaming"),
    ]
    result = [tag for pattern, tag in known if re.search(pattern, text, flags=re.IGNORECASE)]
    words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]{4,}", str(item.get("title", "")))
    for word in words:
        if _plain(word).lower() not in _STOPWORDS:
            result.append(_hashtag_slug(word))
    return result


def ensure_specific_hashtags(post, item, brand, proposed=None, count=5):
    """Return caption with exactly five hashtags, led by the active brand."""
    brand = normalize_brand(brand)
    body = re.sub(r"(?<!\w)#[\wÁÉÍÓÚÜÑáéíóúüñ]+", "", str(post or ""), flags=re.UNICODE)
    body = re.sub(r"[ \t]+\n", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    candidates = []
    if isinstance(proposed, str):
        candidates.extend(re.findall(r"#?([\wÁÉÍÓÚÜÑáéíóúüñ]+)", proposed))
    elif isinstance(proposed, (list, tuple)):
        candidates.extend(str(value).lstrip("#") for value in proposed)
    candidates.extend(_topic_hashtag_candidates(item))

    chosen = [BRAND_HASHTAGS[brand]]
    seen = {chosen[0].lower()}
    specific = []
    generic = []
    for candidate in candidates:
        slug = _hashtag_slug(candidate)
        if not slug:
            continue
        target = f"#{slug}"
        if target.lower() in seen:
            continue
        if _plain(slug).lower() in _GENERIC_HASHTAGS:
            generic.append(target)
        else:
            specific.append(target)
        seen.add(target.lower())

    fallback = ["#NoticiasGaming", "#CulturaGamer", "#GamingLatam", "#ComunidadGamer"]
    for tag in specific + generic + fallback:
        if len(chosen) >= count:
            break
        if tag.lower() not in {value.lower() for value in chosen}:
            chosen.append(tag)
    return f"{body}\n\n{' '.join(chosen[:count])}".strip(), chosen[:count]


def _topic_tokens(value):
    words = re.findall(r"[a-z0-9]{3,}", _plain(value).lower())
    return {word for word in words if word not in _STOPWORDS}


def topic_similarity(left, right):
    left_plain = _plain(left).lower()
    right_plain = _plain(right).lower()
    if not left_plain or not right_plain:
        return 0.0
    left_tokens = _topic_tokens(left_plain)
    right_tokens = _topic_tokens(right_plain)
    union = left_tokens | right_tokens
    jaccard = len(left_tokens & right_tokens) / len(union) if union else 0.0
    sequence = SequenceMatcher(None, left_plain, right_plain).ratio()
    return max(jaccard, sequence)


def load_recent_topics(path):
    path = Path(path)
    empty = {"GAMER_CAVE": [], "DAVIET_GAMING": []}
    if not path.exists():
        return empty
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return empty
    for brand in empty:
        if not isinstance(data.get(brand), list):
            data[brand] = []
    return data


def find_recent_duplicate(path, item, brand, today=None, threshold=0.72):
    brand = normalize_brand(brand)
    today = str(today or date.today())
    news_id = canonical_news_id(item)
    title = str(item.get("title", ""))
    history = load_recent_topics(path)
    for stored_brand, entries in history.items():
        for entry in entries:
            same_brand = stored_brand == brand
            same_day = str(entry.get("date", "")) == today
            if entry.get("news_id") == news_id and (same_brand or same_day):
                return entry
            if not same_brand and not same_day:
                continue
            if same_brand or same_day:
                if topic_similarity(title, entry.get("title", "")) >= threshold:
                    return entry
    return None


def remember_topic(path, item, brand, label, today=None, limit=20):
    path = Path(path)
    brand = normalize_brand(brand)
    entry = {
        "news_id": canonical_news_id(item),
        "title": str(item.get("title", "")).strip(),
        "angle": normalize_label(label, brand)[0],
        "date": str(today or date.today()),
    }
    with _HISTORY_LOCK:
        history = load_recent_topics(path)
        entries = [old for old in history[brand] if old.get("news_id") != entry["news_id"]]
        history[brand] = ([entry] + entries)[:limit]
        path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return entry
