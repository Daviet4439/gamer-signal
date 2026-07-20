# -*- coding: utf-8 -*-

import json
import re
import uuid
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from html import unescape as html_unescape
from html import escape as html_escape
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

import feedparser
import streamlit as st
from streamlit.components.v1 import html as components_html


APP_VERSION = "2026.07.20-2"

st.set_page_config(page_title="Gamer Signal", page_icon="\U0001F4E1", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2family=Inter:wght@400;600;700;800;900&family=Orbitron:wght@700;800;900&family=Rajdhani:wght@600;700&display=swap');

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

    .corner-gs-logo {
        position: fixed;
        top: 92px;
        right: 22px;
        z-index: 999;
        width: 52px;
        height: 52px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: "Orbitron", "Inter", sans-serif;
        font-size: 18px;
        font-weight: 900;
        color: var(--gc-white);
        background:
            radial-gradient(circle at 70% 24%, rgba(255, 255, 255, 0.95), transparent 10%),
            linear-gradient(135deg, var(--gc-gold) 0%, var(--gc-red) 48%, var(--gc-black) 100%);
        border: 1px solid rgba(255, 215, 0, 0.75);
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.20), 0 12px 30px rgba(225, 6, 0, 0.18);
        pointer-events: none;
    }

    .corner-gs-logo::before,
    .corner-gs-logo::after {
        content: "";
        position: absolute;
        border: 2px solid rgba(255, 255, 255, 0.78);
        border-left-color: transparent;
        border-bottom-color: transparent;
        border-radius: 50%;
        transform: rotate(-25deg);
    }

    .corner-gs-logo::before {
        width: 34px;
        height: 34px;
    }

    .corner-gs-logo::after {
        width: 24px;
        height: 24px;
    }

    .corner-gs-logo span {
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.55);
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

    .gamer-signal-build {
        color: rgba(255, 215, 0, 0.68);
        font-size: 11px;
        margin-top: 8px;
        font-family: "Rajdhani", "Inter", sans-serif;
        letter-spacing: 0;
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

    .post-section-title {
        text-align: center;
        color: var(--gc-white);
        font-family: "Orbitron", "Inter", sans-serif;
        font-size: 24px;
        font-weight: 900;
        line-height: 1.2;
        margin: 30px auto 16px auto;
        letter-spacing: 0;
    }

    @media (max-width: 760px) {
        .corner-gs-logo {
            top: 72px;
            right: 12px;
            width: 42px;
            height: 42px;
            border-radius: 13px;
            font-size: 15px;
        }

        .corner-gs-logo::before {
            width: 28px;
            height: 28px;
        }

        .corner-gs-logo::after {
            width: 20px;
            height: 20px;
        }

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
        "lunes", "martes", "mi\u00e9rcoles", "jueves",
        "viernes", "s\u00e1bado", "domingo",
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
                fecha + " \u00b7 " + hora + " \u00b7 Puerto Rico";
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
FECHA_FINAL = HOY

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
NEWS_CACHE_TTL_SECONDS = 600
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
    "Crunchyroll News oficial": "https://www.crunchyroll.com/news/rss",
    "Anime News Network confiable": "https://www.animenewsnetwork.com/all/rss.xml?ann-edition=us",
    "MyAnimeList News confiable": "https://myanimelist.net/rss/news.xml",
    "Anime Corner confiable": "https://animecorner.me/feed/",
    "VIZ Blog oficial": "https://www.viz.com/blog/rss",

    # Tecnolog\u00eda oficial
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
    "GamesIndustry.biz confiable": "https://www.gamesindustry.biz/feed",
    "Siliconera confiable": "https://www.siliconera.com/feed/",
    "Nintendo Life confiable": "https://www.nintendolife.com/feeds/latest",
    "Engadget confiable": "https://www.engadget.com/rss.xml",
    "TechCrunch AI confiable": "https://techcrunch.com/category/artificial-intelligence/feed/",
}

FUENTES_COMUNIDAD = {
    "Reddit Gaming - se\u00f1al de comunidad": "https://www.reddit.com/r/gaming/top/.rss?t=day",
    "Reddit Games - se\u00f1al de comunidad": "https://www.reddit.com/r/Games/top/.rss?t=day",
    "Reddit TrueGaming - se\u00f1al de debate": "https://www.reddit.com/r/truegaming/top/.rss?t=week",
    "Reddit PatientGamers - se\u00f1al nostalgia": "https://www.reddit.com/r/patientgamers/top/.rss?t=week",
    "Reddit RetroGaming - se\u00f1al nostalgia": "https://www.reddit.com/r/retrogaming/top/.rss?t=week",
    "Reddit Nintendo - se\u00f1al comunidad": "https://www.reddit.com/r/nintendo/top/.rss?t=week",
    "Reddit PlayStation - se\u00f1al comunidad": "https://www.reddit.com/r/playstation/top/.rss?t=week",
    "Reddit Xbox - se\u00f1al comunidad": "https://www.reddit.com/r/xbox/top/.rss?t=week",
    "Reddit PCGaming - se\u00f1al comunidad": "https://www.reddit.com/r/pcgaming/top/.rss?t=week",
    "Reddit IndieGaming - se\u00f1al indie": "https://www.reddit.com/r/indiegaming/top/.rss?t=week",
    "Reddit IndieDev - se\u00f1al indie/dev": "https://www.reddit.com/r/IndieDev/top/.rss?t=week",
    "Reddit Anime - se\u00f1al anime": "https://www.reddit.com/r/anime/top/.rss?t=day",
    "Reddit Manga - se\u00f1al anime": "https://www.reddit.com/r/manga/top/.rss?t=week",
    "Reddit JRPG - se\u00f1al fandom": "https://www.reddit.com/r/JRPG/top/.rss?t=week",
    "Reddit FanTheories - teor\u00edas geek": "https://www.reddit.com/r/FanTheories/top/.rss?t=week",
    "Reddit GamingLeaksAndRumours - rumores comunidad": "https://www.reddit.com/r/GamingLeaksAndRumours/top/.rss?t=day",
    "Reddit Argaming - se\u00f1al LatAm": "https://www.reddit.com/r/Argaming/top/.rss?t=week",
    "Reddit VideojuegosMX - se\u00f1al M\u00e9xico": "https://www.reddit.com/r/videojuegosMX/top/.rss?t=week",
}

TEMAS_DEBATE = [
    "Juegos f\u00edsicos vs juegos digitales",
    "Battle pass y microtransacciones",
    "Juegos incompletos de lanzamiento",
    "Multiplayer local vs online",
    "Remakes vs juegos nuevos",
    "Nostalgia vs innovaci\u00f3n",
    "Consolas vs PC",
    "Game Pass, PS Plus y suscripciones",
    "Juegos que necesitan conexi\u00f3n permanente",
    "IA en videojuegos",
    "Comunidades t\u00f3xicas en juegos online",
    "Precios de videojuegos",
]

TEMAS_COMUNIDAD = [
    "\u00bfLos juegos f\u00edsicos todav\u00eda tienen valor o ya todo se fue digital",
    "\u00bfLos remakes nos emocionan porque son buenos o porque extra?amos otra ?poca",
    "\u00bfGame Pass y PS Plus cambiaron la forma en que valoramos los juegos",
    "\u00bfEl multiplayer local se siente m\u00e1s especial que jugar online",
    "\u00bfLos juegos como servicio est\u00e1n cansando a la comunidad",
    "\u00bfLa IA en videojuegos puede ayudar o le quita alma al desarrollo",
    "\u00bfLas ediciones deluxe y los precios actuales est\u00e1n alejando a los jugadores",
    "\u00bfLos trailers muestran demasiado antes de que salga un juego",
]

TEMAS_ANIME = [
    "anime de temporada y el hype que se forma antes de los estrenos",
    "regresos de animes cl\u00e1sicos que despiertan nostalgia",
    "adaptaciones de manga que la comunidad espera con miedo y emoci\u00f3n",
    "peleas, openings y momentos de anime que se vuelven conversaci\u00f3n gamer",
    "anime que conect\u00f3 con gamers por sus mundos, poderes o esp\u00edritu de aventura",
]

TEMAS_NOSTALGIA = [
    "Game Boy",
    "GameCube",
    "Nintendo 64",
    "PlayStation 1",
    "PlayStation 2",
    "PlayStation 3",
    "Xbox cl\u00e1sico",
    "Xbox 360",
    "Pok\u00e9mon",
    "Mario",
    "Kirby",
    "The Legend of Zelda",
    "Rayman",
    "Crazy Taxi",
    "juegos f\u00edsicos",
    "cartuchos",
    "discos",
    "manuales de juegos",
    "multiplayer local",
    "memory cards",
    "pantallas divididas",
    "jugar con primos o amigos",
    "llegar de la escuela y prender la consola",
    "cibercaf?s",
    "juegos que nunca terminaste",
    "juegos que daban miedo de peque\u00f1o",
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
    "Pok\u00e9mon": {
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
    "AnimeStudios": [
        ("Crunchyroll News oficial", "https://www.crunchyroll.com/news", "noticias oficiales, trailers, fechas y anuncios de anime"),
        ("Anime News Network confiable", "https://www.animenewsnetwork.com/", "contraste de noticias de anime, manga e industria"),
        ("MyAnimeList News confiable", "https://myanimelist.net/news", "contexto de anime, manga, staff, estudios y fechas"),
        ("MangaPlus oficial", "https://mangaplus.shueisha.co.jp/updates", "actualizaciones oficiales de manga disponible en MangaPlus"),
        ("Aniplex oficial", "https://www.aniplex.co.jp/", "pagina oficial para confirmar proyectos, trailers y franquicias"),
        ("Bandai Namco Filmworks oficial", "https://www.bnfw.co.jp/", "pagina oficial para confirmar producciones y anuncios"),
        ("KADOKAWA Anime oficial", "https://www.kadokawa.co.jp/global/", "pagina oficial para contexto de anime, manga y publicaciones"),
        ("Toei Animation oficial", "https://corp.toei-anim.co.jp/en/press/", "comunicados y anuncios oficiales de Toei Animation"),
        ("MAPPA oficial", "https://www.mappa.co.jp/en/", "pagina oficial del estudio para confirmar proyectos y staff"),
        ("ufotable oficial", "https://www.ufotable.com/", "pagina oficial del estudio para confirmar producciones"),
        ("Kyoto Animation oficial", "https://www.kyotoanimation.co.jp/en/", "pagina oficial del estudio para contexto de proyectos"),
        ("Production I.G oficial", "https://www.production-ig.co.jp/", "pagina oficial del estudio para producciones y anuncios"),
        ("Studio Trigger oficial", "https://www.st-trigger.co.jp/", "pagina oficial del estudio para noticias y proyectos"),
    ],
}


NICHO_PR_LATAM = {
    "region": "Puerto Rico y Latinoam\u00e9rica",
    "audience": [
        "gamers adultos que crecieron con consolas, rentals, juegos f\u00edsicos, multiplayer local y tardes jugando con amistades o familia",
        "jugadores que consumen PlayStation, Xbox, Nintendo, PC gaming, anime, tecnolog\u00eda, cultura geek y entretenimiento digital",
        "comunidad que comenta m\u00e1s cuando el tema toca precio, nostalgia, valor real para el jugador, hype, decepci\u00f3n, exclusivas o cambios en la industria",
    ],
    "engagement_goals": [
        "convertir noticias calientes en conversaci\u00f3n f\u00e1cil de comentar",
        "informar primero y luego abrir debate sano",
        "conectar noticias actuales con recuerdos, experiencias y h\u00e1bitos de gamers de Puerto Rico y LatAm",
        "evitar posts fr\u00edos; cada publicaci\u00f3n debe tener un \u00e1ngulo humano o comunitario",
    ],
    "hot_angles": [
        "precio, valor y si realmente vale la pena",
        "juegos f\u00edsicos vs digitales",
        "servicios como Game Pass, PS Plus, Nintendo Switch Online y suscripciones",
        "nostalgia de consolas viejas, cartuchos, discos, manuales y multiplayer local",
        "hype vs realidad cuando anuncian trailers, remakes, remasters o secuelas",
        "tecnolog\u00eda explicada desde c\u00f3mo afecta al gamer com\u00fan",
        "anime, cultura geek y gaming cuando mueven conversaci\u00f3n de comunidad",
    ],
    "rules": [
        "priorizar noticias hot que puedan generar comentarios, no solo anuncios informativos",
        "si una noticia es verificada, convertirla en una pregunta o debate \u00fatil para la comunidad",
        "si el tema es nostalgia u opini\u00f3n, no presentarlo como noticia confirmada",
        "hablar en espa\u00f1ol natural para Puerto Rico y LatAm; usar ingl\u00e9s solo en nombres oficiales",
        "mantener respeto entre plataformas, fandoms y comunidades",
        "cerrar con una pregunta clara que invite a comentar sin sonar desesperada",
    ],
}

PALABRAS_HOT_NICHO = [
    "nintendo", "switch", "playstation", "ps5", "ps plus", "xbox", "game pass",
    "steam", "pc gaming", "pokemon", "pok\u00e9mon", "mario", "zelda", "kirby",
    "anime", "manga", "crunchyroll", "nvidia", "rtx", "gpu", "hardware",
    "capcom", "resident evil", "monster hunter", "street fighter", "ea", "battlefield",
    "ubisoft", "assassin", "riot", "league of legends", "valorant", "blizzard",
    "diablo", "overwatch", "warcraft", "epic games", "fortnite", "unreal engine",
    "unity", "intel", "amd", "myanimelist", "anime news network",
    "remake", "remaster", "sequel", "demo", "gratis", "free", "precio",
    "subscription", "suscripci\u00f3n", "dlc", "battle pass", "microtransacciones",
    "physical", "digital", "f\u00edsico", "fisico", "multiplayer", "coop",
]

SENALES_TENDENCIA = {
    "movimiento fuerte": [
        "viral", "trending", "record", "r\u00e9cord", "million", "mill\u00f3n",
        "sales", "ventas", "best seller", "top played", "most played",
        "players", "jugadores", "wishlists", "lista de deseados",
    ],
    "actualidad": [
        "announces", "anuncia", "reveals", "revela", "launch", "lanza",
        "release", "estreno", "update", "actualizaci\u00f3n", "trailer", "tr\u00e1iler",
        "demo", "beta", "early access", "acceso anticipado",
    ],
    "conversaci\u00f3n": [
        "precio", "price", "delay", "retraso", "cancel", "cancela",
        "physical", "f\u00edsico", "digital", "subscription", "suscripci\u00f3n",
        "microtransaction", "microtransacci\u00f3n", "exclusive", "exclusiva",
    ],
    "nostalgia activa": [
        "anniversary", "aniversario", "remake", "remaster", "reboot",
        "classic", "cl\u00e1sico", "retro", "collection", "colecci?n",
    ],
}

SENALES_INDIE = [
    "indie", "independent", "independiente", "small team", "solo developer",
    "steam next fest", "next fest", "indie world", "kickstarter",
    "debut game", "debut project", "primer juego", "estudio independiente",
]

CATEGORIA_SENALES = {
    "anime": [
        "anime", "manga", "crunchyroll", "myanimelist", "anime news network",
        "anime corner", "shonen", "shojo", "seinen", "isekai", "otaku",
        "visual", "opening", "ending", "temporada", "adaptacion", "adaptación",
        "serialization", "serializacion", "serialización",
    ],
    "tecnologia": [
        "hardware", "gpu", "rtx", "nvidia", "amd", "intel", "processor",
        "cpu", "pc gaming", "steam deck", "handheld", "asus rog", "msi",
        "ios", "macos", "apple", "beta", "unreal engine", "unity engine",
        "godot", "developer tools", "inteligencia artificial", "artificial intelligence",
        "generative ai", "openai", "cloud gaming", "ray tracing", "rendimiento",
    ],
    "indie": [
        "indie", "indies", "independent", "independiente", "small team",
        "solo developer", "steam next fest", "next fest", "kickstarter",
        "debut game", "debut project", "primer juego", "estudio independiente",
        "demo", "early access", "acceso anticipado",
    ],
    "debate": [
        "debate", "vs", "versus", "precio", "price", "delay", "retraso",
        "cancel", "cancelado", "layoff", "layoffs", "despidos", "workers",
        "subscription", "suscripcion", "suscripción", "game pass", "ps plus",
        "battle pass", "microtransaction", "microtransacciones", "physical",
        "fisico", "físico", "digital", "exclusive", "exclusiva",
        "review bombing", "controversia",
    ],
    "nostalgia": [
        "nostalgia", "retro", "classic", "clasico", "clásico", "collection",
        "coleccion", "colección", "anniversary", "aniversario", "remake",
        "remaster", "reboot", "preservation", "preservacion", "preservación",
        "cartucho", "disco", "manual", "multiplayer local", "memory card",
        "gamecube", "game boy", "nintendo 64", "ps1", "ps2", "xbox 360",
    ],
}

ACCION_PATRONES_TITULO = [
    (r"\b(trailer|teaser|visual|avance|gameplay)\b", "{tema}: nuevo avance para comentar"),
    (r"\b(update|patch|details|detailed|version|actualizacion|actualización)\b", "{tema}: nuevos detalles para jugadores"),
    (r"\b(pre[- ]order|preorder|preventa)\b", "{tema}: preventa disponible"),
    (r"\b(release date|launch|launches|coming|lanzamiento|estreno)\b", "{tema}: lanzamiento bajo la lupa"),
    (r"\b(monthly games|free play days|game catalog|ps plus|game pass|juegos incluidos)\b", "Juegos incluidos este mes para comentar"),
    (r"\b(concludes|serialization|ends|ending|termina|cierre)\b", "{tema}: cierre importante para el fandom"),
    (r"\b(anime adaptation|getting an anime|adaptation|adaptacion|adaptación)\b", "{tema}: adaptación anime en camino"),
    (r"\b(preservation|program|classic|collection|remaster|remake)\b", "{tema}: preservación gamer para comentar"),
    (r"\b(layoffs|fired workers|visas|workers|despidos)\b", "{tema}: cambios en la industria para debatir"),
    (r"\b(public betas|ios|macos|platforms|gpu|hardware|rtx|nvidia|amd|intel)\b", "{tema}: tecnología gamer para mirar con calma"),
    (r"\b(physical|digital|fisico|físico)\b", "Los juegos físicos vuelven al debate"),
    (r"\b(joins|following|vote|patron)\b", "{tema}: movimiento para comentar"),
    (r"\b(turns|becomes|into|bosses|friends)\b", "{tema}: mecánica nueva para comentar"),
    (r"\b(refutes|notion|claims|responds)\b", "{tema}: respuesta oficial para debatir"),
    (r"\b(drops|increases|recommendation|recommended)\b", "{tema}: requisito técnico bajo la lupa"),
]


def _texto_categoria_desde_item(item):
    if isinstance(item, dict):
        texto = f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}"
    else:
        texto = str(item or "")
    texto = reparar_texto_roto(limpiar_html(texto)).lower()
    return texto


def _puntuar_categorias(item):
    texto = _texto_categoria_desde_item(item)
    scores = {categoria: 0 for categoria in CATEGORIA_SENALES}
    for categoria, senales in CATEGORIA_SENALES.items():
        for senal in senales:
            if senal.lower() in texto:
                scores[categoria] += 1

    if re.search(r"\b(:ai|ia)\b", texto):
        scores["tecnologia"] += 2
    if detectar_angulo_nostalgia(item if isinstance(item, dict) else {"title": texto, "summary": ""}):
        scores["nostalgia"] += 2
    if "anime" in texto or "manga" in texto:
        scores["anime"] += 2
    if any(senal in texto for senal in SENALES_INDIE):
        scores["indie"] += 2
    return scores


def _categoria_ganadora(scores):
    if not scores:
        return "gaming"
    orden = ["anime", "tecnologia", "indie", "debate", "nostalgia"]
    categoria, puntos = max(scores.items(), key=lambda par: (par[1], -orden.index(par[0]) if par[0] in orden else -99))
    return categoria if puntos > 0 else "gaming"


def _estilo_a_categoria(estilo):
    mapa = {
        "news": "gaming",
        "noticia": "gaming",
        "hardware": "tecnologia",
        "technology": "tecnologia",
        "tecnologia": "tecnologia",
        "anime": "anime",
        "indie": "indie",
        "debate": "debate",
        "nostalgia": "nostalgia",
        "emocional": "nostalgia",
    }
    return mapa.get(str(estilo or "").lower(), "gaming")


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


def limpiar_pedido_contexto(pregunta):
    texto = pregunta.lower()
    frases = [
        "busca informacion de", "busca informaci\u00f3n de", "busca informacion sobre", "busca informaci\u00f3n sobre",
        "dame informacion de", "dame informaci\u00f3n de", "dame informacion sobre", "dame informaci\u00f3n sobre",
        "contexto de", "contexto sobre", "contexto",
        "datos de", "datos sobre", "datos",
        "informacion de", "informaci\u00f3n de", "informacion sobre", "informaci\u00f3n sobre",
        "busca informacion", "busca informaci\u00f3n",
        "dame informacion", "dame informaci\u00f3n",
        "como se juega", "c\u00f3mo se juega", "como funciona", "c\u00f3mo funciona",
        "funciones de", "funciones", "mecanicas de", "mec\u00e1nicas de", "mecanicas", "mec\u00e1nicas",
        "modos de juego de", "modos de juego", "gameplay de", "gameplay",
        "que sabes de", "qu\u00e9 sabes de", "que sabes", "qu\u00e9 sabes",
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
        "pokemon": "Pok\u00e9mon",
        "pok\u00e9mon": "Pok\u00e9mon",
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

    if tema_norm in ["Nintendo", "GameCube", "Game Boy", "Game Boy Advance", "Nintendo 64", "Pok\u00e9mon", "The Legend of Zelda"] or any(
        palabra in texto for palabra in ["nintendo", "mario", "zelda", "kirby", "pokemon", "pok\u00e9mon", "switch"]
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
    if any(palabra in texto for palabra in ["anime", "manga", "crunchyroll", "toei", "mappa", "ufotable", "kyoto animation", "production i.g", "trigger", "shonen", "otaku"]):
        grupos.append("AnimeStudios")

    if not grupos:
        grupos = ["Nintendo", "PlayStation", "Xbox", "PC", "Publishers", "AnimeStudios"]

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
        "**Qu\u00e9 mirar para explicar c\u00f3mo se juega:**\n"
        "- G\u00e9nero y objetivo principal del juego.\n"
        "- Modos: historia, online, cooperativo, competitivo o local.\n"
        "- Mec\u00e1nicas principales: combate, exploraci\u00f3n, progresi\u00f3n, construcci\u00f3n, carreras, RPG, puzzles o estrategia.\n"
        "- Plataformas disponibles y si tiene crossplay, edici\u00f3n especial, DLC o servicio online.\n"
        "- Qu\u00e9 lo hace interesante para la comunidad gamer de Puerto Rico y LatAm.\n"
        "- Pregunta final para comentarios: \u00bflo jugar\u00edas?, lo recomiendas o lo dejar\u00edas pasar\n"
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


def crear_contexto_editorial(pregunta):
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
        respuesta += "\n**Se\u00f1ales recientes de comunidad (no son noticia confirmada):**\n"
        for senal in senales:
            titulo = titulo_publico_en_espanol(senal.get("title", ""), "debate")
            respuesta += f"- {titulo} | {senal.get('source', 'comunidad')}\n"
    respuesta += "Nota: esto ayuda con contexto. Para noticias actuales sigo usando filtro estricto de fuentes oficiales o 2+ fuentes confiables."
    return limpiar_gramatica_post_final(respuesta)


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
        "informaci\u00f3n de",
        "informacion sobre",
        "informaci\u00f3n sobre",
        "busca informacion",
        "busca informaci\u00f3n",
        "dame informacion",
        "dame informaci\u00f3n",
        "como se juega",
        "c\u00f3mo se juega",
        "como funciona",
        "c\u00f3mo funciona",
        "funciones de",
        "mecanicas",
        "mec\u00e1nicas",
        "modos de juego",
        "gameplay de",
        "investiga",
        "que sabes de",
        "qu\u00e9 sabes de",
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
        f"{brand.get('audience', 'gamers')}. Tambi\u00e9n debe pensar en el nicho gamer de "
        "Puerto Rico y Latinoam\u00e9rica: comunidad que consume noticias, nostalgia, anime, "
        "tecnolog\u00eda, debates de industria y contenido f\u00e1cil de comentar."
    )
    brand["rules"] = unir_unicos(brand.get("rules", []), contexto_nicho.get("rules", NICHO_PR_LATAM["rules"]))
    brand["main_topics"] = unir_unicos(
        brand.get("main_topics", []),
        [
            "temas calientes que generen debate sano",
            "noticias convertidas en conversaci\u00f3n comunitaria",
            "h\u00e1bitos de consumo gamer en Puerto Rico y LatAm",
            "contenido de opini\u00f3n, nostalgia y cultura geek que provoque comentarios",
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
            "description": "Comunidad enfocada en videojuegos, cultura geek, tecnolog\u00eda, entretenimiento y conversaci\u00f3n entre fan\u00e1ticos.",
            "audience": "adultos de 25 a 44 a\u00f1os, jugadores casuales y hardcore, fans de Nintendo, Xbox, PlayStation, PC Gaming, anime, cine, series, tecnolog\u00eda y cultura geek en Puerto Rico y Latinoam\u00e9rica",
            "tone": ["cercano", "conversacional", "entusiasta", "informativo", "comunitario", "gamer", "positivo", "f\u00e1cil de comentar", "espa\u00f1ol natural"],
            "avoid_tone": ["corporativo", "fr\u00edo", "demasiado t\u00e9cnico", "arrogante", "hostil", "ofensivo"],
            "default_hashtags": ["#elgamercave", "#gaming", "#videojuegos", "#gamers", "#geekculture", "#puertorico", "#gamingpr"],
            "content_priority": [
                "breaking news verificadas",
                "noticias interesantes de gaming",
                "debates de comunidad",
                "nostalgia gamer",
                "tecnolog\u00eda gaming",
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
                "tecnolog\u00eda gaming",
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
                "innovaci\u00f3n relacionada al gaming",
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
                "maximizar comentarios, compartidos, likes, guardados, tiempo de lectura y discusi\u00f3n sana",
                "priorizar contenido por potencial de engagement: breaking news, noticias interesantes, debate, nostalgia, tecnolog\u00eda, desarrollo, anime, indies, industria y curiosidades",
                "no publicar solo noticias todo el d\u00eda; alternar noticias, discusi\u00f3n, tecnolog\u00eda, anime, opini\u00f3n, industria, indie, curiosidad y retro",
                "buscar temas en varias categor\u00edas: gaming, anime, manga, pel\u00edculas, series, tecnolog\u00eda, IA, desarrollo, Unreal Engine, Unity, Godot, Steam, PlayStation, Nintendo, Xbox, PC gaming, VR, AR, indies, mods, hardware, esports, cosplay, coleccionismo, industria, arte, m\u00e1sica, entrevistas y blogs de desarrolladores",
                "usar primero fuentes oficiales como Steam, Nintendo, PlayStation Blog, Xbox Wire, Valve, Epic Games, Crunchyroll, Bandai Namco, Ubisoft, Capcom, Riot, Blizzard, web oficial, blog oficial o redes oficiales",
                "usar medios confiables como IGN, GameSpot, Gematsu, VGC, Eurogamer, PC Gamer, The Verge o GamesRadar solo cuando no haya fuente oficial o para contraste",
                "si el usuario provee fuente, link, imagen o captura, esa fuente gana sobre todo lo dem\u00e1s",
                "no inventar datos, fechas, anuncios, juegos, anime, precios, estad\u00edsticas ni fuentes",
                "si falta informaci\u00f3n, decir que falta; no completar con suposiciones",
                "verificar noticias actuales con fuentes confiables",
                "si es rumor, aclararlo claramente",
                "evitar t\u00edtulos enga\u00f1osos",
                "mantener objetividad en la parte informativa",
                "priorizar comunidad sobre controversia",
                "mantener respeto hacia todas las plataformas y jugadores",
                "informar antes que exagerar",
                "si ya se public\u00f3 recientemente sobre la misma noticia, anime, juego, franquicia, desarrollador o discusi\u00f3n, buscar otro tema salvo que exista informaci\u00f3n completamente nueva",
                "evaluar cada tema por relevancia, originalidad, potencial de comentarios, potencial de compartidos, potencial de guardados, calidad visual, variedad y frescura",
                "si un tema no tiene suficiente valor o verificaci\u00f3n, no inventar; convertirlo en opini\u00f3n, nostalgia o debate claramente identificado",
                "escribir los posts en espa\u00f1ol natural; solo dejar en ingl\u00e9s nombres oficiales de juegos, compa\u00f1\u00edas o productos",
                "no copiar res\u00famenes en ingl\u00e9s directo de las fuentes",
                "usar exactamente cinco hashtags en min\u00fasculas y poner #elgamercave primero",
                "no usar la palabra carrusel dentro del post",
                "cerrar con una pregunta concreta que invite a comentar",
                "recordar que El Gamer Cave es una comunidad, no \u00fanicamente un medio de noticias",
                "el gancho, el cuerpo y la pregunta final deben estar alineados; si el gancho promete noticia actual, el cuerpo debe explicar el hecho actual",
                "si el cuerpo es nost\u00e1lgico, el gancho debe sonar nost\u00e1lgico y no como noticia actual",
                "eliminar notas internas como 'lo importante es aterrizarlo a la comunidad' antes de entregar el post",
                "si el usuario pide un ajuste espec\u00edfico, modificar solo ese elemento",
                "no agregar logos, iconos, fechas, precios, banners o texto extra si no se pidi\u00f3",
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
                "t\u00edtulo de m\u00e1ximo seis palabras cuando sea posible",
                "que se entienda en menos de dos segundos",
                "priorizar legibilidad sobre impacto",
            ],
            "cover_rules": [
                "la portada no es el post completo; solo debe hacer que la gente abra el post",
                "portada con m\u00e1ximo t\u00edtulo y subt\u00edtulo",
                "no incluir fechas, precios, estad\u00edsticas, p\u00e1rrafos largos, banners de noticia, logos, iconos o informaci\u00f3n extra si no se piden",
                "cada portada debe representar visualmente el tema principal y no usar fondo genrico",
                "dejar m\u00e1rgenes seguros para Instagram 1080x1350 y evitar palabras cortadas",
                "variar estilo visual seg\u00fan el tema: anime m\u00e1s colorido, tecnolog\u00eda m\u00e1s limpia, retro m\u00e1s vintage, horror m\u00e1s oscuro, indie m\u00e1s creativo e industria m\u00e1s minimal",
                "no cambiar logos, marcas ni personajes oficiales",
            ],
            "platform_rules": {
                "facebook": "textos m\u00e1s extensos para debate y comentarios",
                "instagram": "texto directo, enfoque visual fuerte y CTA claro",
                "tiktok": "gancho inmediato, mensaje rpido y lenguaje dinmico",
                "whatsapp": "formato corto, resumido y f\u00e1cil de leer",
            },
            "visual_rules": [
                "formato vertical 1080 x 1350 px",
                "usar logo oficial de forma consistente solo cuando aplique o se pida",
                "usar im\u00e1genes promocionales oficiales cuando est\u00e1n disponibles",
                "no alterar logos oficiales de compa\u00f1\u00edas",
                "no cambiar el significado de artes promocionales",
                "priorizar legibilidad m\u00f3vil sobre impacto visual",
            ],
            **base,
        }
    elif active_brand == "Daviet Gaming":
        base = {
            "brand": "Daviet Gaming",
            "description": "Marca de contenido sobre videojuegos, tecnolog\u00eda, cultura gamer, anime, PC gaming y temas de comunidad.",
            "audience": "gamers de Puerto Rico y Latinoam\u00e9rica que siguen noticias, opini\u00f3n, cultura gaming, anime, PC gaming, hardware y tecnolog\u00eda",
            "tone": ["casual", "directo", "natural", "gamer", "con opini\u00f3n", "claro", "f\u00e1cil de entender", "con hype moderado", "espa\u00f1ol natural"],
            "avoid_tone": ["demasiado formal", "corporativo", "exagerado", "gen\u00e9rico", "fr\u00edo"],
            "default_hashtags": ["#davietgaming", "#gaming", "#videojuegos", "#pcgaming", "#gamers", "#gamingcommunity", "#tecnologia", "#puertorico"],
            "main_topics": [
                "noticias actuales de videojuegos",
                "tecnolog\u00eda gaming",
                "PC gaming",
                "anime relacionado con gaming o hardware",
                "opini\u00f3n sobre la industria",
                "debates gamer",
                "nostalgia gamer",
                "consolas",
                "hardware",
                "colaboraciones especiales",
                "tendencias de gaming y tecnolog\u00eda",
            ],
            "rules": [
                "no inventar informaci\u00f3n",
                "verificar noticias actuales antes de crear posts",
                "no decir que algo es oficial si no est\u00e1 confirmado",
                "si una noticia ya pas\u00f3 hace d\u00edas, darle un \u00e1ngulo actualizado de forma natural",
                "no usar lenguaje demasiado formal",
                "no usar frases gen\u00e9ricas como el mundo gamer est\u00e1 emocionado si no hay contexto real",
                "no repetir la misma estructura siempre",
                "no usar la palabra carrusel dentro del post",
                "escribir en espa\u00f1ol natural; solo dejar en ingl\u00e9s nombres oficiales de juegos, compa\u00f1\u00edas o productos",
                "hashtags siempre en min\u00fascula",
            ],
            "post_structure": [
                "t\u00edtulo corto y llamativo",
                "subt\u00edtulo corto",
                "texto principal del post",
                "opini\u00f3n o \u00e1ngulo de Daviet Gaming",
                "pregunta final para generar interacci\u00f3n",
                "hashtags en min\u00fascula",
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
                "no usar logos de compa\u00f1\u00edas si no se pide",
                "no cambiar el logo de Daviet Gaming",
                "evitar dise\u00f1os demasiado gen\u00e9ricos de AI",
            ],
            "platform_rules": {
                "facebook": "puede tener m\u00e1s contexto, opini\u00f3n y debate",
                "instagram": "directo, visual, f\u00e1cil de leer y con CTA claro",
                "tiktok": "gancho r\u00e1pido y lenguaje din\u00e1mico",
            },
        }
    elif active_brand == "General":
        base = {
            **base,
            "brand": "Gamer Signal",
            "audience": "gamers de Puerto Rico y Latinoam\u00e9rica",
            "tone": ["casual", "claro", "gamer", "nost\u00e1lgico"],
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
    texto = limpiar_texto_publicable_final(texto).lower()
    patrones = [
        r"\b(?:post\s+de\s+la\s+)?(?:noticia|publicaci[oó]n|opci[oó]n|item)\s*(?:n[uú]mero|num\.?|#)?\s*(\d{1,2})\b",
        r"\b(?:post\s+de\s+la\s+)?(?:noticia|publicaci[oó]n|opci[oó]n|item)\s+(uno|una|dos|tres|cuatro|cinco|seis|siete|ocho)\b",
        r"\b(primera|segunda|tercera|cuarta|quinta|sexta|s[eé]ptima|octava)\s+(?:noticia|publicaci[oó]n|opci[oó]n|item)\b",
    ]
    ordinales = {
        "primera": 1,
        "segunda": 2,
        "tercera": 3,
        "cuarta": 4,
        "quinta": 5,
        "sexta": 6,
        "septima": 7,
        "séptima": 7,
        "octava": 8,
    }
    for patron in patrones:
        match = re.search(patron, texto)
        if not match:
            continue
        valor = match.group(1).lower()
        if valor.isdigit():
            return int(valor)
        if valor in NUMEROS_EN_TEXTO:
            return NUMEROS_EN_TEXTO[valor]
        if valor in ordinales:
            return ordinales[valor]
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
    palabras_cantidad = [
        "post", "posts", "publicaci\u00f3n", "publicaciones", "publicacion",
        "caption", "captions", "noticia", "noticias", "tema", "temas",
        "idea", "ideas", "opciones",
    ]
    if not any(p in texto for p in palabras_cantidad):
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
            "noticia n?mero",
            "noticia numero",
            "post de noticia",
            "post de la noticia",
        ]
    )


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
        if categoria_item == categoria:
            titulos_usados.add(titulo_key)
            return dict(item)

    return None


def plataforma_de_item(item):
    texto = f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}".lower()
    if any(p in texto for p in ["xbox", "microsoft", "game pass"]):
        return "xbox"
    if any(p in texto for p in ["playstation", "ps5", "ps plus", "sony"]):
        return "playstation"
    if any(p in texto for p in ["nintendo", "switch", "mario", "zelda", "pokemon", "pok\u00e9mon"]):
        return "nintendo"
    if any(p in texto for p in ["steam", "pc gamer", "pc gaming", "nvidia", "amd", "intel", "gpu"]):
        return "pc"
    if any(p in texto for p in ["anime", "manga", "crunchyroll", "myanimelist"]):
        return "anime"
    if any(p in texto for p in SENALES_INDIE):
        return "indie"
    return "general"


def detectar_exclusiones_usuario(texto):
    """Lee frases como 'que no sea Xbox' o 'sin PlayStation'."""
    texto = limpiar_texto_publicable_final(texto).lower()
    exclusiones = []
    mapa = {
        "xbox": ["xbox", "xbox wire", "microsoft"],
        "playstation": ["playstation", "ps5", "ps plus", "sony"],
        "nintendo": ["nintendo", "switch", "mario", "zelda", "pokemon", "pok\u00e9mon"],
        "pc": ["pc gaming", "steam", "nvidia", "amd", "gpu"],
        "anime": ["anime", "manga", "crunchyroll"],
    }
    patrones = ["no sea", "sin", "no de", "que no sea", "que no salga", "otra que no sea"]
    for clave, palabras in mapa.items():
        if any(patron in texto and clave in texto for patron in patrones):
            exclusiones.extend(palabras)
    return list(dict.fromkeys(exclusiones))


def item_cumple_exclusiones(item, exclusiones):
    if not exclusiones:
        return True
    texto = f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}".lower()
    return not any(exclusion.lower() in texto for exclusion in exclusiones)


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
        return "\u00bfPara cu\u00e1l marca quieres el calendario: Gamer Cave o Daviet Gaming?"

    if marca == "Daviet Gaming":
        return """
### Calendario semanal de Daviet Gaming

**Lunes:** noticia reciente de gaming, PC o tecnolog\u00eda explicada de forma sencilla.

**Martes:** hardware, accesorios, setup o una funci\u00f3n \u00fatil para gamers.

**Mi\u00e9rcoles:** anime, cultura geek o recomendaci\u00f3n relacionada con gaming.

**Jueves:** nostalgia, opini\u00f3n personal o experiencia gamer.

**Viernes:** noticia hot convertida en una pregunta para conversaci\u00f3n.

**S\u00e1bado:** recomendaci\u00f3n, comparaci\u00f3n o tema para compartir con la comunidad.

**Domingo:** resumen ligero, recuerdo gamer o adelanto de la pr\u00f3xima semana.
"""

    return """
### Calendario semanal de El Gamer Cave

**Lunes:** noticia oficial de gaming o tecnolog\u00eda.

**Martes:** nostalgia gamer: consolas viejas, juegos f\u00edsicos, Game Boy, GameCube o Pok\u00e9mon.

**Mi\u00e9rcoles:** debate de comunidad: f\u00edsico vs digital, online vs local, remakes vs originales.

**Jueves:** post emocional: recuerdos de infancia, jugar con primos, controles prestados o memory cards.

**Viernes:** pregunta r\u00e1pida para comentarios.

**S\u00e1bado:** recomendaci\u00f3n o comparaci\u00f3n gamer.

**Domingo:** post ligero de recuerdos, ranking o "\u00bfte acuerdas de...".
"""


