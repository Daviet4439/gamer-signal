# -*- coding: utf-8 -*-

import json
import os
import re
import uuid
import base64
from datetime import date, datetime, timedelta, timezone
from html import unescape as html_unescape
from html import escape as html_escape
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import feedparser
import streamlit as st
from streamlit.components.v1 import html as components_html


st.set_page_config(page_title="Gamer Signal", page_icon="📡", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=Orbitron:wght@700;800;900&family=Rajdhani:wght@600;700&display=swap');

    :root {
        --gc-black: #0D0D0D;
        --gc-gold: #FFD700;
        --gc-red: #E10600;
        --gc-white: #FFFFFF;
        --gc-gray: #2A2A2A;
    }

    section[data-testid="stSidebar"] {
        width: 54px !important;
        min-width: 54px !important;
        transition: width 0.25s ease;
        overflow: hidden;
    }

    section[data-testid="stSidebar"]:hover {
        width: 310px !important;
        min-width: 310px !important;
    }

    section[data-testid="stSidebar"] > div {
        width: 310px !important;
        overflow-x: hidden;
    }

    section[data-testid="stSidebar"]:not(:hover) [data-testid="stVerticalBlock"] {
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.12s ease;
    }

    section[data-testid="stSidebar"]:hover [data-testid="stVerticalBlock"] {
        opacity: 1;
        pointer-events: auto;
        transition: opacity 0.2s ease 0.08s;
    }

    section[data-testid="stSidebar"]::after {
        content: "☰";
        position: fixed;
        top: 84px;
        left: 18px;
        color: var(--gc-gold);
        font-size: 22px;
        font-weight: 700;
        z-index: 999;
        pointer-events: none;
    }

    section[data-testid="stSidebar"]:hover::after {
        content: "";
    }

    div[data-testid="stAppViewContainer"] {
        transition: margin-left 0.25s ease;
    }

    .gamer-signal-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-top: 18px;
        margin-bottom: 26px;
    }

    .gamer-signal-logo {
        width: 82px;
        height: 82px;
        border-radius: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--gc-white);
        font-size: 30px;
        font-weight: 900;
        letter-spacing: 0;
        background:
            linear-gradient(135deg, var(--gc-gold) 0%, var(--gc-red) 48%, var(--gc-black) 100%);
        border: 2px solid rgba(255, 215, 0, 0.75);
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.12), 0 18px 42px rgba(225, 6, 0, 0.28), 0 0 34px rgba(255, 215, 0, 0.20);
        position: relative;
        margin-bottom: 14px;
        font-family: "Orbitron", "Inter", sans-serif;
    }

    .gamer-signal-logo::before,
    .gamer-signal-logo::after {
        content: "";
        position: absolute;
        border: 2px solid rgba(255, 215, 0, 0.75);
        border-left-color: transparent;
        border-bottom-color: transparent;
        border-radius: 50%;
        transform: rotate(-25deg);
    }

    .gamer-signal-logo::before {
        width: 58px;
        height: 58px;
    }

    .gamer-signal-logo::after {
        width: 42px;
        height: 42px;
    }

    .gamer-signal-logo.mascot {
        width: 128px;
        height: 128px;
        padding: 0;
        background: transparent;
        border: 0;
        box-shadow: none;
    }

    .gamer-signal-logo.mascot::before,
    .gamer-signal-logo.mascot::after {
        display: none;
    }

    .gamer-signal-logo.mascot img {
        width: 128px;
        height: 128px;
        object-fit: contain;
        filter: drop-shadow(0 0 16px rgba(255, 215, 0, 0.28));
    }

    .gamer-signal-title {
        font-size: 42px;
        font-weight: 900;
        line-height: 1.1;
        margin: 0;
        letter-spacing: 0;
        color: var(--gc-white);
        font-family: "Orbitron", "Inter", sans-serif;
        text-transform: uppercase;
    }

    .gamer-signal-subtitle {
        color: rgba(255, 255, 255, 0.74);
        font-size: 15px;
        margin-top: 10px;
        font-family: "Inter", sans-serif;
    }

    .signal-brand-title {
        color: var(--gc-gold);
        text-align: center;
        font-size: 13px;
        font-weight: 800;
        margin: 18px 0 10px;
        font-family: "Rajdhani", "Inter", sans-serif;
        text-transform: uppercase;
    }

    .signal-actions-space {
        height: 4px;
    }

    .st-key-signal_control_bar {
        position: sticky;
        top: 10px;
        z-index: 997;
        max-width: 820px;
        margin: 0 auto 22px auto !important;
        padding: 10px 14px 14px;
        border: 1px solid rgba(255, 215, 0, 0.38);
        border-radius: 22px;
        background:
            linear-gradient(180deg, rgba(42, 42, 42, 0.90), rgba(13, 13, 13, 0.92));
        box-shadow: 0 18px 44px rgba(0, 0, 0, 0.32), 0 0 34px rgba(255, 215, 0, 0.10);
        backdrop-filter: blur(18px);
        transition: transform 0.22s ease, opacity 0.18s ease, box-shadow 0.18s ease;
    }

    .st-key-signal_control_bar.signal-nav-hidden {
        transform: translateY(-135%);
        opacity: 0;
        pointer-events: none;
    }

    .st-key-signal_control_bar .signal-brand-title {
        margin-top: 0;
    }

    .brand-logo-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 150px;
        padding: 12px 8px;
        margin-bottom: 8px;
        border-radius: 16px;
        border: 1px solid rgba(255, 215, 0, 0.20);
        background: linear-gradient(180deg, rgba(42, 42, 42, 0.72), rgba(13, 13, 13, 0.78));
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
        transition: box-shadow 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
    }

    .brand-logo-card.active {
        border-color: rgba(255, 215, 0, 0.90);
        box-shadow:
            0 0 0 1px rgba(225, 6, 0, 0.60),
            0 0 22px rgba(255, 215, 0, 0.28),
            0 12px 28px rgba(225, 6, 0, 0.18);
        transform: translateY(-1px);
    }

    .brand-logo-card img {
        width: 118px;
        height: 104px;
        object-fit: contain;
        border-radius: 0;
        border: 0;
        margin-bottom: 6px;
        background: transparent;
        filter: drop-shadow(0 0 14px rgba(255, 215, 0, 0.22));
    }

    .brand-logo-card .brand-logo-name {
        color: var(--gc-white);
        font-family: "Rajdhani", "Inter", sans-serif;
        font-size: 14px;
        font-weight: 800;
        text-align: center;
        line-height: 1.05;
    }

    .brand-logo-card.active .brand-logo-name {
        color: var(--gc-gold);
    }

    .st-key-signal_control_bar div[data-testid="stButton"] > button {
        min-height: 38px;
    }

    .st-key-signal_control_bar .signal-actions-space + div div[data-testid="stButton"] > button {
        min-height: 28px;
        padding: 2px 6px;
        border: 0;
        background: transparent;
        box-shadow: none;
        color: rgba(255, 255, 255, 0.86);
        white-space: nowrap;
        word-break: keep-all;
        overflow-wrap: normal;
        line-height: 1;
    }

    .st-key-signal_control_bar .signal-actions-space + div div[data-testid="stButton"] > button:hover {
        color: var(--gc-gold);
        background: transparent;
        border: 0;
    }

    .st-key-signal_control_bar .signal-actions-space + div div[data-testid="stButton"] > button p {
        white-space: nowrap;
        word-break: keep-all;
        overflow-wrap: normal;
    }

    .daily-radar-panel {
        max-width: 820px;
        margin: 0 auto 24px auto;
        padding: 16px;
        border-radius: 18px;
        border: 1px solid rgba(255, 215, 0, 0.26);
        background: linear-gradient(180deg, rgba(13, 13, 13, 0.84), rgba(42, 42, 42, 0.62));
        box-shadow: 0 18px 44px rgba(0, 0, 0, 0.22);
    }

    .daily-radar-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 12px;
    }

    .daily-radar-title {
        color: var(--gc-gold);
        font-family: "Rajdhani", "Inter", sans-serif;
        font-size: 17px;
        font-weight: 800;
        text-transform: uppercase;
    }

    .daily-radar-date {
        color: rgba(255, 255, 255, 0.66);
        font-size: 12px;
        text-align: right;
    }

    .daily-radar-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
    }

    .daily-radar-card {
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.10);
        background: rgba(0, 0, 0, 0.28);
        padding: 12px;
        min-height: 142px;
    }

    .daily-radar-brand {
        color: var(--gc-white);
        font-weight: 800;
        margin-bottom: 8px;
    }

    .daily-radar-section-title {
        margin: 12px 0 8px;
        color: rgba(255, 215, 0, 0.88);
        font-family: "Rajdhani", "Inter", sans-serif;
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
    }

    .daily-radar-brand-grid {
        margin-bottom: 10px;
    }

    .daily-radar-brand-grid.single-brand {
        grid-template-columns: minmax(280px, 460px);
        justify-content: center;
    }

    .daily-radar-brand-grid.two-brands {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .daily-radar-brand-heading {
        display: flex;
        align-items: center;
        gap: 10px;
        color: var(--gc-white);
        font-weight: 900;
        margin-bottom: 10px;
    }

    .daily-radar-brand-heading img {
        width: 44px;
        height: 44px;
        object-fit: contain;
        display: block;
    }

    .daily-radar-item {
        color: rgba(255, 255, 255, 0.88);
        font-size: 13px;
        line-height: 1.35;
        margin-bottom: 10px;
    }

    .daily-radar-angle {
        color: rgba(255, 215, 0, 0.78);
        font-size: 12px;
        line-height: 1.35;
    }

    @media (max-width: 760px) {
        .st-key-signal_control_bar {
            top: 6px;
            padding: 8px 10px 12px;
            border-radius: 18px;
        }

        .daily-radar-grid {
            grid-template-columns: 1fr;
        }
    }

    div[data-testid="stRadio"] > label {
        display: none;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex;
        justify-content: center;
        gap: 8px;
        flex-wrap: wrap;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background: rgba(13, 13, 13, 0.82);
        border: 1px solid rgba(255, 215, 0, 0.26);
        border-radius: 999px;
        padding: 8px 12px;
        margin: 0;
    }

    div[data-testid="stButton"] > button {
        min-height: 40px;
        min-width: 96px;
        border-radius: 10px;
        border: 1px solid rgba(255, 215, 0, 0.34);
        background: rgba(42, 42, 42, 0.72);
        color: var(--gc-white);
        font-family: "Rajdhani", "Inter", sans-serif;
        font-weight: 700;
        white-space: nowrap;
        word-break: keep-all;
        overflow-wrap: normal;
        text-align: center;
    }

    div[data-testid="stButton"] > button p {
        white-space: nowrap;
        word-break: keep-all;
        overflow-wrap: normal;
        margin: 0;
    }

    .stApp {
        font-family: "Inter", sans-serif;
        background:
            linear-gradient(rgba(255, 215, 0, 0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 215, 0, 0.028) 1px, transparent 1px),
            linear-gradient(135deg, rgba(225, 6, 0, 0.08), transparent 42%),
            var(--gc-black);
        background-size: 42px 42px, 42px 42px, auto, auto;
    }

    .news-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 12px;
        margin-top: 12px;
    }

    .news-card {
        border: 1px solid rgba(255, 215, 0, 0.22);
        border-radius: 12px;
        padding: 16px;
        background: rgba(42, 42, 42, 0.55);
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
    }

    .news-card-title {
        font-size: 18px;
        font-weight: 800;
        color: var(--gc-white);
        margin-bottom: 10px;
        font-family: "Rajdhani", "Inter", sans-serif;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
    }

    .signal-badge {
        border-radius: 999px;
        padding: 4px 9px;
        font-size: 12px;
        font-weight: 700;
        background: rgba(255, 215, 0, 0.14);
        color: var(--gc-gold);
        border: 1px solid rgba(255, 215, 0, 0.26);
    }

    .signal-badge.good {
        background: rgba(225, 6, 0, 0.16);
        color: #ffb4b0;
    }

    .post-copy-box {
        border: 1px solid rgba(255, 215, 0, 0.25);
        border-radius: 12px;
        padding: 16px;
        background: rgba(13, 13, 13, 0.72);
        margin-top: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

ZONA_HORARIA_PR = timezone(timedelta(hours=-4), name="Puerto Rico")


def ahora_en_puerto_rico():
    return datetime.now(ZONA_HORARIA_PR)


def fecha_hora_actual_texto():
    ahora = ahora_en_puerto_rico()
    dias = [
        "lunes", "martes", "miércoles", "jueves",
        "viernes", "sábado", "domingo",
    ]
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    ]
    hora = ahora.strftime("%I:%M:%S %p").lstrip("0")
    return (
        f"{dias[ahora.weekday()]}, {ahora.day} de {meses[ahora.month - 1]} "
        f"de {ahora.year}, {hora} (Puerto Rico)"
    )


def render_reloj_actual():
    components_html(
        """
        <div id="gamer-signal-clock" style="
            color:#aeb8ca;
            font-family:Inter,Arial,sans-serif;
            font-size:13px;
            text-align:center;
            padding:2px 0 8px;
        "></div>
        <script>
        function actualizarRelojGamerSignal() {
            const ahora = new Date();
            const fecha = new Intl.DateTimeFormat("es-PR", {
                timeZone: "America/Puerto_Rico",
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric"
            }).format(ahora);
            const hora = new Intl.DateTimeFormat("es-PR", {
                timeZone: "America/Puerto_Rico",
                hour: "numeric",
                minute: "2-digit",
                second: "2-digit"
            }).format(ahora);
            document.getElementById("gamer-signal-clock").textContent =
                fecha + " · " + hora + " · Puerto Rico";
        }
        actualizarRelojGamerSignal();
        setInterval(actualizarRelojGamerSignal, 1000);
        </script>
        """,
        height=34,
    )


def activar_auto_refresh_10_minutos():
    refresh_ms = RADAR_REFRESH_MINUTES * 60 * 1000
    components_html(
        f"""
        <script>
        (function () {{
            const REFRESH_MS = {refresh_ms};
            function userIsTyping() {{
                const active = window.parent.document.activeElement;
                if (!active) return false;
                const tag = (active.tagName || "").toLowerCase();
                return tag === "textarea" || tag === "input" || active.isContentEditable;
            }}
            setTimeout(function () {{
                if (!userIsTyping()) {{
                    window.parent.location.reload();
                }} else {{
                    setTimeout(function () {{
                        if (!userIsTyping()) window.parent.location.reload();
                    }}, 60 * 1000);
                }}
            }}, REFRESH_MS);
        }})();
        </script>
        """,
        height=0,
    )


HOY = ahora_en_puerto_rico().date()
ANIO_NOTICIAS = HOY.year
FECHA_INICIO = HOY - timedelta(days=14)
FECHA_FINAL = HOY + timedelta(days=14)

MEMORY_DIR = Path("memory")
PREFS_FILE = MEMORY_DIR / "user_preferences.json"
FEEDBACK_FILE = MEMORY_DIR / "feedback_log.json"
USED_FILE = MEMORY_DIR / "used_topics.json"
MONITOR_FILE = MEMORY_DIR / "monitor_log.json"
MONITOR_BRAND_FILE = MEMORY_DIR / "monitor_brand_memory.json"
ACCESS_LOG_FILE = MEMORY_DIR / "access_log.json"
APPROVED_POSTS_DIR = Path("posts_aprobados")
ASSETS_DIR = Path("assets")

PROMPTS_DIR = Path("prompts")
BRAND_VOICE_FILE = PROMPTS_DIR / "brand_voice.json"
PROMPT_LIBRARY_FILE = PROMPTS_DIR / "prompt_library.json"
NICHE_MEMORY_FILE = PROMPTS_DIR / "niche_memory.json"

FEED_TIMEOUT_SECONDS = 3
MAX_ENTRADAS_POR_FUENTE = 8
NEWS_CACHE_TTL_SECONDS = 1800
API_TIMEOUT_SECONDS = 8
RADAR_REFRESH_MINUTES = 10

BRAND_LOGOS = {
    "Gamer Cave": ASSETS_DIR / "assistant_8bit.png",
    "Daviet Gaming": ASSETS_DIR / "assistant_dragon_pixel.png",
}

ASSISTANT_MASCOTS = {
    "Gamer Cave": ASSETS_DIR / "assistant_8bit.png",
    "Daviet Gaming": ASSETS_DIR / "assistant_dragon_pixel.png",
}

API_DOCS = {
    "RAWG": "https://rawg.io/apidocs",
    "YouTube": "https://developers.google.com/youtube/v3/docs/search/list",
    "IGDB": "https://api-docs.igdb.com/",
    "Wikimedia": "https://api.wikimedia.org/wiki/API_reference/Page_content/Get_page_summary",
}

FUENTES = {
    # Gaming oficial
    "PlayStation Blog oficial": "https://blog.playstation.com/feed/",
    "Xbox Wire oficial": "https://news.xbox.com/en-us/feed/",
    "Nintendo News oficial": "https://www.nintendo.com/us/whatsnew/rss/",
    "Steam News oficial": "https://store.steampowered.com/feeds/news.xml",
    "Epic Games Store oficial": "https://store.epicgames.com/en-US/news/rss",
    "Capcom News oficial": "https://news.capcomusa.com/feed/",
    "EA News oficial": "https://www.ea.com/news.rss",
    "Ubisoft News oficial": "https://news.ubisoft.com/en-us/rss",
    "Blizzard News oficial": "https://news.blizzard.com/en-us/feed",
    "Riot Games News oficial": "https://www.riotgames.com/en/rss.xml",
    "Bungie News oficial": "https://www.bungie.net/7/en/News/Rss",
    "GOG News oficial": "https://www.gog.com/news/feed",

    # Anime oficial/confiable
    "Crunchyroll News oficial": "https://www.crunchyroll.com/newsrss",
    "Anime News Network confiable": "https://www.animenewsnetwork.com/all/rss.xml?ann-edition=us",
    "MyAnimeList News confiable": "https://myanimelist.net/rss/news.xml",
    "Anime Corner confiable": "https://animecorner.me/feed/",
    "VIZ Blog oficial": "https://www.viz.com/blog/rss",

    # Tecnología oficial
    "OpenAI News oficial": "https://openai.com/news/rss.xml",
    "NVIDIA Blog oficial": "https://blogs.nvidia.com/feed/",
    "Unity Blog oficial": "https://blog.unity.com/feed",
    "Unreal Engine Blog oficial": "https://www.unrealengine.com/en-US/feed",
    "Intel Newsroom oficial": "https://www.intel.com/content/www/us/en/newsroom/rss.xml",

    # Medios confiables para contraste y tendencias
    "The Verge confiable": "https://www.theverge.com/rss/index.xml",
    "Polygon confiable": "https://www.polygon.com/rss/index.xml",
    "IGN Games confiable": "https://feeds.ign.com/ign/games-all",
    "GameSpot confiable": "https://www.gamespot.com/feeds/mashup/",
    "VGC confiable": "https://www.videogameschronicle.com/feed/",
    "Gematsu confiable": "https://www.gematsu.com/feed/",
    "PC Gamer confiable": "https://www.pcgamer.com/rss/",
    "Rock Paper Shotgun confiable": "https://www.rockpapershotgun.com/feed",
    "Engadget confiable": "https://www.engadget.com/rss.xml",
    "TechCrunch AI confiable": "https://techcrunch.com/category/artificial-intelligence/feed/",
}

FUENTES_COMUNIDAD = {
    "Reddit Gaming - señal de comunidad": "https://www.reddit.com/r/gaming/.rss",
    "Reddit TrueGaming - señal de debate": "https://www.reddit.com/r/truegaming/.rss",
    "Reddit PatientGamers - señal nostalgia": "https://www.reddit.com/r/patientgamers/.rss",
    "Reddit RetroGaming - señal nostalgia": "https://www.reddit.com/r/retrogaming/.rss",
    "Reddit Nintendo - señal comunidad": "https://www.reddit.com/r/nintendo/.rss",
    "Reddit PlayStation - señal comunidad": "https://www.reddit.com/r/playstation/.rss",
    "Reddit Xbox - señal comunidad": "https://www.reddit.com/r/xbox/.rss",
    "Reddit PCGaming - señal comunidad": "https://www.reddit.com/r/pcgaming/.rss",
    "Reddit IndieGaming - señal indie": "https://www.reddit.com/r/indiegaming/.rss",
    "Reddit Anime - señal anime": "https://www.reddit.com/r/anime/.rss",
    "Reddit Manga - señal anime": "https://www.reddit.com/r/manga/.rss",
    "Reddit JRPG - señal fandom": "https://www.reddit.com/r/JRPG/.rss",
    "Reddit Argaming - señal LatAm": "https://www.reddit.com/r/Argaming/.rss",
}

TEMAS_DEBATE = [
    "Juegos físicos vs juegos digitales",
    "Battle pass y microtransacciones",
    "Juegos incompletos de lanzamiento",
    "Multiplayer local vs online",
    "Remakes vs juegos nuevos",
    "Nostalgia vs innovación",
    "Consolas vs PC",
    "Game Pass, PS Plus y suscripciones",
    "Juegos que necesitan conexión permanente",
    "IA en videojuegos",
    "Comunidades tóxicas en juegos online",
    "Precios de videojuegos",
]

TEMAS_COMUNIDAD = [
    "¿Los juegos físicos todavía tienen valor o ya todo se fue digital?",
    "¿Los remakes nos emocionan porque son buenos o porque extrañamos otra época?",
    "¿Game Pass y PS Plus cambiaron la forma en que valoramos los juegos?",
    "¿El multiplayer local se siente más especial que jugar online?",
    "¿Los juegos como servicio están cansando a la comunidad?",
    "¿La IA en videojuegos puede ayudar o le quita alma al desarrollo?",
    "¿Las ediciones deluxe y los precios actuales están alejando a los jugadores?",
    "¿Los trailers muestran demasiado antes de que salga un juego?",
]

TEMAS_ANIME = [
    "anime de temporada y el hype que se forma antes de los estrenos",
    "regresos de animes clásicos que despiertan nostalgia",
    "adaptaciones de manga que la comunidad espera con miedo y emoción",
    "peleas, openings y momentos de anime que se vuelven conversación gamer",
    "anime que conectó con gamers por sus mundos, poderes o espíritu de aventura",
]

TEMAS_NOSTALGIA = [
    "Game Boy",
    "GameCube",
    "Nintendo 64",
    "PlayStation 1",
    "PlayStation 2",
    "PlayStation 3",
    "Xbox clásico",
    "Xbox 360",
    "Pokémon",
    "Mario",
    "Kirby",
    "The Legend of Zelda",
    "Rayman",
    "Crazy Taxi",
    "juegos físicos",
    "cartuchos",
    "discos",
    "manuales de juegos",
    "multiplayer local",
    "memory cards",
    "pantallas divididas",
    "jugar con primos o amigos",
    "llegar de la escuela y prender la consola",
    "cibercafés",
    "juegos que nunca terminaste",
    "juegos que daban miedo de pequeño",
]

CONTEXTO_LOCAL_NOSTALGIA = {
    "GameCube": {
        "name": "GameCube",
        "summary": (
            "Tema ideal para nostalgia gamer: consola de Nintendo recordada por su control, juegos fisicos, "
            "multiplayer local, tardes jugando con amistades y franquicias como Mario, Zelda, Metroid, Smash, "
            "Mario Kart y Resident Evil. Para Puerto Rico y LatAm puede conectar con recuerdos de alquilar juegos, "
            "prestar controles, cuidar discos y jugar en casa con familia o panas."
        ),
    },
    "Game Boy": {
        "name": "Game Boy",
        "summary": (
            "Tema fuerte para nostalgia portatil: pilas, cartuchos, pantallas simples, Pokemon, Tetris, Mario, "
            "viajes largos y jugar donde fuera. Conecta con la idea de que antes no hacia falta internet para vivir "
            "momentos memorables."
        ),
    },
    "Game Boy Advance": {
        "name": "Game Boy Advance",
        "summary": (
            "Buen tema para hablar de portatil clasico, cartuchos, Pokemon, Zelda, Mario, Metroid y juegos que muchos "
            "llevaban a la escuela, viajes o reuniones familiares."
        ),
    },
    "Nintendo 64": {
        "name": "Nintendo 64",
        "summary": (
            "Tema nostalgico perfecto para multiplayer local, cuatro controles, Mario Kart 64, Super Smash Bros., "
            "GoldenEye, Zelda y esa etapa donde juntarse a jugar era parte central de la experiencia."
        ),
    },
    "PlayStation 2": {
        "name": "PlayStation 2",
        "summary": (
            "Tema enorme de nostalgia gamer: discos, memory cards, juegos fisicos, GTA, Final Fantasy, Metal Gear, "
            "Kingdom Hearts, Dragon Ball y muchas tardes repitiendo juegos sin cansarse."
        ),
    },
    "Pokémon": {
        "name": "Pokemon",
        "summary": (
            "Tema fuerte para comunidad: juegos portatiles, intercambios, batallas, cartas, anime, recuerdos de infancia "
            "y debates sobre generaciones favoritas. Funciona muy bien para comentarios."
        ),
    },
    "The Legend of Zelda": {
        "name": "The Legend of Zelda",
        "summary": (
            "Tema ideal para hablar de aventura, descubrimiento, nostalgia y debate entre juegos clasicos y modernos. "
            "Puede mover comentarios preguntando cual entrega marco mas a la comunidad."
        ),
    },
    "Nintendo": {
        "name": "Nintendo: de NES a Switch 2",
        "summary": (
            "Linea retro para posts: NES/Famicom, Super Nintendo, Nintendo 64, GameCube, Wii, Wii U, Nintendo Switch "
            "y Nintendo Switch 2. Sirve para comparar generaciones: cartuchos, controles, multiplayer local, innovacion "
            "familiar, portabilidad y como Nintendo ha vendido nostalgia sin dejar de probar ideas nuevas. Angulo bueno: "
            "cual generacion de Nintendo marco mas a tu familia o grupo de panas."
        ),
    },
    "PlayStation": {
        "name": "PlayStation: de PS1 a PS5/PS5 Pro",
        "summary": (
            "Linea retro para posts: PlayStation, PS2, PS3, PS4, PS5 y PS5 Pro. Conecta con discos, memory cards, "
            "demos, tiendas de juegos, sagas cinematicas, online moderno y el salto visual de cada generacion. Angulo bueno: "
            "si la nostalgia de PS1/PS2 pesa mas que la potencia actual."
        ),
    },
    "Xbox": {
        "name": "Xbox: de la Xbox original a Series X|S",
        "summary": (
            "Linea retro para posts: Xbox original, Xbox 360, Xbox One y Xbox Series X|S. Conecta con Halo, Xbox Live, "
            "multiplayer local, logros, Game Pass, retrocompatibilidad y el debate de servicios vs comprar juegos. Angulo bueno: "
            "si Xbox 360 fue la etapa mas fuerte para la comunidad."
        ),
    },
    "Sega": {
        "name": "Sega: de Master System a Dreamcast",
        "summary": (
            "Linea retro para posts: Master System, Genesis/Mega Drive, Saturn y Dreamcast. Funciona para nostalgia de arcade, "
            "Sonic, controles clasicos, VMU, juegos adelantados a su epoca y el debate de por que Dreamcast todavia tiene culto."
        ),
    },
}


