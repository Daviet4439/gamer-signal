import ast
from pathlib import Path


APP = Path(__file__).with_name("app.py")
SOURCE = APP.read_text(encoding="utf-8-sig")
TREE = ast.parse(SOURCE)
ENGINE = Path(__file__).with_name("editorial_engine_final.py")
ENGINE_SOURCE = ENGINE.read_text(encoding="utf-8-sig")
ENGINE_TREE = ast.parse(ENGINE_SOURCE)

EDITORIAL_FUNCTIONS_THAT_MUST_STAY_OUT_OF_APP = {
    "_categoria_final_item",
    "_limpiar_tema_titulo",
    "_resumen_fuente_util",
    "aplicar_reglas_editoriales_fuertes",
    "asegurar_hashtags_editoriales",
    "asegurar_pregunta_final",
    "caption_necesita_regenerarse",
    "categoria_de_item",
    "categorias_para_posts",
    "crear_hashtags",
    "crear_item_editorial_categoria",
    "crear_opciones_post_recientes",
    "crear_post_limpio",
    "crear_varios_posts",
    "detalle_contextual_para_post",
    "detectar_accion_titulo",
    "detectar_content_angle",
    "entrada_usada_aplica_a_marca",
    "estado_verificacion_item",
    "etiqueta_publicacion_limpia",
    "extraer_tema_para_titulo",
    "formatear_noticias",
    "generate_social_post",
    "item_es_contexto_editorial",
    "limpiar_gramatica_post_final",
    "limpiar_lineas_para_caption",
    "limpiar_pedido_post",
    "limpiar_texto_publicable_final",
    "linea_no_publicable",
    "parece_texto_ingles",
    "pregunta_engagement",
    "quitar_prefijos_editoriales",
    "reparar_texto_roto",
    "resumen_publico_en_espanol",
    "seleccionar_noticias_variadas",
    "tema_muy_similar",
    "tema_repetido",
    "titulo_publico_en_espanol",
    "titulo_visible_seguro",
}


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


def engine_function_source(name):
    matches = [
        node for node in ast.walk(ENGINE_TREE)
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if not matches:
        raise AssertionError(f"No encontre la funcion {name} en editorial_engine_final.py")
    return ast.get_source_segment(ENGINE_SOURCE, matches[-1]) or ""


def test_parallel_feeds_exist():
    assert "ThreadPoolExecutor" in SOURCE
    assert "def leer_feeds_en_paralelo" in SOURCE
    assert "for fuente, entradas in leer_feeds_en_paralelo(FUENTES)" in SOURCE


def test_final_editorial_engine_is_last_layer():
    assert 'APP_VERSION = "2026.07.20-2"' in SOURCE
    assert "from editorial_engine_final import install_editorial_engine" in SOURCE
    assert "install_editorial_engine(globals())" in SOURCE
    assert "Motor editorial final" in ENGINE_SOURCE
    assert engine_source_contains("generate_social_post")
    assert "crear_post_limpio" in ENGINE_SOURCE
    assert "aplicar_reglas_editoriales_fuertes" in ENGINE_SOURCE
    assert "st.session_state.last_post_text = post" in ENGINE_SOURCE


def test_no_dangerous_question_replacement_in_final_cleaner():
    src = engine_function_source("limpiar_pedido_post")
    assert '("?", "a")' not in src
    assert '("?", "e")' not in src
    assert "quitar_marca_de_texto" in src


def test_no_duplicate_editorial_functions_in_app():
    app_defs = {
        node.name
        for node in TREE.body
        if isinstance(node, ast.FunctionDef)
    }
    duplicated = sorted(app_defs & EDITORIAL_FUNCTIONS_THAT_MUST_STAY_OUT_OF_APP)
    assert duplicated == []


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


def test_radar_sources_and_fallbacks_are_present():
    assert "https://www.crunchyroll.com/news/rss" in SOURCE
    assert "https://www.animenewsnetwork.com/all/rss.xml?ann-edition=us" in SOURCE
    assert "Reddit FanTheories - teor" in SOURCE
    assert "Reddit GamingLeaksAndRumours - rumores comunidad" in SOURCE
    assert "Reddit VideojuegosMX - se" in SOURCE
    assert "AnimeStudios" in SOURCE
    assert "Toei Animation oficial" in SOURCE
    assert "MAPPA oficial" in SOURCE
    assert "RADAR_BUCKET_FALLBACKS" in SOURCE
    assert "crear_item_radar_editorial" in SOURCE
    assert "titulo_radar_seguro" in SOURCE
    assert "Buscando una oportunidad buena, no cualquier noticia." not in SOURCE


def test_extraer_numero_requires_explicit_news_reference():
    src = function_source("extraer_numero")
    assert "palabra.isdigit()" not in src
    assert "noticia|publicaci" in src
    assert "Diablo 4" not in src


if __name__ == "__main__":
    test_parallel_feeds_exist()
    test_final_editorial_engine_is_last_layer()
    test_no_dangerous_question_replacement_in_final_cleaner()
    test_no_duplicate_editorial_functions_in_app()
    test_multi_post_uses_variety_and_real_category()
    test_final_editorial_customs_exists()
    test_final_caption_blocks_old_filler_phrases()
    test_final_layer_does_not_depend_on_specific_titles()
    test_radar_sources_and_fallbacks_are_present()
    test_extraer_numero_requires_explicit_news_reference()
    print("static checks ok")