def es_modo_dueno():
    try:
        owner = st.query_params.get("owner", "")
    except Exception:
        try:
            owner = st.experimental_get_query_params().get("owner", [""])[0]
        except Exception:
            owner = ""
    return str(owner).strip().lower() in [
        "daviet",
        "davietes",
        "davietgaming",
        "daviet-gaming",
        "admin",
        "owner",
        "1",
        "true",
    ]


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
            st.button("5 posts", use_container_width=True, on_click=set_quick_prompt, args=("cr\u00e9ame 5 posts hot",))
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
        "noticia_actual": "Convertirlo en noticia clara: qu\u00e9 pas\u00f3, por qu\u00e9 importa y pregunta final.",
        "debate": "Usarlo para abrir conversaci\u00f3n con dos lados claros y sin imponer conclusi\u00f3n.",
        "nostalgia": "Conectarlo con recuerdos gamer, consolas viejas, juegos f\u00edsicos y comunidad.",
        "tecnologia": "Explicarlo desde c\u00f3mo afecta la experiencia gamer, PC, hardware o servicios.",
        "anime": "Cruzar anime y cultura geek con gaming, hype, fandom o adaptaci\u00f3n.",
        "indie": "Presentarlo como descubrimiento: qu\u00e9 lo hace diferente y por qu\u00e9 vale mirarlo.",
    }
    return angulos.get(bucket, "Convertirlo en post simple, \u00fatil y f\u00e1cil de comentar.")