FUENTES_OFICIALES_JUEGOS = {
    "Nintendo": [
        ("Nintendo oficial", "https://www.nintendo.com/us/store/games/", "pagina oficial para juegos, plataformas y detalles de Nintendo"),
        ("Nintendo News oficial", "https://www.nintendo.com/us/whatsnew/", "anuncios oficiales y novedades"),
    ],
    "PlayStation": [
        ("PlayStation Store oficial", "https://store.playstation.com/", "pagina oficial para juegos, plataformas, funciones y ediciones"),
        ("PlayStation Blog oficial", "https://blog.playstation.com/", "anuncios oficiales y contexto de lanzamientos"),
    ],
    "Xbox": [
        ("Xbox Games oficial", "https://www.xbox.com/games", "pagina oficial para juegos, plataformas, Game Pass y funciones"),
        ("Xbox Wire oficial", "https://news.xbox.com/", "anuncios oficiales y noticias de Xbox"),
    ],
    "PC": [
        ("Steam oficial", "https://store.steampowered.com/", "pagina oficial de PC para requisitos, tags, funciones y reviews de usuarios"),
        ("Epic Games Store oficial", "https://store.epicgames.com/", "pagina oficial para juegos, ediciones y disponibilidad"),
    ],
    "Publishers": [
        ("EA oficial", "https://www.ea.com/games", "juegos, modos, temporadas y paginas oficiales de EA"),
        ("Ubisoft oficial", "https://www.ubisoft.com/games", "juegos, actualizaciones y paginas oficiales de Ubisoft"),
        ("Capcom oficial", "https://www.capcom-games.com/", "juegos y anuncios oficiales de Capcom"),
        ("Blizzard oficial", "https://www.blizzard.com/games", "juegos, temporadas y soporte oficial de Blizzard"),
        ("Riot Games oficial", "https://www.riotgames.com/", "juegos, esports y noticias oficiales de Riot"),
    ],
}


NICHO_PR_LATAM = {
    "region": "Puerto Rico y Latinoamérica",
    "audience": [
        "gamers adultos que crecieron con consolas, rentals, juegos físicos, multiplayer local y tardes jugando con amistades o familia",
        "jugadores que consumen PlayStation, Xbox, Nintendo, PC gaming, anime, tecnología, cultura geek y entretenimiento digital",
        "comunidad que comenta más cuando el tema toca precio, nostalgia, valor real para el jugador, hype, decepción, exclusivas o cambios en la industria",
    ],
    "engagement_goals": [
        "convertir noticias calientes en conversación fácil de comentar",
        "informar primero y luego abrir debate sano",
        "conectar noticias actuales con recuerdos, experiencias y hábitos de gamers de Puerto Rico y LatAm",
        "evitar posts fríos; cada publicación debe tener un ángulo humano o comunitario",
    ],
    "hot_angles": [
        "precio, valor y si realmente vale la pena",
        "juegos físicos vs digitales",
        "servicios como Game Pass, PS Plus, Nintendo Switch Online y suscripciones",
        "nostalgia de consolas viejas, cartuchos, discos, manuales y multiplayer local",
        "hype vs realidad cuando anuncian trailers, remakes, remasters o secuelas",
        "tecnología explicada desde cómo afecta al gamer común",
        "anime, cultura geek y gaming cuando mueven conversación de comunidad",
    ],
    "rules": [
        "priorizar noticias hot que puedan generar comentarios, no solo anuncios informativos",
        "si una noticia es verificada, convertirla en una pregunta o debate útil para la comunidad",
        "si el tema es nostalgia u opinión, no presentarlo como noticia confirmada",
        "hablar en español natural para Puerto Rico y LatAm; usar inglés solo en nombres oficiales",
        "mantener respeto entre plataformas, fandoms y comunidades",
        "cerrar con una pregunta clara que invite a comentar sin sonar desesperada",
    ],
}

PALABRAS_HOT_NICHO = [
    "nintendo", "switch", "playstation", "ps5", "ps plus", "xbox", "game pass",
    "steam", "pc gaming", "pokemon", "pokémon", "mario", "zelda", "kirby",
    "anime", "manga", "crunchyroll", "nvidia", "rtx", "gpu", "hardware",
    "capcom", "resident evil", "monster hunter", "street fighter", "ea", "battlefield",
    "ubisoft", "assassin", "riot", "league of legends", "valorant", "blizzard",
    "diablo", "overwatch", "warcraft", "epic games", "fortnite", "unreal engine",
    "unity", "intel", "amd", "myanimelist", "anime news network",
    "remake", "remaster", "sequel", "demo", "gratis", "free", "precio",
    "subscription", "suscripción", "dlc", "battle pass", "microtransacciones",
    "physical", "digital", "físico", "fisico", "multiplayer", "coop",
]

SENALES_TENDENCIA = {
    "movimiento fuerte": [
        "viral", "trending", "record", "récord", "million", "millón",
        "sales", "ventas", "best seller", "top played", "most played",
        "players", "jugadores", "wishlists", "lista de deseados",
    ],
    "actualidad": [
        "announces", "anuncia", "reveals", "revela", "launch", "lanza",
        "release", "estreno", "update", "actualización", "trailer", "tráiler",
        "demo", "beta", "early access", "acceso anticipado",
    ],
    "conversación": [
        "precio", "price", "delay", "retraso", "cancel", "cancela",
        "physical", "físico", "digital", "subscription", "suscripción",
        "microtransaction", "microtransacción", "exclusive", "exclusiva",
    ],
    "nostalgia activa": [
        "anniversary", "aniversario", "remake", "remaster", "reboot",
        "classic", "clásico", "retro", "collection", "colección",
    ],
}

SENALES_INDIE = [
    "indie", "independent", "independiente", "small team", "solo developer",
    "steam next fest", "next fest", "indie world", "kickstarter",
    "debut game", "debut project", "primer juego", "estudio independiente",
]


def preparar_memoria():
    MEMORY_DIR.mkdir(exist_ok=True)
    for archivo in [PREFS_FILE, FEEDBACK_FILE, USED_FILE, MONITOR_FILE, MONITOR_BRAND_FILE, ACCESS_LOG_FILE]:
        if not archivo.exists():
            archivo.write_text("[]", encoding="utf-8")
    prefs = leer_json(PREFS_FILE, [])
    cambio = False
    if not any(pref.get("key") == "hashtag_limit" for pref in prefs):
        prefs.append({
            "key": "hashtag_limit",
            "value": "5",
            "weight": 10,
            "last_updated": ahora(),
            "source_feedback": "default Instagram limit",
        })
        cambio = True

    reglas_seguridad = [
        "Las noticias actuales solo se publican si vienen de fuente oficial o estan confirmadas por 2 o mas fuentes confiables.",
        "Wikipedia solo se usa como contexto historico o nostalgia; nunca confirma noticias actuales.",
        "Si algo no esta verificado, debe tratarse como opinion, nostalgia o debate, no como noticia.",
        "No inventar datos, fechas, fuentes, lanzamientos, precios ni plataformas.",
    ]
    reglas_existentes = {
        str(pref.get("value", "")).lower()
        for pref in prefs
        if pref.get("key") == "permanent_rule"
    }
    for regla in reglas_seguridad:
        if regla.lower() not in reglas_existentes:
            prefs.append({
                "key": "permanent_rule",
                "value": regla,
                "weight": 10,
                "last_updated": ahora(),
                "source_feedback": "regla editorial de verificacion",
            })
            cambio = True

    if cambio:
        guardar_json(PREFS_FILE, prefs)


def leer_json(archivo, default=None):
    if default is None:
        default = []
    try:
        if not archivo.exists():
            return default
        return json.loads(archivo.read_text(encoding="utf-8"))
    except Exception:
        return default


def guardar_json(archivo, datos):
    archivo.parent.mkdir(exist_ok=True)
    archivo.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def obtener_secreto(nombre):
    valor = st.session_state.get(nombre)
    if valor:
        return valor.strip()

    try:
        valor = st.secrets.get(nombre, "")
        if valor:
            return str(valor).strip()
    except Exception:
        pass

    return os.environ.get(nombre, "").strip()


def telegram_configurado():
    return bool(obtener_secreto("TELEGRAM_BOT_TOKEN") and obtener_secreto("TELEGRAM_CHAT_ID"))


def enviar_telegram(mensaje):
    token = obtener_secreto("TELEGRAM_BOT_TOKEN")
    chat_id = obtener_secreto("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False

    try:
        data = urlencode({
            "chat_id": chat_id,
            "text": mensaje,
            "disable_web_page_preview": "true",
        }).encode("utf-8")
        request = Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data,
            headers={"User-Agent": "GamerSignal/1.0"},
        )
        with urlopen(request, timeout=API_TIMEOUT_SECONDS) as response:
            return 200 <= response.status < 300
    except Exception:
        return False


def notificar_hallazgos_telegram(nuevos):
    if not nuevos or not telegram_configurado():
        return False

    lineas = [
        "Gamer Signal encontró noticias nuevas para revisar:",
        "",
    ]
    for item in nuevos[:5]:
        titulo = titulo_publico_en_espanol(item.get("title", ""), "news")
        fuente = item.get("source", "fuente")
        lineas.append(f"- {titulo} ({fuente})")

    lineas.append("")
    lineas.append("Abre Gamer Signal para convertirlas en post.")
    return enviar_telegram("\n".join(lineas))


def api_disponible(nombre):
    if nombre == "RAWG":
        return bool(obtener_secreto("RAWG_API_KEY"))
    if nombre == "YouTube":
        return bool(obtener_secreto("YOUTUBE_API_KEY"))
    if nombre == "IGDB":
        return bool(obtener_secreto("IGDB_CLIENT_ID") and obtener_secreto("IGDB_CLIENT_SECRET"))
    if nombre == "Wikimedia":
        return True
    return False


def estado_apis():
    return {
        "RAWG": api_disponible("RAWG"),
        "YouTube": api_disponible("YouTube"),
        "IGDB": api_disponible("IGDB"),
        "Wikimedia": True,
    }


def leer_json_url(url, headers=None, data=None, timeout=API_TIMEOUT_SECONDS):
    headers = headers or {}
    headers.setdefault("User-Agent", "GamerSignal/1.0")
    try:
        payload = None
        if data is not None:
            payload = data.encode("utf-8") if isinstance(data, str) else data
        request = Request(url, headers=headers, data=payload)
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def rawg_buscar_juego(tema, api_key):
    if not api_key or not tema:
        return None

    params = urlencode({
        "key": api_key,
        "search": tema,
        "page_size": 3,
    })
    data = leer_json_url(f"https://api.rawg.io/api/games?{params}")
    resultados = (data or {}).get("results", [])
    if not resultados:
        return None

    juego = resultados[0]
    detalle = None
    slug = juego.get("slug")
    if slug:
        detalle = leer_json_url(f"https://api.rawg.io/api/games/{quote(slug)}?{urlencode({'key': api_key})}")

    detalle = detalle or {}
    plataformas = [
        p.get("platform", {}).get("name", "")
        for p in (detalle.get("platforms") or juego.get("platforms") or [])
        if p.get("platform", {}).get("name")
    ]
    generos = [
        g.get("name", "")
        for g in (detalle.get("genres") or juego.get("genres") or [])
        if g.get("name")
    ]

    return {
        "provider": "RAWG",
        "name": detalle.get("name") or juego.get("name") or tema,
        "released": detalle.get("released") or juego.get("released") or "",
        "rating": detalle.get("rating") or juego.get("rating") or "",
        "platforms": plataformas[:6],
        "genres": generos[:5],
        "summary": limpiar_html(detalle.get("description_raw", ""))[:420],
        "url": detalle.get("website") or "",
        "role": "contexto de base de datos de videojuegos",
    }


@st.cache_data(ttl=1800, show_spinner=False)
def youtube_buscar_tema(tema, api_key):
    if not api_key or not tema:
        return None

    params = urlencode({
        "key": api_key,
        "part": "snippet",
        "q": f"{tema} gaming anime tecnologia",
        "type": "video",
        "maxResults": 3,
        "order": "relevance",
        "safeSearch": "moderate",
    })
    data = leer_json_url(f"https://www.googleapis.com/youtube/v3/search?{params}")
    items = (data or {}).get("items", [])
    videos = []
    for item in items:
        snippet = item.get("snippet", {})
        videos.append({
            "title": limpiar_html(snippet.get("title", "")),
            "channel": limpiar_html(snippet.get("channelTitle", "")),
            "published": snippet.get("publishedAt", "")[:10],
        })

    if not videos:
        return None

    return {
        "provider": "YouTube",
        "videos": videos,
        "role": "senales de conversacion y tendencias; no confirma noticias por si solo",
    }


@st.cache_data(ttl=3300, show_spinner=False)
def igdb_token(client_id, client_secret):
    if not client_id or not client_secret:
        return ""

    params = urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    })
    data = leer_json_url(f"https://id.twitch.tv/oauth2/token?{params}", data=b"")
    return (data or {}).get("access_token", "")


@st.cache_data(ttl=3600, show_spinner=False)
def igdb_buscar_juego(tema, client_id, client_secret):
    if not client_id or not client_secret or not tema:
        return None

    token = igdb_token(client_id, client_secret)
    if not token:
        return None

    tema_seguro = tema.replace('"', "")
    body = (
        f'search "{tema_seguro}"; '
        "fields name,summary,first_release_date,total_rating,genres.name,platforms.name; "
        "where version_parent = null; limit 3;"
    )
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    data = leer_json_url("https://api.igdb.com/v4/games", headers=headers, data=body)
    if not data:
        return None

    juego = data[0]
    plataformas = [p.get("name", "") for p in juego.get("platforms", []) if p.get("name")]
    generos = [g.get("name", "") for g in juego.get("genres", []) if g.get("name")]
    lanzamiento = ""
    if juego.get("first_release_date"):
        try:
            lanzamiento = datetime.fromtimestamp(juego["first_release_date"]).date().isoformat()
        except Exception:
            lanzamiento = ""

    return {
        "provider": "IGDB",
        "name": juego.get("name", tema),
        "released": lanzamiento,
        "rating": juego.get("total_rating", ""),
        "platforms": plataformas[:6],
        "genres": generos[:5],
        "summary": limpiar_html(juego.get("summary", ""))[:420],
        "role": "contexto de base de datos de videojuegos",
    }


def buscar_contexto_apis(tema):
    contexto = []
    rawg_key = obtener_secreto("RAWG_API_KEY")
    youtube_key = obtener_secreto("YOUTUBE_API_KEY")
    igdb_client_id = obtener_secreto("IGDB_CLIENT_ID")
    igdb_client_secret = obtener_secreto("IGDB_CLIENT_SECRET")

    rawg = rawg_buscar_juego(tema, rawg_key) if rawg_key else None
    if rawg:
        contexto.append(rawg)

    igdb = igdb_buscar_juego(tema, igdb_client_id, igdb_client_secret) if igdb_client_id and igdb_client_secret else None
    if igdb:
        contexto.append(igdb)

    youtube = youtube_buscar_tema(tema, youtube_key) if youtube_key else None
    if youtube:
        contexto.append(youtube)

    return contexto


def resumir_contexto_apis(contextos):
    if not contextos:
        return ""

    partes = []
    for ctx in contextos:
        proveedor = ctx.get("provider", "API")
        if proveedor in ["RAWG", "IGDB"]:
            detalle = []
            if ctx.get("released"):
                detalle.append(f"lanzamiento: {ctx['released']}")
            if ctx.get("platforms"):
                detalle.append("plataformas: " + ", ".join(ctx["platforms"][:4]))
            if ctx.get("genres"):
                detalle.append("generos: " + ", ".join(ctx["genres"][:3]))
            if ctx.get("summary"):
                detalle.append("contexto: " + recortar_texto(ctx["summary"], 220))
            if detalle:
                partes.append(f"{proveedor}: {ctx.get('name', 'tema')} | " + " | ".join(detalle))
        elif proveedor == "YouTube":
            titulos = [
                f"{video.get('title')} ({video.get('channel')})"
                for video in ctx.get("videos", [])[:3]
                if video.get("title")
            ]
            if titulos:
                partes.append("YouTube: temas/videos relacionados: " + "; ".join(titulos))

    if not partes:
        return ""

    return " Contexto extra revisado por APIs: " + " ".join(partes)


def mostrar_estado_apis():
    estado = estado_apis()
    respuesta = "### Conexiones de contexto de Gamer Signal\n\n"
    respuesta += (
        "La base para noticias reales sigue siendo RSS oficiales y fuentes confiables verificadas. "
        "Estas conexiones solo ayudan con contexto, juegos, fechas, plataformas, nostalgia y señales de conversación.\n\n"
    )
    for nombre, activo in estado.items():
        marca = "activa" if activo else "sin configurar"
        respuesta += f"- **{nombre}:** {marca}\n"
    respuesta += (
        "\nUso recomendado:\n"
        "- RSS oficiales: noticias reales y verificadas.\n"
        "- RAWG/IGDB: contexto de juegos, plataformas, fechas y datos historicos.\n"
        "- YouTube: senales de conversacion; no confirma noticias por si solo.\n"
        "- Wikimedia: contexto historico/nostalgia, no confirmacion de noticias.\n"
    )
    return respuesta


