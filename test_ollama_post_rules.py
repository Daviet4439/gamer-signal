import json
import tempfile
from pathlib import Path

from ollama_post_rules import (
    ALLOWED_LABELS,
    canonical_news_id,
    ensure_specific_hashtags,
    find_recent_duplicate,
    news_context,
    normalize_label,
    post_quality_issues,
    post_cache_key,
    remember_topic,
    spanish_post_is_valid,
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
assert not translated_title_is_valid("Diablo 4 Update", "Diablo 4 Update")
assert translated_title_is_valid(
    "The Legend of Zelda update",
    "The Legend of Zelda recibe una actualización",
)

zelda_a["body"] = (
    "Nintendo confirmó el 3 de agosto de 2026 que la actualización de Zelda "
    "añadirá un nuevo desafío gratuito en Nintendo Switch."
)
zelda_a["verification_level"] = "fuente oficial"
zelda_a["content_angle"] = "gaming"
contexto = news_context(zelda_a, ["Nintendo oficial", "Nintendo Life"])
assert contexto["resumen_o_cuerpo"] == zelda_a["body"]
assert contexto["fecha"] == "2026-08-03"
assert contexto["fuente_principal"] == "Nintendo oficial"
assert contexto["nivel_verificacion"] == "fuente oficial"
assert contexto["categoria_o_angulo"] == "gaming"

posts_publicables = [
    (
        zelda_a,
        "Nintendo confirmó el 3 de agosto de 2026 una actualización gratuita de Zelda para Nintendo Switch. "
        "El contenido añadirá un desafío nuevo para quienes ya terminaron la aventura principal. "
        "¿Qué tipo de reto te gustaría encontrar en esta actualización?",
    ),
    (
        diablo,
        "Blizzard presentó una nueva temporada de Diablo 4 con cambios para sus jugadores. "
        "La actualización modifica la progresión y suma actividades que renuevan el recorrido. "
        "¿Cuál de estos cambios te animaría a regresar a Santuario?",
    ),
    (
        anime,
        "El nuevo avance de Frieren mostró escenas inéditas y confirmó novedades para la serie. "
        "La producción vuelve a reunir a los personajes que acompañan el viaje de la protagonista. "
        "¿Qué momento esperas ver desarrollado en esta nueva etapa?",
    ),
]
for item, post in posts_publicables:
    assert spanish_post_is_valid(post)
    assert post_quality_issues(post, item) == []

assert not spanish_post_is_valid(
    "The new update will bring more challenges and this reveal gets fans ready for launch."
)
assert post_quality_issues(
    "Es un tema reciente. Lo importante es explicar qué pasó. Esto abre conversación.",
    zelda_a,
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