def render_news_cards():
    news = st.session_state.get("news_by_number", {})
    if not news:
        return

    st.markdown("#### Noticias recientes")
    st.markdown('<div class="news-grid">', unsafe_allow_html=True)
    for numero, item in news.items():
        title = html_escape(item.get("title", "Sin t\u00edtulo"))
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
    copy_icon = """
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <rect x="9" y="9" width="11" height="11" rx="2"></rect>
            <rect x="4" y="4" width="11" height="11" rx="2"></rect>
        </svg>
    """
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
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                ">{copy_icon}</button>
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
        const copyIcon = `{copy_icon}`;
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
                btn.innerHTML = "&#10003;";
                status.innerText = "Copiado";
            }} catch (error) {{
                btn.innerText = "!";
                status.innerText = "No se pudo copiar. Abre las opciones y usa Descargar.";
            }}
            setTimeout(() => {{
                btn.innerHTML = copyIcon;
                status.innerText = "";
            }}, 1800);
        }});
        </script>
        """,
        height=height,
    )


def dividir_posts_generados(post):
    partes = [parte.strip() for parte in post.split("\n\n---\n\n") if parte.strip()]
    if len(partes) > 1 and all(limpiar_texto_publicable_final(parte).startswith("PUBLICACI\u00d3N") for parte in partes):
        return partes
    return [post]


def render_post_response(post):
    partes = dividir_posts_generados(post)
    for index, parte in enumerate(partes, start=1):
        contenido = parte
        etiqueta = f"Post {index}"
        if limpiar_texto_publicable_final(parte).startswith("PUBLICACI\u00d3N") and "\n\n" in parte:
            etiqueta, contenido = parte.split("\n\n", 1)
            etiqueta = limpiar_gramatica_post_final(etiqueta).title()
        if len(partes) > 1:
            st.markdown(
                f'<h4 class="post-section-title">{html_escape(etiqueta)}</h4>',
                unsafe_allow_html=True,
            )
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
                save_feedback(st.session_state.get("last_item_id"), "post/topic", "approved", "post aprobado desde bot?n")
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


def palabras_clave_tema(texto):
    texto = texto.lower()
    reemplazos = [":", "-", "_", "/", "\\", "|", ",", ".", "", "!", "(", ")", "[", "]"]
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
        "ps1", "ps2", "xbox 360", "wii", "pok\u00e9mon", "pokemon",
        "mario", "zelda", "kirby", "sonic", "final fantasy",
        "kingdom hearts", "nvidia", "openai", "ia", "hardware",
        "pc gaming", "juegos f\u00edsicos", "multiplayer local",
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
        "remake": "infancia gamer, juegos cl\u00e1sicos y nostalgia.",
        "remaster": "infancia gamer, juegos cl\u00e1sicos y nostalgia.",
        "anniversary": "aniversarios, recuerdos y etapas importantes de la comunidad.",
        "aniversario": "aniversarios, recuerdos y etapas importantes de la comunidad.",
        "retro": "consolas, juegos y experiencias de otras generaciones.",
        "classic collection": "colecciones de juegos cl\u00e1sicos y recuerdos de otras generaciones.",
        "colecci?n cl?sica": "colecciones de juegos cl\u00e1sicos y recuerdos de otras generaciones.",
        "return of the classic": "regresos de juegos cl\u00e1sicos y recuerdos de la comunidad.",
        "regreso del cl\u00e1sico": "regresos de juegos cl\u00e1sicos y recuerdos de la comunidad.",
    }
    for palabra, angulo in mapa.items():
        if palabra in texto:
            return angulo
    return ""


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
    titulo = item.get("title") or item_id or st.session_state.get("last_post_title", "post sin t\u00edtulo")
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
        if "m\u00e1s corto" in texto or "mas corto" in texto:
            ajustar_preferencia("style_rule", "posts m\u00e1s cortos", 3, feedback_text)
        if "m\u00e1s nostalgia" in texto or "mas nostalgia" in texto:
            ajustar_preferencia("preferred_category", "nostalgia gaming", 3, feedback_text)
        if "m\u00e1s debate" in texto or "mas debate" in texto:
            ajustar_preferencia("preferred_category", "debate gamer", 3, feedback_text)
        if "no digas carrusel" in texto:
            ajustar_preferencia("banned_phrase", "carrusel", 10, feedback_text)
        if "no repetir" in texto:
            ajustar_preferencia("avoid_repeat", titulo, 5, feedback_text)
            marcar_tema_usado(titulo, categoria, "user requested no repeat")
        if "no inventes logos" in texto:
            ajustar_preferencia("permanent_rule", "no inventar logos", 10, feedback_text)
        accion = "updated style and rule preferences"

    if "eso ya pas\u00f3" in texto or "eso ya paso" in texto:
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
            razones.append("publicado en las ?ltimas 24-48 horas")
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
        if any(palabra in texto for palabra in ["precio", "suscripci\u00f3n", "subscription", "remake", "remaster", "digital", "f\u00edsico", "fisico", "microtransacciones"]):
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
            "title": entrada.get("title", "Sin t\u00edtulo"),
            "summary": entrada.get("summary", ""),
            "link": entrada.get("link", ""),
            "year": fecha.tm_year,
            "month": fecha.tm_mon,
            "day": fecha.tm_mday,
        })
    return entradas_limpias


def leer_feeds_en_paralelo(fuentes, max_workers=10):
    """Lee varios RSS en paralelo para que un feed lento no frene todo el radar."""
    fuentes = list((fuentes or {}).items())
    resultados = []
    if not fuentes:
        return resultados

    workers = max(1, min(max_workers, len(fuentes)))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futuros = {
            executor.submit(leer_feed, url): fuente
            for fuente, url in fuentes
        }
        for futuro in as_completed(futuros):
            fuente = futuros[futuro]
            try:
                entradas = futuro.result()
            except Exception:
                entradas = []
            resultados.append((fuente, entradas))
    return resultados


@st.cache_data(ttl=3600)
def buscar_wikipedia(tema):
    """Wikipedia se usa solo como apoyo historico, nunca para confirmar noticias."""
    tema = normalizar_tema_contexto(tema)
    alternativas = {
        "GameCube": ["GameCube", "Nintendo GameCube"],
        "Game Boy": ["Game Boy", "Game Boy Advance"],
        "Nintendo 64": ["Nintendo 64"],
        "PlayStation 2": ["PlayStation 2"],
        "Pok\u00e9mon": ["Pok\u00e9mon"],
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
                "source": "Wikipedia en espa\u00f1ol (solo contexto hist\u00f3rico)",
                "date": None,
                "source_official": False,
                "content_angle": "nostalgia",
                "confidence_level": "support",
                "nostalgia_angle": "Apoyo hist\u00f3rico para crear contenido nost\u00e1lgico; no confirma noticias actuales.",
            }
        except Exception:
            continue

    return None


def limpiar_tema_nostalgia(pregunta):
    texto = pregunta.lower()
    frases = [
        "nostalgia sobre", "nostalgia de", "retro sobre", "retro de",
        "h\u00e1blame de", "hablame de", "dame informaci\u00f3n sobre",
        "dame informacion sobre", "informaci\u00f3n sobre", "informacion sobre",
    ]
    for frase in frases:
        texto = texto.replace(frase, "")
    quitar = ["nostalgia", "retro", "cl\u00e1sico", "clasico", "viejo", "antiguo", "sobre"]
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
        "pokemon": "Pok\u00e9mon",
        "pok\u00e9mon": "Pok\u00e9mon",
        "mario": "Mario",
        "kirby": "Kirby",
        "zelda": "The Legend of Zelda",
    }
    return nombres.get(tema, tema.title()) if tema else None


@st.cache_data(ttl=NEWS_CACHE_TTL_SECONDS, show_spinner=False)
def cargar_noticias_base():
    noticias = []
    for fuente, entradas in leer_feeds_en_paralelo(FUENTES):
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
            titulo = limpiar_html(noticia.get("title", "Sin t\u00edtulo"))
            resumen = limpiar_html(noticia.get("summary", ""))
            link = noticia.get("link", "")
            item = {
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{fuente}|{link}|{titulo}")),
                "title": limpiar_html(noticia.get("title", "Sin t\u00edtulo")),
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
    for fuente, entradas in leer_feeds_en_paralelo(FUENTES_COMUNIDAD, max_workers=6):
        for entrada in entradas:
            fecha = date(entrada["year"], entrada["month"], entrada["day"])
            if fecha.year != ANIO_NOTICIAS or fecha < fecha_minima or fecha > FECHA_FINAL:
                continue

            titulo = limpiar_html(entrada.get("title", "Tema de comunidad"))
            resumen_original = limpiar_html(entrada.get("summary", ""))
            resumen = (
                "Se\u00f1al de conversaci\u00f3n detectada en comunidad. "
                "Usar con cautela como idea de nostalgia, teor\u00eda, debate o fandom; no presentarlo como noticia confirmada."
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
                "verification_level": "se\u00f1al de comunidad; no confirma noticia",
            }
            item["nostalgia_angle"] = detectar_angulo_nostalgia(item)
            item["content_angle"] = detectar_content_angle(item)
            fuente_baja = fuente.lower()
            if "nostalgia" in fuente_baja or "retro" in fuente_baja or item["nostalgia_angle"]:
                item["content_angle"] = "nostalgia"
            elif any(p in fuente_baja for p in ["debate", "truegaming", "fantheories", "rumores", "leaks"]):
                item["content_angle"] = "debate"
            elif "indie" in fuente_baja:
                item["content_angle"] = "indie"
            elif "anime" in fuente_baja or "manga" in fuente_baja or "jrpg" in fuente_baja:
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
    angulo = categoria_de_item(item)
    texto = f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}".lower()
    if angulo == "anime" or any(p in texto for p in [
        "anime", "manga", "crunchyroll", "myanimelist", "anime news network",
        "anime corner", "toei", "mappa", "ufotable", "kyoto animation",
        "production i.g", "studio trigger", "shonen", "otaku"
    ]):
        return "anime"
    if angulo in ["tecnologia", "hardware", "technology"] or any(p in texto for p in [
        "nvidia", "rtx", "gpu", "hardware", "pc gaming", "steam deck",
        "unreal engine", "unity", "amd", "intel", "geforce", "radeon",
        "ios", "android", "switch 2", "handheld", "portable pc"
    ]):
        return "tecnologia"
    if angulo == "indie" or any(p in texto for p in SENALES_INDIE) or any(p in texto for p in [
        "indiedev", "indie dev", "demo", "early access", "steam next fest",
        "itch.io", "solo developer", "small studio"
    ]):
        return "indie"
    if angulo == "nostalgia" or detectar_angulo_nostalgia(item):
        return "nostalgia"
    if angulo == "debate" or any(p in texto for p in [
        "precio", "suscripcion", "suscripci\u00f3n", "digital", "fisico", "f\u00edsico",
        "game pass", "ps plus", "microtransacciones", "opinion", "hot take",
        "unpopular opinion", "theory", "teoria", "teor\u00eda", "fan theory",
        "rumor", "rumour", "leak", "conspiracy", "speculation", "controversy",
        "debate", "thoughts", "community"
    ]):
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
            razones[marca].append("tiene se\u00f1ales hot")

    orden = sorted(scores, key=scores.get, reverse=True)
    return scores, razones, orden


def monitor_angulo_para_marca(item, marca):
    bucket = item.get("monitor_bucket") or monitor_bucket_item(item)
    titulo = titulo_publico_en_espanol(item.get("title", ""), "news")
    if marca == "Gamer Cave":
        if bucket == "nostalgia":
            return "Conectarlo con recuerdos de comunidad: juegos f\u00edsicos, controles prestados, tardes con panas y debate sano."
        if bucket == "debate":
            return "Convertirlo en pregunta de comunidad con dos lados claros, sin imponer conclusi\u00f3n."
        if bucket == "anime":
            return "Cruzar anime y gaming: hype, adaptaci\u00f3n, fandom y conversaci\u00f3n geek."
        return "Explicar qu\u00e9 pas\u00f3, por qu\u00e9 importa y cerrar con una pregunta para la tribu geek."
    if marca == "Daviet Gaming":
        if bucket == "tecnologia":
            return "Explicarlo desde el valor real para gamers: rendimiento, precio, PC, setup o experiencia."
        if bucket == "anime":
            return "Darle un \u00e1ngulo casual de cultura geek/anime con opini\u00f3n corta y pregunta directa."
        if bucket == "indie":
            return "Presentarlo como descubrimiento gamer: qu\u00e9 lo hace diferente y por qu\u00e9 vale mirarlo."
        return "Dar contexto r\u00e1pido, opini\u00f3n natural y cerrar con una pregunta clara para comentarios."
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
            "confidence_level": item.get("confidence_level", ""),
            "source_official": item.get("source_official", False),
            "source_trusted": item.get("source_trusted", False),
            "is_community_signal": item.get("is_community_signal", False),
            "verification_count": item.get("verification_count", 0),
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
        "monitor", "monitoreo", "monitorea", "radar", "que encontro", "que encontr",
        "hallazgos", "recolectar informacion", "recolectar informacin", "buscando noticias",
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


def elegir_noticia_nueva_para_post(categoria_preferida=None, texto_usuario=""):
    exclusiones = detectar_exclusiones_usuario(texto_usuario)
    noticias = [
        item for item in filtrar_noticias_verificadas(buscar_noticias())
        if item_cumple_exclusiones(item, exclusiones)
    ]
    if categoria_preferida:
        preferidas = [
            item for item in noticias
            if categoria_de_item(item) == categoria_preferida
        ]
        noticias = preferidas + [item for item in noticias if item not in preferidas]

    for item in noticias:
        titulo = item.get("title", "")
        if tema_repetido(titulo) or tema_muy_similar(titulo):
            continue
        item = dict(item)
        st.session_state.generated_items[item["id"]] = item
        st.session_state.last_item_id = item["id"]
        return item

    if noticias:
        item = dict(noticias[0])
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


def texto_menciona_hashtags(texto):
    palabras = ["hashtag", "hashtags", "hastag", "hastags", "hashtach", "hastach", "hash"]
    return any(palabra in texto for palabra in palabras)


def pide_cinco_hashtags(texto):
    if not texto_menciona_hashtags(texto):
        return False
    return any(frase in texto for frase in ["5", "cinco", "solo cinco", "solo 5", "nada mas 5", "nada m\u00e1s 5"])


def es_pedido_solo_hashtags(texto):
    if not texto_menciona_hashtags(texto):
        return False
    palabras_post = ["post", "publicaci\u00f3n", "publicacion", "caption", "noticia", "noticias"]
    return not any(palabra in texto for palabra in palabras_post)


def limpiar_pedido_hashtags(pregunta):
    texto = pregunta.lower()
    frases = [
        "dame", "hazme", "creame", "cr\u00e9ame", "crea", "crear", "generame", "gen\u00e9rame",
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
        "Listo. Guard\u00e9 la regla: usar solo 5 hashtags.\n\n"
        f"{hashtags}"
    )


def limpiar_html(texto):
    if not texto:
        return ""
    texto = html_unescape(str(texto))
    texto = re.sub(r"<a\b[^>]*>(.*)</a>", r"\1", texto, flags=re.IGNORECASE | re.DOTALL)
    texto = re.sub(r"<br\s*/>", " ", texto, flags=re.IGNORECASE)
    texto = re.sub(r"</p\s*>", " ", texto, flags=re.IGNORECASE)
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = re.sub(r"https://\S+", "", texto)
    texto = re.sub(r"\bThe post\b.*\bappeared first on\b[^.!]*(:[.!]|$)", "", texto, flags=re.IGNORECASE | re.DOTALL)
    texto = re.sub(r"\bappeared first on\b[^.!]*(:[.!]|$)", "", texto, flags=re.IGNORECASE | re.DOTALL)
    while "  " in texto:
        texto = texto.replace("  ", " ")
    return reparar_texto_roto(texto.strip())


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


def crear_item_desde_pedido(pregunta, estilo):
    tema = limpiar_pedido_post(pregunta)
    if not tema or tema in ["un", "una", "nuevo", "nueva"]:
        return None
    titulo = tema[:1].upper() + tema[1:]
    texto = f"{titulo} es un tema solicitado para crear contenido gamer con enfoque {estilo}."
    if estilo in ["nostalgia", "emocional"]:
        texto += " La idea es conectar con recuerdos de infancia, consolas viejas, juegos f\u00edsicos y comunidad."
    elif estilo == "debate":
        texto += " La idea es provocar comentarios sin sonar agresivo ni inventar datos."
    else:
        texto += " La idea es explicarlo claro y convertirlo en un post \u00fatil para redes."

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
        "content_angle": estilo if estilo != "news" else "opini\u00f3n",
        "nostalgia_angle": detectar_angulo_nostalgia({"title": titulo, "summary": texto}),
        "confidence_level": "manual",
        "context_source": contexto_local.get("provider", "") if contexto_local else "",
    }
    st.session_state.generated_items[item["id"]] = item
    st.session_state.last_item_id = item["id"]
    return item


def crear_subtitulo(estilo, titulo):
    if estilo == "debate":
        return "Un tema para prender la conversaci\u00f3n gamer"
    if estilo in ["noticia", "news"]:
        return "Lo importante es entender por qu\u00e9 importa ahora"
    if estilo == "emocional":
        return "De esos recuerdos que muchos gamers entienden r\u00e1pido"
    if estilo == "corto":
        return "R?pido, directo y listo para comentarios"
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
        return "Background nost\u00e1lgico con consola retro, controles, cartuchos o discos sobre una mesa, luz c\u00e1lida, formato vertical 1080x1350, sin texto."
    if "hardware" in texto or "nvidia" in texto or "amd" in texto or "msi" in texto or "asus" in texto:
        return "Background de setup PC gaming con luces limpias, hardware como protagonista, espacio libre para t\u00edtulo, formato vertical 1080x1350."
    if "game jam" in texto or "puerto rico" in texto or "gamedev" in texto:
        return "Background de comunidad gamer y desarrollo indie, laptops, controles y ambiente de evento local, formato vertical 1080x1350."
    if estilo == "debate":
        return "Background dividido visualmente entre dos ideas opuestas, estilo gamer limpio, espacio central para t\u00edtulo, formato vertical 1080x1350."
    return "Background gaming oscuro con detalles retro, consola o control como elemento principal, espacio limpio para texto, formato vertical 1080x1350."


def normalizar_titulo_gamer(titulo):
    reemplazos = {
        "gamecube": "GameCube",
        "game boy": "Game Boy",
        "pokemon": "Pok\u00e9mon",
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
            "Para la comunidad, la discusi\u00f3n est\u00e1 en si otros estudios deber\u00edan mover sus fechas "
            "o competir directamente por la atenci\u00f3n de los jugadores."
        )
    if estilo == "debate":
        return "La conversaci\u00f3n se pone buena cuando la comunidad compara experiencias sin convertirlo en pelea de plataformas."
    if "precio" in texto or "suscripci\u00f3n" in texto or "game pass" in texto or "ps plus" in texto:
        return "Para muchos gamers de Puerto Rico y LatAm, la pregunta real es si esto vale el dinero y el tiempo."
    if "digital" in texto or "f\u00edsico" in texto or "fisico" in texto:
        return "Este tema conecta r\u00e1pido porque muchos todav\u00eda recuerdan comprar, prestar o guardar juegos f\u00edsicos."
    if "remake" in texto or "remaster" in texto or "nostalgia" in texto:
        return "Aqu\u00e9 la nostalgia pesa, pero tambi\u00e9n vale preguntar si queremos recuerdos o experiencias nuevas."
    if "anime" in texto or "manga" in texto:
        return "Anime y gaming se cruzan mucho en nuestra comunidad, especialmente cuando hay hype, regreso de cl\u00e1sicos o debate de adaptaci\u00f3n."
    if "hardware" in texto or "nvidia" in texto or "rtx" in texto or "gpu" in texto:
        return "La clave es explicarlo desde el beneficio real para el gamer com\u00fan, no como ficha t\u00e9cnica fr\u00eda."
    return (
        "Este tipo de tema conecta con la comunidad porque cada gamer puede vivirlo, "
        "recordarlo o interpretarlo de una manera diferente."
    )


def revisar_coherencia_editorial(post, estilo):
    """Limpia notas internas y comprueba que el caption suene publicable."""
    texto = str(post or "").strip()
    reemplazos = {
        "Lo importante es aterrizarlo a la comunidad: qu\u00e9 cambia, a qui\u00e9n le interesa y qu\u00e9 opini\u00f3n puede abrir.": (
            "Este tema conecta con la comunidad porque cada gamer puede vivirlo "
            "o interpretarlo de una manera diferente."
        ),
        "La clave est\u00e1 en entender qu\u00e9 cambia, a qui\u00e9n le interesa y por qu\u00e9 puede importar para la comunidad.": (
            "La noticia importa por el efecto que puede tener en los jugadores "
            "y en la conversaci\u00f3n de la comunidad."
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
    if "?" not in cuerpo_sin_hashtags and "\u00bf" not in cuerpo_sin_hashtags:
        cierre = "👇 ¿Qué opinas"
        partes = texto.rsplit("\n\n", 1)
        if len(partes) == 2 and partes[1].lstrip().startswith("#"):
            texto = f"{partes[0]}\n\n{cierre}\n\n{partes[1]}"
        else:
            texto = f"{texto}\n\n{cierre}"

    return texto


def limpiar_primer_parrafo_repetido(texto, titulo):
    """Evita que el caption repita el titulo como primera frase del cuerpo."""
    texto = limpiar_texto_publicable_final(texto)
    titulo_limpio = limpiar_texto_publicable_final(titulo)
    if not texto or not titulo_limpio:
        return texto

    patron = re.escape(titulo_limpio)
    texto = re.sub(
        rf"^{patron}\s+(es|puede|vuelve|se)\b",
        lambda m: m.group(1).capitalize(),
        texto,
        flags=re.IGNORECASE,
    ).strip()
    texto = re.sub(r"^(Es|Puede|Vuelve|Se)\s+un tema reciente dentro del mundo gamer\.\s*", "", texto).strip()
    return texto or "Hay una novedad reciente que vale mirar con calma antes de convertirla en conversación."


# Capa final de idioma y limpieza para evitar que titulares RSS salgan en ingles.
# Las fuentes originales se guardan internamente, pero el caption visible queda en espanol.
def limpiar_para_ui(texto):
    """Texto seguro para mostrar en tarjetas: sin mojibake ni HTML raro."""
    return limpiar_texto_publicable_final(reparar_texto_roto(texto))


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
    return limpiar_gramatica_post_final(salida)


def caption_tiene_ingles_visible(texto):
    """Ignora nombres propios, pero detecta frases largas en ingles dentro del caption."""
    cuerpo = "\n".join(
        linea for linea in str(texto or "").splitlines()
        if not linea.strip().startswith("#")
    )
    return parece_texto_ingles(cuerpo)


def crear_debate():
    prompt = buscar_prompt("debate")
    temas = TEMAS_COMUNIDAD + TEMAS_DEBATE
    respuesta = "Aqu\u00ed tienes temas de debate geek para mover comentarios:\n\n"
    for i, tema in enumerate(temas[:10], start=1):
        respuesta += f"{i}. {limpiar_texto_publicable_final(tema)}\n"
    respuesta += "\n\u00dasalos como conversaci\u00f3n de comunidad, no como noticia confirmada."
    respuesta += "\n\nPregunta para comentar: \u00bfcu\u00e1l de estos temas te prende m\u00e1s el debate?"
    if prompt:
        respuesta += f"\n\nReferencia usada: {prompt}"
    return limpiar_gramatica_post_final(limpiar_texto_publicable_final(respuesta))

def crear_nostalgia(pregunta):
    tema = limpiar_tema_nostalgia(pregunta)
    if not tema:
        respuesta = "\u00bfSobre qu\u00e9 tema nost\u00e1lgico quieres hablar?\n\n"
        for item in TEMAS_NOSTALGIA:
            respuesta += f"- {limpiar_texto_publicable_final(item)}\n"
        return limpiar_gramatica_post_final(respuesta)
    tema = normalizar_tema_contexto(tema)
    info = buscar_wikipedia(tema)
    contexto_local = buscar_contexto_local(tema)
    if not info and not contexto_local:
        return f"No encontr\u00e9 contexto hist\u00f3rico suficiente sobre **{tema}**. Prueba con GameCube, Game Boy, Pok\u00e9mon o PlayStation 2."

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

    return limpiar_gramatica_post_final(f"""