def limpiar_pedido_contexto(pregunta):
    texto = pregunta.lower()
    frases = [
        "busca informacion de", "busca información de", "busca informacion sobre", "busca información sobre",
        "dame informacion de", "dame información de", "dame informacion sobre", "dame información sobre",
        "contexto de", "contexto sobre", "contexto",
        "datos de", "datos sobre", "datos",
        "informacion de", "información de", "informacion sobre", "información sobre",
        "busca informacion", "busca información",
        "dame informacion", "dame información",
        "como se juega", "cómo se juega", "como funciona", "cómo funciona",
        "funciones de", "funciones", "mecanicas de", "mecánicas de", "mecanicas", "mecánicas",
        "modos de juego de", "modos de juego", "gameplay de", "gameplay",
        "que sabes de", "qué sabes de", "que sabes", "qué sabes",
        "historia de", "historia sobre", "historia",
        "ficha de", "ficha sobre", "ficha",
        "investiga sobre", "investiga de", "investiga",
        "buscar", "busca", "por favor", "del tema", "tema",
    ]
    for frase in sorted(frases, key=len, reverse=True):
        texto = texto.replace(frase, " ")
    palabras = [
        palabra
        for palabra in texto.split()
        if palabra not in ["el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "sobre"]
    ]
    return " ".join(palabras).strip(" .,:;-")


def normalizar_tema_contexto(tema):
    tema = " ".join(str(tema or "").split()).strip(" .,:;-")
    bajo = tema.lower()
    alias = {
        "gamecube": "GameCube",
        "nintendo gamecube": "GameCube",
        "game boy": "Game Boy",
        "gameboy": "Game Boy",
        "gba": "Game Boy Advance",
        "n64": "Nintendo 64",
        "nintendo 64": "Nintendo 64",
        "ps1": "PlayStation",
        "ps2": "PlayStation 2",
        "playstation 2": "PlayStation 2",
        "pokemon": "Pokémon",
        "pokémon": "Pokémon",
        "zelda": "The Legend of Zelda",
        "mario": "Mario",
        "kirby": "Kirby",
        "xbox 360": "Xbox 360",
        "dreamcast": "Dreamcast",
    }
    if bajo in alias:
        return alias[bajo]
    if "nintendo" in bajo:
        return "Nintendo"
    if "playstation" in bajo or "ps1" in bajo or "ps2" in bajo or "ps3" in bajo or "ps4" in bajo or "ps5" in bajo:
        return "PlayStation"
    if "xbox" in bajo:
        return "Xbox"
    if "sega" in bajo or "dreamcast" in bajo or "genesis" in bajo or "mega drive" in bajo:
        return "Sega"
    return tema


def buscar_contexto_local(tema):
    tema = normalizar_tema_contexto(tema)
    data = CONTEXTO_LOCAL_NOSTALGIA.get(tema)
    if not data:
        return None
    return {
        "provider": "Memoria Gamer Signal",
        "name": data.get("name", tema),
        "summary": data.get("summary", ""),
        "role": "contexto editorial de nostalgia; no confirma noticias actuales",
    }


def fuentes_oficiales_para_tema(tema):
    tema_norm = normalizar_tema_contexto(tema)
    texto = f"{tema_norm} {tema}".lower()
    grupos = []

    if tema_norm in ["Nintendo", "GameCube", "Game Boy", "Game Boy Advance", "Nintendo 64", "Pokémon", "The Legend of Zelda"] or any(
        palabra in texto for palabra in ["nintendo", "mario", "zelda", "kirby", "pokemon", "pokémon", "switch"]
    ):
        grupos.append("Nintendo")
    if tema_norm == "PlayStation" or any(palabra in texto for palabra in ["playstation", "ps1", "ps2", "ps3", "ps4", "ps5"]):
        grupos.append("PlayStation")
    if tema_norm == "Xbox" or "xbox" in texto or "game pass" in texto:
        grupos.append("Xbox")
    if any(palabra in texto for palabra in ["pc", "steam", "epic", "hardware"]):
        grupos.append("PC")
    if any(palabra in texto for palabra in ["ea", "ubisoft", "capcom", "blizzard", "riot", "resident evil", "monster hunter", "diablo", "overwatch", "valorant"]):
        grupos.append("Publishers")

    if not grupos:
        grupos = ["Nintendo", "PlayStation", "Xbox", "PC", "Publishers"]

    fuentes = []
    for grupo in grupos:
        for nombre, url, uso in FUENTES_OFICIALES_JUEGOS.get(grupo, []):
            if url not in [item["url"] for item in fuentes]:
                fuentes.append({"name": nombre, "url": url, "use": uso})
    return fuentes[:6]


def formatear_fuentes_oficiales(tema):
    fuentes = fuentes_oficiales_para_tema(tema)
    if not fuentes:
        return ""
    respuesta = "**Fuentes oficiales para confirmar detalles:**\n"
    for fuente in fuentes:
        respuesta += f"- {fuente['name']}: {fuente['use']} - {fuente['url']}\n"
    return respuesta


def guia_como_se_juega(tema):
    return (
        "**Qué mirar para explicar cómo se juega:**\n"
        "- Género y objetivo principal del juego.\n"
        "- Modos: historia, online, cooperativo, competitivo o local.\n"
        "- Mecánicas principales: combate, exploración, progresión, construcción, carreras, RPG, puzzles o estrategia.\n"
        "- Plataformas disponibles y si tiene crossplay, edición especial, DLC o servicio online.\n"
        "- Qué lo hace interesante para la comunidad gamer de Puerto Rico y LatAm.\n"
        "- Pregunta final para comentarios: ¿lo jugarías, lo recomiendas o lo dejarías pasar?\n"
    )


def buscar_senales_comunidad_tema(tema, limite=5):
    tema_bajo = normalizar_tema_contexto(tema).lower()
    palabras = palabras_clave_tema(tema_bajo)
    resultados = []
    for item in cargar_senales_comunidad():
        texto = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        if tema_bajo in texto or palabras_clave_tema(texto) & palabras:
            resultados.append(item)
    return resultados[:limite]


def crear_contexto_api(pregunta):
    tema = limpiar_pedido_contexto(pregunta)
    if not tema:
        tema = limpiar_pedido_post(pregunta)
    if not tema:
        tema = limpiar_tema_nostalgia(pregunta)
    tema = normalizar_tema_contexto(tema)
    if not tema:
        return "Dime el tema o juego para buscar contexto. Ejemplo: contexto de GameCube."

    contextos = []
    wiki = buscar_wikipedia(tema)
    if wiki:
        contextos.append({
            "provider": "Wikimedia",
            "name": wiki.get("title", tema),
            "summary": wiki.get("summary", ""),
            "role": "contexto historico; no confirma noticias actuales",
        })
    local = buscar_contexto_local(tema)
    if local:
        contextos.append(local)

    if not contextos:
        return (
            f"No encontre contexto suficiente para **{tema}**.\n\n"
            "Para noticias reales sigo usando RSS oficiales y verificacion por fuentes confiables. "
            "Para nostalgia uso contexto historico y memoria editorial gamer."
        )

    respuesta = f"### Contexto para {tema}\n\n"
    for ctx in contextos:
        respuesta += f"**{ctx.get('provider', 'Fuente de contexto')}** - {ctx.get('role', 'contexto')}\n\n"
        if ctx.get("name"):
            respuesta += f"- Nombre: {ctx['name']}\n"
        if ctx.get("released"):
            respuesta += f"- Fecha/lanzamiento: {ctx['released']}\n"
        if ctx.get("platforms"):
            respuesta += f"- Plataformas: {', '.join(ctx['platforms'])}\n"
        if ctx.get("genres"):
            respuesta += f"- Generos: {', '.join(ctx['genres'])}\n"
        if ctx.get("videos"):
            for video in ctx["videos"]:
                respuesta += f"- Video relacionado: {video.get('title')} | {video.get('channel')}\n"
        if ctx.get("summary"):
            respuesta += f"- Contexto: {recortar_texto(ctx['summary'], 320)}\n"
        respuesta += "\n"

    respuesta += guia_como_se_juega(tema) + "\n"
    respuesta += formatear_fuentes_oficiales(tema) + "\n"
    senales = buscar_senales_comunidad_tema(tema)
    if senales:
        respuesta += "\n**Señales recientes de comunidad (no son noticia confirmada):**\n"
        for senal in senales:
            titulo = titulo_publico_en_espanol(senal.get("title", ""), "debate")
            respuesta += f"- {titulo} | {senal.get('source', 'comunidad')}\n"
    respuesta += "Nota: esto ayuda con contexto. Para noticias actuales sigo usando filtro estricto de fuentes oficiales o 2+ fuentes confiables."
    return respuesta


def es_pedido_estado_conexiones(texto):
    frases = [
        "estado de conexiones",
        "conexiones",
        "fuentes conectadas",
        "que tengo conectado",
        "qué tengo conectado",
        "estado api",
        "estado apis",
        "apis conectadas",
        "api status",
    ]
    return any(frase in texto for frase in frases)


def es_pedido_contexto(texto):
    if es_pedido_post(texto):
        return False
    if any(palabra in texto for palabra in ["noticia", "noticias", "post", "posts", "calendario", "hashtags"]):
        return False

    frases = [
        "contexto de",
        "contexto sobre",
        "datos de",
        "datos sobre",
        "informacion de",
        "información de",
        "informacion sobre",
        "información sobre",
        "busca informacion",
        "busca información",
        "dame informacion",
        "dame información",
        "como se juega",
        "cómo se juega",
        "como funciona",
        "cómo funciona",
        "funciones de",
        "mecanicas",
        "mecánicas",
        "modos de juego",
        "gameplay de",
        "investiga",
        "que sabes de",
        "qué sabes de",
        "historia de",
        "ficha de",
    ]
    return any(frase in texto for frase in frases)


def ahora():
    return ahora_en_puerto_rico().isoformat(timespec="seconds")


def convertir_a_lista(valor):
    if isinstance(valor, list):
        return valor
    if isinstance(valor, dict):
        resultado = []
        for item in valor.values():
            resultado.extend(convertir_a_lista(item))
        return resultado
    if valor:
        return [str(valor)]
    return []


def unir_unicos(lista_actual, lista_nueva):
    resultado = []
    for item in convertir_a_lista(lista_actual) + convertir_a_lista(lista_nueva):
        if item and item not in resultado:
            resultado.append(item)
    return resultado


def aplicar_contexto_nicho(brand):
    contexto_nicho = leer_json(NICHE_MEMORY_FILE, NICHO_PR_LATAM)
    if not isinstance(contexto_nicho, dict):
        contexto_nicho = NICHO_PR_LATAM

    brand["niche_context"] = contexto_nicho
    brand["audience"] = (
        f"{brand.get('audience', 'gamers')}. También debe pensar en el nicho gamer de "
        "Puerto Rico y Latinoamérica: comunidad que consume noticias, nostalgia, anime, "
        "tecnología, debates de industria y contenido fácil de comentar."
    )
    brand["rules"] = unir_unicos(brand.get("rules", []), contexto_nicho.get("rules", NICHO_PR_LATAM["rules"]))
    brand["main_topics"] = unir_unicos(
        brand.get("main_topics", []),
        [
            "temas calientes que generen debate sano",
            "noticias convertidas en conversación comunitaria",
            "hábitos de consumo gamer en Puerto Rico y LatAm",
            "contenido de opinión, nostalgia y cultura geek que provoque comentarios",
        ],
    )
    brand["engagement_goals"] = contexto_nicho.get("engagement_goals", NICHO_PR_LATAM["engagement_goals"])
    brand["hot_angles"] = contexto_nicho.get("hot_angles", NICHO_PR_LATAM["hot_angles"])
    return brand


def get_brand_voice():
    base = leer_json(BRAND_VOICE_FILE, {})
    active_brand = st.session_state.get("active_brand", "Gamer Cave")
    if active_brand == "General":
        active_brand = "Gamer Cave"

    if active_brand == "Gamer Cave":
        base = {
            "brand": "El Gamer Cave",
            "tagline": "Tu tribu geek, tu hogar.",
            "description": "Comunidad enfocada en videojuegos, cultura geek, tecnología, entretenimiento y conversación entre fanáticos.",
            "audience": "adultos de 25 a 44 años, jugadores casuales y hardcore, fans de Nintendo, Xbox, PlayStation, PC Gaming, anime, cine, series, tecnología y cultura geek en Puerto Rico y Latinoamérica",
            "tone": ["cercano", "conversacional", "entusiasta", "informativo", "comunitario", "gamer", "positivo", "fácil de comentar", "español natural"],
            "avoid_tone": ["corporativo", "frío", "demasiado técnico", "arrogante", "hostil", "ofensivo"],
            "default_hashtags": ["#elgamercave", "#gaming", "#videojuegos", "#gamers", "#geekculture", "#puertorico", "#gamingpr"],
            "content_priority": [
                "breaking news verificadas",
                "noticias interesantes de gaming",
                "debates de comunidad",
                "nostalgia gamer",
                "tecnología gaming",
                "desarrollo de videojuegos",
                "anime",
                "juegos indie",
                "industria",
                "curiosidades",
            ],
            "main_topics": [
                "breaking news verificadas",
                "noticias interesantes de gaming",
                "debates de comunidad",
                "nostalgia gamer",
                "tecnología gaming",
                "desarrollo de videojuegos",
                "anime",
                "juegos indie",
                "industria",
                "curiosidades",
                "noticias de videojuegos",
                "lanzamientos",
                "rumores claramente identificados",
                "actualizaciones",
                "DLC",
                "eventos",
                "reviews",
                "rankings",
                "opiniones",
                "anime",
                "manga",
                "cine",
                "series",
                "coleccionismo",
                "cosplay",
                "hardware",
                "consolas",
                "accesorios",
                "servicios digitales",
                "innovación relacionada al gaming",
                "PC gaming",
                "VR y AR",
                "mods",
                "esports",
                "entrevistas",
                "developer blogs",
                "concept art",
                "historias de desarrolladores",
            ],
            "source_priority": [
                "fuente del usuario si existe",
                "fuentes oficiales",
                "Steam",
                "Nintendo",
                "PlayStation Blog",
                "Xbox Wire",
                "Valve",
                "Epic Games",
                "Crunchyroll",
                "Bandai Namco",
                "Ubisoft",
                "Capcom",
                "Riot",
                "Blizzard",
                "web oficial",
                "blog oficial",
                "red social oficial",
                "IGN",
                "GameSpot",
                "Gematsu",
                "VGC",
                "Eurogamer",
                "PC Gamer",
                "The Verge",
                "GamesRadar",
            ],
            "rules": [
                "el objetivo no es solo publicar; el objetivo es crear contenido que la comunidad quiera comentar, compartir, guardar y leer",
                "maximizar comentarios, compartidos, likes, guardados, tiempo de lectura y discusión sana",
                "priorizar contenido por potencial de engagement: breaking news, noticias interesantes, debate, nostalgia, tecnología, desarrollo, anime, indies, industria y curiosidades",
                "no publicar solo noticias todo el día; alternar noticias, discusión, tecnología, anime, opinión, industria, indie, curiosidad y retro",
                "buscar temas en varias categorías: gaming, anime, manga, películas, series, tecnología, IA, desarrollo, Unreal Engine, Unity, Godot, Steam, PlayStation, Nintendo, Xbox, PC gaming, VR, AR, indies, mods, hardware, esports, cosplay, coleccionismo, industria, arte, música, entrevistas y blogs de desarrolladores",
                "usar primero fuentes oficiales como Steam, Nintendo, PlayStation Blog, Xbox Wire, Valve, Epic Games, Crunchyroll, Bandai Namco, Ubisoft, Capcom, Riot, Blizzard, web oficial, blog oficial o redes oficiales",
                "usar medios confiables como IGN, GameSpot, Gematsu, VGC, Eurogamer, PC Gamer, The Verge o GamesRadar solo cuando no haya fuente oficial o para contraste",
                "si el usuario provee fuente, link, imagen o captura, esa fuente gana sobre todo lo demás",
                "no inventar datos, fechas, anuncios, juegos, anime, precios, estadísticas ni fuentes",
                "si falta información, decir que falta; no completar con suposiciones",
                "verificar noticias actuales con fuentes confiables",
                "si es rumor, aclararlo claramente",
                "evitar títulos engañosos",
                "mantener objetividad en la parte informativa",
                "priorizar comunidad sobre controversia",
                "mantener respeto hacia todas las plataformas y jugadores",
                "informar antes que exagerar",
                "si ya se publicó recientemente sobre la misma noticia, anime, juego, franquicia, desarrollador o discusión, buscar otro tema salvo que exista información completamente nueva",
                "evaluar cada tema por relevancia, originalidad, potencial de comentarios, potencial de compartidos, potencial de guardados, calidad visual, variedad y frescura",
                "si un tema no tiene suficiente valor o verificación, no inventar; convertirlo en opinión, nostalgia o debate claramente identificado",
                "escribir los posts en español natural; solo dejar en inglés nombres oficiales de juegos, compañías o productos",
                "no copiar resúmenes en inglés directo de las fuentes",
                "usar exactamente cinco hashtags en minúsculas y poner #elgamercave primero",
                "no usar la palabra carrusel dentro del post",
                "cerrar con una pregunta concreta que invite a comentar",
                "recordar que El Gamer Cave es una comunidad, no únicamente un medio de noticias",
                "el gancho, el cuerpo y la pregunta final deben estar alineados; si el gancho promete noticia actual, el cuerpo debe explicar el hecho actual",
                "si el cuerpo es nostálgico, el gancho debe sonar nostálgico y no como noticia actual",
                "eliminar notas internas como 'lo importante es aterrizarlo a la comunidad' antes de entregar el post",
                "si el usuario pide un ajuste específico, modificar solo ese elemento",
                "no agregar logos, iconos, fechas, precios, banners o texto extra si no se pidió",
            ],
            "post_structure": [
                "hook",
                "contexto",
                "3 a 5 puntos claros si hacen falta",
                "cierre breve",
                "pregunta para la comunidad",
                "exactamente cinco hashtags con #elgamercave primero",
            ],
            "title_rules": [
                "t?tulo de máximo seis palabras cuando sea posible",
                "que se entienda en menos de dos segundos",
                "priorizar legibilidad sobre impacto",
            ],
            "cover_rules": [
                "la portada no es el post completo; solo debe hacer que la gente abra el post",
                "portada con máximo t?tulo y subtítulo",
                "no incluir fechas, precios, estadísticas, párrafos largos, banners de noticia, logos, iconos o información extra si no se piden",
                "cada portada debe representar visualmente el tema principal y no usar fondo gen?rico",
                "dejar márgenes seguros para Instagram 1080x1350 y evitar palabras cortadas",
                "variar estilo visual según el tema: anime más colorido, tecnología más limpia, retro más vintage, horror más oscuro, indie más creativo e industria más minimal",
                "no cambiar logos, marcas ni personajes oficiales",
            ],
            "platform_rules": {
                "facebook": "textos más extensos para debate y comentarios",
                "instagram": "texto directo, enfoque visual fuerte y CTA claro",
                "tiktok": "gancho inmediato, mensaje r?pido y lenguaje din?mico",
                "whatsapp": "formato corto, resumido y fácil de leer",
            },
            "visual_rules": [
                "formato vertical 1080 x 1350 px",
                "usar logo oficial de forma consistente solo cuando aplique o se pida",
                "usar imágenes promocionales oficiales cuando están disponibles",
                "no alterar logos oficiales de compañías",
                "no cambiar el significado de artes promocionales",
                "priorizar legibilidad m?vil sobre impacto visual",
            ],
            **base,
        }
    elif active_brand == "Daviet Gaming":
        base = {
            "brand": "Daviet Gaming",
            "description": "Marca de contenido sobre videojuegos, tecnología, cultura gamer, anime, PC gaming y temas de comunidad.",
            "audience": "gamers de Puerto Rico y Latinoamérica que siguen noticias, opinión, cultura gaming, anime, PC gaming, hardware y tecnología",
            "tone": ["casual", "directo", "natural", "gamer", "con opinión", "claro", "fácil de entender", "con hype moderado", "español natural"],
            "avoid_tone": ["demasiado formal", "corporativo", "exagerado", "genérico", "frío"],
            "default_hashtags": ["#davietgaming", "#gaming", "#videojuegos", "#pcgaming", "#gamers", "#gamingcommunity", "#tecnologia", "#puertorico"],
            "main_topics": [
                "noticias actuales de videojuegos",
                "tecnología gaming",
                "PC gaming",
                "anime relacionado con gaming o hardware",
                "opinión sobre la industria",
                "debates gamer",
                "nostalgia gamer",
                "consolas",
                "hardware",
                "colaboraciones especiales",
                "tendencias de gaming y tecnología",
            ],
            "rules": [
                "no inventar información",
                "verificar noticias actuales antes de crear posts",
                "no decir que algo es oficial si no está confirmado",
                "si una noticia ya pasó hace días, darle un ángulo actualizado de forma natural",
                "no usar lenguaje demasiado formal",
                "no usar frases genéricas como el mundo gamer está emocionado si no hay contexto real",
                "no repetir la misma estructura siempre",
                "no usar la palabra carrusel dentro del post",
                "escribir en español natural; solo dejar en inglés nombres oficiales de juegos, compañías o productos",
                "hashtags siempre en minúscula",
            ],
            "post_structure": [
                "título corto y llamativo",
                "subtítulo corto",
                "texto principal del post",
                "opinión o ángulo de Daviet Gaming",
                "pregunta final para generar interacción",
                "hashtags en minúscula",
            ],
            "visual_rules": [
                "formato vertical 1080x1350 para Instagram",
                "paleta principal: negro profundo, dorado metalico, blanco y gris oscuro",
                "identidad visual con dragon negro metalico o silueta de dragon cuando aplique",
                "estetica gamer premium, futurista, elegante y agresiva sin verse saturada",
                "lineas geometricas, circulos tech, marcos finos y detalles dorados",
                "composicion limpia con mucho espacio negativo para texto",
                "usar sombras oscuras, brillos dorados sutiles y alto contraste",
                "fondos con espacio para texto",
                "no saturar con demasiados elementos",
                "no usar logos de compañías si no se pide",
                "no cambiar el logo de Daviet Gaming",
                "evitar diseños demasiado genéricos de AI",
            ],
            "platform_rules": {
                "facebook": "puede tener más contexto, opinión y debate",
                "instagram": "directo, visual, fácil de leer y con CTA claro",
                "tiktok": "gancho rápido y lenguaje dinámico",
            },
        }
    elif active_brand == "General":
        base = {
            **base,
            "brand": "Gamer Signal",
            "audience": "gamers de Puerto Rico y Latinoamérica",
            "tone": ["casual", "claro", "gamer", "nostálgico"],
            "default_hashtags": ["#gaming", "#nostalgia", "#geek", "#latam"]
        }

    return aplicar_contexto_nicho(base)


def get_prompt_library():
    return leer_json(PROMPT_LIBRARY_FILE, [])


def buscar_prompt(category=None, style=None):
    prompts = get_prompt_library()

    for prompt in prompts:
        if category and prompt.get("category") != category:
            continue
        if style and prompt.get("style") != style:
            continue
        return prompt.get("prompt", "")

    for prompt in prompts:
        if category and prompt.get("category") == category:
            return prompt.get("prompt", "")

    return ""


def extraer_numero(texto):
    for palabra in texto.replace("#", " ").split():
        if palabra.isdigit():
            return int(palabra)
    return None


def seleccionar_item_por_numero(numero):
    if not numero:
        return st.session_state.generated_items.get(st.session_state.last_item_id)
    return st.session_state.news_by_number.get(numero)


NUMEROS_EN_TEXTO = {
    "uno": 1,
    "una": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
}


def extraer_cantidad_posts(texto):
    if not any(p in texto for p in ["post", "posts", "publicación", "publicaciones", "caption", "captions"]):
        return 1

    for palabra in texto.replace("#", " ").split():
        if palabra.isdigit():
            return max(1, min(int(palabra), 8))

    for palabra, numero in NUMEROS_EN_TEXTO.items():
        if f" {palabra} " in f" {texto} ":
            return numero

    return 1


def es_pedido_de_noticia_numerada(texto):
    return any(
        frase in texto
        for frase in [
            "de la noticia",
            "noticia #",
            "noticia número",
            "noticia numero",
            "post de noticia",
            "post de la noticia",
        ]
    )


def categoria_de_item(item):
    texto = f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}".lower()
    angulo = item.get("content_angle", "")

    if angulo == "indie" or any(p in texto for p in SENALES_INDIE):
        return "indie"
    if angulo == "anime" or any(p in texto for p in ["anime", "manga", "crunchyroll", "animenewsnetwork"]):
        return "anime"
    if angulo in ["hardware", "technology"] or any(p in texto for p in ["openai", "nvidia", "rtx", "gpu", "ia", "ai"]):
        return "tecnologia"
    if angulo == "debate":
        return "debate"
    if angulo == "nostalgia":
        return "nostalgia"
    return "gaming"


def seleccionar_noticia_para_categoria(noticias, categoria, titulos_usados):
    for item in noticias:
        titulo = item.get("title", "")
        titulo_key = titulo.lower().strip()
        if not titulo or titulo_key in titulos_usados:
            continue
        if not noticia_verificada_para_publicar(item):
            continue
        if tema_repetido(titulo) or tema_muy_similar(titulo):
            continue
        categoria_item = categoria_de_item(item)
        if categoria_item == categoria or (categoria == "gaming" and categoria_item == "indie"):
            titulos_usados.add(titulo_key)
            return item

    return None


def crear_item_editorial_categoria(categoria, titulos_usados):
    if categoria == "indie":
        temas = [
            "indies con demos que están ganando conversación",
            "juegos independientes que vale la pena seguir",
            "propuestas indie con mecánicas diferentes",
            "joyas independientes que buscan espacio entre grandes lanzamientos",
        ]
        resumen = (
            "Tema editorial para descubrir juegos independientes con una propuesta clara. "
            "No debe presentarse como tendencia confirmada sin señales recientes o fuentes verificadas."
        )
        fuente = "Tema editorial de juegos indie"
        estilo = "indie"
    elif categoria == "nostalgia":
        temas = TEMAS_NOSTALGIA
        resumen = (
            "Tema nostálgico para conectar con recuerdos de infancia, consolas viejas, "
            "juegos físicos, multiplayer local y experiencias que muchos gamers de Puerto Rico y LatAm reconocen."
        )
        fuente = "Tema nostálgico del proyecto"
        estilo = "nostalgia"
    elif categoria == "debate":
        temas = TEMAS_COMUNIDAD
        resumen = (
            "Tema de debate de comunidad. No se presenta como noticia confirmada; sirve para provocar comentarios, "
            "opiniones y conversación gamer sin inventar datos."
        )
        fuente = "Tema de comunidad gamer"
        estilo = "debate"
    elif categoria == "anime":
        temas = TEMAS_ANIME
        resumen = (
            "Tema de anime pensado para conectar cultura otaku y gaming. Si se usa como noticia actual, "
            "conviene verificarlo con una fuente principal antes de publicarlo."
        )
        fuente = "Tema editorial de anime"
        estilo = "anime"
    elif categoria == "tecnologia":
        temas = ["IA en videojuegos", "hardware para PC gaming", "nuevas formas de jugar en la nube", "GPU y rendimiento para gamers"]
        resumen = (
            "Tema de tecnología explicado desde el punto de vista gamer, con lenguaje simple y enfocado en por qué importa."
        )
        fuente = "Tema editorial de tecnología"
        estilo = "technology"
    else:
        temas = [
            f"juegos de {ANIO_NOTICIAS}",
            "lanzamientos esperados",
            "servicios de suscripción gaming",
            "actualidad de consolas",
        ]
        resumen = (
            "Tema gamer general para convertir actualidad, opinión o cultura de videojuegos en un post claro y conversacional."
        )
        fuente = "Tema editorial gamer"
        estilo = "news"

    for tema in temas:
        if tema.lower() not in titulos_usados and not tema_repetido(tema) and not tema_muy_similar(tema):
            titulo = tema
            break
    else:
        titulo = temas[0]

    titulos_usados.add(titulo.lower())
    item = {
        "id": str(uuid.uuid4()),
        "title": titulo,
        "summary": resumen,
        "source": fuente,
        "link": "",
        "date": str(HOY),
        "source_official": False,
        "source_trusted": False,
        "content_angle": estilo,
        "nostalgia_angle": detectar_angulo_nostalgia({"title": titulo, "summary": resumen}),
        "confidence_level": "editorial",
        "verification_count": 0,
        "verification_sources": [],
        "verification_level": "idea editorial / no es noticia confirmada",
    }
    st.session_state.generated_items[item["id"]] = item
    st.session_state.last_item_id = item["id"]
    return item


def categorias_para_posts(cantidad, texto):
    base = ["gaming", "tecnologia", "nostalgia", "anime", "debate"]
    if "anime" in texto:
        base = ["anime", "gaming", "nostalgia", "debate", "tecnologia"]
    elif "debate" in texto:
        base = ["debate", "gaming", "anime", "nostalgia", "tecnologia"]
    elif "nostalgia" in texto or "retro" in texto:
        base = ["nostalgia", "gaming", "anime", "debate", "tecnologia"]

    categorias = []
    while len(categorias) < cantidad:
        categorias.extend(base)
    return categorias[:cantidad]


def crear_varios_posts(cantidad, pregunta):
    cantidad = max(2, min(cantidad, 8))
    texto = pregunta.lower()
    noticias = filtrar_noticias_verificadas(buscar_noticias())
    titulos_usados = set()
    posts = []
    items_generados = []
    st.session_state.news_by_number = {}

    etiquetas = {
        "gaming": "gaming/noticia",
        "indie": "indie/en movimiento",
        "tecnologia": "tecnología",
        "nostalgia": "nostalgia",
        "anime": "anime",
        "debate": "debate",
    }
    estilos = {
        "gaming": "noticia",
        "indie": "noticia",
        "tecnologia": "noticia",
        "nostalgia": "nostalgia",
        "anime": "noticia",
        "debate": "debate",
    }

    for indice, categoria in enumerate(categorias_para_posts(cantidad, texto), start=1):
        item = seleccionar_noticia_para_categoria(noticias, categoria, titulos_usados)
        if not item:
            item = crear_item_editorial_categoria(categoria, titulos_usados)

        st.session_state.generated_items[item["id"]] = item
        st.session_state.news_by_number[indice] = item
        st.session_state.last_item_id = item["id"]
        items_generados.append(item)

        estilo_post = estilos.get(categoria, "noticia")
        if not item.get("source_official") and not item.get("verification_count", 0) >= 2 and categoria in ["gaming", "indie", "tecnologia", "anime"]:
            estilo_post = "debate" if categoria == "anime" else "emocional"

        post = generate_social_post(item, estilo_post)
        etiqueta = etiquetas.get(categoria, categoria)
        if not noticia_verificada_para_publicar(item) and categoria in ["gaming", "indie", "tecnologia", "anime"]:
            etiqueta = f"{categoria}/editorial"

        posts.append(f"PUBLICACIÓN {indice} - {reparar_texto_roto(etiqueta.upper())}\n\n{post}")

    respuesta = "\n\n---\n\n".join(posts)
    respuesta = reparar_texto_roto(limpiar_texto_publicable_final(respuesta))
    st.session_state.last_post_text = respuesta
    st.session_state.last_post_title = f"{cantidad}_posts_gamer_signal"
    st.session_state.last_post_items = items_generados
    return respuesta


def guardar_post_aprobado(post_text, nombre_base="post_gamer"):
    APPROVED_POSTS_DIR.mkdir(exist_ok=True)
    safe_name = "".join(c if c.isalnum() else "_" for c in nombre_base.lower())[:40]
    archivo = APPROVED_POSTS_DIR / f"{ahora_en_puerto_rico().strftime('%Y%m%d_%H%M%S')}_{safe_name}.txt"
    archivo.write_text(post_text, encoding="utf-8")
    return archivo


