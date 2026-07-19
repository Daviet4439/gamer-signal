from datetime import datetime
from editorial_engine_final import install_editorial_engine


class SessionState(dict):
    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, key, value):
        self[key] = value


class FakeStreamlit:
    def __init__(self):
        self.session_state = SessionState(
            active_brand="Gamer Cave",
            post_style="all",
            generated_items={},
            news_by_number={},
        )


st = FakeStreamlit()


SAMPLES = [
    {
        "id": "diablo",
        "title": "Diablo 4 Update Will Drown You In Mythics",
        "summary": "Blizzard shared details for a Diablo 4 update focused on Mythic items and progression changes.",
        "source": "Blizzard oficial",
        "date": "2026-07-18",
        "source_official": True,
        "source_trusted": True,
    },
    {
        "id": "kh4",
        "title": "Kingdom Hearts 4 News Could Come Sooner Than You Think",
        "summary": "Square Enix fans are watching for new information about Kingdom Hearts 4 after recent signals from official channels.",
        "source": "GameSpot confiable",
        "date": "2026-07-18",
        "source_trusted": True,
        "verification_count": 2,
    },
    {
        "id": "anime",
        "title": "Manga 'Ao no Hako' Concludes Serialization",
        "summary": "The manga Blue Box reached the end of its serialization, opening discussion among anime and manga fans.",
        "source": "MyAnimeList News confiable",
        "date": "2026-07-17",
        "source_trusted": True,
        "verification_count": 2,
    },
    {
        "id": "placeholder",
        "title": "Xbox: novedad para la comunidad gamer",
        "summary": "Generic placeholder.",
        "source": "Xbox Wire oficial",
        "date": "2026-07-17",
        "source_official": True,
    },
    {
        "id": "gog",
        "title": "Thief: Gold joins the GOG Preservation Program following the first-ever Patron Vote",
        "summary": "GOG added the classic stealth game to its Preservation Program after a community vote.",
        "source": "GOG News oficial",
        "date": "2026-07-17",
        "source_official": True,
    },
    {
        "id": "real_tama",
        "title": "Web Manga 'Real mo Tama ni wa Uso wo Tsuku' Gets TV Anime in 2027",
        "summary": "A new anime adaptation was announced with early production details.",
        "source": "Anime Corner confiable",
        "date": "2026-07-17",
        "source_trusted": True,
        "verification_count": 2,
    },
    {
        "id": "utopias",
        "title": "Utopias: indie games worth watching",
        "summary": "Enjoy our weekend guide to the best indie games worth checking out.",
        "source": "PC Gamer confiable",
        "date": "2026-07-17",
        "source_trusted": True,
        "verification_count": 2,
    },
    {
        "id": "ai_slop",
        "title": "In An Era Of AI Slop, Meccha Chameleon Embraces Human-Crafted Chaos",
        "summary": "The game highlights human-crafted creative work during a wider AI conversation.",
        "source": "GameSpot confiable",
        "date": "2026-07-17",
        "source_trusted": True,
        "verification_count": 2,
    },
    {
        "id": "zaum",
        "title": "ZA/UM are set for more layoffs only two months after launching Zero Parades: For Dead Spies",
        "summary": "Studio job cuts are being discussed after a recent project launch.",
        "source": "VGC confiable",
        "date": "2026-07-17",
        "source_trusted": True,
        "verification_count": 2,
    },
]


def normalizar_titulo(texto):
    return " ".join(palabra[:1].upper() + palabra[1:] for palabra in str(texto).split())


def plataforma_de_item(item):
    texto = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    if "xbox" in texto:
        return "xbox"
    if "playstation" in texto or "ps5" in texto:
        return "playstation"
    if "nintendo" in texto:
        return "nintendo"
    if "pc" in texto or "steam" in texto or "gog" in texto:
        return "pc"
    return "general"


def make_env():
    return {
        "st": st,
        "normalizar_titulo_gamer": normalizar_titulo,
        "recortar_texto": lambda texto, limite: str(texto)[:limite],
        "leer_json": lambda _path, default: [],
        "USED_FILE": "used.json",
        "ahora_en_puerto_rico": lambda: datetime(2026, 7, 19, 10, 0),
        "plataforma_de_item": plataforma_de_item,
        "estilo_seguro_para_item": lambda _item, estilo: estilo,
        "marca_permitida": lambda marca: marca or "Gamer Cave",
        "get_brand_voice": lambda: {"brand": st.session_state.active_brand},
        "detectar_angulo_nostalgia": lambda _item: "",
        "buscar_noticias": lambda: SAMPLES,
        "ANIO_NOTICIAS": 2026,
        "FECHA_INICIO": "2026-06-21",
        "FECHA_FINAL": "2026-07-19",
        "TEMAS_COMUNIDAD": ["juegos fisicos vs digitales"],
        "TEMAS_NOSTALGIA": ["GameCube y recuerdos de infancia"],
    }