### Contexto nost\u00e1lgico: {info["title"]}

Esto no es noticia actual de {ANIO_NOTICIAS}. Es contexto hist\u00f3rico para hablar de nostalgia gamer.

Importante: Wikipedia queda como apoyo de contexto, no como fuente principal para publicar noticias.

{info["summary"]}

{contexto_extra}

**Referencia de apoyo:** {info["source"]}

**Ideas para post:**
- \u00bfPor qu\u00e9 marc\u00f3 a una generaci\u00f3n?
- \u00bfQu\u00e9 recuerdos despierta en gamers de Puerto Rico y LatAm?
- \u00bfC\u00f3mo se compara con el gaming actual?
- \u00bfQu\u00e9 pregunta puede generar comentarios?

**Referencia Gamer Cave usada:**
{prompt}

ID para feedback: `{info["id"]}`
""")


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
    if any(p in texto for p in ["tecnolog\u00eda", "tecnologia", "hardware", "pc gaming", "gpu"]):
        return "tecnologia"
    if any(p in texto for p in ["nostalgia", "retro", "cl\u00e1sico", "clasico", "remake", "remaster"]):
        return "nostalgia"
    if any(p in texto for p in ["debate", "opini\u00f3n", "opinion", "controversia"]):
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
    return any(palabra in texto for palabra in ["post", "instagram", "facebook", "publicaci\u00f3n", "publicacion", "caption"])


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
        "\u00bfPara cu\u00e1l marca lo hago?\n\n"
        "Puedes responder: **Gamer Cave** o **Daviet Gaming**."
    )


def crear_lista_comandos():
    return """### Comandos \u00fatiles