def crear_calendario_contenido(marca=None):
    marca = marca or st.session_state.get("active_brand", "Gamer Cave")
    if marca == "General":
        st.session_state.pending_calendar_request = True
        return "¿Para cuál marca quieres el calendario: Gamer Cave o Daviet Gaming?"

    if marca == "Daviet Gaming":
        return """
### Calendario semanal de Daviet Gaming

**Lunes:** noticia reciente de gaming, PC o tecnología explicada de forma sencilla.

**Martes:** hardware, accesorios, setup o una función útil para gamers.

**Miércoles:** anime, cultura geek o recomendación relacionada con gaming.

**Jueves:** nostalgia, opinión personal o experiencia gamer.

**Viernes:** noticia hot convertida en una pregunta para conversación.

**Sábado:** recomendación, comparación o tema para compartir con la comunidad.

**Domingo:** resumen ligero, recuerdo gamer o adelanto de la próxima semana.
"""

    return """
### Calendario semanal de El Gamer Cave

**Lunes:** noticia oficial de gaming o tecnología.

**Martes:** nostalgia gamer: consolas viejas, juegos físicos, Game Boy, GameCube o Pokémon.

**Miércoles:** debate de comunidad: físico vs digital, online vs local, remakes vs originales.

**Jueves:** post emocional: recuerdos de infancia, jugar con primos, controles prestados o memory cards.

**Viernes:** pregunta rápida para comentarios.

**Sábado:** recomendación o comparación gamer.

**Domingo:** post ligero de recuerdos, ranking o “¿te acuerdas de...?”.
"""


def es_modo_dueno():
    try:
        owner = st.query_params.get("owner", "")
    except Exception:
        try:
            owner = st.experimental_get_query_params().get("owner", [""])[0]
        except Exception:
            owner = ""
    return str(owner).strip().lower() in ["daviet", "admin", "owner", "1", "true"]


def marcas_visibles():
    return ["Gamer Cave", "Daviet Gaming"] if es_modo_dueno() else ["Gamer Cave"]


def marca_permitida(marca):
    if marca in marcas_visibles():
        return marca
    return "Gamer Cave"


def registrar_acceso_simple():
    if st.session_state.get("access_logged"):
        return

    tipo_link = "dueno" if es_modo_dueno() else "publico"
    ahora_pr = ahora_en_puerto_rico()
    log = leer_json(ACCESS_LOG_FILE, [])
    log.append({
        "tipo": tipo_link,
        "fecha": ahora_pr.strftime("%Y-%m-%d"),
        "hora": ahora_pr.strftime("%I:%M:%S %p"),
        "timestamp": ahora_pr.isoformat(),
    })
    guardar_json(ACCESS_LOG_FILE, log[-300:])
    st.session_state.access_logged = True


def render_access_log_simple():
    if not es_modo_dueno():
        return

    accesos = leer_json(ACCESS_LOG_FILE, [])
    st.divider()
    st.subheader("Accesos al link")
    if not accesos:
        st.write("Todavia no hay accesos registrados.")
        return

    hoy = ahora_en_puerto_rico().strftime("%Y-%m-%d")
    publicos_hoy = sum(1 for item in accesos if item.get("tipo") == "publico" and item.get("fecha") == hoy)
    dueno_hoy = sum(1 for item in accesos if item.get("tipo") == "dueno" and item.get("fecha") == hoy)
    total_publicos = sum(1 for item in accesos if item.get("tipo") == "publico")
    total_dueno = sum(1 for item in accesos if item.get("tipo") == "dueno")

    st.write(f"Hoy: publico {publicos_hoy} / dueno {dueno_hoy}")
    st.write(f"Total guardado: publico {total_publicos} / dueno {total_dueno}")

    for item in list(reversed(accesos))[:12]:
        tipo = "Link de dueno" if item.get("tipo") == "dueno" else "Link publico"
        st.write(f"- {tipo}: {item.get('fecha', '')} {item.get('hora', '')}")


def render_dashboard():
    marcas = marcas_visibles()
    marca_actual = st.session_state.get("active_brand", "Gamer Cave")
    if marca_actual == "General" or marca_actual not in marcas:
        marca_actual = "Gamer Cave"
        st.session_state.active_brand = marca_actual

    left, center, right = st.columns([0.75, 2.5, 0.75])
    with center:
        st.markdown('<div class="signal-brand-title">Marca activa</div>', unsafe_allow_html=True)
        cols = st.columns(len(marcas))
        for col, marca in zip(cols, marcas):
            with col:
                activo = marca_actual == marca
                render_brand_logo_card(marca, activo)
                if st.button(
                    "Activa" if activo else "Usar",
                    key=f"brand_button_{marca.lower().replace(' ', '_')}",
                    type="primary" if activo else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.active_brand = marca
                    st.rerun()


def image_data_url(image_path):
    if not image_path or not image_path.exists():
        return ""
    mime = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def logo_data_url(marca):
    return image_data_url(BRAND_LOGOS.get(marca))


def assistant_mascot_path(marca=None):
    marca = marca or st.session_state.get("active_brand", "Gamer Cave")
    if marca == "General":
        marca = "Gamer Cave"
    path = ASSISTANT_MASCOTS.get(marca) or ASSISTANT_MASCOTS.get("Gamer Cave")
    return path if path and path.exists() else None


def assistant_mascot_avatar(marca=None):
    path = assistant_mascot_path(marca)
    return str(path) if path else None


def assistant_mascot_data_url(marca=None):
    path = assistant_mascot_path(marca)
    return image_data_url(path) if path else ""


def render_brand_logo_card(marca, activo):
    data_url = logo_data_url(marca)
    safe_name = html_escape(marca)
    active_class = " active" if activo else ""
    img_html = f'<img src="{data_url}" alt="{safe_name} logo">' if data_url else ""
    st.markdown(
        f"""
        <div class="brand-logo-card{active_class}">
            {img_html}
            <div class="brand-logo-name">{safe_name}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def set_quick_prompt(prompt):
    st.session_state.quick_prompt = prompt


def render_quick_actions():
    st.markdown('<div class="signal-actions-space quick-actions-row"></div>', unsafe_allow_html=True)
    left, center, right = st.columns([0.4, 3.2, 0.4])
    with center:
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.button("Noticias", use_container_width=True, on_click=set_quick_prompt, args=("noticias oficiales de gaming",))
        with col2:
            st.button("Nostalgia", use_container_width=True, on_click=set_quick_prompt, args=("nostalgia gamer",))
        with col3:
            st.button("Post hot", use_container_width=True, on_click=set_quick_prompt, args=("hazme un post hot",))
        with col4:
            st.button("5 posts", use_container_width=True, on_click=set_quick_prompt, args=("créame 5 posts hot",))
        with col5:
            st.button("Debate", use_container_width=True, on_click=set_quick_prompt, args=("debate gamer",))
        with col6:
            st.button("Calendario", use_container_width=True, on_click=set_quick_prompt, args=("calendario semanal",))


def inject_auto_hide_controls():
    components_html(
        """
        <script>
        (function () {
            const parentWindow = window.parent;
            const doc = parentWindow.document;

            function findBar() {
                return doc.querySelector(".st-key-signal_control_bar");
            }

            function currentScrollY() {
                return parentWindow.scrollY
                    || doc.documentElement.scrollTop
                    || doc.body.scrollTop
                    || 0;
            }

            function setup() {
                const bar = findBar();
                if (!bar || bar.dataset.gamerSignalReady === "1") return;

                bar.dataset.gamerSignalReady = "1";
                let lastY = currentScrollY();
                let locked = false;

                function update() {
                    const y = currentScrollY();
                    const goingDown = y > lastY + 8;
                    const goingUp = y < lastY - 8;

                    if (y < 180 || goingUp) {
                        bar.classList.remove("signal-nav-hidden");
                    } else if (goingDown) {
                        bar.classList.add("signal-nav-hidden");
                    }

                    lastY = y;
                    locked = false;
                }

                function onScroll() {
                    if (locked) return;
                    locked = true;
                    setTimeout(update, 40);
                }

                parentWindow.addEventListener("scroll", onScroll, { passive: true });
                doc.addEventListener("scroll", onScroll, { passive: true });
            }

            setup();
            setTimeout(setup, 300);
            setTimeout(setup, 900);
        })();
        </script>
        """,
        height=0,
    )


def render_control_bar():
    try:
        control_bar = st.container(key="signal_control_bar")
    except TypeError:
        control_bar = st.container()

    with control_bar:
        render_dashboard()
        render_quick_actions()

    inject_auto_hide_controls()


def angulo_para_bucket(bucket):
    angulos = {
        "noticia_actual": "Convertirlo en noticia clara: qué pasó, por qué importa y pregunta final.",
        "debate": "Usarlo para abrir conversación con dos lados claros y sin imponer conclusión.",
        "nostalgia": "Conectarlo con recuerdos gamer, consolas viejas, juegos físicos y comunidad.",
        "tecnologia": "Explicarlo desde cómo afecta la experiencia gamer, PC, hardware o servicios.",
        "anime": "Cruzar anime y cultura geek con gaming, hype, fandom o adaptación.",
        "indie": "Presentarlo como descubrimiento: qué lo hace diferente y por qué vale mirarlo.",
    }
    return angulos.get(bucket, "Convertirlo en post simple, útil y fácil de comentar.")



def render_news_cards():
    news = st.session_state.get("news_by_number", {})
    if not news:
        return

    st.markdown("#### Noticias recientes")
    st.markdown('<div class="news-grid">', unsafe_allow_html=True)
    for numero, item in news.items():
        title = html_escape(item.get("title", "Sin título"))
        source = html_escape(item.get("source", ""))
        date_text = html_escape(item.get("date", ""))
        confidence = html_escape(item.get("confidence_level", ""))
        angle = html_escape(item.get("content_angle", ""))
        link = html_escape(item.get("link", ""), quote=True)
        st.markdown(
            f"""
            <div class="news-card">
                <div class="badge-row">
                    <span class="signal-badge">noticia {numero}</span>
                    <span class="signal-badge good">{confidence}</span>
                    <span class="signal-badge">{angle}</span>
                    <span class="signal-badge">{date_text}</span>
                </div>
                <div class="news-card-title">{title}</div>
                <div>{source}</div>
                <div><a href="{link}" target="_blank">Abrir fuente</a></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def nombre_archivo_post(nombre_base="post_gamer"):
    safe_name = "".join(c if c.isalnum() else "_" for c in nombre_base.lower())[:40]
    if not safe_name:
        safe_name = "post_gamer"
    return f"{ahora_en_puerto_rico().strftime('%Y%m%d_%H%M%S')}_{safe_name}.txt"


def render_post_card(post):
    post_json = json.dumps(post).replace("</", "<\\/")
    post_html = html_escape(post).replace("\n", "<br>")
    lineas_estimadas = 0
    for linea in post.splitlines() or [""]:
        lineas_estimadas += max(1, (len(linea) + 78) // 79)
    height = max(190, min(900, 98 + lineas_estimadas * 28 + post.count("\n\n") * 8))
    button_id = f"copyPostBtn_{uuid.uuid4().hex}"
    components_html(
        f"""
        <div style="
            background: #2b2b2c;
            border-radius: 22px;
            padding: 14px 20px 16px;
            color: #f8fafc;
            font-family: Arial, sans-serif;
            line-height: 1.52;
            box-sizing: border-box;
        ">
            <div style="display:flex; justify-content:flex-end; align-items:center; margin-bottom:6px;">
                <button id="{button_id}" title="Copiar post" aria-label="Copiar post" style="
                    width: 32px;
                    height: 32px;
                    border-radius: 8px;
                    border: 0;
                    background: transparent;
                    color: #f8fafc;
                    font-size: 20px;
                    cursor: pointer;
                ">⧉</button>
            </div>
            <div style="font-size:16px; white-space:normal;">{post_html}</div>
            <div id="{button_id}_status" style="
                min-height: 14px;
                margin-top: 6px;
                font-size: 12px;
                color: #a7f3d0;
            "></div>
        </div>
        <script>
        const btn = document.getElementById("{button_id}");
        const status = document.getElementById("{button_id}_status");
        const postText = {post_json};
        async function copyTextToClipboard(text) {{
            if (window.navigator && window.navigator.clipboard && window.isSecureContext) {{
                await window.navigator.clipboard.writeText(text);
                return true;
            }}
            const area = document.createElement("textarea");
            area.value = text;
            area.setAttribute("readonly", "");
            area.style.position = "fixed";
            area.style.top = "0";
            area.style.left = "0";
            area.style.opacity = "0";
            document.body.appendChild(area);
            area.focus();
            area.select();
            area.setSelectionRange(0, area.value.length);
            const ok = document.execCommand("copy");
            document.body.removeChild(area);
            if (!ok) {{
                throw new Error("copy command failed");
            }}
            return true;
        }}
        btn.addEventListener("click", async () => {{
            try {{
                await copyTextToClipboard(postText);
                btn.innerText = "✓";
                status.innerText = "Copiado";
            }} catch (error) {{
                btn.innerText = "!";
                status.innerText = "No se pudo copiar. Abre las opciones y usa Descargar.";
            }}
            setTimeout(() => {{
                btn.innerText = "⧉";
                status.innerText = "";
            }}, 1800);
        }});
        </script>
        """,
        height=height,
    )


def dividir_posts_generados(post):
    partes = [parte.strip() for parte in post.split("\n\n---\n\n") if parte.strip()]
    if len(partes) > 1 and all(parte.startswith("PUBLICACIÓN") for parte in partes):
        return partes
    return [post]


def render_post_response(post):
    partes = dividir_posts_generados(post)
    for index, parte in enumerate(partes, start=1):
        contenido = parte
        etiqueta = f"Post {index}"
        if parte.startswith("PUBLICACIÓN") and "\n\n" in parte:
            etiqueta, contenido = parte.split("\n\n", 1)
            etiqueta = etiqueta.title()
        if len(partes) > 1:
            st.markdown(f"#### {etiqueta}")
        render_post_card(contenido.strip())


def feedback_rapido(texto_feedback):
    item_id = st.session_state.get("last_item_id")
    return save_feedback(item_id, "post/topic", "correction", texto_feedback)


def render_last_post_box(key_prefix="last_post"):
    post = st.session_state.get("last_post_text", "")
    if not post:
        return

    with st.expander("Guardar o descargar", expanded=False):
        col_download, col_save = st.columns(2)
        with col_download:
            st.download_button(
                "Descargar",
                post,
                file_name=nombre_archivo_post(st.session_state.get("last_post_title", "post_gamer")),
                mime="text/plain",
                use_container_width=True,
                key=f"{key_prefix}_download",
            )
        with col_save:
            if st.button("Guardar aprobado", use_container_width=True, key=f"{key_prefix}_save"):
                archivo = guardar_post_aprobado(post, st.session_state.get("last_post_title", "post_gamer"))
                save_feedback(st.session_state.get("last_item_id"), "post/topic", "approved", "post aprobado desde botón")
                st.success(f"Post guardado: {archivo}")


def get_user_preferences():
    return leer_json(PREFS_FILE, [])


def update_preference(key, value, weight=1, source_feedback="manual"):
    prefs = get_user_preferences()
    for pref in prefs:
        if pref["key"] == key and str(pref["value"]).lower() == str(value).lower():
            pref["weight"] = int(weight)
            pref["last_updated"] = ahora()
            pref["source_feedback"] = source_feedback
            guardar_json(PREFS_FILE, prefs)
            return

    prefs.append({
        "key": key,
        "value": value,
        "weight": int(weight),
        "last_updated": ahora(),
        "source_feedback": source_feedback,
    })
    guardar_json(PREFS_FILE, prefs)


def ajustar_preferencia(key, value, cambio, source_feedback):
    prefs = get_user_preferences()
    for pref in prefs:
        if pref["key"] == key and str(pref["value"]).lower() == str(value).lower():
            pref["weight"] = max(-10, min(10, int(pref["weight"]) + cambio))
            pref["last_updated"] = ahora()
            pref["source_feedback"] = source_feedback
            guardar_json(PREFS_FILE, prefs)
            return

    prefs.append({
        "key": key,
        "value": value,
        "weight": max(-10, min(10, cambio)),
        "last_updated": ahora(),
        "source_feedback": source_feedback,
    })
    guardar_json(PREFS_FILE, prefs)


def borrar_preferencia(key, value):
    prefs = [
        pref for pref in get_user_preferences()
        if not (pref["key"] == key and str(pref["value"]).lower() == str(value).lower())
    ]
    guardar_json(PREFS_FILE, prefs)


def borrar_memoria():
    guardar_json(PREFS_FILE, [])
    guardar_json(FEEDBACK_FILE, [])
    guardar_json(USED_FILE, [])


def entrada_usada_aplica_a_marca(item, marca=None):
    marca = marca or st.session_state.get("active_brand", "Gamer Cave")
    marcas = item.get("brands")
    if not marcas:
        return True
    if not isinstance(marcas, list):
        marcas = [str(marcas)]
    if marca == "General":
        return True
    return marca in marcas


def tema_repetido(topic, marca=None):
    topic = topic.lower().strip()
    return any(
        item.get("topic", "").lower().strip() == topic and entrada_usada_aplica_a_marca(item, marca)
        for item in leer_json(USED_FILE, [])
    )


def palabras_clave_tema(texto):
    texto = texto.lower()
    reemplazos = [":", "-", "_", "/", "\\", "|", ",", ".", "?", "!", "(", ")", "[", "]"]
    for caracter in reemplazos:
        texto = texto.replace(caracter, " ")

    ignorar = {
        "the", "and", "para", "con", "por", "una", "uno", "unos", "unas", "los", "las",
        "del", "que", "this", "that", "about", "official", "podcast", "episode",
        "news", "blog", "game", "games", "gaming", "nuevo", "nueva", "more", "plus"
    }
    return {p for p in texto.split() if len(p) > 3 and p not in ignorar}


def texto_clave_noticia(item):
    return f"{item.get('title', '')} {item.get('summary', '')}"


def similitud_texto(a, b):
    palabras_a = palabras_clave_tema(a)
    palabras_b = palabras_clave_tema(b)
    if not palabras_a or not palabras_b:
        return 0
    overlap = len(palabras_a & palabras_b)
    base = min(len(palabras_a), len(palabras_b))
    return overlap / base if base else 0


def fuentes_unicas(items):
    fuentes = []
    for item in items:
        fuente = item.get("source", "")
        if fuente and fuente not in fuentes:
            fuentes.append(fuente)
    return fuentes


def agregar_verificacion_cruzada(noticias):
    for item in noticias:
        similares = [item]
        texto_item = texto_clave_noticia(item)
        fecha_item = item.get("date", "")

        for otro in noticias:
            if otro is item:
                continue
            if otro.get("source") == item.get("source"):
                continue
            if fecha_item and otro.get("date") and abs((date.fromisoformat(fecha_item) - date.fromisoformat(otro["date"])).days) > 7:
                continue
            if similitud_texto(texto_item, texto_clave_noticia(otro)) >= 0.45:
                similares.append(otro)

        fuentes = fuentes_unicas(similares)
        item["verification_count"] = len(fuentes)
        item["verification_sources"] = fuentes[:3]

        if len(fuentes) >= 3:
            item["verification_level"] = "verificada por 3 fuentes"
        elif len(fuentes) >= 2:
            item["verification_level"] = "verificada por 2 fuentes"
        elif item.get("source_official"):
            item["verification_level"] = "fuente oficial verificada"
        elif item.get("source_trusted"):
            item["verification_level"] = "fuente confiable no oficial"
        else:
            item["verification_level"] = "sin corroborar"

    return noticias


def noticia_verificada_para_publicar(item):
    if not item:
        return False
    fuente = str(item.get("source", "")).lower()
    confianza = str(item.get("confidence_level", "")).lower()

    if "wikipedia" in fuente:
        return False
    if fuente.startswith("tema "):
        return False
    if confianza in ["editorial", "manual", "support", "low"]:
        return False
    if not item.get("date"):
        return False

    if item.get("verification_count", 1) >= 2:
        return True
    if item.get("source_official"):
        return True
    return False


def filtrar_noticias_verificadas(noticias):
    return [item for item in noticias if noticia_verificada_para_publicar(item)]


def filtrar_items_para_monitor(noticias):
    items = []
    for item in noticias:
        if noticia_verificada_para_publicar(item):
            items.append(item)
            continue
        if item.get("is_community_signal") and item.get("content_angle") in ["nostalgia", "debate", "anime", "indie"]:
            items.append(item)
    return items


def item_es_contexto_editorial(item):
    if not item:
        return True
    fuente = str(item.get("source", "")).lower()
    confianza = str(item.get("confidence_level", "")).lower()
    if "wikipedia" in fuente:
        return True
    if fuente.startswith("tema "):
        return True
    if confianza in ["editorial", "manual", "support"]:
        return True
    return False


def estilo_seguro_para_item(item, estilo):
    estilo = estilo or "all"
    if estilo == "all":
        angulo = item.get("content_angle", "news") if item else "news"
        estilo = "nostalgia" if angulo == "nostalgia" else "news"

    if estilo in ["news", "noticia"] and not noticia_verificada_para_publicar(item):
        angulo = item.get("content_angle", "") if item else ""
        if angulo == "nostalgia":
            return "nostalgia"
        return "debate"

    return estilo


def tema_muy_similar(topic, threshold=0.45, marca=None):
    usados = leer_json(USED_FILE, [])
    palabras_topic = palabras_clave_tema(topic)
    if not palabras_topic:
        return False

    for item in usados:
        if not entrada_usada_aplica_a_marca(item, marca):
            continue
        palabras_usadas = palabras_clave_tema(item.get("topic", ""))
        if not palabras_usadas:
            continue
        overlap = len(palabras_topic & palabras_usadas)
        base = min(len(palabras_topic), len(palabras_usadas))
        if base and overlap / base >= threshold:
            return True

    return False


def marcar_tema_usado(topic, category="general", notes="used"):
    usados = leer_json(USED_FILE, [])
    if tema_repetido(topic):
        return
    usados.append({
        "topic": topic,
        "category": category,
        "brands": [st.session_state.get("active_brand", "Gamer Cave")],
        "used_date": str(HOY),
        "platform": "instagram/facebook",
        "notes": notes,
    })
    guardar_json(USED_FILE, usados)


def marcar_publicacion_usada(topic, category="post", marcas=None, notes="published by user"):
    marcas = marcas or [st.session_state.get("active_brand", "Gamer Cave")]
    usados = leer_json(USED_FILE, [])
    topic_key = topic.lower().strip()

    for item in usados:
        if item.get("topic", "").lower().strip() == topic_key:
            marcas_guardadas = item.get("brands", [])
            if not isinstance(marcas_guardadas, list):
                marcas_guardadas = [str(marcas_guardadas)]
            item["brands"] = list(dict.fromkeys(marcas_guardadas + marcas))
            item["category"] = category
            item["used_date"] = str(HOY)
            item["platform"] = "instagram/facebook"
            item["notes"] = notes
            guardar_json(USED_FILE, usados)
            return

    usados.append({
        "topic": topic,
        "category": category,
        "brands": list(dict.fromkeys(marcas)),
        "used_date": str(HOY),
        "platform": "instagram/facebook",
        "notes": notes,
    })
    guardar_json(USED_FILE, usados)


def detectar_temas(texto):
    texto = texto.lower()
    palabras = [
        "nintendo", "playstation", "xbox", "gamecube", "game boy",
        "ps1", "ps2", "xbox 360", "wii", "pokémon", "pokemon",
        "mario", "zelda", "kirby", "sonic", "final fantasy",
        "kingdom hearts", "nvidia", "openai", "ia", "hardware",
        "pc gaming", "juegos físicos", "multiplayer local",
        "capcom", "resident evil", "monster hunter", "street fighter",
        "ea", "ubisoft", "riot", "league of legends", "valorant",
        "blizzard", "diablo", "overwatch", "warcraft", "epic games",
        "fortnite", "unreal engine", "unity", "anime", "manga",
        "crunchyroll", "myanimelist", "intel", "amd",
    ]
    return [p for p in palabras if p in texto]


def detectar_angulo_nostalgia(item):
    texto = f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}".lower()
    mapa = {
        "remake": "infancia gamer, juegos clásicos y nostalgia.",
        "remaster": "infancia gamer, juegos clásicos y nostalgia.",
        "anniversary": "aniversarios, recuerdos y etapas importantes de la comunidad.",
        "aniversario": "aniversarios, recuerdos y etapas importantes de la comunidad.",
        "retro": "consolas, juegos y experiencias de otras generaciones.",
        "classic collection": "colecciones de juegos clásicos y recuerdos de otras generaciones.",
        "colección clásica": "colecciones de juegos clásicos y recuerdos de otras generaciones.",
        "return of the classic": "regresos de juegos clásicos y recuerdos de la comunidad.",
        "regreso del clásico": "regresos de juegos clásicos y recuerdos de la comunidad.",
    }
    for palabra, angulo in mapa.items():
        if palabra in texto:
            return angulo
    return ""


def detectar_content_angle(item):
    texto = f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}".lower()
    if any(p in texto for p in SENALES_INDIE):
        return "indie"
    if any(p in texto for p in [
        "anime", "manga", "crunchyroll", "myanimelist", "anime news network",
        "anime corner", "shonen", "bleach", "dragon ball", "naruto", "one piece",
        "jujutsu", "demon slayer", "my hero academia", "chainsaw man",
    ]):
        return "anime"
    if any(p in texto for p in [
        "vs", "debate", "digital", "dlc", "game pass", "ps plus",
        "subscription", "suscripción", "battle pass", "microtransaction",
        "microtransacciones", "precio", "price", "physical", "físico", "fisico",
    ]):
        return "debate"
    if any(p in texto for p in [
        "hardware", "gpu", "rtx", "pc", "nvidia", "amd", "intel",
        "steam deck", "handheld", "asus rog", "msi", "processor", "cpu",
    ]):
        return "hardware"
    if (
        any(p in texto for p in [
            "openai", "inteligencia artificial", "artificial intelligence",
            "unreal engine", "unity engine", "developer tools", "generative ai",
        ])
        or re.search(r"\b(?:ai|ia)\b", texto)
    ):
        return "technology"
    if detectar_angulo_nostalgia(item):
        return "nostalgia"
    return "news"


def nivel_confianza(item):
    if item.get("source_official") and item.get("date"):
        return "high"
    if item.get("source_trusted") and item.get("date"):
        return "medium-high"
    if item.get("date"):
        return "medium"
    return "low"


def save_feedback(item_id, item_type, feedback_type, feedback_text):
    log = leer_json(FEEDBACK_FILE, [])
    item = st.session_state.generated_items.get(item_id, {})
    titulo = item.get("title") or item_id or st.session_state.get("last_post_title", "post sin título")
    fuente = item.get("source", "")
    categoria = item.get("content_angle", item_type)
    texto = feedback_text.lower()
    accion = "saved feedback"

    log.append({
        "id": str(uuid.uuid4()),
        "item_type": item_type,
        "item_id": item_id,
        "feedback_type": feedback_type,
        "feedback_text": feedback_text,
        "action_taken": accion,
        "created_at": ahora(),
    })
    guardar_json(FEEDBACK_FILE, log)

    if feedback_type == "approved":
        ajustar_preferencia("preferred_category", categoria, 2, "user approved item")
        if fuente:
            ajustar_preferencia("trusted_source", fuente, 2, "user approved source")
        for tema in detectar_temas(titulo):
            ajustar_preferencia("preferred_topic", tema, 2, "user approved theme")
        marcar_tema_usado(titulo, categoria, "approved by user")
        accion = "increased preference weights"
    elif feedback_type == "rejected":
        ajustar_preferencia("avoid_category", categoria, 2, "user rejected item")
        if fuente:
            ajustar_preferencia("avoid_source", fuente, 2, "user rejected source")
        for tema in detectar_temas(titulo):
            ajustar_preferencia("avoid_topic", tema, 2, "user rejected theme")
        marcar_tema_usado(titulo, categoria, "rejected by user")
        accion = "decreased recommendation priority"
    elif feedback_type == "correction":
        if "más corto" in texto or "mas corto" in texto:
            ajustar_preferencia("style_rule", "posts más cortos", 3, feedback_text)
        if "más nostalgia" in texto or "mas nostalgia" in texto:
            ajustar_preferencia("preferred_category", "nostalgia gaming", 3, feedback_text)
        if "más debate" in texto or "mas debate" in texto:
            ajustar_preferencia("preferred_category", "debate gamer", 3, feedback_text)
        if "no digas carrusel" in texto:
            ajustar_preferencia("banned_phrase", "carrusel", 10, feedback_text)
        if "no repetir" in texto:
            ajustar_preferencia("avoid_repeat", titulo, 5, feedback_text)
            marcar_tema_usado(titulo, categoria, "user requested no repeat")
        if "no inventes logos" in texto:
            ajustar_preferencia("permanent_rule", "no inventar logos", 10, feedback_text)
        accion = "updated style and rule preferences"

    if "eso ya pasó" in texto or "eso ya paso" in texto:
        marcar_tema_usado(titulo, categoria, "user said it already happened")
        ajustar_preferencia("used_or_old_topic", titulo, 5, feedback_text)
        accion = "marked topic as old or used"

    log = leer_json(FEEDBACK_FILE, [])
    if log:
        log[-1]["action_taken"] = accion
        guardar_json(FEEDBACK_FILE, log)

    return accion


def calcular_senales_editoriales(item):
    texto = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    puntos = 0
    razones = []

    try:
        fecha = date.fromisoformat(str(item.get("date", ""))[:10])
        antiguedad = max(0, (ahora_en_puerto_rico().date() - fecha).days)
        if antiguedad <= 1:
            puntos += 12
            razones.append("publicado en las últimas 24-48 horas")
        elif antiguedad <= 3:
            puntos += 8
            razones.append("noticia muy reciente")
        elif antiguedad <= 7:
            puntos += 4
            razones.append("noticia de esta semana")
    except (TypeError, ValueError):
        pass

    for nombre, palabras in SENALES_TENDENCIA.items():
        coincidencias = sum(1 for palabra in palabras if palabra in texto)
        if coincidencias:
            puntos += min(8, coincidencias * 3)
            razones.append(nombre)

    if any(palabra in texto for palabra in SENALES_INDIE):
        puntos += 5
        razones.append("juego indie o descubrimiento emergente")

    if item.get("source_official"):
        puntos += 4
        razones.append("fuente oficial")
    if item.get("verification_count", 0) >= 2:
        puntos += 6
        razones.append("confirmado por varias fuentes")

    item["trend_score"] = puntos
    item["trend_reasons"] = list(dict.fromkeys(razones))
    return puntos


def aplicar_preferencias(noticias):
    prefs = get_user_preferences()
    for item in noticias:
        score = 0
        texto = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        fuente = item.get("source", "").lower()
        if item.get("source_official"):
            score += 5
        elif item.get("source_trusted"):
            score += 3
        if item.get("date"):
            score += 4
        if item.get("confidence_level") == "high":
            score += 4
        if item.get("verification_count", 1) >= 3:
            score += 8
        elif item.get("verification_count", 1) >= 2:
            score += 5
        if item.get("nostalgia_angle"):
            score += 3
        if item.get("content_angle") == "debate":
            score += 2
        score += calcular_senales_editoriales(item)
        for palabra in PALABRAS_HOT_NICHO:
            if palabra in texto:
                score += 2
        if any(palabra in texto for palabra in ["precio", "suscripción", "subscription", "remake", "remaster", "digital", "físico", "fisico", "microtransacciones"]):
            score += 4
        if tema_repetido(item.get("title", "")):
            score -= 100
        if tema_muy_similar(item.get("title", "")):
            score -= 40

        for pref in prefs:
            key = pref.get("key", "")
            value = str(pref.get("value", "")).lower()
            weight = int(pref.get("weight", 0))
            if key in ["preferred_category", "preferred_topic"] and value in texto:
                score += weight
            if key == "trusted_source" and value == fuente:
                score += weight
            if key in ["avoid_category", "avoid_topic"] and value in texto:
                score -= abs(weight)
            if key == "avoid_source" and value == fuente:
                score -= abs(weight)
        item["ranking_score"] = score
    return sorted(noticias, key=lambda x: x["ranking_score"], reverse=True)


@st.cache_data(ttl=NEWS_CACHE_TTL_SECONDS, show_spinner=False)
def leer_feed(url):
    try:
        request = Request(url, headers={"User-Agent": "GamerSignal/1.0"})
        with urlopen(request, timeout=FEED_TIMEOUT_SECONDS) as response:
            data = response.read()
        feed = feedparser.parse(data)
    except Exception:
        return []

    entradas_limpias = []
    for entrada in feed.entries[:MAX_ENTRADAS_POR_FUENTE]:
        fecha = entrada.get("published_parsed") or entrada.get("updated_parsed")
        if not fecha:
            continue
        entradas_limpias.append({
            "title": entrada.get("title", "Sin título"),
            "summary": entrada.get("summary", ""),
            "link": entrada.get("link", ""),
            "year": fecha.tm_year,
            "month": fecha.tm_mon,
            "day": fecha.tm_mday,
        })
    return entradas_limpias


@st.cache_data(ttl=3600)
def buscar_wikipedia(tema):
    """Wikipedia se usa solo como apoyo historico, nunca para confirmar noticias."""
    tema = normalizar_tema_contexto(tema)
    alternativas = {
        "GameCube": ["GameCube", "Nintendo GameCube"],
        "Game Boy": ["Game Boy", "Game Boy Advance"],
        "Nintendo 64": ["Nintendo 64"],
        "PlayStation 2": ["PlayStation 2"],
        "Pokémon": ["Pokémon"],
        "The Legend of Zelda": ["The Legend of Zelda", "Zelda"],
    }.get(tema, [tema])

    for candidato in alternativas:
        tema_url = quote(candidato.strip().replace(" ", "_"))
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{tema_url}"
        try:
            request = Request(url, headers={"User-Agent": "GamerSignal/1.0"})
            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
            resumen = data.get("extract", "")
            if not resumen:
                continue
            return {
                "id": f"nostalgia-{uuid.uuid4()}",
                "title": data.get("title", candidato),
                "summary": resumen,
                "link": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "source": "Wikipedia en español (solo contexto histórico)",
                "date": None,
                "source_official": False,
                "content_angle": "nostalgia",
                "confidence_level": "support",
                "nostalgia_angle": "Apoyo histórico para crear contenido nostálgico; no confirma noticias actuales.",
            }
        except Exception:
            continue

    return None


def limpiar_tema_nostalgia(pregunta):
    texto = pregunta.lower()
    frases = [
        "nostalgia sobre", "nostalgia de", "retro sobre", "retro de",
        "háblame de", "hablame de", "dame información sobre",
        "dame informacion sobre", "información sobre", "informacion sobre",
    ]
    for frase in frases:
        texto = texto.replace(frase, "")
    quitar = ["nostalgia", "retro", "clásico", "clasico", "viejo", "antiguo", "sobre"]
    palabras = [p for p in texto.split() if p not in quitar]
    tema = " ".join(palabras).strip()
    nombres = {
        "playstation 2": "PlayStation 2",
        "ps2": "PlayStation 2",
        "playstation": "PlayStation",
        "ps1": "PlayStation",
        "nintendo 64": "Nintendo 64",
        "n64": "Nintendo 64",
        "game boy": "Game Boy",
        "gameboy": "Game Boy",
        "gamecube": "GameCube",
        "pokemon": "Pokémon",
        "pokémon": "Pokémon",
        "mario": "Mario",
        "kirby": "Kirby",
        "zelda": "The Legend of Zelda",
    }
    return nombres.get(tema, tema.title()) if tema else None


@st.cache_data(ttl=NEWS_CACHE_TTL_SECONDS, show_spinner=False)
def cargar_noticias_base():
    noticias = []
    for fuente, url in FUENTES.items():
        entradas = leer_feed(url)
        for noticia in entradas:
            fecha = date(
                noticia["year"],
                noticia["month"],
                noticia["day"],
            )
            if fecha.year != ANIO_NOTICIAS:
                continue
            if not (FECHA_INICIO <= fecha <= FECHA_FINAL):
                continue
            titulo = limpiar_html(noticia.get("title", "Sin título"))
            resumen = limpiar_html(noticia.get("summary", ""))
            link = noticia.get("link", "")
            item = {
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{fuente}|{link}|{titulo}")),
                "title": limpiar_html(noticia.get("title", "Sin título")),
                "summary": limpiar_html(noticia.get("summary", "")),
                "date": str(fecha),
                "source": fuente,
                "link": noticia.get("link", ""),
                "source_official": "oficial" in fuente.lower(),
                "source_trusted": True,
            }
            item["nostalgia_angle"] = detectar_angulo_nostalgia(item)
            item["content_angle"] = detectar_content_angle(item)
            item["confidence_level"] = nivel_confianza(item)
            noticias.append(item)
    noticias = agregar_verificacion_cruzada(noticias)
    return noticias


@st.cache_data(ttl=NEWS_CACHE_TTL_SECONDS, show_spinner=False)
def cargar_senales_comunidad():
    senales = []
    fecha_minima = FECHA_FINAL - timedelta(days=45)
    for fuente, url in FUENTES_COMUNIDAD.items():
        entradas = leer_feed(url)
        for entrada in entradas:
            fecha = date(entrada["year"], entrada["month"], entrada["day"])
            if fecha.year != ANIO_NOTICIAS or fecha < fecha_minima or fecha > FECHA_FINAL:
                continue

            titulo = limpiar_html(entrada.get("title", "Tema de comunidad"))
            resumen_original = limpiar_html(entrada.get("summary", ""))
            resumen = (
                "Señal de conversación detectada en comunidad. "
                "Usar con cautela como idea de nostalgia, debate o fandom; no presentarlo como noticia confirmada."
            )
            if resumen_original:
                resumen += " " + recortar_texto(resumen_original, 180)

            item = {
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{fuente}|{entrada.get('link', '')}|{titulo}")),
                "title": titulo,
                "summary": resumen,
                "date": str(fecha),
                "source": fuente,
                "link": entrada.get("link", ""),
                "source_official": False,
                "source_trusted": False,
                "is_community_signal": True,
                "confidence_level": "community_signal",
                "verification_count": 0,
                "verification_level": "señal de comunidad; no confirma noticia",
            }
            item["nostalgia_angle"] = detectar_angulo_nostalgia(item)
            item["content_angle"] = detectar_content_angle(item)
            if "nostalgia" in fuente.lower() or item["nostalgia_angle"]:
                item["content_angle"] = "nostalgia"
            elif "debate" in fuente.lower() or "truegaming" in fuente.lower():
                item["content_angle"] = "debate"
            elif "anime" in fuente.lower() or "manga" in fuente.lower():
                item["content_angle"] = "anime"
            senales.append(item)
    return senales


def buscar_noticias():
    noticias = [dict(item) for item in cargar_noticias_base()]
    noticias.extend(dict(item) for item in cargar_senales_comunidad())
    return aplicar_preferencias(noticias)


def monitor_item_key(item):
    base = item.get("link") or f"{item.get('source', '')}|{item.get('title', '')}|{item.get('date', '')}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, base))


def monitor_registrar_hallazgos(noticias):
    log = leer_json(MONITOR_FILE, [])
    conocidos = {entrada.get("id") for entrada in log}
    nuevos = []

    for item in filtrar_items_para_monitor(noticias):
        item_id = monitor_item_key(item)
        if item_id in conocidos:
            continue
        entrada = {
            "id": item_id,
            "title": item.get("title", "Sin titulo"),
            "summary": recortar_texto(limpiar_html(item.get("summary", "")), 240),
            "source": item.get("source", "fuente"),
            "date": item.get("date", ""),
            "link": item.get("link", ""),
            "content_angle": item.get("content_angle", "news"),
            "trend_score": item.get("trend_score", 0),
            "trend_reasons": item.get("trend_reasons", []),
            "verification_level": item.get("verification_level", "verificada"),
            "discovered_at": ahora(),
        }
        log.append(entrada)
        nuevos.append(entrada)
        st.session_state.generated_items[item.get("id", item_id)] = item
        if len(nuevos) >= 12:
            break

    log = sorted(log, key=lambda x: x.get("discovered_at", ""), reverse=True)[:120]
    guardar_json(MONITOR_FILE, log)
    st.session_state.monitor_last_run = ahora()
    st.session_state.monitor_new_count = len(nuevos)
    return nuevos


def monitor_revisar_fuentes(force=False):
    if force:
        try:
            leer_feed.clear()
            cargar_noticias_base.clear()
            cargar_senales_comunidad.clear()
        except Exception:
            try:
                st.cache_data.clear()
            except Exception:
                pass
    noticias = buscar_noticias()
    return monitor_registrar_hallazgos(noticias)


def monitor_bucket_item(item):
    angulo = item.get("content_angle") or detectar_content_angle(item)
    texto = f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}".lower()
    if angulo == "anime" or "anime" in texto or "manga" in texto or "crunchyroll" in texto:
        return "anime"
    if angulo in ["hardware", "technology"] or any(p in texto for p in ["nvidia", "rtx", "gpu", "hardware", "pc gaming", "steam deck", "unreal engine", "unity"]):
        return "tecnologia"
    if angulo == "indie" or any(p in texto for p in SENALES_INDIE):
        return "indie"
    if angulo == "nostalgia" or detectar_angulo_nostalgia(item):
        return "nostalgia"
    if angulo == "debate" or any(p in texto for p in ["precio", "suscripcion", "suscripción", "digital", "fisico", "físico", "game pass", "ps plus", "microtransacciones"]):
        return "debate"
    return "noticia_actual"


