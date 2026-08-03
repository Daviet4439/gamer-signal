import json
import tempfile
from pathlib import Path

from ollama_post_rules import (
    ALLOWED_LABELS,
    canonical_news_id,
    ensure_specific_hashtags,
    find_recent_duplicate,
    normalize_label,
    post_cache_key,
    remember_topic,
    translated_title_is_valid,
)


zelda_a = {
    "title": "Nintendo reveals a new Zelda update",
    "summary": "The update adds a new challenge to Zelda on Nintendo Switch.",
    "source": "Nintendo oficial",
    "link": "https://example.com/zelda-update?utm_source=rss",
    "date": "2026-08-03",
}
zelda_b = {
    **zelda_a,
    "id": "otro-id-del-mismo-feed",
    "summary": "Un resumen diferente del mismo artículo.",
    "date": "2026-08-04",
    "link": "https://example.com/zelda-update?utm_medium=feed",
}
diablo = {
    "title": "Diablo 4 recibe una nueva temporada",
    "summary": "Blizzard detalló los cambios de la temporada.",
    "source": "Blizzard oficial",
    "link": "https://example.com/diablo-4-season",
}
anime = {
    "title": "Nuevo avance del anime de Frieren",
    "summary": "El tráiler confirma novedades para la serie.",
    "source": "Anime News Network",
    "link": "https://example.com/frieren-trailer",
}


assert canonical_news_id(zelda_a) == canonical_news_id(zelda_b)
assert post_cache_key(zelda_a, "Gamer Cave") == post_cache_key(zelda_b, "Gamer Cave")
assert post_cache_key(zelda_a, "Gamer Cave") != post_cache_key(zelda_a, "Daviet Gaming")

for brand, invalid_values in {
    "GAMER_CAVE": ["Nostalgia", "Tecnología", "Indie/Editorial"],
    "DAVIET_GAMING": ["Nostalgia", "Tecnología", "Debate"],
}.items():
    for value in invalid_values:
        normalized, valid = normalize_label(value, brand)
        assert not valid
        assert normalized in ALLOWED_LABELS[brand]

assert normalize_label("ANÁLISIS", "GAMER_CAVE") == ("ANÁLISIS", True)
assert normalize_label("OPINIÓN", "DAVIET_GAMING") == ("OPINIÓN", True)
assert not translated_title_is_valid(
    "Nintendo reveals a new Zelda update",
    "Nintendo reveals a new Zelda update",
)
assert translated_title_is_valid(
    "Nintendo reveals a new Zelda update",
    "Nintendo revela una nueva actualización de Zelda",
)

zelda_post, zelda_tags = ensure_specific_hashtags(
    "Una novedad de Zelda que cambia el reto.\n\n#gaming #videojuegos",
    zelda_a,
    "GAMER_CAVE",
    ["#Zelda", "#NintendoSwitch", "#gaming"],
)
diablo_post, diablo_tags = ensure_specific_hashtags(
    "La nueva temporada cambia Diablo 4.",
    diablo,
    "DAVIET_GAMING",
    ["#Diablo4", "#Blizzard", "#gaming"],
)
anime_post, anime_tags = ensure_specific_hashtags(
    "Frieren regresa con un nuevo avance.",
    anime,
    "GAMER_CAVE",
    ["#Frieren", "#Anime", "#Manga"],
)
for post, tags in [(zelda_post, zelda_tags), (diablo_post, diablo_tags), (anime_post, anime_tags)]:
    assert len(tags) == 5
    assert post.count("#") == 5
assert zelda_tags[0] == "#elgamercave"
assert diablo_tags[0] == "#DavietGaming"
assert "#Zelda" in zelda_tags and "#Diablo4" in diablo_tags and "#Frieren" in anime_tags
assert set(zelda_tags) != set(diablo_tags) != set(anime_tags)

with tempfile.TemporaryDirectory() as directory:
    history_path = Path(directory) / "temas_recientes.json"
    history_path.write_text(json.dumps({"GAMER_CAVE": [], "DAVIET_GAMING": []}), encoding="utf-8")
    remember_topic(history_path, zelda_a, "GAMER_CAVE", "NOTICIA", today="2026-08-03")
    assert find_recent_duplicate(history_path, zelda_b, "GAMER_CAVE", today="2026-08-04")
    assert find_recent_duplicate(history_path, zelda_b, "DAVIET_GAMING", today="2026-08-03")
    assert not find_recent_duplicate(history_path, zelda_b, "DAVIET_GAMING", today="2026-08-04")
    assert not find_recent_duplicate(history_path, diablo, "GAMER_CAVE", today="2026-08-03")

print("ollama post rules checks ok")