- **hazme un post para Daviet Gaming**
- **hazme un post para Gamer Cave**
- **hazme un post**
- **hazme 6 posts variados**
- **6 noticias variadas que no sean de Xbox**
- **cr\u00e9ame 5 posts hot**
- **noticias oficiales de gaming**
- **opciones de post recientes**
- **contexto de GameCube**
- **busca informaci\u00f3n sobre Pok\u00e9mon**
- **datos de Zelda**
- **c\u00f3mo se juega Zelda**
- **modelos de Nintendo desde el primero hasta el actual**
- **debate gamer**
- **nostalgia gamer**
- **voy a publicar estos posts**
- **no repetir este tema**
- **m\u00e1s corto**
- **m\u00e1s debate**
- **m\u00e1s nostalgia**

Si pides un post sin marca, te voy a preguntar si es para Gamer Cave o Daviet Gaming."""


def es_comando_de_publicacion(texto):
    frases = [
        "voy a publicar",
        "voy publicar",
        "publicar estos post",
        "publicar estos posts",
        "publicar este post",
        "ya publiqu\u00e9",
        "ya publique",
        "ya los publiqu\u00e9",
        "ya los publique",
        "marcalos como usados",
        "m?rcalos como usados",
        "marcar como usados",
        "guardalos como usados",
        "gu?rdalos como usados",
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
        "los usar?",
        "usare esos post",
        "usar? esos post",
        "usare esos posts",
        "usar? esos posts",
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
        return "Todav\u00eda no tengo posts recientes para marcar como publicados. Primero crea uno o varios posts."

    marcas = marcas_para_publicacion(texto)
    for item in items:
        titulo = item.get("title", "post sin t\u00edtulo")
        categoria = item.get("content_angle", "post")
        marcar_publicacion_usada(
            titulo,
            categoria,
            marcas,
            f"published by user for {', '.join(marcas)}"
        )

    marcas_texto = ", ".join(marcas)
    return f"Listo. Marqu\u00e9 {len(items)} post(s) como usados/publicados para: {marcas_texto}."


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
        "qu\u00e9 d\u00eda es hoy", "que dia es hoy", "fecha de hoy",
        "qu\u00e9 fecha es", "que fecha es", "qu\u00e9 hora es", "que hora es",
        "d\u00eda y hora", "dia y hora", "fecha y hora",
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
        return crear_contexto_editorial(pregunta)

    if "comandos" in texto or "lista de comandos" in texto or "ayuda" in texto:
        return crear_lista_comandos()

    if "calendario" in texto or "plan semanal" in texto:
        return crear_calendario_contenido(marca_mencionada)

    if "guardar post" in texto or "exportar post" in texto:
        if not st.session_state.get("last_post_text"):
            return "Todav\u00eda no hay un post para guardar. Primero crea uno con: crea un post para Instagram."
        archivo = guardar_post_aprobado(st.session_state.last_post_text, st.session_state.get("last_post_title", "post_gamer"))
        return f"Listo. Guard\u00e9 el post en:\n\n`{archivo}`"

    if texto.startswith("aprobar") or "me gusta" in texto:
        accion = save_feedback(st.session_state.last_item_id, "news/post/topic", "approved", pregunta)
        extra = ""
        if st.session_state.get("last_post_text"):
            archivo = guardar_post_aprobado(st.session_state.last_post_text, st.session_state.get("last_post_title", "post_gamer"))
            extra = f"\n\nTambi\u00e9n guard? el ?ltimo post aprobado en:\n\n`{archivo}`"
        return f"Listo. Guard\u00e9 tu aprobaci\u00f3n.\n\nAcci?n: {accion}{extra}"
    if texto.startswith("rechazar") or "no me gusta" in texto:
        accion = save_feedback(st.session_state.last_item_id, "news/post/topic", "rejected", pregunta)
        return f"Listo. Guard\u00e9 el rechazo.\n\nAcci?n: {accion}"
    if (
        texto.startswith("corrige")
        or "no digas" in texto
        or "m\u00e1s corto" in texto
        or "mas corto" in texto
        or "m\u00e1s nostalgia" in texto
        or "mas nostalgia" in texto
        or "m\u00e1s debate" in texto
        or "mas debate" in texto
        or "no repetir" in texto
    ):
        accion = save_feedback(st.session_state.last_item_id, "post/topic", "correction", pregunta)
        return f"Listo. Guard\u00e9 esa correcci\u00f3n.\n\nAcci?n: {accion}"
    if "ver prompts" in texto:
        prompts = get_prompt_library()
        if not prompts:
            return "No encontr\u00e9 prompts guardados en prompts/prompt_library.json."
        return "### Prompts guardados\n\n" + "\n\n".join(
            f"**{p.get('name', 'sin nombre')}**\n{p.get('prompt', '')}"
            for p in prompts
        )
    if "ver voz de marca" in texto:
        brand = get_brand_voice()
        if not brand:
            return "No encontr\u00e9 la voz de marca en prompts/brand_voice.json."
        return f"### Voz de marca\n\n```json\n{json.dumps(brand, ensure_ascii=False, indent=2)}\n```"
    if "memoria" in texto or "preferencias" in texto:
        prefs = get_user_preferences()
        if not prefs:
            return "Todav\u00eda no hay preferencias guardadas."
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
        pedido_generico = tema_manual in ["", "nuevo", "nueva", "redes", "publicar", "hot", "viral", "del dia", "del d\u00eda"]

        if not marca_mencionada and pedido_generico and not numero and len(marcas_visibles()) > 1:
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
            item = elegir_noticia_nueva_para_post(detectar_interes_editorial(texto), pregunta)
        else:
            estilo_manual = "nostalgia" if estilo == "all" else estilo
            item = crear_item_desde_pedido(pregunta, estilo_manual)

        if not item:
            return (
                "No encontr\u00e9 una noticia verificada nueva para crear el post. "
                "Estoy usando filtro estricto: fuente oficial o confirmaci?n por 2+ fuentes. "
                "Puedes pedirme un debate, nostalgia u opini\u00f3n si quieres contenido editorial."
            )

        post = generate_social_post(item, estilo)
        st.session_state.last_post_items = [item]
        return post
    if any(p in texto for p in ["nostalgia", "retro", "cl\u00e1sico", "clasico", "viejo", "antiguo"]):
        return crear_nostalgia(pregunta)
    if any(p in texto for p in ["debate", "opini\u00f3n", "opinion", "vs", "versus"]):
        return crear_debate()
    cantidad_noticias = cantidad_posts if cantidad_posts > 1 else 5
    return formatear_noticias(buscar_noticias(), pregunta, cantidad_noticias)


# ---------------------------------------------------------------------------
# Motor editorial final
# Esta capa sobreescribe rutas viejas de generacion que quedaron de parches
# anteriores. La meta es simple: posts en espanol, coherentes con la noticia,
# sin frases internas, sin links visibles y sin mezclar categorias.
# ---------------------------------------------------------------------------

MOJIBAKE_FIXES_FINAL = {
    "Ã¡": "\u00e1", "Ã©": "\u00e9", "Ã­": "\u00ed", "Ã³": "\u00f3", "Ãº": "\u00fa", "Ã±": "\u00f1",
    "Ã�": "\u00c1", "Ã‰": "\u00c9", "Ã�": "\u00cd", "Ã“": "\u00d3", "Ãš": "\u00da", "Ã‘": "\u00d1",
    "Â¿": "\u00bf", "Â¡": "\u00a1", "Â": "",
    "ðŸŽ®": "\U0001f3ae", "ðŸ‘‡": "\U0001f447",
    "â€™": "'", "â€œ": '"', "â€�": '"', "â€“": "-", "â€”": "-", "â€¦": "...",
    "PUBLICACI?N": "PUBLICACI\u00d3N", "TECNOLOG?A": "TECNOLOG\u00cdA",
    "Preg?ntame": "Preg\u00fantame", "autom?ticamente": "autom\u00e1ticamente",
    "verificaci?n": "verificaci\u00f3n", "Verificaci?n": "Verificaci\u00f3n",
    "conversaci?n": "conversaci\u00f3n", "Conversaci?n": "Conversaci\u00f3n",
    "informaci?n": "informaci\u00f3n", "Informaci?n": "Informaci\u00f3n",
    "publicaci?n": "publicaci\u00f3n", "Publicaci?n": "Publicaci\u00f3n",
    "adaptaci?n": "adaptaci\u00f3n", "serializaci?n": "serializaci\u00f3n",
    "tecnolog?a": "tecnolog\u00eda", "Tecnolog?a": "Tecnolog\u00eda",
    "espa?ol": "espa\u00f1ol", "Espa?ol": "Espa\u00f1ol",
    "ingl?s": "ingl\u00e9s", "Ingl?s": "Ingl\u00e9s",
    "qu?": "qu\u00e9", "Qu?": "Qu\u00e9", "c?mo": "c\u00f3mo", "C?mo": "C\u00f3mo",
    "cu?l": "cu\u00e1l", "Cu?l": "Cu\u00e1l", "t?": "t\u00fa", "T?": "T\u00fa",
    "m?s": "m\u00e1s", "M?s": "M\u00e1s", "est?": "est\u00e1", "Est?": "Est\u00e1",
    "est?n": "est\u00e1n", "Est?n": "Est\u00e1n", "todav?a": "todav\u00eda",
    "f?sicos": "f\u00edsicos", "f?sico": "f\u00edsico", "t?cnico": "t\u00e9cnico",
    "cl?sicos": "cl\u00e1sicos", "cl?sico": "cl\u00e1sico",
    "nost?lgico": "nost\u00e1lgico", "nost?lgica": "nost\u00e1lgica",
    "se?al": "se\u00f1al", "se?ales": "se\u00f1ales",
}


def _texto_item_final(item):
    item = item or {}
    return limpiar_texto_publicable_final(
        f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}"
    ).lower()


def _tema_principal_final(titulo):
    titulo = limpiar_texto_publicable_final(titulo)
    if not titulo:
        return "Tema gamer"
    conocidos = [
        "Kingdom Hearts 4", "Diablo 4", "Diablo IV", "The Sinking City 2",
        "The Alters", "Palworld", "Call of Duty", "Black Ops", "Castlevania",
        "Belmont's Curse", "Thief: Gold", "Blue Box", "Ao no Hako",
        "Tetsuryo Meet With Tetsudou Musume", "Space Dragons", "GTA 6",
        "Grand Theft Auto VI", "Nintendo", "Xbox", "PlayStation", "GOG",
        "Apple", "iOS", "macOS",
    ]
    bajo = titulo.lower()
    for nombre in conocidos:
        if nombre.lower() in bajo:
            return nombre
    for patron in [r"'([^']{3,80})'", r'"([^"]{3,80})"', r"manga\s+([A-Z][^:,-]{3,70})", r"anime\s+([A-Z][^:,-]{3,70})"]:
        match = re.search(patron, titulo, flags=re.IGNORECASE)
        if match:
            return normalizar_titulo_gamer(match.group(1).strip())
    for sep in [":", " - ", " | "]:
        if sep in titulo:
            parte = titulo.split(sep, 1)[0].strip()
            if 2 < len(parte) < 80:
                return normalizar_titulo_gamer(parte)
    for sep in [
        " is ", " are ", " will ", " could ", " gets ", " joins ", " turns ",
        " concludes ", " ends ", " unveils ", " announces ", " reveals ",
        " update ", " news ", " release date ",
    ]:
        idx = bajo.find(sep)
        if idx > 2:
            return normalizar_titulo_gamer(titulo[:idx].strip(" -:,."))
    return normalizar_titulo_gamer(titulo[:70].strip(" -:,."))


def seleccionar_noticia_para_categoria(noticias, categoria, titulos_usados):
    for item in noticias:
        titulo = limpiar_texto_publicable_final(item.get("title", ""))
        key = titulo.lower().strip()
        if not key or key in titulos_usados:
            continue
        if tema_repetido(titulo) or tema_muy_similar(titulo):
            continue
        if _categoria_final_item(item, categoria) == categoria:
            titulos_usados.add(key)
            return dict(item)
    return None


def crear_item_desde_pedido(pregunta, estilo):
    tema = limpiar_pedido_post(pregunta)
    if not tema:
        return None
    titulo = normalizar_titulo_gamer(tema)
    categoria = _estilo_a_categoria(estilo)
    if categoria == "gaming":
        categoria = "nostalgia" if any(p in tema.lower() for p in ["gamecube", "game boy", "ps2", "retro", "nostalgia"]) else "debate"
    resumen = (
        f"{titulo} es un tema editorial solicitado por el usuario. "
        "No se presenta como noticia confirmada; se trabaja como conversaci\u00f3n de comunidad."
    )
    contexto_local = buscar_contexto_local(titulo)
    if contexto_local:
        resumen += " " + contexto_local.get("summary", "")
    item = {
        "id": str(uuid.uuid4()),
        "title": titulo,
        "summary": resumen,
        "source": "Tema solicitado por el usuario",
        "link": "",
        "date": str(ahora_en_puerto_rico().date()),
        "content_angle": categoria,
        "nostalgia_angle": detectar_angulo_nostalgia({"title": titulo, "summary": resumen}),
        "confidence_level": "manual",
    }
    st.session_state.generated_items[item["id"]] = item
    st.session_state.last_item_id = item["id"]
    return item


# ---------------------------------------------------------------------------
# Motor editorial descartado 2026-07-18
# Esta es la capa que manda antes de iniciar Streamlit. Usa patrones generales
# de categoria/accion/contenido y evita parches por nombre de noticia.
# ---------------------------------------------------------------------------

PALABRAS_INGLES_GENERALES = {
    "the", "and", "with", "for", "from", "this", "that", "players", "player",
    "update", "patch", "available", "coming", "launch", "launches", "release",
    "date", "report", "details", "official", "episode", "expect", "caused",
    "today", "july", "november", "acclaimed", "fantasy", "getting", "adaptation",
    "announced", "announces", "revealed", "reveals", "alongside", "teaser",
    "trailer", "could", "inherit", "physical", "digital", "crown", "default",
    "monthly", "games", "free", "days", "refutes", "notion", "foreign",
    "worker", "workers", "visas", "behind", "mass", "layoffs", "breaking",
    "concludes", "serialization", "hands", "president", "weighs", "drops",
    "increases", "ends", "after", "weekly", "shonen", "jump", "feature",
    "fired", "platforms", "builds", "transformative", "style", "joins",
    "turns", "tough", "bosses", "friends", "will", "drown", "mythics",
    "news", "sooner", "think", "unveils", "visual", "vote", "following",
    "first", "ever", "patron", "deep", "dive", "hands-on", "soon",
}

ACCIONES_TITULO_GENERALES = [
    ("cierre_serializacion", r"\b(concludes|ends|ending|final chapter|serialization|serializacion|serializaci[o\u00f3]n|termina|finaliza|cierre)\b"),
    ("adaptacion_anime", r"\b(getting an anime|anime adaptation|adaptation|adaptacion|adaptaci[o\u00f3]n)\b"),
    ("avance", r"\b(trailer|teaser|visual|gameplay|preview|avance|nuevo material)\b"),
    ("actualizacion", r"\b(update|patch|version|details|detailed|actualizacion|actualizaci[o\u00f3]n|parche)\b"),
    ("preventa", r"\b(pre[- ]?order|preorder|preventa|reserva)\b"),
    ("lanzamiento", r"\b(release date|launch|launches|coming soon|coming in|lanzamiento|estreno|sale el)\b"),
    ("preservacion", r"\b(preservation|preservacion|preservaci[o\u00f3]n|classic|classics|collection|remaster|remake|program)\b"),
    ("industria", r"\b(layoffs|despidos|fired workers|workers|visas|refutes|responds|claims|notion|studio closure|cierre de estudio)\b"),
    ("tecnologia", r"\b(public betas|ios|macos|platforms|gpu|hardware|rtx|nvidia|amd|intel|ram|recommended gpu|requisito)\b"),
    ("fisico_digital", r"\b(physical|digital|f[i\u00ed]sico|formato f[i\u00ed]sico|digital only)\b"),
    ("impresiones", r"\b(hands-on|hands on|impressions|report|deep dive|primeras impresiones|vistazo)\b"),
    ("mecanica", r"\b(turns|becomes|into|bosses|friends|mechanic|mecanica|mec[a\u00e1]nica)\b"),
]


def _texto_total_item(item):
    if isinstance(item, dict):
        base = f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}"
    else:
        base = str(item or "")
    return limpiar_texto_publicable_final(limpiar_html(base))


def _puntuar_categorias_final(item):
    scores = _puntuar_categorias(item)
    texto = _texto_total_item(item).lower()
    fuente = str((item or {}).get("source", "")).lower() if isinstance(item, dict) else ""
    if any(p in fuente for p in ["anime", "myanimelist", "crunchyroll", "anime corner"]):
        scores["anime"] += 3
    if any(p in texto for p in ["manga", "anime", "shonen", "visual", "serialization", "serializacion", "serializaci\u00f3n"]):
        scores["anime"] += 2
    if any(p in texto for p in ["gpu", "hardware", "ios", "macos", "apple", "nvidia", "amd", "intel", "ram", "unreal engine"]):
        scores["tecnologia"] += 2
    if any(p in texto for p in ["indie", "independent", "independiente", "demo", "steam next fest", "early access"]):
        scores["indie"] += 2
    if any(p in texto for p in ["layoff", "despidos", "workers", "price", "precio", "delay", "physical", "digital", "suscripci"]):
        scores["debate"] += 2
    if any(p in texto for p in ["preservation", "preservaci", "classic", "clasico", "cl\u00e1sico", "retro", "remake", "remaster"]):
        scores["nostalgia"] += 2
    return scores


def _limpiar_tema_extraido(tema):
    tema = limpiar_texto_publicable_final(tema)
    tema = re.sub(r"^(manga|anime|game|juego|the post)\s+", "", tema, flags=re.IGNORECASE).strip()
    tema = re.sub(r"\s+(manga|anime|game|juego|news|update|patch|trailer|teaser)$", "", tema, flags=re.IGNORECASE).strip()
    tema = tema.strip(" -:.,'\"")
    if not tema:
        return "Tema gamer"
    return normalizar_titulo_gamer(tema)


def traducir_basico_en_espanol(texto):
    limpio = limpiar_texto_publicable_final(limpiar_html(texto))
    if not limpio:
        return ""
    reemplazos = [
        (r"\bhas announced\b", "anunci\u00f3"),
        (r"\bannounced\b", "anunci\u00f3"),
        (r"\bannounces\b", "anuncia"),
        (r"\brevealed\b", "revel\u00f3"),
        (r"\breveals\b", "revela"),
        (r"\bunveils\b", "muestra"),
        (r"\bgetting an anime\b", "tendr\u00e1 adaptaci\u00f3n al anime"),
        (r"\banime adaptation\b", "adaptaci\u00f3n al anime"),
        (r"\bcoming in\b", "llegar\u00e1 en"),
        (r"\bcoming soon\b", "llegar\u00e1 pronto"),
        (r"\brelease date\b", "fecha de lanzamiento"),
        (r"\bteaser trailer\b", "avance"),
        (r"\btrailer\b", "avance"),
        (r"\bnew visual\b", "nuevo visual"),
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
        (r"\bafter\b", "despu\u00e9s de"),
        (r"\bwith\b", "con"),
        (r"\balongside\b", "junto a"),
        (r"\bfor\b", "para"),
        (r"\bwill\b", ""),
        (r"\bcould\b", "podr\u00eda"),
    ]
    traducido = limpio
    for patron, reemplazo in reemplazos:
        traducido = re.sub(patron, reemplazo, traducido, flags=re.IGNORECASE)
    traducido = re.sub(r"\s{2,}", " ", traducido).strip()
    return limpiar_texto_publicable_final(traducido)


def _frase_real_del_resumen(resumen, titulo_publico=""):
    resumen = limpiar_texto_publicable_final(resumen)
    if not resumen:
        return ""
    frases = re.split(r"(?<=[.!?])\s+", resumen)
    for frase in frases:
        frase = limpiar_texto_publicable_final(frase)
        if len(frase) < 45:
            continue
        if linea_no_publicable(frase) or parece_texto_ingles(frase):
            continue
        if titulo_publico and frase.lower().startswith(titulo_publico.lower()):
            continue
        return recortar_texto(frase, 260)
    return ""


def seleccionar_noticia_para_categoria(noticias, categoria, titulos_usados):
    for item in noticias:
        titulo = limpiar_texto_publicable_final(item.get("title", ""))
        key = titulo.lower().strip()
        if not key or key in titulos_usados:
            continue
        if tema_repetido(titulo) or tema_muy_similar(titulo):
            continue
        if _categoria_final_item(item, categoria) == categoria:
            titulos_usados.add(key)
            return dict(item)
    return None


# ---------------------------------------------------------------------------
# Motor editorial saneado
# Ultima capa activa antes de iniciar Streamlit. Evita los errores vistos:
# - titulos largos en ingles visibles
# - cuerpo que no corresponde con la categoria
# - frases internas o genericas en captions
# - fallback que etiqueta cualquier noticia como cualquier categoria
# ---------------------------------------------------------------------------

FRASES_PLANTILLA_BLOQUEADAS = [
    "lo importante es explicar",
    "lo interesante es mirar",
    "tema reciente dentro del mundo gamer",
    "puede servir para descubrir algo fuera",
    "el feed no trae suficiente detalle",
    "conviene usarlo como punto de entrada",
    "la clave es explicar",
    "este tipo de tema conecta con la comunidad porque cada gamer",
    "qu\u00e9 conversaci\u00f3n puede abrir",
    "que conversacion puede abrir",
    "qu\u00e9 pregunta puede mover comentarios reales",
    "que pregunta puede mover comentarios reales",
    "noticia para comentar es un tema",
]

PALABRAS_INGLES_VISIBLES = {
    "the", "and", "with", "for", "from", "this", "that", "into", "after",
    "before", "players", "player", "update", "patch", "available", "today",
    "coming", "launch", "release", "date", "details", "announced", "revealed",
    "unveils", "trailer", "teaser", "could", "will", "joins", "following",
    "physical", "digital", "workers", "layoffs", "ends", "concludes", "gets",
    "getting", "hands", "deep", "dive", "first", "ever", "mass", "refutes",
    "behind", "powerful", "friends", "bosses", "drown", "mythics", "news",
    "new", "gameplay", "mechanic", "changes", "rewards", "progression",
    "classic", "stealth", "part", "program", "fans", "may", "information",
    "soon", "tough", "conversation", "about", "changing", "retail",
    "strategies", "games",
}

PATRONES_ACCION_TITULO = [
    ("senal", r"\b(could come|news could|sooner than|may get|might get|podr[i\u00ed]a)\b"),
    ("cierre_serializacion", r"\b(concludes|ends|final chapter|termina|finaliza|cierra|serialization|serializaci[o\u00f3]n)\b"),
    ("adaptacion_anime", r"\b(getting an anime|anime adaptation|adaptaci[o\u00f3]n al anime)\b"),
    ("avance", r"\b(trailer|teaser|new visual|visual|gameplay|hands[- ]on|preview|avance|tr[a\u00e1]iler)\b"),
    ("mecanica", r"\b(turns tough|bosses|powerful friends|mechanic|mec[a\u00e1]nica)\b"),
    ("actualizacion", r"\b(update|patch|version|temporada|season|actualizaci[o\u00f3]n|nuevos detalles|new details)\b"),
    ("preventa", r"\b(pre[- ]?order|preventa|reserva)\b"),
    ("lanzamiento", r"\b(release date|launch|launches|coming soon|coming in|llega|lanzamiento|estreno)\b"),
    ("preservacion", r"\b(preservation|preservaci[o\u00f3]n|classic|cl[a\u00e1]sico|collection|remaster|remake)\b"),
    ("industria", r"\b(layoff|layoffs|despidos|workers|fired|visas|studio closes|industria)\b"),
    ("fisico_digital", r"\b(physical|digital|f[i\u00ed]sico|cartucho|disco|manual)\b"),
    ("tecnologia", r"\b(gpu|rtx|nvidia|amd|intel|hardware|ios|macos|apple|ram|cloud|unreal engine|godot)\b"),
]


def _texto_item_editorial(item):
    item = item or {}
    return limpiar_texto_publicable_final(
        f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}"
    ).lower()


def traducir_basico_en_espanol(texto):
    limpio = limpiar_texto_publicable_final(texto)
    reemplazos = [
        (r"\bhas announced\b", "anunci\u00f3"),
        (r"\bannounced\b", "anunci\u00f3"),
        (r"\bannounces\b", "anuncia"),
        (r"\brevealed\b", "revel\u00f3"),
        (r"\breveals\b", "revela"),
        (r"\bunveils\b", "muestra"),
        (r"\bgetting an anime\b", "tendr\u00e1 adaptaci\u00f3n al anime"),
        (r"\banime adaptation\b", "adaptaci\u00f3n al anime"),
        (r"\bcoming in\b", "llegar\u00e1 en"),
        (r"\bcoming soon\b", "llegar\u00e1 pronto"),
        (r"\brelease date\b", "fecha de lanzamiento"),
        (r"\bteaser trailer\b", "avance"),
        (r"\btrailer\b", "avance"),
        (r"\bnew visual\b", "nuevo visual"),
        (r"\bnew details\b", "nuevos detalles"),
        (r"\bupdate\b", "actualizaci\u00f3n"),
        (r"\bavailable today\b", "disponible hoy"),
        (r"\bhands-on\b", "primeras impresiones"),
        (r"\bplayers\b", "jugadores"),
        (r"\bdevelopers\b", "desarrolladores"),
        (r"\bcommunity\b", "comunidad"),
        (r"\bfans\b", "fans"),
        (r"\bseason\b", "temporada"),
        (r"\bphysical games\b", "juegos f\u00edsicos"),
        (r"\bdigital games\b", "juegos digitales"),
        (r"\bopen world\b", "mundo abierto"),
        (r"\ba conversation about\b", "Una conversación sobre"),
        (r"\bchanging retail strategies\b", "cambios en las estrategias de venta"),
        (r"\bclassic stealth game\b", "juego clásico de sigilo"),
        (r"\bjoins the preservation program\b", "entra al programa de preservación"),
        (r"\bgames\b", "juegos"),
        (r"\bgame\b", "juego"),
        (r"\band\b", "y"),
        (r"^\bthe\b\s+", "El "),
    ]
    salida = limpio
    for patron, reemplazo in reemplazos:
        salida = re.sub(patron, reemplazo, salida, flags=re.IGNORECASE)
    return limpiar_texto_publicable_final(salida)


def seleccionar_noticia_para_categoria(noticias, categoria, titulos_usados):
    for item in noticias:
        titulo = limpiar_texto_publicable_final(item.get("title", ""))
        key = titulo.lower().strip()
        if not key or key in titulos_usados:
            continue
        if tema_repetido(titulo) or tema_muy_similar(titulo):
            continue
        if _categoria_final_item(item) == categoria:
            titulos_usados.add(key)
            return dict(item)
    return None


from editorial_engine_final import install_editorial_engine

install_editorial_engine(globals())


preparar_memoria()
registrar_acceso_simple()

if st.session_state.get("app_version") != APP_VERSION:
    for key in [
        "mensajes",
        "generated_items",
        "last_item_id",
        "news_by_number",
        "last_post_text",
        "last_post_title",
        "last_post_items",
        "pending_post_request",
    ]:
        st.session_state.pop(key, None)
    st.session_state.app_version = APP_VERSION

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {
            "role": "assistant",
            "content": "Hola. Soy Gamer Signal. Pregúntame por noticias gamer, nostalgia, debates o posts para Instagram/Facebook.",
        }
    ]
else:
    for mensaje in st.session_state.mensajes:
        if mensaje.get("role") == "assistant" and "content" in mensaje:
            mensaje["content"] = limpiar_gramatica_post_final(mensaje["content"])

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
    <div class="corner-gs-logo" aria-label="Gamer Signal"><span>GS</span></div>
    <div class="gamer-signal-header">
        {header_mascot_html}
        <h1 class="gamer-signal-title">Gamer Signal</h1>
        <div class="gamer-signal-subtitle">Noticias, nostalgia gamer, debates y posts para tus marcas.</div>
        <div class="gamer-signal-build">Actualizado {APP_VERSION}</div>
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

    st.caption("Tip: puedes escribir 'post de la noticia 2' para usar una noticia espec\u00edfica.")

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
        st.cache_data.clear()
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
        st.write("Todav\u00eda no hay temas usados.")
    st.divider()
    st.subheader("Preferencias guardadas")
    prefs = get_user_preferences()
    if prefs:
        st.json(prefs)
    else:
        st.write("No hay preferencias guardadas todav\u00eda.")

    render_access_log_simple()

RADAR_BUCKET_FALLBACKS = {
    "noticia_actual": {
        "title": "Tema gamer actual para vigilar",
        "summary": "Oportunidad editorial para buscar una fuente oficial o confiable antes de convertirla en noticia.",
        "source": "Radar editorial Gamer Signal",
        "angle": "Usarlo solo cuando aparezca una fuente fuerte: qu\u00e9 pas\u00f3, por qu\u00e9 importa y pregunta final.",
    },
    "debate": {
        "title": "Teor\u00eda geek para abrir debate",
        "summary": "Tema de comunidad para presentar dos lados, aclarando que no es noticia confirmada.",
        "source": "Se\u00f1al de comunidad / teor\u00eda fandom",
        "angle": "Plantearlo como conversaci\u00f3n: qu\u00e9 piensa la comunidad, qu\u00e9 evidencia hay y qu\u00e9 dudas quedan.",
    },
    "nostalgia": {
        "title": "Recuerdo gamer que puede mover comentarios",
        "summary": "Tema nost\u00e1lgico para conectar con juegos f\u00edsicos, consolas viejas y experiencias de infancia.",
        "source": "Memoria editorial Gamer Signal",
        "angle": "Conectarlo con una escena concreta: cartuchos, discos, controles prestados o multiplayer local.",
    },
    "tecnologia": {
        "title": "Tecnolog\u00eda gamer para explicar simple",
        "summary": "Tema para bajar hardware, servicios o funciones a lenguaje claro para jugadores.",
        "source": "Radar editorial Gamer Signal",
        "angle": "Explicarlo desde el impacto real: rendimiento, precio, comodidad, acceso o experiencia.",
    },
    "anime": {
        "title": "Anime/geek para conectar con fandom",
        "summary": "Tema de anime, manga o casa productora para buscar confirmaci\u00f3n en fuentes oficiales/confiables.",
        "source": "Radar anime / fuentes de estudios",
        "angle": "Cruzar fandom, hype, adaptaci\u00f3n, estudio, staff o fecha sin inventar detalles.",
    },
    "indie": {
        "title": "Indie para poner en el radar",
        "summary": "Tema para descubrir juegos peque\u00f1os, demos o proyectos que puedan crecer por recomendaci\u00f3n.",
        "source": "Radar editorial Gamer Signal",
        "angle": "Presentarlo como descubrimiento: qu\u00e9 lo hace diferente y por qu\u00e9 vale mirarlo.",
    },
}


def crear_item_radar_editorial(bucket):
    data = RADAR_BUCKET_FALLBACKS.get(bucket, RADAR_BUCKET_FALLBACKS["noticia_actual"])
    categoria = "gaming" if bucket == "noticia_actual" else bucket
    return {
        "id": f"radar-editorial-{bucket}",
        "title": data["title"],
        "summary": data["summary"],
        "source": data["source"],
        "date": str(ahora_en_puerto_rico().date()),
        "link": "",
        "content_angle": categoria,
        "monitor_bucket": bucket,
        "is_editorial": True,
        "is_community_signal": bucket in ["debate", "nostalgia"],
        "source_official": False,
        "source_trusted": False,
        "confidence_level": "editorial",
        "verification_count": 0,
        "verification_level": "idea editorial / no es noticia confirmada",
        "angle": data["angle"],
    }


def titulo_crudo_sigue_en_ingles(texto):
    texto = limpiar_para_ui(limpiar_texto_publicable_final(texto or ""))
    bajo = f" {texto.lower()} "
    patrones = [
        " i was ", " i am ", " will ", " could ", " gets ", " getting ",
        " joins ", " following ", " after ", " before ", " worth ", " checking ",
        " weekend guide ", " release date ", " hands-on ", " unveils ",
        " reveals ", " announced ", " update will ", " are set for ",
    ]
    return any(p in bajo for p in patrones)


def titulo_radar_seguro(item, bucket):
    item = item or {}
    try:
        titulo = titulo_visible_seguro(item, "news", bucket)
    except Exception:
        titulo = item.get("title", "")
    titulo = limpiar_gramatica_post_final(limpiar_para_ui(titulo))
    try:
        pobre = titulo_generico_o_pobre(titulo)
    except Exception:
        pobre = len(titulo.strip()) < 10

    if pobre or titulo_crudo_sigue_en_ingles(titulo) or parece_texto_ingles(titulo):
        try:
            convertido = titulo_publico_en_espanol(item.get("title", ""), bucket)
            convertido = limpiar_gramatica_post_final(limpiar_para_ui(convertido))
        except Exception:
            convertido = ""
        try:
            convertido_pobre = titulo_generico_o_pobre(convertido)
        except Exception:
            convertido_pobre = len(convertido.strip()) < 10
        if convertido and not convertido_pobre and not titulo_crudo_sigue_en_ingles(convertido) and not parece_texto_ingles(convertido):
            titulo = convertido
        else:
            titulo = RADAR_BUCKET_FALLBACKS.get(bucket, RADAR_BUCKET_FALLBACKS["noticia_actual"])["title"]

    return limpiar_gramatica_post_final(titulo)


def contenido_radar_item(item, bucket, fallback_angle=None):
    item = item or crear_item_radar_editorial(bucket)
    titulo = html_escape(titulo_radar_seguro(item, bucket))
    fuente = html_escape(limpiar_para_ui(item.get("source", "fuente")))
    if item.get("is_editorial"):
        color, verificacion = "Editorial", "idea para crear contenido; no es noticia confirmada"
    else:
        color, verificacion = estado_verificacion_item(item)
    color = limpiar_para_ui(color)
    verificacion = limpiar_para_ui(verificacion)
    angulo = item.get("angle") or fallback_angle or angulo_para_bucket(bucket)
    angulo = html_escape(limpiar_para_ui(limpiar_gramatica_post_final(angulo)))
    return (
        f'<div class="daily-radar-item"><strong>{titulo}</strong><br>{fuente}</div>'
        f'<div class="daily-radar-angle">Verificaci\u00f3n: {html_escape(color)} - {html_escape(verificacion)}</div>'
        f'<div class="daily-radar-angle">{angulo}</div>'
    )


def render_daily_radar_panel():
    left, center, right = st.columns([1, 1.6, 1])
    with center:
        if st.button("Actualizar radar", key="refresh_daily_radar", use_container_width=True):
            st.cache_data.clear()
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
        ("tecnologia", "Tecnolog\u00eda"),
        ("anime", "Anime / Geek"),
        ("indie", "Indie"),
    ]

    brand_cards = []
    for marca, fallback in marcas:
        items = memoria.get("brands", {}).get(marca, [])[:1]
        logo = html_escape(logo_data_url(marca), quote=True)
        if items:
            item = items[0]
            bucket = item.get("bucket") or item.get("monitor_bucket") or monitor_bucket_item(item)
            contenido = contenido_radar_item(item, bucket, fallback)
        else:
            contenido = f'<div class="daily-radar-item">{html_escape(limpiar_para_ui(fallback))}</div>'
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
            contenido = contenido_radar_item(item, bucket)
        else:
            contenido = contenido_radar_item(crear_item_radar_editorial(bucket), bucket)
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
            <div class="daily-radar-section-title">Temas calientes por categor\u00eda</div>
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
            contenido = mensaje["content"]
            if mensaje["role"] == "assistant":
                contenido = limpiar_gramatica_post_final(contenido)
            st.write(contenido)

if chat_iniciado:
    render_last_post_box()