def monitor_brand_scores(item):
    texto = f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}".lower()
    bucket = monitor_bucket_item(item)
    scores = {"Gamer Cave": 1, "Daviet Gaming": 1}
    razones = {"Gamer Cave": [], "Daviet Gaming": []}

    if bucket in ["noticia_actual", "anime", "debate", "nostalgia", "indie"]:
        scores["Gamer Cave"] += 3
        razones["Gamer Cave"].append(f"encaja con {bucket}")
    if bucket in ["tecnologia", "indie", "noticia_actual"]:
        scores["Daviet Gaming"] += 3
        razones["Daviet Gaming"].append(f"encaja con {bucket}")
    if bucket in ["debate", "nostalgia"]:
        scores["Gamer Cave"] += 1
        razones["Gamer Cave"].append("sirve como tema de comunidad")

    if any(p in texto for p in ["nintendo", "playstation", "xbox", "anime", "manga", "remake", "remaster", "nostalgia"]):
        scores["Gamer Cave"] += 2
        razones["Gamer Cave"].append("alto potencial de comunidad PR/LatAm")
    if any(p in texto for p in ["pc", "steam", "nvidia", "amd", "intel", "gpu", "hardware", "setup", "unreal", "unity", "ai", "ia"]):
        scores["Daviet Gaming"] += 2
        razones["Daviet Gaming"].append("conecta con gaming/PC/tech")
    if item.get("trend_score", 0) >= 8:
        for marca in scores:
            scores[marca] += 1
            razones[marca].append("tiene señales hot")

    orden = sorted(scores, key=scores.get, reverse=True)
    return scores, razones, orden


def monitor_angulo_para_marca(item, marca):
    bucket = item.get("monitor_bucket") or monitor_bucket_item(item)
    titulo = titulo_publico_en_espanol(item.get("title", ""), "news")
    if marca == "Gamer Cave":
        if bucket == "nostalgia":
            return "Conectarlo con recuerdos de comunidad: juegos físicos, controles prestados, tardes con panas y debate sano."
        if bucket == "debate":
            return "Convertirlo en pregunta de comunidad con dos lados claros, sin imponer conclusión."
        if bucket == "anime":
            return "Cruzar anime y gaming: hype, adaptación, fandom y conversación geek."
        return "Explicar qué pasó, por qué importa y cerrar con una pregunta para la tribu geek."
    if marca == "Daviet Gaming":
        if bucket == "tecnologia":
            return "Explicarlo desde el valor real para gamers: rendimiento, precio, PC, setup o experiencia."
        if bucket == "anime":
            return "Darle un ángulo casual de cultura geek/anime con opinión corta y pregunta directa."
        if bucket == "indie":
            return "Presentarlo como descubrimiento gamer: qué lo hace diferente y por qué vale mirarlo."
        return "Dar contexto rápido, opinión natural y cerrar con una pregunta clara para comentarios."
    return f"Usarlo como tema general: {titulo}, explicado simple y con pregunta final."


def monitor_actualizar_memoria_marca(log):
    memoria = {
        "updated_at": ahora(),
        "brands": {
            "Gamer Cave": [],
            "Daviet Gaming": [],
        },
        "buckets": {
            "noticia_actual": [],
            "debate": [],
            "nostalgia": [],
            "anime": [],
            "tecnologia": [],
            "indie": [],
        },
    }
    for item in log:
        bucket = item.get("monitor_bucket") or monitor_bucket_item(item)
        item["monitor_bucket"] = bucket
        scores, razones, orden = monitor_brand_scores(item)
        item["brand_scores"] = scores
        item["recommended_brands"] = orden
        item["brand_reasons"] = razones
        resumen = {
            "id": item.get("id"),
            "title": item.get("title"),
            "source": item.get("source"),
            "date": item.get("date"),
            "bucket": bucket,
            "trend_score": item.get("trend_score", 0),
            "verification_level": item.get("verification_level", ""),
        }
        if bucket in memoria["buckets"] and len(memoria["buckets"][bucket]) < 12:
            memoria["buckets"][bucket].append(resumen)
        for marca in orden:
            if len(memoria["brands"][marca]) < 15:
                resumen_marca = dict(resumen)
                resumen_marca["angle"] = monitor_angulo_para_marca(item, marca)
                resumen_marca["score"] = scores.get(marca, 0)
                memoria["brands"][marca].append(resumen_marca)
    guardar_json(MONITOR_BRAND_FILE, memoria)
    guardar_json(MONITOR_FILE, log)
    return memoria


def daily_news_briefing():
    log = leer_json(MONITOR_FILE, [])
    if not log:
        nuevos = monitor_revisar_fuentes()
        log = leer_json(MONITOR_FILE, [])
        if not log:
            return (
                "Todavia no tengo hallazgos para un briefing diario. "
                "Activa el monitor o vuelve a intentar en unos minutos."
            )

    memoria = monitor_actualizar_memoria_marca(log)
    fecha = fecha_hora_actual_texto()
    respuesta = (
        "### Daily News Briefing de Gamer Signal\n\n"
        f"Fecha y hora: **{fecha}**\n\n"
        "Estas son oportunidades detectadas por el monitor, organizadas para crear posts sin repetir temas demasiado parecidos.\n\n"
    )

    categorias = [
        ("noticia_actual", "Actualidad"),
        ("debate", "Debate"),
        ("nostalgia", "Nostalgia"),
        ("tecnologia", "Tecnologia"),
        ("anime", "Anime / Geek"),
        ("indie", "Indie"),
    ]
    for bucket, label in categorias:
        items = memoria.get("buckets", {}).get(bucket, [])[:2]
        respuesta += f"## {label}\n\n"
        if not items:
            respuesta += "Todavia no hay una oportunidad fuerte en esta categoria.\n\n"
            continue

        for idx, item in enumerate(items, start=1):
            titulo = titulo_publico_en_espanol(item.get("title", ""), "news")
            respuesta += (
                f"{idx}. **{titulo}**\n"
                f"- Fuente: {item.get('source', 'fuente')}\n"
                f"- Fecha: {item.get('date', '')}\n"
                f"- Angulo posible: {angulo_para_bucket(bucket)}\n\n"
            )

    respuesta += (
        "Puedes pedirme: **usa el radar diario para 5 posts**, "
        "**crea un post de debate del radar** o **hazme un post de nostalgia del radar**."
    )
    return respuesta


def resumen_monitor(limit=8):
    log = leer_json(MONITOR_FILE, [])
    if not log:
        return (
            "El monitor todavia no tiene hallazgos guardados. "
            "Usa **revisar monitor ahora** o activa el monitor en la barra lateral."
        )

    total = len(log)
    memoria_marca = monitor_actualizar_memoria_marca(log)
    recientes = log[:limit]
    ultima = st.session_state.get("monitor_last_run", "sin revisar en esta sesion")
    estado = "activo" if st.session_state.get("monitor_active") else "manual"
    respuesta = (
        "### Monitor de Gamer Signal\n\n"
        f"- Estado: {estado}\n"
        f"- Ultima revision: {ultima}\n"
        f"- Hallazgos guardados: {total}\n\n"
        "**Temas recientes detectados:**\n"
    )
    for i, item in enumerate(recientes, start=1):
        razones = item.get("trend_reasons") or []
        razon_txt = f" | senales: {', '.join(razones[:2])}" if razones else ""
        titulo = titulo_publico_en_espanol(item.get("title", ""), "news")
        marcas = ", ".join(item.get("recommended_brands", [])[:2]) if item.get("recommended_brands") else "Gamer Cave"
        respuesta += (
            f"{i}. **{titulo}**\n"
            f"   Fuente: {item.get('source', 'fuente')} | Fecha: {item.get('date', '')} | "
            f"{item.get('verification_level', 'verificada')} | mejor para: {marcas}{razon_txt}\n"
        )
    respuesta += "\n**Top por marca:**\n"
    for marca, items in memoria_marca.get("brands", {}).items():
        if items:
            respuesta += f"- {marca}: {titulo_publico_en_espanol(items[0].get('title', ''), 'news')}\n"
    respuesta += "\nPuedes decir: **daily news briefing**, **hazme un post del hallazgo 1** o **hazme 5 posts con lo mas nuevo**."
    return respuesta


def es_pedido_monitor(texto):
    frases = [
        "monitor", "monitoreo", "monitorea", "radar", "que encontro", "que encontr?",
        "hallazgos", "recolectar informacion", "recolectar informaci?n", "buscando noticias",
    ]
    return any(frase in texto for frase in frases)


def es_pedido_daily_briefing(texto):
    frases = [
        "daily news briefing", "daily briefing", "briefing diario", "resumen diario",
        "noticias del dia", "noticias del d\u00eda", "briefing de hoy",
        "angulos posibles", "angulos para cada marca", "angulos por marca",
        "radar diario", "usa el radar", "usar el radar", "del radar",
    ]
    return any(frase in texto for frase in frases)


def responder_monitor(texto):
    if "desactivar" in texto or "apagar" in texto:
        st.session_state.monitor_active = False
        return "Monitor desactivado. Puedes volver a activarlo desde la barra lateral o diciendo: activar monitor."
    if "activar" in texto or "prender" in texto:
        st.session_state.monitor_active = True
        nuevos = monitor_revisar_fuentes()
        return f"Monitor activado. Hice una revision inicial y encontre {len(nuevos)} hallazgo(s) nuevo(s).\n\n" + resumen_monitor()
    if "ahora" in texto or "revisar" in texto or "buscar" in texto:
        nuevos = monitor_revisar_fuentes()
        return f"Revision lista. Hallazgos nuevos: {len(nuevos)}.\n\n" + resumen_monitor()
    return resumen_monitor()


def elegir_noticia_nueva_para_post(categoria_preferida=None):
    noticias = filtrar_noticias_verificadas(buscar_noticias())
    if categoria_preferida:
        preferidas = [
            item for item in noticias
            if categoria_de_item(item) == categoria_preferida
            or (categoria_preferida == "gaming" and categoria_de_item(item) == "indie")
        ]
        noticias = preferidas + [item for item in noticias if item not in preferidas]

    for item in noticias:
        titulo = item.get("title", "")
        if tema_repetido(titulo) or tema_muy_similar(titulo):
            continue
        st.session_state.generated_items[item["id"]] = item
        st.session_state.last_item_id = item["id"]
        return item

    if noticias:
        item = noticias[0]
        st.session_state.generated_items[item["id"]] = item
        st.session_state.last_item_id = item["id"]
        return item

    return None


