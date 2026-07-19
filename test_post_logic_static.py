import ast
from pathlib import Path


APP = Path(__file__).with_name("app.py")
SOURCE = APP.read_text(encoding="utf-8-sig")
TREE = ast.parse(SOURCE)
ENGINE = Path(__file__).with_name("editorial_engine_final.py")
ENGINE_SOURCE = ENGINE.read_text(encoding="utf-8-sig")
ENGINE_TREE = ast.parse(ENGINE_SOURCE)


def function_source(name):
    matches = [
        node for node in TREE.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if not matches:
        raise AssertionError(f"No encontre la funcion {name}")
    return ast.get_source_segment(SOURCE, matches[-1]) or ""


def engine_source_contains(name):
    return f"def {name}" in ENGINE_SOURCE


def test_parallel_feeds_exist():
    assert "ThreadPoolExecutor" in SOURCE
    assert "def leer_feeds_en_paralelo" in SOURCE
    assert "for fuente, entradas in leer_feeds_en_paralelo(FUENTES)" in SOURCE


def test_final_editorial_engine_is_last_layer():
    assert 'APP_VERSION = "2026.07.19-2"' in SOURCE
    assert "from editorial_engine_final import install_editorial_engine" in SOURCE
    assert "install_editorial_engine(globals())" in SOURCE
    assert "Motor editorial final" in ENGINE_SOURCE
    assert engine_source_contains("generate_social_post")
    assert "crear_post_limpio" in ENGINE_SOURCE
    assert "aplicar_reglas_editoriales_fuertes" in ENGINE_SOURCE
    assert "st.session_state.last_post_text = post" in ENGINE_SOURCE


def test_no_dangerous_question_replacement_in_final_cleaner():
    src = function_source("limpiar_pedido_post")
    assert '("?", "a")' not in src
    assert '("?", "e")' not in src
    assert "quitar_marca_de_texto" in src


def test_multi_post_uses_variety_and_real_category():
    src = ENGINE_SOURCE
    assert "_categoria_final_item" in src
    assert "seleccionar_noticias_variadas" in src
    assert "PUBLICACIÓN" in src
    assert "categoria_de_publicacion" in src


def test_final_editorial_customs_exists():
    assert "Aduana editorial final" in ENGINE_SOURCE
    assert "ENGLISH_BLOCKERS_FINAL" in ENGINE_SOURCE
    assert "ACTION_PATTERNS_FINAL" in ENGINE_SOURCE
    assert "creatividad_ia" in ENGINE_SOURCE
    assert "enjoy our weekend guide" in ENGINE_SOURCE


def test_final_caption_blocks_old_filler_phrases():
    src = ENGINE_SOURCE
    final_src = ENGINE_SOURCE
    banned = [
        "lo importante es explicar",
        "lo interesante es mirar",
        "puede servir para descubrir algo fuera",
        "el feed no trae suficiente detalle",
        "tema reciente dentro del mundo gamer",
    ]
    assert "FILLER_PHRASES" in src
    for phrase in banned:
        assert phrase in final_src


def test_final_layer_does_not_depend_on_specific_titles():
    final_src = ENGINE_SOURCE
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
    test_final_editorial_customs_exists()
    test_final_caption_blocks_old_filler_phrases()
    test_final_layer_does_not_depend_on_specific_titles()
    print("static checks ok")
