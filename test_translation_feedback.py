import sys
import types
from pathlib import Path


class FakeGoogleTranslator:
    def __init__(self, source, target):
        assert source == "auto"
        assert target == "es"

    def translate(self, text):
        replacements = {
            "Nintendo reveals a new Zelda update": "Nintendo revela una nueva actualizacion de Zelda",
            "The update adds a new challenge for Nintendo Switch players.": (
                "La actualizacion anade un nuevo desafio para jugadores de Nintendo Switch."
            ),
        }
        return replacements.get(text, f"Traduccion: {text}")


fake_deep_translator = types.ModuleType("deep_translator")
fake_deep_translator.GoogleTranslator = FakeGoogleTranslator
sys.modules.setdefault("deep_translator", fake_deep_translator)

from supabase_feedback import count_good_examples, recent_good_examples, save_feedback
from translation_layer import traducir_noticia, traducir_texto_al_espanol


class FakeResponse:
    def __init__(self, data=None, count=None):
        self.data = data or []
        self.count = count


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows
        self.operation = "select"
        self.payload = None
        self.filters = []
        self.sort_field = None
        self.sort_desc = False
        self.max_rows = None
        self.exact_count = False

    def insert(self, payload):
        self.operation = "insert"
        self.payload = dict(payload)
        return self

    def select(self, _columns, count=None):
        self.operation = "select"
        self.exact_count = count == "exact"
        return self

    def eq(self, field, value):
        self.filters.append((field, value))
        return self

    def order(self, field, desc=False):
        self.sort_field = field
        self.sort_desc = desc
        return self

    def limit(self, amount):
        self.max_rows = amount
        return self

    def execute(self):
        if self.operation == "insert":
            row = {"id": len(self.rows) + 1, **self.payload}
            self.rows.append(row)
            return FakeResponse([row])

        result = list(self.rows)
        for field, value in self.filters:
            result = [row for row in result if row.get(field) == value]
        total = len(result)
        if self.sort_field:
            result.sort(key=lambda row: row.get(self.sort_field, ""), reverse=self.sort_desc)
        if self.max_rows is not None:
            result = result[: self.max_rows]
        return FakeResponse(result, total if self.exact_count else None)


class FakeSupabaseClient:
    def __init__(self):
        self.rows = []

    def table(self, name):
        assert name == "ejemplos_posts"
        return FakeQuery(self.rows)


traducir_texto_al_espanol.cache_clear()
english_news = {
    "title": "Nintendo reveals a new Zelda update",
    "summary": "The update adds a new challenge for Nintendo Switch players.",
    "body": "The update adds a new challenge for Nintendo Switch players.",
    "link": "https://example.com/zelda",
}
translated = traducir_noticia(english_news)
assert translated["title"] == "Nintendo revela una nueva actualizacion de Zelda"
assert translated["summary"].startswith("La actualizacion")
assert translated["body"].startswith("La actualizacion")
assert translated["original_title"] == english_news["title"]
assert translated["original_body"] == english_news["body"]
assert translated["link"] == english_news["link"]

client = FakeSupabaseClient()
for index in range(4):
    save_feedback(
        client,
        {
            "marca": "GAMER_CAVE",
            "etiqueta": "NOTICIA",
            "noticia_original": f"Noticia {index}",
            "post": f"Post aprobado {index}",
            "feedback": "bueno",
            "fecha_creado": f"2026-08-0{index + 1}T12:00:00+00:00",
        },
    )
save_feedback(
    client,
    {
        "marca": "DAVIET_GAMING",
        "etiqueta": "OPINION",
        "noticia_original": "Otra noticia",
        "post": "Ejemplo personal de Daviet",
        "feedback": "bueno",
        "fecha_creado": "2026-08-03T12:00:00+00:00",
    },
)
save_feedback(
    client,
    {
        "marca": "GAMER_CAVE",
        "etiqueta": "DEBATE",
        "noticia_original": "Tema descartado",
        "post": "Este ejemplo no debe entrar al prompt",
        "feedback": "malo",
        "fecha_creado": "2026-08-05T12:00:00+00:00",
    },
)

assert count_good_examples(client) == {"GAMER_CAVE": 4, "DAVIET_GAMING": 1}
assert [item["post"] for item in recent_good_examples(client, "GAMER_CAVE", 3)] == [
    "Post aprobado 3",
    "Post aprobado 2",
    "Post aprobado 1",
]

app_source = Path("app.py").read_text(encoding="utf-8")
assert 'st.button("👍"' in app_source
assert 'st.button("👎"' in app_source
assert 'ejemplos = cargar_ejemplos_buenos(marca_clave)' in app_source
assert 'st.secrets.get("SUPABASE_URL"' in app_source
assert 'st.secrets.get("SUPABASE_KEY"' in app_source
assert "GOOD_EXAMPLES_FILE" not in app_source
assert "BAD_EXAMPLES_FILE" not in app_source

print("translation and Supabase feedback checks ok")