def obtener_limite_hashtags():
    prefs = get_user_preferences()
    for pref in reversed(prefs):
        if pref.get("key") == "hashtag_limit":
            try:
                return max(1, min(10, int(pref.get("value", 5))))
            except (TypeError, ValueError):
                return 5
    return 5


def guardar_regla_cinco_hashtags():
    update_preference("hashtag_limit", "5", 10, "Instagram hashtag limit requested by user")


def limitar_hashtags_texto(hashtags_texto, limite=None):
    limite = limite or obtener_limite_hashtags()
    tags = []
    for tag in hashtags_texto.split():
        tag = tag.strip().lower()
        if not tag.startswith("#"):
            tag = f"#{tag}"
        if tag not in tags:
            tags.append(tag)
    return " ".join(tags[:limite])


def crear_hashtags(texto, limite=None):
    texto = texto.lower()
    brand = get_brand_voice()
    hashtags = brand.get("default_hashtags", ["#gaming", "#nostalgia", "#geek", "#puertorico", "#latam"])
    if "nintendo" in texto or "mario" in texto or "zelda" in texto or "kirby" in texto:
        hashtags.extend(["#nintendo", "#nintendoswitch"])
    if "playstation" in texto or "ps2" in texto or "ps1" in texto:
        hashtags.extend(["#playstation", "#ps5"])
    if "xbox" in texto:
        hashtags.extend(["#xbox", "#xboxseriesx"])
    if "pokemon" in texto or "pokémon" in texto:
        hashtags.append("#pokemon")
    if "pc" in texto or "steam" in texto:
        hashtags.extend(["#pcgaming", "#steam"])
    if "hardware" in texto or "nvidia" in texto or "rtx" in texto or "gpu" in texto or "tecnología" in texto or "technology" in texto:
        hashtags.extend(["#tech", "#gamingtech", "#hardware"])
    if "anime" in texto or "manga" in texto or "crunchyroll" in texto:
        hashtags.extend(["#anime", "#geek", "#otaku", "#popculture"])
    if brand.get("brand") == "Daviet Gaming":
        if "noticia" in texto or "news" in texto or "anuncio" in texto or "lanzamiento" in texto:
            hashtags.extend(["#gamingnews", "#noticiasgaming", "#gamerslatam"])
        if "setup" in texto or "pc gaming" in texto or "gaming pc" in texto:
            hashtags.extend(["#setupgamer", "#gamingpc"])
        if "msi" in texto:
            hashtags.append("#msi")
        if "frieren" in texto:
            hashtags.extend(["#frieren", "#animegaming"])

    hashtags = list(dict.fromkeys(tag.lower() for tag in hashtags))
    if brand.get("brand") == "Daviet Gaming":
        hashtags = ["#davietgaming"] + [tag for tag in hashtags if tag != "#davietgaming"]
    elif brand.get("brand") == "El Gamer Cave":
        hashtags = ["#elgamercave"] + [tag for tag in hashtags if tag != "#elgamercave"]
    return limitar_hashtags_texto(" ".join(hashtags), limite)


def texto_menciona_hashtags(texto):
    palabras = ["hashtag", "hashtags", "hastag", "hastags", "hashtach", "hastach", "hash"]
    return any(palabra in texto for palabra in palabras)


def pide_cinco_hashtags(texto):
    if not texto_menciona_hashtags(texto):
        return False
    return any(frase in texto for frase in ["5", "cinco", "solo cinco", "solo 5", "nada mas 5", "nada más 5"])


def es_pedido_solo_hashtags(texto):
    if not texto_menciona_hashtags(texto):
        return False
    palabras_post = ["post", "publicación", "publicacion", "caption", "noticia", "noticias"]
    return not any(palabra in texto for palabra in palabras_post)


def limpiar_pedido_hashtags(pregunta):
    texto = pregunta.lower()
    frases = [
        "dame", "hazme", "creame", "créame", "crea", "crear", "generame", "genérame",
        "solo", "cinco", "5", "hashtags", "hashtag", "hastags", "hastag", "hashtach",
        "hastach", "para instagram", "para facebook", "instagram", "facebook",
        "para", "sobre", "de", "del", "la", "el", "los", "las",
    ]
    for frase in frases:
        texto = texto.replace(frase, " ")
    return " ".join(texto.split()).strip(" .,:;-")


def crear_respuesta_hashtags(pregunta):
    guardar_regla_cinco_hashtags()
    tema = limpiar_pedido_hashtags(pregunta)
    item = st.session_state.generated_items.get(st.session_state.get("last_item_id"), {})
    base = tema or f"{item.get('title', '')} {item.get('summary', '')}" or st.session_state.get("active_brand", "gaming")
    hashtags = crear_hashtags(base, limite=5)
    return (
        "Listo. Guardé la regla: usar solo 5 hashtags.\n\n"
        f"{hashtags}"
    )


def limpiar_html(texto):
    if not texto:
        return ""
    texto = html_unescape(str(texto))
    texto = re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", texto, flags=re.IGNORECASE | re.DOTALL)
    texto = re.sub(r"<br\s*/?>", " ", texto, flags=re.IGNORECASE)
    texto = re.sub(r"</p\s*>", " ", texto, flags=re.IGNORECASE)
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = re.sub(r"https?://\S+", "", texto)
    texto = re.sub(r"\bThe post\b.*?\bappeared first on\b[^.?!]*(?:[.?!]|$)", "", texto, flags=re.IGNORECASE | re.DOTALL)
    texto = re.sub(r"\bappeared first on\b[^.?!]*(?:[.?!]|$)", "", texto, flags=re.IGNORECASE | re.DOTALL)
    while "  " in texto:
        texto = texto.replace("  ", " ")
    return reparar_texto_roto(texto.strip())


def reparar_texto_roto(texto):
    if not texto:
        return ""
    reemplazos = {
        "Ã¡": "\u00e1",
        "Ã©": "\u00e9",
        "Ã­": "\u00ed",
        "Ã³": "\u00f3",
        "Ãº": "\u00fa",
        "Ã±": "\u00f1",
        "Ã": "\u00c1",
        "Ã‰": "\u00c9",
        "Ã": "\u00cd",
        "Ã“": "\u00d3",
        "Ãš": "\u00da",
        "Ã‘": "\u00d1",
        "Â¿": "\u00bf",
        "Â¡": "\u00a1",
        "â€“": "-",
        "â€”": "-",
        "â€˜": "'",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "ðŸŽ®": "\U0001f3ae",
        "ðŸ‘‡": "\U0001f447",
        "ðŸ“¡": "\U0001f4e1",
        "Ãº": "\u00fa",
        "Ã³": "\u00f3",
        "Ã­a": "\u00eda",
        "Ã©n": "\u00e9n",
        "Ã³n": "\u00f3n",
    }
    for malo, bueno in reemplazos.items():
        texto = texto.replace(malo, bueno)
    return texto


def recortar_texto(texto, limite=360):
    texto = limpiar_html(texto)
    if len(texto) <= limite:
        return texto
    corte = texto[:limite].rsplit(" ", 1)[0]
    return corte + "..."


def quitar_marca_de_texto(texto):
    reemplazos = [
        "para daviet gaming", "para davietgaming", "para daviet", "daviet gaming", "davietgaming", "daviet",
        "para el gamer cave", "para gamer cave", "para el gamer", "el gamer cave", "gamer cave",
        "para marca general", "para general", "marca general",
    ]
    limpio = texto.lower()
    for frase in reemplazos:
        limpio = limpio.replace(frase, " ")
    return " ".join(limpio.split()).strip()


def limpiar_pedido_post(pregunta):
    texto = pregunta.strip()
    texto_lower = texto.lower()
    frases = [
        "créame un post", "creame un post", "crea un post", "crear un post",
        "hazme un post", "haz un post", "post para instagram", "post para facebook",
        "caption para tiktok", "caption para reel", "post", "instagram", "facebook",
        "hazme", "creame", "créame", "crea", "crear", "hacer", "hace", "haz",
    ]
    for frase in frases:
        texto_lower = texto_lower.replace(frase, " ")
    texto_lower = quitar_marca_de_texto(texto_lower)
    for separador in [" sobre ", " de "]:
        if separador in texto_lower:
            texto_lower = texto_lower.split(separador, 1)[1]
    texto_lower = texto_lower.strip()
    for prefijo in ["sobre ", "de "]:
        if texto_lower.startswith(prefijo):
            texto_lower = texto_lower[len(prefijo):]
    ruido = [
        "por favor", "para redes", "para publicar", "con estilo gamer", "del tema",
        "para la marca", "para marca", "para mi marca", "para mi pagina", "para mi página",
        "para", "la marca", "marca",
    ]
    for item in ruido:
        texto_lower = texto_lower.replace(item, " ")
    return " ".join(texto_lower.split()).strip(" .,:;-")


def crear_item_desde_pedido(pregunta, estilo):
    tema = limpiar_pedido_post(pregunta)
    if not tema or tema in ["un", "una", "nuevo", "nueva"]:
        return None
    titulo = tema[:1].upper() + tema[1:]
    texto = f"{titulo} es un tema solicitado para crear contenido gamer con enfoque {estilo}."
    if estilo in ["nostalgia", "emocional"]:
        texto += " La idea es conectar con recuerdos de infancia, consolas viejas, juegos físicos y comunidad."
    elif estilo == "debate":
        texto += " La idea es provocar comentarios sin sonar agresivo ni inventar datos."
    else:
        texto += " La idea es explicarlo claro y convertirlo en un post útil para redes."

    contexto_local = buscar_contexto_local(titulo)
    if contexto_local:
        texto += " " + contexto_local.get("summary", "")

    item = {
        "id": str(uuid.uuid4()),
        "title": titulo,
        "summary": texto,
        "source": "Tema solicitado por el usuario",
        "link": "",
        "date": str(ahora_en_puerto_rico().date()),
        "content_angle": estilo if estilo != "news" else "opinión",
        "nostalgia_angle": detectar_angulo_nostalgia({"title": titulo, "summary": texto}),
        "confidence_level": "manual",
        "context_source": contexto_local.get("provider", "") if contexto_local else "",
    }
    st.session_state.generated_items[item["id"]] = item
    st.session_state.last_item_id = item["id"]
    return item


def crear_subtitulo(estilo, titulo):
    if estilo == "debate":
        return "Un tema para prender la conversación gamer"
    if estilo in ["noticia", "news"]:
        return "Lo importante es entender por qué importa ahora"
    if estilo == "emocional":
        return "De esos recuerdos que muchos gamers entienden rápido"
    if estilo == "corto":
        return "Rápido, directo y listo para comentarios"
    return "No era solo jugar, era parte de la experiencia"


def sugerencia_visual(estilo, texto):
    texto = texto.lower()
    if st.session_state.get("active_brand") == "Daviet Gaming":
        return (
            "Background Daviet Gaming estilo premium: negro profundo, dragon negro metalico o silueta de dragon, "
            "detalles dorados, lineas geometricas futuristas, alto contraste blanco/dorado, espacio limpio para texto, "
            "formato vertical 1080x1350, sin logos de companias ni texto extra."
        )
    if "gamecube" in texto or "game boy" in texto or "nintendo" in texto:
        return "Background nostálgico con consola retro, controles, cartuchos o discos sobre una mesa, luz cálida, formato vertical 1080x1350, sin texto."
    if "hardware" in texto or "nvidia" in texto or "amd" in texto or "msi" in texto or "asus" in texto:
        return "Background de setup PC gaming con luces limpias, hardware como protagonista, espacio libre para título, formato vertical 1080x1350."
    if "game jam" in texto or "puerto rico" in texto or "gamedev" in texto:
        return "Background de comunidad gamer y desarrollo indie, laptops, controles y ambiente de evento local, formato vertical 1080x1350."
    if estilo == "debate":
        return "Background dividido visualmente entre dos ideas opuestas, estilo gamer limpio, espacio central para título, formato vertical 1080x1350."
    return "Background gaming oscuro con detalles retro, consola o control como elemento principal, espacio limpio para texto, formato vertical 1080x1350."


def normalizar_titulo_gamer(titulo):
    reemplazos = {
        "gamecube": "GameCube",
        "game boy": "Game Boy",
        "pokemon": "Pokémon",
        "playstation": "PlayStation",
        "xbox": "Xbox",
        "nintendo": "Nintendo",
        "zelda": "Zelda",
        "mario": "Mario",
        "kirby": "Kirby",
    }
    limpio = titulo.strip()
    bajo = limpio.lower()
    return reemplazos.get(bajo, limpio[:1].upper() + limpio[1:])



def enfoque_comunidad_pr_latam(titulo, texto_base, estilo):
    texto = f"{titulo} {texto_base}".lower()
    if ("gta 6" in texto or "grand theft auto vi" in texto) and any(
        palabra in texto for palabra in ["lanzamiento", "release date", "calendario"]
    ):
        return (
            "Para la comunidad, la discusión está en si otros estudios deberían mover sus fechas "
            "o competir directamente por la atención de los jugadores."
        )
    if estilo == "debate":
        return "La conversación se pone buena cuando la comunidad compara experiencias sin convertirlo en pelea de plataformas."
    if "precio" in texto or "suscripción" in texto or "game pass" in texto or "ps plus" in texto:
        return "Para muchos gamers de Puerto Rico y LatAm, la pregunta real es si esto vale el dinero y el tiempo."
    if "digital" in texto or "físico" in texto or "fisico" in texto:
        return "Este tema conecta rápido porque muchos todavía recuerdan comprar, prestar o guardar juegos físicos."
    if "remake" in texto or "remaster" in texto or "nostalgia" in texto:
        return "Aquí la nostalgia pesa, pero también vale preguntar si queremos recuerdos o experiencias nuevas."
    if "anime" in texto or "manga" in texto:
        return "Anime y gaming se cruzan mucho en nuestra comunidad, especialmente cuando hay hype, regreso de clásicos o debate de adaptación."
    if "hardware" in texto or "nvidia" in texto or "rtx" in texto or "gpu" in texto:
        return "La clave es explicarlo desde el beneficio real para el gamer común, no como ficha técnica fría."
    return (
        "Este tipo de tema conecta con la comunidad porque cada gamer puede vivirlo, "
        "recordarlo o interpretarlo de una manera diferente."
    )





def revisar_coherencia_editorial(post, estilo):
    """Limpia notas internas y comprueba que el caption suene publicable."""
    texto = str(post or "").strip()
    reemplazos = {
        "Lo importante es aterrizarlo a la comunidad: qué cambia, a quién le interesa y qué opinión puede abrir.": (
            "Este tema conecta con la comunidad porque cada gamer puede vivirlo "
            "o interpretarlo de una manera diferente."
        ),
        "La clave está en entender qué cambia, a quién le interesa y por qué puede importar para la comunidad.": (
            "La noticia importa por el efecto que puede tener en los jugadores "
            "y en la conversación de la comunidad."
        ),
    }
    for frase_interna, frase_publica in reemplazos.items():
        texto = texto.replace(frase_interna, frase_publica)

    texto = limpiar_texto_publicable_final(texto)
    texto = "\n".join(linea.rstrip() for linea in texto.splitlines())
    texto = re.sub(r"\n{3,}", "\n\n", texto).strip()

    cuerpo_sin_hashtags = "\n".join(
        linea for linea in texto.splitlines() if not linea.lstrip().startswith("#")
    )
    if "?" not in cuerpo_sin_hashtags and "¿" not in cuerpo_sin_hashtags:
        cierre = "👇 ¿Qué opinas?"
        partes = texto.rsplit("\n\n", 1)
        if len(partes) == 2 and partes[1].lstrip().startswith("#"):
            texto = f"{partes[0]}\n\n{cierre}\n\n{partes[1]}"
        else:
            texto = f"{texto}\n\n{cierre}"

    return texto


def pregunta_engagement(titulo, estilo):
    texto = titulo.lower()
    if ("gta 6" in texto or "grand theft auto vi" in texto) and any(
        palabra in texto for palabra in ["lanzamiento", "release date", "calendario"]
    ):
        return "👇 ¿Crees que otros estudios deberían mover sus juegos o competir de frente?"
    if estilo == "debate":
        return "👇 ¿Tú cómo lo ves: buena movida o mala decisión?"
    if "precio" in texto or "suscripción" in texto or "game pass" in texto or "ps plus" in texto:
        return "👇 ¿Lo pagarías o esperarías una mejor oferta?"
    if "remake" in texto or "remaster" in texto:
        return "👇 ¿Te emociona este regreso o prefieres juegos nuevos?"
    if "digital" in texto or "físico" in texto or "fisico" in texto:
        return "👇 ¿Tú eres team físico o team digital?"
    if "anime" in texto or "manga" in texto:
        return "👇 ¿Este tema te da hype o lo dejarías pasar?"
    if estilo in ["nostalgia", "emocional"]:
        return "👇 ¿Qué recuerdo gamer te vino a la mente?"
    return "👇 ¿Esto te interesa o lo dejarías pasar?"


def crear_post_daviet(titulo, texto_base, estilo, nostalgia, hashtags):
    if estilo == "debate":
        subtitulo = "Un tema para prender la conversación"
        opinion = (
            "En mi opinión, este tipo de tema funciona porque no todos los gamers lo viven igual. "
            "Hay quienes miran la comodidad, otros la nostalgia y otros simplemente quieren que la industria no pierda el foco."
        )
        pregunta = pregunta_engagement(titulo, estilo)
    elif estilo in ["noticia", "news"]:
        subtitulo = "Una noticia para mirar con calma"
        opinion = (
            "Mi ángulo: más allá del anuncio, lo interesante es ver si esto realmente le aporta algo al jugador "
            "o si se queda solo en ruido de momento."
        )
        pregunta = pregunta_engagement(titulo, estilo)
    elif estilo == "emocional":
        subtitulo = "De esos temas que conectan con la comunidad"
        opinion = (
            "En mi opinión, el gaming pega más fuerte cuando conecta con recuerdos, etapas y momentos que uno vivió de verdad."
        )
        pregunta = pregunta_engagement(titulo, estilo)
    elif estilo == "corto":
        subtitulo = "Rápido y al punto"
        opinion = "Mi ángulo: esto puede abrir una conversación buena si la comunidad se activa."
        pregunta = pregunta_engagement(titulo, estilo)
    else:
        subtitulo = "No era solo jugar, era parte de la experiencia"
        opinion = (
            "En mi opinión, estos temas funcionan porque mezclan nostalgia, comunidad y esa forma en que cada gamer "
            "recuerda su propia etapa."
        )
        pregunta = pregunta_engagement(titulo, estilo)

    if nostalgia and estilo not in ["noticia", "news"]:
        opinion += f" También conecta con {nostalgia}"
    opinion += f" {enfoque_comunidad_pr_latam(titulo, texto_base, estilo)}"

    return f"""🎮 {titulo}

{subtitulo}

{texto_base}

{opinion}

{pregunta}

{hashtags}"""


def crear_post_limpio(titulo, resumen, estilo, nostalgia, hashtags):
    titulo_original = titulo
    titulo = titulo_publico_en_espanol(titulo_original, estilo)
    texto_base = resumen_publico_en_espanol(titulo_original, resumen, estilo)
    if not texto_base or len(texto_base) < 35:
        texto_base = (
            f"{titulo} es un tema reciente dentro del mundo gamer. "
            "Lo importante es mirar qué puede cambiar, a quién le interesa y qué conversación puede abrir en la comunidad."
        )

    if get_brand_voice().get("brand") == "Daviet Gaming":
        return crear_post_daviet(titulo, texto_base, estilo, nostalgia, hashtags)

    if estilo == "debate":
        gancho = f"🎮 {titulo} es uno de esos temas que siempre divide opiniones en la comunidad."
        cuerpo = (
            "Por un lado está la comodidad de lo moderno: descargas rápidas, juegos siempre disponibles "
            "y menos espacio ocupado.\n\n"
            "Pero también está esa parte que muchos extrañan: tener el juego en la mano, prestarlo, "
            "ver la portada, leer el manual y sentir que de verdad era tuyo."
        )
        cuerpo += f"\n\n{enfoque_comunidad_pr_latam(titulo, texto_base, estilo)}"
        cierre = pregunta_engagement(titulo, estilo)
    elif estilo in ["noticia", "news"]:
        gancho = f"🎮 {titulo}"
        cuerpo = (
            f"{texto_base}\n\n"
            "Lo interesante es mirar por qué esto importa para los jugadores y cómo puede mover conversación "
            "entre la comunidad gamer.\n\n"
            f"{enfoque_comunidad_pr_latam(titulo, texto_base, estilo)}"
        )
        cierre = pregunta_engagement(titulo, estilo)
    elif estilo == "emocional":
        titulo_bajo = titulo.lower()
        if "recuerdo" in titulo_bajo or "conecta" in titulo_bajo or "fibra" in titulo_bajo:
            gancho = f"\U0001F3AE {titulo}"
        else:
            gancho = f"\U0001F3AE {titulo} toca una fibra gamer."
        cuerpo = (
            "Hay juegos, consolas y momentos que no solo se recuerdan por los gráficos o la tecnología, "
            "sino por la etapa de vida en la que llegaron.\n\n"
            "A veces era llegar de la escuela, prender la consola, pasar controles y repetir el mismo juego "
            "como si nunca cansara."
        )
        cuerpo += f"\n\n{enfoque_comunidad_pr_latam(titulo, texto_base, estilo)}"
        cierre = pregunta_engagement(titulo, estilo)
    elif estilo == "corto":
        gancho = f"🎮 {titulo}"
        cuerpo = "Esto puede traer recuerdos, debate o una conversación buena entre gamers."
        cuerpo += f"\n\n{enfoque_comunidad_pr_latam(titulo, texto_base, estilo)}"
        cierre = pregunta_engagement(titulo, estilo)
    else:
        gancho = f"🎮 {titulo} no era solo jugar, era parte de la experiencia."
        cuerpo = (
            "Antes de los mundos abiertos gigantes, los updates eternos y el juego online en todos lados, "
            "había momentos más simples que muchos gamers todavía recuerdan.\n\n"
            f"Para algunos fue {titulo}. Para otros fue Mario, Pokémon, Zelda, Halo, Final Fantasy, GTA "
            "o ese juego que se repetía mil veces sin cansarse.\n\n"
            "Lo importante no era solo el juego, era la memoria que venía con él: la consola, el control, "
            "los discos, los cartuchos, los primos, las amistades y esas tardes que se iban demasiado rápido."
        )
        cuerpo += f"\n\n{enfoque_comunidad_pr_latam(titulo, texto_base, estilo)}"
        cierre = pregunta_engagement(titulo, estilo)

    if nostalgia and estilo not in ["noticia", "news"]:
        cuerpo += f"\n\nEso conecta con {nostalgia}"

    return f"""{gancho}

{cuerpo}

{cierre}

{hashtags}"""


def generate_social_post(item, estilo=None):
    titulo = limpiar_html(item.get("title", "Tema gamer"))
    resumen = limpiar_html(item.get("summary", ""))
    angulo = detectar_content_angle(item)
    item["content_angle"] = angulo
    item["nostalgia_angle"] = detectar_angulo_nostalgia(item)
    nostalgia = limpiar_html(item.get("nostalgia_angle", ""))
    brand = get_brand_voice()
    estilo = estilo or st.session_state.get("post_style", "all")
    estilo_real = "nostalgia" if estilo == "all" and angulo == "nostalgia" else estilo
    estilo_real = "news" if estilo_real == "all" else estilo_real
    estilo_real = estilo_seguro_para_item(item, estilo_real)

    corto = any(
        pref.get("key") == "style_rule" and "corto" in str(pref.get("value", "")).lower()
        for pref in get_user_preferences()
    ) or estilo_real == "corto"
    if corto:
        estilo_real = "corto"

    hashtags = crear_hashtags(titulo + " " + resumen)
    if brand.get("brand") == "El Gamer Cave" and "#elgamercave" not in hashtags.split():
        hashtags = "#elgamercave " + hashtags
    hashtags = limitar_hashtags_texto(hashtags)

    post = crear_post_limpio(titulo, resumen, estilo_real, nostalgia, hashtags)
    post = asegurar_caption_en_espanol(post, titulo, resumen, estilo_real)
    post = revisar_coherencia_editorial(post, estilo_real)
    post = asegurar_caption_en_espanol(post, titulo, resumen, estilo_real)
    post = aplicar_reglas_editoriales_fuertes(post, item, estilo_real)
    st.session_state.last_post_text = post
    st.session_state.last_post_title = normalizar_titulo_gamer(titulo)
    return post


