import sys
import tempfile
import types
from pathlib import Path


class FakeGoogleTranslator:
    def __init__(self, source, target):
        assert source == "auto"
        assert target == "es"

    def translate(self, text):
        replacements = {
            "Nintendo reveals a new Zelda update": "Nintendo revela una nueva actualización de Zelda",
            "The update adds a new challenge for Nintendo Switch players.": (
                "La actualización añade un nuevo desafío para jugadores de Nintendo Switch."
            ),
        }
        return replacements.get(text, f"Traducción: {text}")


fake_deep_translator = types.ModuleType("deep_translator")
fake_deep_translator.GoogleTranslator = FakeGoogleTranslator
sys.modules.setdefault("deep_translator", fake_deep_translator)

from feedback_learning import count_examples, recent_examples, save_example
from translation_layer import traducir_noticia, traducir_texto_al_espanol


traducir_texto_al_espanol.cache_clear()
english_news = {
    "title": "Nintendo reveals a new Zelda update",
    "summary": "The update adds a new challenge for Nintendo Switch players.",
    "body": "The update adds a new challenge for Nintendo Switch players.",
    "link": "https://example.com/zelda",
}
translated = traducir_noticia(english_news)
assert translated["title"] == "Nintendo revela una nueva actualización de Zelda"
assert translated["summary"].startswith("La actualización")
assert translated["body"].startswith("La actualización")
assert translated["original_title"] == english_news["title"]
assert translated["original_body"] == english_news["body"]
assert translated["link"] == english_news["link"]

with tempfile.TemporaryDirectory() as directory:
    good_path = Path(directory) / "ejemplos_buenos.json"
    for index in range(4):
        save_example(
            good_path,
            "GAMER_CAVE",
            {
                "marca": "GAMER_CAVE",
                "etiqueta": "NOTICIA",
                "noticia_original": f"Noticia {index}",
                "post": f"Post aprobado {index}",
                "fecha": f"2026-08-0{index + 1}",
            },
        )
    save_example(
        good_path,
        "DAVIET_GAMING",
        {
            "marca": "DAVIET_GAMING",
            "etiqueta": "OPINIÓN",
            "noticia_original": "Otra noticia",
            "post": "Ejemplo personal de Daviet",
            "fecha": "2026-08-03",
        },
    )
    save_example(good_path, "GAMER_CAVE", recent_examples(good_path, "GAMER_CAVE")[-1])
    assert count_examples(good_path) == {"GAMER_CAVE": 4, "DAVIET_GAMING": 1}
    assert [item["post"] for item in recent_examples(good_path, "GAMER_CAVE", 3)] == [
        "Post aprobado 1", "Post aprobado 2", "Post aprobado 3"
    ]

app_source = Path("app.py").read_text(encoding="utf-8")
assert 'st.button("👍"' in app_source
assert 'st.button("👎"' in app_source
assert 'ejemplos = cargar_ejemplos_buenos(marca_clave)' in app_source
assert 'return ejemplos[-3:]' in app_source

print("translation and feedback checks ok")