def assert_clean_caption(texto):
    bajo = texto.lower()
    prohibidas = [
        "lo importante es explicar",
        "tema reciente dentro",
        "puede servir para descubrir algo fuera",
        "el feed no trae suficiente detalle",
        "xbox: novedad para la comunidad gamer",
        "enjoy our weekend guide",
        "worth checking out",
        "are set for more layoffs",
        "human-crafted chaos",
        "gets tv anime",
        "could come sooner than you think",
        "indie games worth watching",
        "in an era of ai slop",
    ]
    for frase in prohibidas:
        assert frase not in bajo, frase
    assert "http" not in bajo
    assert "Ã" not in texto
    assert "�" not in texto
    hashtags = [linea for linea in texto.splitlines() if linea.strip().startswith("#")]
    if hashtags:
        assert len(hashtags[-1].split()) == 5


def test_titles_are_spanish_and_contextual():
    env = make_env()
    install_editorial_engine(env)
    assert env["titulo_visible_seguro"](SAMPLES[0]).startswith("Diablo 4 recibe")
    assert "Kingdom Hearts 4: posible novedad" in env["titulo_visible_seguro"](SAMPLES[1])
    assert env["_categoria_final_item"](SAMPLES[2]) == "anime"
    assert env["titulo_generico_o_pobre"](SAMPLES[3]["title"])


def test_posts_are_clean_and_brand_specific():
    env = make_env()
    install_editorial_engine(env)
    post = env["generate_social_post"](SAMPLES[0])
    assert_clean_caption(post)
    assert "#elgamercave" in post

    st.session_state.active_brand = "Daviet Gaming"
    post_daviet = env["generate_social_post"](SAMPLES[0])
    assert_clean_caption(post_daviet)
    assert "#davietgaming" in post_daviet
    st.session_state.active_brand = "Gamer Cave"


def test_multi_post_variety_filters_placeholders():
    env = make_env()
    install_editorial_engine(env)
    respuesta = env["crear_varios_posts"](5, "dame noticias variadas de gaming, anime, tecnologia e indie")
    assert "PUBLICACIÓN 1" in respuesta
    assert "PUBLICACIÓN 5" in respuesta
    assert "Xbox: novedad para la comunidad gamer" not in respuesta
    assert "Diablo 4 Update Will Drown" not in respuesta
    assert "Kingdom Hearts 4 News Could Come" not in respuesta
    assert "ANIME" in respuesta
    assert "INDIE" in respuesta
    assert_clean_caption(respuesta)


def test_screenshot_regressions_are_blocked():
    env = make_env()
    install_editorial_engine(env)

    thief = env["generate_social_post"](SAMPLES[4], "nostalgia")
    assert_clean_caption(thief)
    assert "actualización" not in thief.lower()
    assert "#nintendo" not in thief.lower()
    assert "#playstation" not in thief.lower()

    anime = env["generate_social_post"](SAMPLES[5], "anime")
    assert_clean_caption(anime)
    assert "Gets TV Anime" not in anime
    assert "tendrá adaptación al anime" in anime

    indie = env["generate_social_post"](SAMPLES[6], "indie")
    assert_clean_caption(indie)
    assert "Enjoy our weekend" not in indie

    ai_post = env["generate_social_post"](SAMPLES[7], "debate")
    assert_clean_caption(ai_post)
    assert "Human-Crafted Chaos" not in ai_post
    assert "creatividad" in ai_post.lower()

    industry_post = env["generate_social_post"](SAMPLES[8], "debate")
    assert_clean_caption(industry_post)
    assert "are set for more layoffs" not in industry_post.lower()
    assert "industria" in industry_post.lower()


if __name__ == "__main__":
    test_titles_are_spanish_and_contextual()
    test_posts_are_clean_and_brand_specific()
    test_multi_post_variety_filters_placeholders()
    test_screenshot_regressions_are_blocked()
    print("dynamic editorial checks ok")