# Capa final de idioma y limpieza para evitar que titulares RSS salgan en ingles.
# Las fuentes originales se guardan internamente, pero el caption visible queda en espanol.
def limpiar_texto_publicable_final(texto):
    limpio = str(texto or "")
    reemplazos = {
        "todavÃ­a": "todav\u00eda",
        "tendrÃ¡": "tendr\u00e1",
        "adaptaciÃ³n": "adaptaci\u00f3n",
        "atenciÃ³n": "atenci\u00f3n",
        "conversaciÃ³n": "conversaci\u00f3n",
        "mÃ¡s": "m\u00e1s",
        "trÃ¡iler": "tr\u00e1iler",
        "tecnologÃ­a": "tecnolog\u00eda",
        "quÃ©": "qu\u00e9",
        "quiÃ©n": "qui\u00e9n",
        "por quÃ©": "por qu\u00e9",
        "cÃ³mo": "c\u00f3mo",
        "estÃ¡": "est\u00e1",
        "estÃ¡n": "est\u00e1n",
        "fÃ­sico": "f\u00edsico",
        "fÃ­sicos": "f\u00edsicos",
        "grÃ¡ficos": "gr\u00e1ficos",
        "aÃ±o": "a\u00f1o",
        "aÃ±os": "a\u00f1os",
        "Ã¡ngulo": "\u00e1ngulo",
        "nostÃ¡lgico": "nost\u00e1lgico",
        "PokÃ©mon": "Pok\u00e9mon",
        "Â¿": "\u00bf",
        "Â¡": "\u00a1",
        "â€”": "-",
        "â€“": "-",
        "â€™": "'",
        "â€œ": "\"",
        "â€": "\"",
        "ðŸŽ®": "\U0001f3ae",
        "ðŸ‘‡": "\U0001f447",
    }
    for malo, bueno in reemplazos.items():
        limpio = limpio.replace(malo, bueno)

    limpio = re.sub(r"https?://\S+", "", limpio)
    limpio = re.sub(r"\bThe post\b.*?\bappeared first on\b.*?(?:\.|\n|$)", "", limpio, flags=re.IGNORECASE | re.DOTALL)
    limpio = re.sub(r"\bappeared first on\b.*?(?:\.|\n|$)", "", limpio, flags=re.IGNORECASE | re.DOTALL)
    limpio = re.sub(r"\n{3,}", "\n\n", limpio)
    limpio = re.sub(r"[ \t]{2,}", " ", limpio)
    return limpio.strip()


def parece_texto_ingles(texto):
    texto_bajo = f" {limpiar_html(texto).lower()} "
    frases_ingles = [
        "release date", "hands-on", "available today", "coming soon", "coming to",
        "is about", "about fear", "questionable choices", "official podcast",
        "handing players the keys", "keys to the seas", "appeared first",
        "the post", "update details", "launches", "launching", "announces",
        "reveals", "report", "new trailer", "season", "this november",
        "this july", "this summer", "acclaimed", "fantasy manga",
        "getting an anime", "anime adaptation", "just announced", "alongside",
        "teaser trailer", "could inherit", "by default", "physical gaming crown",
        "monthly games", "free play days", "drops its", "recommendation",
        "enhancements detailed", "finally addresses", "plot hole",
    ]
    if any(frase in texto_bajo for frase in frases_ingles):
        return True
    palabras = [
        " the ", " and ", " with ", " for ", " from ", " this ", " that ",
        " players ", " update ", " available ", " coming ", " launches ",
        " launch ", " report ", " details ", " official ", " podcast ",
        " episode ", " expect ", " chaos ", " caused ", " release ", " date ",
        " fear ", " empathy ", " choices ", " today ", " november ", "july",
        "acclaimed", "fantasy", "getting", "adaptation", "announced",
        "alongside", "teaser", "trailer", "could", "inherit", "physical",
        "crown", "default", "monthly", "games", "free", "days",
    ]
    return sum(1 for palabra in palabras if palabra in texto_bajo) >= 2


def extraer_tema_para_titulo(titulo):
    limpio = limpiar_texto_publicable_final(limpiar_html(titulo))
    limpio = re.sub(r"\s+", " ", limpio).strip(" -:|")

    patrones = [
        r"\bGTA\s*6\b",
        r"\bGrand Theft Auto\s*VI\b",
        r"\bNintendo Switch\s*2\b",
        r"\bPlayStation\s*5\b",
        r"\bPS5\b",
        r"\bXbox\b",
        r"\bSteam Deck\b",
        r"\bSea of Thieves\b",
        r"\bCall of Duty\b",
        r"\bAssassin.?s Creed[^:,-]*",
        r"\bOne Piece\b",
        r"\bGameCube\b",
        r"\bGame Boy\b",
    ]
    for patron in patrones:
        match = re.search(patron, limpio, flags=re.IGNORECASE)
        if match:
            return normalizar_titulo_gamer(match.group(0).strip())

    anime_match = re.search(
        r"(?:manga|anime)\s+(.+?)\s+(?:is getting|gets|will get|getting|receives|announced|tendr)",
        limpio,
        flags=re.IGNORECASE,
    )
    if anime_match:
        return anime_match.group(1).strip(" -:.,")

    for separador in [" - ", " – ", " — ", ":"]:
        if separador in limpio:
            posible = limpio.split(separador, 1)[0].strip()
            if 3 <= len(posible) <= 80:
                return normalizar_titulo_gamer(posible)

    palabras_corte = [" is ", " are ", " gets ", " launches ", " reveals ", " announces ", " drops ", " details "]
    bajo = limpio.lower()
    for separador in palabras_corte:
        if separador in bajo:
            posible = limpio[:bajo.find(separador)].strip()
            if 3 <= len(posible) <= 80:
                return normalizar_titulo_gamer(posible)

    return normalizar_titulo_gamer(limpio[:80].strip(" -:.,") or "tema gamer")


def titulo_publico_en_espanol(titulo, estilo):
    original = limpiar_texto_publicable_final(limpiar_html(titulo))
    if not original:
        return "Tema gamer para comentar"

    tema = normalizar_titulo_gamer(extraer_tema_para_titulo(original))
    bajo = original.lower()

    if not parece_texto_ingles(original):
        limpio = normalizar_titulo_gamer(original)
        if estilo in ["nostalgia", "emocional"] and re.search(r"\b20\d{2}\b", limpio):
            limpio = re.sub(r"\b(?:de\s+)?20\d{2}\b", "", limpio, flags=re.IGNORECASE)
            limpio = re.sub(r"\s{2,}", " ", limpio).strip(" -:")
            return f"{limpio}: recuerdos que todav\u00eda conectan"
        return limpio

    if re.search(r"\bgta\s*6\b|grand theft auto\s*vi", bajo):
        return "GTA 6 vuelve a mover la conversaci\u00f3n gamer"
    if "physical gaming crown" in bajo or "physical" in bajo and "gaming" in bajo:
        return "Los juegos f\u00edsicos vuelven al debate"
    if "getting an anime" in bajo or "anime adaptation" in bajo:
        return f"{tema} tendr\u00e1 adaptaci\u00f3n al anime"
    if "podcast" in bajo:
        return f"{tema}: tema oficial para comentar"
    if "free play days" in bajo or "monthly games" in bajo:
        return "Juegos incluidos este mes para comentar"
    if "hands-on" in bajo or "demo available" in bajo or "available today" in bajo:
        return f"{tema}: demo y primeras impresiones"
    if "trailer" in bajo or "teaser" in bajo:
        return f"{tema}: nuevo avance para comentar"
    if "update" in bajo or "details" in bajo or "enhancements" in bajo:
        return f"{tema}: nuevos detalles para jugadores"
    if "release date" in bajo or "launch" in bajo or "coming" in bajo:
        return f"{tema}: lanzamiento bajo la lupa"
    if "plot hole" in bajo:
        return f"{tema}: detalle que encendi\u00f3 la conversaci\u00f3n"

    if estilo == "debate":
        return f"{tema} abre debate gamer"
    if estilo in ["nostalgia", "emocional"]:
        return f"{tema}: recuerdos gamer"
    if estilo == "corto":
        return f"{tema}: tema r\u00e1pido para comentar"
    return f"{tema}: noticia para comentar"


def titulo_visible_seguro(item, estilo="news", bucket=None):
    """Titulo final para UI: nunca deja un headline entero en ingles."""
    item = item or {}
    original = item.get("title", "") if isinstance(item, dict) else str(item)
    titulo = titulo_publico_en_espanol(original, estilo)
    titulo = limpiar_texto_publicable_final(titulo)
    bajo = titulo.lower()
    palabras_ingles_visibles = [
        " could ", " inherit ", " crown", " by default", " hands-on", " available",
        " today", " announced", " revealed", " finally", " addresses", " release date",
        " coming", " getting", " trailer", " report", " details", " version",
    ]
    if not parece_texto_ingles(titulo) and not any(p in f" {bajo} " for p in palabras_ingles_visibles):
        return titulo

    tema = normalizar_titulo_gamer(extraer_tema_para_titulo(original))
    if parece_texto_ingles(tema):
        tema = "Tema gamer"

    bucket = bucket or item.get("content_angle", "")
    if bucket in ["debate"]:
        return f"{tema}: debate para la comunidad"
    if bucket in ["nostalgia"]:
        return f"{tema}: recuerdos gamer para comentar"
    if bucket in ["tecnologia", "hardware", "technology"]:
        return f"{tema}: tecnologia explicada para gamers"
    if bucket in ["anime"]:
        return f"{tema}: tema anime/geek para comentar"
    if bucket in ["indie"]:
        return f"{tema}: indie para tener en el radar"
    return f"{tema}: noticia para comentar"


def estado_verificacion_item(item):
    item = item or {}
    if item.get("source_official"):
        return ("Verde", "fuente oficial")
    if item.get("verification_count", 0) >= 2:
        return ("Verde", "confirmada por varias fuentes")
    if item.get("is_community_signal"):
        return ("Amarillo", "senal de comunidad, usar como debate")
    if item.get("source_trusted"):
        return ("Amarillo", "fuente confiable, revisar contexto")
    return ("Rojo", "no usar como noticia confirmada")


def traducir_basico_en_espanol(texto):
    limpio = limpiar_texto_publicable_final(limpiar_html(texto))
    if not limpio:
        return ""
    reemplazos = [
        (r"\bhas announced\b", "anunci\u00f3"),
        (r"\bannounced\b", "anunci\u00f3"),
        (r"\brevealed\b", "revel\u00f3"),
        (r"\breveals\b", "revela"),
        (r"\bgetting an anime\b", "tendr\u00e1 adaptaci\u00f3n al anime"),
        (r"\banime adaptation\b", "adaptaci\u00f3n al anime"),
        (r"\bcoming in\b", "llegar\u00e1 en"),
        (r"\bcoming soon\b", "llegar\u00e1 pronto"),
        (r"\brelease date\b", "fecha de lanzamiento"),
        (r"\bteaser trailer\b", "avance"),
        (r"\btrailer\b", "avance"),
        (r"\bnew details\b", "nuevos detalles"),
        (r"\bupdate\b", "actualizaci\u00f3n"),
        (r"\bavailable today\b", "disponible hoy"),
        (r"\bhands-on\b", "primeras impresiones"),
        (r"\bplayers\b", "jugadores"),
        (r"\bdevelopers\b", "desarrolladores"),
        (r"\bdeveloper\b", "desarrollador"),
        (r"\bcommunity\b", "comunidad"),
        (r"\bfans\b", "fans"),
        (r"\bseason\b", "temporada"),
        (r"\bgames\b", "juegos"),
        (r"\bgame\b", "juego"),
        (r"\bphysical games\b", "juegos f\u00edsicos"),
        (r"\bdigital games\b", "juegos digitales"),
        (r"\bopen world\b", "mundo abierto"),
        (r"\blocal multiplayer\b", "multiplayer local"),
    ]
    traducido = limpio
    for patron, reemplazo in reemplazos:
        traducido = re.sub(patron, reemplazo, traducido, flags=re.IGNORECASE)
    return limpiar_texto_publicable_final(traducido)


def resumen_publico_en_espanol(titulo, resumen, estilo):
    resumen_limpio = limpiar_texto_publicable_final(limpiar_html(resumen))
    tema = titulo_publico_en_espanol(titulo, estilo).replace(": noticia para comentar", "")
    tema = tema.replace(": tema oficial para comentar", "").strip()

    if resumen_limpio and not parece_texto_ingles(resumen_limpio):
        return recortar_texto(resumen_limpio, 260)

    traducido = traducir_basico_en_espanol(resumen_limpio)
    if traducido and not parece_texto_ingles(traducido):
        return recortar_texto(traducido, 260)

    bajo = f"{titulo} {resumen}".lower()
    if "anime" in bajo or "manga" in bajo:
        return (
            f"{tema} se est\u00e1 moviendo dentro de la conversaci\u00f3n geek. "
            "La clave es explicarlo simple y conectar con fans de anime, manga y cultura gamer."
        )
    if "gta 6" in bajo or "grand theft auto vi" in bajo:
        return (
            "GTA 6 sigue siendo uno de los temas que m\u00e1s mueve conversaci\u00f3n. "
            "Lo interesante es mirar c\u00f3mo afecta el calendario, el hype y las expectativas de la comunidad."
        )
    if estilo == "debate":
        return (
            f"{tema} puede abrir una conversaci\u00f3n buena entre jugadores. "
            "La idea es presentar los dos lados sin convertirlo en pelea."
        )
    if estilo in ["nostalgia", "emocional"]:
        return (
            f"{tema} conecta con recuerdos gamer, consolas viejas, juegos f\u00edsicos "
            "y momentos que muchos todav\u00eda reconocen."
        )
    return (
        f"{tema} es un tema reciente dentro del mundo gamer. "
        "Lo importante es explicar qu\u00e9 pas\u00f3, por qu\u00e9 importa y qu\u00e9 conversaci\u00f3n puede abrir."
    )


def asegurar_caption_en_espanol(post, titulo_original="", resumen_original="", estilo="news"):
    texto = limpiar_texto_publicable_final(post)
    titulo_es = titulo_publico_en_espanol(titulo_original, estilo)
    resumen_es = resumen_publico_en_espanol(titulo_original, resumen_original, estilo)
    lineas = []
    cambio_resumen = False

    for linea in texto.splitlines():
        limpia = linea.strip()
        if not limpia:
            lineas.append("")
            continue
        if limpia.startswith("#"):
            lineas.append(limitar_hashtags_texto(limpia))
            continue
        sin_emoji = re.sub(r"^[^\w#\u00bf\u00a1]+", "", limpia).strip()
        if parece_texto_ingles(sin_emoji):
            if len(sin_emoji) <= 140:
                prefijo = "\U0001f3ae " if limpia.startswith("\U0001f3ae") else ""
                lineas.append(f"{prefijo}{titulo_es}")
            elif not cambio_resumen:
                lineas.append(resumen_es)
                cambio_resumen = True
            continue
        lineas.append(limpia)

    salida = "\n".join(lineas)
    salida = salida.replace("Eso conecta con Puede conectar con", "Eso conecta con")
    salida = salida.replace("conecta con Puede conectar con", "conecta con")
    salida = re.sub(r"\n{3,}", "\n\n", salida).strip()

    cuerpo = "\n".join(linea for linea in salida.splitlines() if not linea.lstrip().startswith("#"))
    if parece_texto_ingles(cuerpo):
        hashtags = "\n".join(linea for linea in salida.splitlines() if linea.lstrip().startswith("#"))
        if not hashtags:
            hashtags = limitar_hashtags_texto(crear_hashtags(f"{titulo_original} {resumen_original}"))
        salida = crear_post_limpio(titulo_es, resumen_es, estilo, "", hashtags)
    return limpiar_texto_publicable_final(salida)


def quitar_prefijos_editoriales(linea):
    """Convierte notas tipo 'Titulo:' o 'Post:' en caption limpio."""
    texto = str(linea or "").strip()
    patrones = [
        r"^(t[i\u00ed]tulo|titulo)\s*:\s*",
        r"^(subt[i\u00ed]tulo|subtitulo)\s*:\s*",
        r"^(post|caption|publicaci[o\u00f3]n)\s*:\s*",
        r"^(cierre|pregunta|cta)\s*:\s*",
        r"^(hashtags?)\s*:\s*",
    ]
    for patron in patrones:
        texto = re.sub(patron, "", texto, flags=re.IGNORECASE).strip()
    return texto


def linea_no_publicable(linea):
    """Detecta lineas que son para control interno, no para redes."""
    texto = limpiar_texto_publicable_final(linea).strip().lower()
    if not texto:
        return False
    prefijos = [
        "fuente:", "fuentes:", "link:", "fecha:", "confianza:",
        "id para feedback:", "referencia interna", "referencia usada",
        "sugerencia visual:", "angulo recomendado:", "\u00e1ngulo recomendado:",
        "verificacion:", "verificaci\u00f3n:", "nota interna:",
        "prompt:", "accion:", "acci\u00f3n:",
    ]
    if any(texto.startswith(prefijo) for prefijo in prefijos):
        return True
    frases_internas = [
        "lo importante es aterrizarlo a la comunidad",
        "que cambia, a quien le interesa",
        "qu\u00e9 cambia, a qui\u00e9n le interesa",
        "referencia gamer cave usada",
        "tema de opinion/nostalgia solicitado por el usuario",
        "no se presenta como noticia confirmada",
    ]
    return any(frase in texto for frase in frases_internas)


def limpiar_lineas_para_caption(texto):
    """Deja solo el caption publicable: sin links, fuentes ni etiquetas internas."""
    limpio = limpiar_texto_publicable_final(reparar_texto_roto(texto))
    lineas_limpias = []
    for linea in limpio.splitlines():
        linea = quitar_prefijos_editoriales(linea)
        if linea_no_publicable(linea):
            continue
        if re.search(r"https?://|www\.", linea, flags=re.IGNORECASE):
            continue
        linea = linea.strip()
        lineas_limpias.append(linea)
    salida = "\n".join(lineas_limpias)
    salida = re.sub(r"\n{3,}", "\n\n", salida)
    salida = re.sub(r"[ \t]{2,}", " ", salida)
    return salida.strip()


def asegurar_hashtags_editoriales(texto, titulo_original="", resumen_original=""):
    """Siempre deja exactamente 5 hashtags y la marca primero."""
    brand = get_brand_voice().get("brand", "")
    lineas = texto.splitlines()
    hashtags = []
    cuerpo = []
    for linea in lineas:
        tags_linea = re.findall(r"#[a-zA-Z0-9_\u00f1\u00d1]+", linea)
        if tags_linea and linea.strip().startswith("#"):
            hashtags.extend(tags_linea)
            continue
        cuerpo.append(linea)

    if not hashtags:
        hashtags = crear_hashtags(f"{titulo_original} {resumen_original}").split()

    if brand == "Daviet Gaming":
        hashtags = ["#davietgaming"] + [tag for tag in hashtags if tag.lower() != "#davietgaming"]
    elif brand == "El Gamer Cave":
        hashtags = ["#elgamercave"] + [tag for tag in hashtags if tag.lower() != "#elgamercave"]

    tags_finales = limitar_hashtags_texto(" ".join(hashtags), 5)
    cuerpo_limpio = "\n".join(cuerpo).strip()
    return f"{cuerpo_limpio}\n\n{tags_finales}".strip()


def asegurar_pregunta_final(texto, titulo_original="", estilo="news"):
    """El caption debe cerrar con una pregunta antes de hashtags."""
    partes = texto.strip().splitlines()
    if not partes:
        return texto

    hashtag_line = ""
    if partes[-1].strip().startswith("#"):
        hashtag_line = partes.pop().strip()

    cuerpo = "\n".join(partes).strip()
    if "?" not in cuerpo and "\u00bf" not in cuerpo:
        cuerpo = f"{cuerpo}\n\n{pregunta_engagement(titulo_original or cuerpo[:80], estilo)}".strip()

    if hashtag_line:
        return f"{cuerpo}\n\n{hashtag_line}".strip()
    return cuerpo


def caption_tiene_ingles_visible(texto):
    """Ignora nombres propios, pero detecta frases largas en ingles dentro del caption."""
    cuerpo = "\n".join(
        linea for linea in str(texto or "").splitlines()
        if not linea.strip().startswith("#")
    )
    return parece_texto_ingles(cuerpo)


def aplicar_reglas_editoriales_fuertes(post, item=None, estilo="news"):
    """
    Capa final sin IA: el caption visible debe quedar publicable.
    Reglas:
    - Espanol natural.
    - Sin links, fuentes, fechas, notas internas ni referencia usada.
    - Gancho, cuerpo y pregunta alineados.
    - Exactamente 5 hashtags y marca primero.
    """
    item = item or {}
    titulo_original = limpiar_html(item.get("title", "Tema gamer"))
    resumen_original = limpiar_html(item.get("summary", ""))
    nostalgia = limpiar_html(item.get("nostalgia_angle", ""))

    hashtags = crear_hashtags(f"{titulo_original} {resumen_original}")
    texto = limpiar_lineas_para_caption(post)

    if caption_tiene_ingles_visible(texto):
        texto = crear_post_limpio(
            titulo_publico_en_espanol(titulo_original, estilo),
            resumen_publico_en_espanol(titulo_original, resumen_original, estilo),
            estilo,
            nostalgia,
            hashtags,
        )
        texto = limpiar_lineas_para_caption(texto)

    texto = texto.replace("Eso conecta con Puede conectar con", "Eso conecta con")
    texto = texto.replace("conecta con Puede conectar con", "conecta con")
    texto = texto.replace("y la nostalgia gamer y la nostalgia gamer", "y la nostalgia gamer")
    texto = re.sub(r"\b20\d{2}\s+y\s+la nostalgia gamer\b", "nostalgia gamer", texto, flags=re.IGNORECASE)
    texto = asegurar_hashtags_editoriales(texto, titulo_original, resumen_original)
    texto = asegurar_pregunta_final(texto, titulo_original, estilo)
    texto = limpiar_texto_publicable_final(reparar_texto_roto(texto))
    texto = re.sub(r"\n{3,}", "\n\n", texto).strip()
    return texto


def crear_debate():
    prompt = buscar_prompt("debate")
    temas = TEMAS_COMUNIDAD + TEMAS_DEBATE
    respuesta = "Aquí tienes temas de debate geek para mover comentarios:\n\n"
    for i, tema in enumerate(temas[:10], start=1):
        respuesta += f"{i}. {tema}\n"
    respuesta += "\nÚsalos como conversación de comunidad, no como noticia confirmada."
    respuesta += "\n\nPregunta para comentar: ¿cuál de estos temas te prende más el debate?"
    if prompt:
        respuesta += f"\n\nReferencia usada: {prompt}"
    return respuesta


def crear_nostalgia(pregunta):
    tema = limpiar_tema_nostalgia(pregunta)
    if not tema:
        respuesta = "¿Sobre qué tema nostálgico quieres hablar?\n\n"
        for item in TEMAS_NOSTALGIA:
            respuesta += f"- {item}\n"
        return respuesta
    tema = normalizar_tema_contexto(tema)
    info = buscar_wikipedia(tema)
    contexto_local = buscar_contexto_local(tema)
    if not info and not contexto_local:
        return f"No encontré contexto histórico suficiente sobre **{tema}**. Prueba con GameCube, Game Boy, Pokémon o PlayStation 2."

    if not info:
        info = {
            "id": f"nostalgia-{uuid.uuid4()}",
            "title": tema,
            "summary": contexto_local.get("summary", ""),
            "source": contexto_local.get("provider", "Memoria Gamer Signal"),
        }

    st.session_state.generated_items[info["id"]] = info
    st.session_state.last_item_id = info["id"]
    prompt = buscar_prompt("nostalgia")
    contexto_extra = ""
    if contexto_local and contexto_local.get("summary") not in info.get("summary", ""):
        contexto_extra = contexto_local.get("summary", "")

    return f"""
### Contexto nostálgico: {info["title"]}

Esto no es noticia actual de {ANIO_NOTICIAS}. Es contexto histórico para hablar de nostalgia gamer.

Importante: Wikipedia queda como apoyo de contexto, no como fuente principal para publicar noticias.

{info["summary"]}

{contexto_extra}

**Referencia de apoyo:** {info["source"]}

**Ideas para post:**
- ¿Por qué marcó a una generación?
- ¿Qué recuerdos despierta en gamers de Puerto Rico y LatAm?
- ¿Cómo se compara con el gaming actual?
- ¿Qué pregunta puede generar comentarios?

**Referencia Gamer Cave usada:**
{prompt}

ID para feedback: `{info["id"]}`
"""


def formatear_noticias(noticias):
    noticias = filtrar_noticias_verificadas(noticias)
    if not noticias:
        return (
            f"No encontré noticias que pasen la verificación automática del año {ANIO_NOTICIAS}.\n\n"
            "Estoy filtrando solo fuentes oficiales o noticias confirmadas por varias fuentes."
        )
    respuesta = f"Busqué y filtré noticias verificadas del año {ANIO_NOTICIAS}.\n\n"
    respuesta += f"Rango usado: {FECHA_INICIO} hasta {FECHA_FINAL}\n\n"
    st.session_state.news_by_number = {}
    for numero, item in enumerate(noticias[:5], start=1):
        st.session_state.generated_items[item["id"]] = item
        st.session_state.last_item_id = item["id"]
        st.session_state.news_by_number[numero] = item
        titulo_visible = titulo_publico_en_espanol(item.get("title", ""), "news")
        respuesta += f"### Noticia {numero}: {titulo_visible}\n\n"
        respuesta += f"**Fecha:** {item['date']}\n\n"
        respuesta += f"**Fuente:** {item['source']}\n\n"
        respuesta += f"**Confianza:** {item['confidence_level']}\n\n"
        respuesta += f"**Verificación:** {item.get('verification_level', 'sin corroborar')}\n\n"
        if item.get("verification_sources"):
            respuesta += f"**Fuentes revisadas:** {', '.join(item['verification_sources'])}\n\n"
        respuesta += f"**Ángulo:** {item['content_angle']}\n\n"
        if item["nostalgia_angle"]:
            respuesta += f"**Ángulo nostálgico:** {reparar_texto_roto(item['nostalgia_angle'])}\n\n"
        respuesta += f"**Link:** {item['link']}\n\n"
        respuesta += f"ID para feedback: `{item['id']}`\n\n---\n\n"
    return respuesta


