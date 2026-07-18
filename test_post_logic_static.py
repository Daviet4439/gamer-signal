import ast
from pathlib import Path


APP = Path(__file__).with_name("app.py")
SOURCE = APP.read_text(encoding="utf-8-sig")
TREE = ast.parse(SOURCE)


def function_source(name):
    matches = [
        node for node in TREE.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if not matches:
        raise AssertionError(f"No encontre la funcion {name}")
    return ast.get_source_segment(SOURCE, matches[-1]) or ""


def test_parallel_feeds_exist():
    assert "ThreadPoolExecutor" in SOURCE
    assert "def leer_feeds_en_paralelo" in SOURCE
    assert "for fuente, entradas in leer_feeds_en_paralelo(FUENTES)" in SOURCE


def test_final_editorial_engine_is_last_layer():
    assert "Motor editorial final" in SOURCE
    assert 'APP_VERSION = "2026.07.18-9"' in SOURCE
    src = function_source("generate_social_post")
    assert "crear_post_limpio" in src
    assert "aplicar_reglas_editoriales_fuertes" in src
    assert "st.session_state.last_post_text = post" in src


def test_no_dangerous_question_replacement_in_final_cleaner():
    src = function_source("limpiar_pedido_post")
    assert '("?", "a")' not in src
    assert '("?", "e")' not in src
    assert "quitar_marca_de_texto" in src


def test_multi_post_uses_variety_and_real_category():
    src = function_source("crear_varios_posts")
    assert "_categoria_final_item" in src
    assert "seleccionar_noticias_variadas" in src
    assert "PUBLICACI\\u00d3N" in src


def test_final_caption_blocks_old_filler_phrases():
    src = function_source("caption_necesita_regenerarse")
    final_src = SOURCE.split("# Motor editorial saneado", 1)[-1]
    banned = [
        "lo importante es explicar",
        "lo interesante es mirar",
        "puede servir para descubrir algo fuera",
        "el feed no trae suficiente detalle",
        "tema reciente dentro del mundo gamer",
    ]
    assert "FRASES_PLANTILLA_BLOQUEADAS" in src
    for phrase in banned:
        assert phrase in final_src


def test_final_layer_does_not_depend_on_specific_titles():
    final_src = SOURCE.split("# Motor editorial saneado", 1)[-1]
    forbidden = [
        "diablo 4 recibe",
        "kingdom hearts 4 podr",
        "castlevania convierte",
        "blue box termina",
        "thief: gold entra",
    ]
    for phrase in forbidden:
        assert phrase not in final_src.lower()


if __name__ == "__main__":
    test_parallel_feeds_exist()
    test_final_editorial_engine_is_last_layer()
    test_no_dangerous_question_replacement_in_final_cleaner()
    test_multi_post_uses_variety_and_real_category()
    test_final_caption_blocks_old_filler_phrases()
    test_final_layer_does_not_depend_on_specific_titles()
    print("static checks ok")