def crear_opciones_post_recientes():
    noticias = filtrar_noticias_verificadas(buscar_noticias())
    titulos_usados = set()
    st.session_state.news_by_number = {}
    respuesta = f"### Opciones de post para {ANIO_NOTICIAS}\n\n"
    respuesta += (
        "Te dejo ideas ya filtradas automáticamente. Las noticias pasan por verificación; "
        "debate y nostalgia se manejan como contenido editorial, no como noticia confirmada.\n\n"
    )

    for numero, categoria in enumerate(["gaming", "tecnologia", "nostalgia", "anime", "debate"], start=1):
        item = seleccionar_noticia_para_categoria(noticias, categoria, titulos_usados)
        if not item:
            item = crear_item_editorial_categoria(categoria, titulos_usados)

        st.session_state.generated_items[item["id"]] = item
        st.session_state.news_by_number[numero] = item
        st.session_state.last_item_id = item["id"]

        titulo = titulo_publico_en_espanol(item.get("title", "Noticia gamer"), "news")
        fuente = item.get("source", "Fuente no disponible")
        fecha = item.get("date", "")
        angulo = item.get("content_angle", "noticia")
        nostalgia = item.get("nostalgia_angle", "")

        if angulo == "nostalgia" or nostalgia:
            idea = "post nostálgico con conexión a recuerdos gamer"
        elif angulo == "debate":
            idea = "post de debate para generar comentarios"
        elif angulo == "anime":
            idea = "post de anime conectado con cultura gamer y comunidad"
        elif angulo in ["hardware", "technology"]:
            idea = "post de tecnología explicado para gamers"
        else:
            idea = "post informativo con pregunta para la comunidad"

        respuesta += f"**{numero}. {titulo}**\n\n"
        respuesta += f"- **Fuente:** {fuente}\n"
        respuesta += f"- **Fecha:** {fecha}\n"
        respuesta += f"- **Verificación:** {item.get('verification_level', 'idea editorial / no es noticia confirmada')}\n"
        if item.get("verification_sources"):
            respuesta += f"- **Fuentes revisadas:** {', '.join(item['verification_sources'])}\n"
        respuesta += f"- **Idea:** {idea}\n"
        respuesta += f"- **Ángulo:** {angulo}\n"
        if nostalgia:
            respuesta += f"- **Conexión nostálgica:** {reparar_texto_roto(nostalgia)}\n"
        respuesta += f"- **Para usarla:** crea post de la noticia {numero}\n\n"

    return respuesta


def detectar_marca_en_texto(texto):
    texto = texto.lower()
    limpio = " ".join(texto.split()).strip(" .,:;-")
    if limpio in ["daviet", "daviet gaming", "davietgaming"]:
        return "Daviet Gaming"
    if limpio in ["gamer cave", "el gamer cave", "el gamer"]:
        return "Gamer Cave"
    if limpio in ["general", "marca general"]:
        return "Gamer Cave"
    if "daviet gaming" in texto or "davietgaming" in texto or "para daviet" in texto:
        return "Daviet Gaming"
    if "el gamer cave" in texto or "gamer cave" in texto or "para el gamer" in texto:
        return "Gamer Cave"
    if "marca general" in texto or "para general" in texto:
        return "Gamer Cave"
    return None


def detectar_interes_editorial(texto):
    if any(p in texto for p in ["indie", "indies", "independiente", "next fest"]):
        return "indie"
    if any(p in texto for p in ["anime", "manga", "otaku"]):
        return "anime"
    if any(p in texto for p in ["tecnología", "tecnologia", "hardware", "pc gaming", "gpu"]):
        return "tecnologia"
    if any(p in texto for p in ["nostalgia", "retro", "clásico", "clasico", "remake", "remaster"]):
        return "nostalgia"
    if any(p in texto for p in ["debate", "opinión", "opinion", "controversia"]):
        return "debate"
    return None


def aplicar_marca_si_el_usuario_la_menciona(texto):
    marca = detectar_marca_en_texto(texto)
    if marca and marca in marcas_visibles():
        st.session_state.active_brand = marca
    elif marca:
        marca = "Gamer Cave"
        st.session_state.active_brand = marca
    return marca


def es_pedido_post(texto):
    return any(palabra in texto for palabra in ["post", "instagram", "facebook", "publicación", "publicacion", "caption"])


def es_respuesta_marca_simple(texto):
    marca = detectar_marca_en_texto(texto)
    if not marca:
        return False
    limpio = quitar_marca_de_texto(texto)
    return limpio in ["", "general"]


def pedir_marca_para_post(pregunta):
    st.session_state.pending_post_request = {
        "pregunta": pregunta,
        "created_at": ahora(),
    }
    if not es_modo_dueno():
        st.session_state.active_brand = "Gamer Cave"
        return "Lo hago para **Gamer Cave**."
    return (
        "¿Para cuál marca lo hago?\n\n"
        "Puedes responder: **Gamer Cave** o **Daviet Gaming**."
    )


def crear_lista_comandos():
    return """### Comandos útiles

- **hazme un post para Daviet Gaming**
- **hazme un post para Gamer Cave**
- **hazme un post**
- **créame 5 posts hot**
- **noticias oficiales de gaming**
- **opciones de post recientes**
- **contexto de GameCube**
- **busca información sobre Pokémon**
- **datos de Zelda**
- **cómo se juega Zelda**
- **modelos de Nintendo desde el primero hasta el actual**
- **debate gamer**
- **nostalgia gamer**
- **voy a publicar estos posts**
- **no repetir este tema**
- **más corto**
- **más debate**
- **más nostalgia**

Si pides un post sin marca, te voy a preguntar si es para Gamer Cave o Daviet Gaming."""


def es_comando_de_publicacion(texto):
    frases = [
        "voy a publicar",
        "voy publicar",
        "publicar estos post",
        "publicar estos posts",
        "publicar este post",
        "ya publiqué",
        "ya publique",
        "ya los publiqué",
        "ya los publique",
        "marcalos como usados",
        "márcalos como usados",
        "marcar como usados",
        "guardalos como usados",
        "guárdalos como usados",
        "los voy a usar",
        "voy a usar estos",
        "voy a usar estos post",
        "voy a usar estos posts",
        "voy a usar esos",
        "voy a usar esos post",
        "voy a usar esos posts",
        "esos los voy a usar",
        "estos los voy a usar",
        "los usare",
        "los usaré",
        "usare esos post",
        "usaré esos post",
        "usare esos posts",
        "usaré esos posts",
        "me quedo con esos",
        "me quedo con estos",
        "esos van",
        "estos van",
    ]
    return any(frase in texto for frase in frases)


def marcas_para_publicacion(texto):
    if es_modo_dueno() and any(p in texto for p in ["ambas marcas", "ambas marca", "las dos marcas", "las 2 marcas", "ambas"]):
        return ["Gamer Cave", "Daviet Gaming"]

    marca = detectar_marca_en_texto(texto)
    if marca and marca in marcas_visibles():
        return [marca]

    return [marca_permitida(st.session_state.get("active_brand", "Gamer Cave"))]


def marcar_ultimos_posts_como_publicados(texto):
    items = st.session_state.get("last_post_items", [])
    if not items:
        item = st.session_state.generated_items.get(st.session_state.get("last_item_id"))
        if item:
            items = [item]

    if not items:
        return "Todavía no tengo posts recientes para marcar como publicados. Primero crea uno o varios posts."

    marcas = marcas_para_publicacion(texto)
    for item in items:
        titulo = item.get("title", "post sin título")
        categoria = item.get("content_angle", "post")
        marcar_publicacion_usada(
            titulo,
            categoria,
            marcas,
            f"published by user for {', '.join(marcas)}"
        )

    marcas_texto = ", ".join(marcas)
    return f"Listo. Marqué {len(items)} post(s) como usados/publicados para: {marcas_texto}."


def responder(pregunta):
    texto = pregunta.lower()
    pending_post = st.session_state.get("pending_post_request")
    pending_calendar = st.session_state.get("pending_calendar_request", False)
    marca_mencionada = detectar_marca_en_texto(texto)

    if pending_calendar and marca_mencionada and es_respuesta_marca_simple(texto):
        st.session_state.active_brand = marca_mencionada
        st.session_state.pending_calendar_request = False
        return crear_calendario_contenido(marca_mencionada)
    elif pending_post and marca_mencionada and es_respuesta_marca_simple(texto):
        st.session_state.active_brand = marca_mencionada
        pregunta = f"{pending_post.get('pregunta', 'hazme un post')} para {marca_mencionada}"
        texto = pregunta.lower()
        st.session_state.pending_post_request = None
        marca_mencionada = marca_mencionada
    else:
        marca_mencionada = aplicar_marca_si_el_usuario_la_menciona(texto)

    numero = extraer_numero(texto)
    cantidad_posts = extraer_cantidad_posts(texto)

    preguntas_fecha_hora = [
        "qué día es hoy", "que dia es hoy", "fecha de hoy",
        "qué fecha es", "que fecha es", "qué hora es", "que hora es",
        "día y hora", "dia y hora", "fecha y hora",
    ]
    if any(frase in texto for frase in preguntas_fecha_hora):
        return f"Ahora mismo es **{fecha_hora_actual_texto()}**."

    if es_pedido_daily_briefing(texto) and es_pedido_post(texto):
        cantidad_radar = cantidad_posts if cantidad_posts > 1 else 1
        return crear_varios_posts(cantidad_radar, pregunta)

    if es_pedido_daily_briefing(texto):
        return daily_news_briefing()

    if es_pedido_monitor(texto):
        return responder_monitor(texto)

    if pide_cinco_hashtags(texto):
        guardar_regla_cinco_hashtags()
        if es_pedido_solo_hashtags(texto):
            return crear_respuesta_hashtags(pregunta)

    if es_comando_de_publicacion(texto):
        return marcar_ultimos_posts_como_publicados(texto)

    if "opciones de post" in texto or "ideas de post" in texto or "ideas para post" in texto:
        return crear_opciones_post_recientes()

    if es_pedido_contexto(texto):
        return crear_contexto_api(pregunta)

    if "comandos" in texto or "lista de comandos" in texto or "ayuda" in texto:
        return crear_lista_comandos()

    if "calendario" in texto or "plan semanal" in texto:
        return crear_calendario_contenido(marca_mencionada)

    if "guardar post" in texto or "exportar post" in texto:
        if not st.session_state.get("last_post_text"):
            return "Todavía no hay un post para guardar. Primero crea uno con: crea un post para Instagram."
        archivo = guardar_post_aprobado(st.session_state.last_post_text, st.session_state.get("last_post_title", "post_gamer"))
        return f"Listo. Guardé el post en:\n\n`{archivo}`"

    if texto.startswith("aprobar") or "me gusta" in texto:
        accion = save_feedback(st.session_state.last_item_id, "news/post/topic", "approved", pregunta)
        extra = ""
        if st.session_state.get("last_post_text"):
            archivo = guardar_post_aprobado(st.session_state.last_post_text, st.session_state.get("last_post_title", "post_gamer"))
            extra = f"\n\nTambién guardé el último post aprobado en:\n\n`{archivo}`"
        return f"Listo. Guardé tu aprobación.\n\nAcción: {accion}{extra}"
    if texto.startswith("rechazar") or "no me gusta" in texto:
        accion = save_feedback(st.session_state.last_item_id, "news/post/topic", "rejected", pregunta)
        return f"Listo. Guardé el rechazo.\n\nAcción: {accion}"
    if (
        texto.startswith("corrige")
        or "no digas" in texto
        or "más corto" in texto
        or "mas corto" in texto
        or "más nostalgia" in texto
        or "mas nostalgia" in texto
        or "más debate" in texto
        or "mas debate" in texto
        or "no repetir" in texto
    ):
        accion = save_feedback(st.session_state.last_item_id, "post/topic", "correction", pregunta)
        return f"Listo. Guardé esa corrección.\n\nAcción: {accion}"
    if "ver prompts" in texto:
        prompts = get_prompt_library()
        if not prompts:
            return "No encontré prompts guardados en prompts/prompt_library.json."
        return "### Prompts guardados\n\n" + "\n\n".join(
            f"**{p.get('name', 'sin nombre')}**\n{p.get('prompt', '')}"
            for p in prompts
        )
    if "ver voz de marca" in texto:
        brand = get_brand_voice()
        if not brand:
            return "No encontré la voz de marca en prompts/brand_voice.json."
        return f"### Voz de marca\n\n```json\n{json.dumps(brand, ensure_ascii=False, indent=2)}\n```"
    if "memoria" in texto or "preferencias" in texto:
        prefs = get_user_preferences()
        if not prefs:
            return "Todavía no hay preferencias guardadas."
        return "### Memoria actual\n\n" + "\n".join(
            f"- **{p['key']}**: {p['value']} | peso: {p['weight']}"
            for p in prefs
        )
    if es_pedido_post(texto):
        estilo = st.session_state.get("post_style", "all")
        if "corto" in texto:
            estilo = "corto"
        elif "debate" in texto:
            estilo = "debate"
        elif "emocional" in texto:
            estilo = "emocional"
        elif "noticia" in texto:
            estilo = "noticia"

        tema_manual = limpiar_pedido_post(pregunta)
        pedido_generico = tema_manual in ["", "nuevo", "nueva", "redes", "publicar", "hot", "viral", "del dia", "del día"]

        if not marca_mencionada and pedido_generico and not numero:
            return pedir_marca_para_post(pregunta)

        if cantidad_posts > 1 and not es_pedido_de_noticia_numerada(texto):
            return crear_varios_posts(cantidad_posts, pregunta)

        if numero:
            item = seleccionar_item_por_numero(numero)
        elif (
            pedido_generico
            or "noticia" in texto
            or "actual" in texto
            or "reciente" in texto
            or detectar_interes_editorial(texto)
        ):
            item = elegir_noticia_nueva_para_post(detectar_interes_editorial(texto))
        else:
            estilo_manual = "nostalgia" if estilo == "all" else estilo
            item = crear_item_desde_pedido(pregunta, estilo_manual)

        if not item:
            return (
                "No encontré una noticia verificada nueva para crear el post. "
                "Estoy usando filtro estricto: fuente oficial o confirmación por 2+ fuentes. "
                "Puedes pedirme un debate, nostalgia u opinión si quieres contenido editorial."
            )

        post = generate_social_post(item, estilo)
        st.session_state.last_post_items = [item]
        return post
    if any(p in texto for p in ["nostalgia", "retro", "clásico", "clasico", "viejo", "antiguo"]):
        return crear_nostalgia(pregunta)
    if any(p in texto for p in ["debate", "opinión", "opinion", "vs", "versus"]):
        return crear_debate()
    return formatear_noticias(buscar_noticias())


preparar_memoria()
registrar_acceso_simple()

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {
            "role": "assistant",
            "content": "Hola. Soy Gamer Signal. Pregúntame por noticias gamer, nostalgia, debates o posts para Instagram/Facebook.",
        }
    ]

if "generated_items" not in st.session_state:
    st.session_state.generated_items = {}

if "last_item_id" not in st.session_state:
    st.session_state.last_item_id = None

if "news_by_number" not in st.session_state:
    st.session_state.news_by_number = {}

if "last_post_text" not in st.session_state:
    st.session_state.last_post_text = ""

if "last_post_title" not in st.session_state:
    st.session_state.last_post_title = "post_gamer"

if "last_post_items" not in st.session_state:
    st.session_state.last_post_items = []

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None

if "pending_post_request" not in st.session_state:
    st.session_state.pending_post_request = None

if "pending_calendar_request" not in st.session_state:
    st.session_state.pending_calendar_request = False

if "active_brand" not in st.session_state:
    st.session_state.active_brand = "Gamer Cave"
elif st.session_state.active_brand == "General":
    st.session_state.active_brand = "Gamer Cave"
elif st.session_state.active_brand not in marcas_visibles():
    st.session_state.active_brand = "Gamer Cave"

if "monitor_active" not in st.session_state:
    st.session_state.monitor_active = True

if "monitor_interval_minutes" not in st.session_state:
    st.session_state.monitor_interval_minutes = RADAR_REFRESH_MINUTES

if "monitor_last_run" not in st.session_state:
    st.session_state.monitor_last_run = None

if "monitor_new_count" not in st.session_state:
    st.session_state.monitor_new_count = 0

header_mascot = assistant_mascot_data_url()
header_mascot_html = (
    f'<div class="gamer-signal-logo mascot"><img src="{header_mascot}" alt="Mascota asistente"></div>'
    if header_mascot else '<div class="gamer-signal-logo">GS</div>'
)
st.markdown(
    f"""
    <div class="gamer-signal-header">
        {header_mascot_html}
        <h1 class="gamer-signal-title">Gamer Signal</h1>
        <div class="gamer-signal-subtitle">Noticias, nostalgia gamer, debates y posts para tus marcas.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
render_reloj_actual()
activar_auto_refresh_10_minutos()

if st.session_state.get("monitor_active"):
    try:
        ultimo = st.session_state.get("monitor_last_run")
        debe_revisar = True
        if ultimo:
            ultimo_dt = datetime.fromisoformat(ultimo)
            debe_revisar = (ahora_en_puerto_rico() - ultimo_dt).total_seconds() >= RADAR_REFRESH_MINUTES * 60
        if debe_revisar:
            monitor_revisar_fuentes()
    except Exception:
        pass

with st.sidebar:
    st.header("Memoria")
    st.write("Aprendo solo cuando apruebas, rechazas o corriges.")

    st.subheader("Modo Gamer Cave")
    st.session_state.post_style = st.selectbox(
        "Estilo de post",
        ["all", "nostalgia", "emocional", "debate", "noticia", "corto"],
        index=0
    )

    st.caption("Tip: puedes escribir 'post de la noticia 2' para usar una noticia específica.")

    if st.button("Borrar toda la memoria"):
        borrar_memoria()
        st.success("Memoria borrada.")
    st.divider()
    st.subheader("Editar preferencia")
    pref_key = st.text_input("key", placeholder="preferred_category")
    pref_value = st.text_input("value", placeholder="nostalgia gaming")
    pref_weight = st.number_input("weight", min_value=-10, max_value=10, value=1)
    if st.button("Guardar preferencia"):
        if pref_key and pref_value:
            update_preference(pref_key, pref_value, pref_weight, "manual sidebar edit")
            st.success("Preferencia guardada.")
    if st.button("Borrar preferencia"):
        if pref_key and pref_value:
            borrar_preferencia(pref_key, pref_value)
            st.success("Preferencia borrada.")

    st.divider()
    st.subheader("Monitor")
    st.session_state.monitor_active = st.toggle("Monitor activo", value=st.session_state.monitor_active)
    st.session_state.monitor_interval_minutes = st.selectbox(
        "Revisar cada",
        [5, 10, 15, 30, 60],
        index=[5, 10, 15, 30, 60].index(st.session_state.monitor_interval_minutes)
        if st.session_state.monitor_interval_minutes in [5, 10, 15, 30, 60] else 2,
        format_func=lambda x: f"{x} min",
    )
    if st.button("Revisar monitor ahora"):
        nuevos = monitor_revisar_fuentes(force=True)
        st.success(f"Monitor revisado. Nuevos: {len(nuevos)}")
        st.rerun()
    st.caption(f"Ultima revision: {st.session_state.monitor_last_run or 'pendiente'}")
    st.caption(f"Nuevos en la ultima revision: {st.session_state.monitor_new_count}")
    log_monitor = leer_json(MONITOR_FILE, [])
    if log_monitor:
        with st.expander("Ultimos hallazgos", expanded=False):
            for item in log_monitor[:5]:
                st.write(f"- {titulo_publico_en_espanol(item.get('title', ''), 'news')} | {item.get('source', '')}")

    st.divider()
    st.subheader("Temas usados")
    usados = leer_json(USED_FILE, [])
    if usados:
        for item in list(reversed(usados))[:8]:
            st.write(f"- {item.get('topic', 'tema')} ({item.get('category', 'general')})")
    else:
        st.write("Todavía no hay temas usados.")
    st.divider()
    st.subheader("Preferencias guardadas")
    prefs = get_user_preferences()
    if prefs:
        st.json(prefs)
    else:
        st.write("No hay preferencias guardadas todavía.")

    render_access_log_simple()

def render_daily_radar_panel():
    left, center, right = st.columns([1, 1.6, 1])
    with center:
        if st.button("Actualizar radar", key="refresh_daily_radar", use_container_width=True):
            nuevos = monitor_revisar_fuentes(force=True)
            st.session_state.monitor_new_count = len(nuevos)
            st.success(f"Radar actualizado. Nuevos: {len(nuevos)}")
            st.rerun()

    action_cols = st.columns([1, 1, 1])
    with action_cols[0]:
        st.button("Crear post del radar", key="radar_make_post", use_container_width=True, on_click=set_quick_prompt, args=("usa el radar diario para crear un post",))
    with action_cols[1]:
        st.button("5 posts del radar", key="radar_make_5_posts", use_container_width=True, on_click=set_quick_prompt, args=("usa el radar diario para 5 posts",))
    with action_cols[2]:
        st.button("Debate del radar", key="radar_make_debate", use_container_width=True, on_click=set_quick_prompt, args=("hazme un post de debate del radar",))

    log = leer_json(MONITOR_FILE, [])
    if not log:
        try:
            monitor_revisar_fuentes()
            log = leer_json(MONITOR_FILE, [])
        except Exception:
            log = []

    memoria = monitor_actualizar_memoria_marca(log) if log else {
        "brands": {"Gamer Cave": [], "Daviet Gaming": []},
        "buckets": {},
    }
    fecha = html_escape(fecha_hora_actual_texto())
    descripciones_marca = {
        "Gamer Cave": "8Bit busca temas para comunidad, nostalgia, anime, debate y noticias gamer.",
        "Daviet Gaming": "Dragon Pixel busca gaming, PC, tecnologia, cultura geek y posts con enfoque creativo.",
    }
    marcas = [(marca, descripciones_marca[marca]) for marca in marcas_visibles()]
    brand_grid_class = "two-brands" if len(marcas) > 1 else "single-brand"
    categorias = [
        ("noticia_actual", "Actualidad"),
        ("debate", "Debate"),
        ("nostalgia", "Nostalgia"),
        ("tecnologia", "Tecnologia"),
        ("anime", "Anime / Geek"),
        ("indie", "Indie"),
    ]

    brand_cards = []
    for marca, fallback in marcas:
        items = memoria.get("brands", {}).get(marca, [])[:1]
        logo = html_escape(logo_data_url(marca), quote=True)
        if items:
            item = items[0]
            titulo = html_escape(titulo_visible_seguro(item, "news"))
            fuente = html_escape(item.get("source", "fuente"))
            color, verificacion = estado_verificacion_item(item)
            angulo = html_escape(item.get("angle", fallback))
            contenido = (
                f'<div class="daily-radar-item"><strong>{titulo}</strong><br>{fuente}</div>'
                f'<div class="daily-radar-angle">Verificacion: {html_escape(color)} - {html_escape(verificacion)}</div>'
                f'<div class="daily-radar-angle">{angulo}</div>'
            )
        else:
            contenido = f'<div class="daily-radar-item">{html_escape(fallback)}</div>'
        brand_cards.append(
            f'<div class="daily-radar-card daily-radar-brand-card">'
            f'<div class="daily-radar-brand-heading">'
            f'<img src="{logo}" alt="{html_escape(marca)}">'
            f'<span>{html_escape(marca)}</span>'
            f'</div>'
            f'{contenido}'
            f'</div>'
        )

    cards = []
    for bucket, label in categorias:
        items = memoria.get("buckets", {}).get(bucket, [])[:1]
        if items:
            item = items[0]
            titulo = html_escape(titulo_visible_seguro(item, "news", bucket))
            fuente = html_escape(item.get("source", "fuente"))
            color, verificacion = estado_verificacion_item(item)
            contenido = (
                f'<div class="daily-radar-item"><strong>{titulo}</strong><br>{fuente}</div>'
                f'<div class="daily-radar-angle">Verificacion: {html_escape(color)} - {html_escape(verificacion)}</div>'
                f'<div class="daily-radar-angle">{html_escape(angulo_para_bucket(bucket))}</div>'
            )
        else:
            contenido = '<div class="daily-radar-item">Buscando una oportunidad buena, no cualquier noticia.</div>'
        cards.append(
            f'<div class="daily-radar-card">'
            f'<div class="daily-radar-brand">{html_escape(label)}</div>'
            f'{contenido}'
            f'</div>'
        )

    st.markdown(
        f"""
        <div class="daily-radar-panel">
            <div class="daily-radar-header">
                <div class="daily-radar-title">Radar diario</div>
                <div class="daily-radar-date">{fecha}</div>
            </div>
            <div class="daily-radar-section-title">Oportunidades por marca</div>
            <div class="daily-radar-grid daily-radar-brand-grid {brand_grid_class}">
                {''.join(brand_cards)}
            </div>
            <div class="daily-radar-section-title">Temas calientes por categoria</div>
            <div class="daily-radar-grid">
                {''.join(cards)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


pregunta = st.chat_input("Pregunta por noticias, nostalgia, debates, posts, prompts o memoria...")

if st.session_state.quick_prompt:
    pregunta = st.session_state.quick_prompt
    st.session_state.quick_prompt = None

if pregunta:
    st.session_state.mensajes.append({"role": "user", "content": pregunta})
    respuesta = responder(pregunta)
    es_post = bool(st.session_state.get("last_post_text")) and respuesta == st.session_state.last_post_text
    st.session_state.mensajes.append({
        "role": "assistant",
        "content": respuesta,
        "type": "post" if es_post else "text",
    })

chat_iniciado = any(mensaje.get("role") == "user" for mensaje in st.session_state.mensajes)

render_control_bar()
render_daily_radar_panel()

for mensaje in st.session_state.mensajes:
    avatar = assistant_mascot_avatar() if mensaje["role"] == "assistant" else None
    chat_ctx = st.chat_message(mensaje["role"], avatar=avatar) if avatar else st.chat_message(mensaje["role"])
    with chat_ctx:
        if mensaje.get("type") == "post":
            render_post_response(mensaje["content"])
        else:
            st.write(mensaje["content"])

if chat_iniciado:
    render_last_post_box()
