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


APP_VERSION = "2026.07.18-9"

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
    "Crunchyroll News oficial": "https://www.crunchyroll.com/newsrss",
    "Anime News Network confiable": "https://www.animenewsnetwork.com/all/rss.xmlann-edition=us",
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
    "Engadget confiable": "https://www.engadget.com/rss.xml",
    "TechCrunch AI confiable": "https://techcrunch.com/category/artificial-intelligence/feed/",
}

FUENTES_COMUNIDAD = {
    "Reddit Gaming - se\u00f1al de comunidad": "https://www.reddit.com/r/gaming/.rss",
    "Reddit TrueGaming - se\u00f1al de debate": "https://www.reddit.com/r/truegaming/.rss",
    "Reddit PatientGamers - se\u00f1al nostalgia": "https://www.reddit.com/r/patientgamers/.rss",
    "Reddit RetroGaming - se\u00f1al nostalgia": "https://www.reddit.com/r/retrogaming/.rss",
    "Reddit Nintendo - se\u00f1al comunidad": "https://www.reddit.com/r/nintendo/.rss",
    "Reddit PlayStation - se\u00f1al comunidad": "https://www.reddit.com/r/playstation/.rss",
    "Reddit Xbox - se\u00f1al comunidad": "https://www.reddit.com/r/xbox/.rss",
    "Reddit PCGaming - se\u00f1al comunidad": "https://www.reddit.com/r/pcgaming/.rss",
    "Reddit IndieGaming - se\u00f1al indie": "https://www.reddit.com/r/indiegaming/.rss",
    "Reddit Anime - se\u00f1al anime": "https://www.reddit.com/r/anime/.rss",
    "Reddit Manga - se\u00f1al anime": "https://www.reddit.com/r/manga/.rss",
    "Reddit JRPG - se\u00f1al fandom": "https://www.reddit.com/r/JRPG/.rss",
    "Reddit Argaming - se\u00f1al LatAm": "https://www.reddit.com/r/Argaming/.rss",
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
        "**Qu? mirar para explicar c\u00f3mo se juega:**\n"
        "- G\u00e9nero y objetivo principal del juego.\n"
        "- Modos: historia, online, cooperativo, competitivo o local.\n"
        "- Mec?nicas principales: combate, exploraci\u00f3n, progresi\u00f3n, construcci?n, carreras, RPG, puzzles o estrategia.\n"
        "- Plataformas disponibles y si tiene crossplay, edici\u00f3n especial, DLC o servicio online.\n"
        "- Qu? lo hace interesante para la comunidad gamer de Puerto Rico y LatAm.\n"
        "- Pregunta final para comentarios: \u00bflo jugar?as?, lo recomiendas o lo dejar?as pasar\n"
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
        respuesta += "\n**Se?ales recientes de comunidad (no son noticia confirmada):**\n"
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


def categoria_de_item(item):
    item = item or {}
    angulo = str(item.get("content_angle", "")).lower()
    if angulo in ["anime", "indie", "debate", "nostalgia"]:
        return angulo
    if angulo in ["hardware", "technology", "tecnologia"]:
        return "tecnologia"
    return _categoria_ganadora(_puntuar_categorias(item))


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


def seleccionar_noticias_variadas(noticias, cantidad, texto_usuario=""):
    """Elige noticias reales con mezcla de categorias y fuentes."""
    cantidad = max(1, min(cantidad, 8))
    exclusiones = detectar_exclusiones_usuario(texto_usuario)
    disponibles = [
        item for item in filtrar_noticias_verificadas(noticias)
        if item_cumple_exclusiones(item, exclusiones)
    ]
    titulos_usados = set()
    fuentes_usadas = {}
    plataformas_usadas = {}
    seleccionadas = []

    def puede_usarse(item, controlar_fuente=True):
        titulo_key = item.get("title", "").lower().strip()
        if not titulo_key or titulo_key in titulos_usados:
            return False
        if tema_repetido(item.get("title", "")) or tema_muy_similar(item.get("title", "")):
            return False
        if controlar_fuente and cantidad >= 4:
            fuente = item.get("source", "fuente")
            if fuentes_usadas.get(fuente, 0) >= 2:
                return False
            plataforma = plataforma_de_item(item)
            if plataforma != "general" and plataformas_usadas.get(plataforma, 0) >= 2:
                return False
        return True

    def agregar(item):
        titulo_key = item.get("title", "").lower().strip()
        fuente = item.get("source", "fuente")
        plataforma = plataforma_de_item(item)
        titulos_usados.add(titulo_key)
        fuentes_usadas[fuente] = fuentes_usadas.get(fuente, 0) + 1
        plataformas_usadas[plataforma] = plataformas_usadas.get(plataforma, 0) + 1
        seleccionadas.append(dict(item))

    for categoria in categorias_para_posts(cantidad, texto_usuario or "noticias"):
        for item in disponibles:
            if len(seleccionadas) >= cantidad:
                break
            if categoria_de_item(item) == categoria and puede_usarse(item):
                agregar(item)
                break
        if len(seleccionadas) >= cantidad:
            break

    for controlar_fuente in [True, False]:
        for item in disponibles:
            if len(seleccionadas) >= cantidad:
                break
            if puede_usarse(item, controlar_fuente=controlar_fuente):
                agregar(item)

    return seleccionadas


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


def crear_item_editorial_categoria(categoria, titulos_usados):
    if categoria == "indie":
        temas = [
            "indies con demos que est\u00e1n ganando conversaci\u00f3n",
            "juegos independientes que vale la pena seguir",
            "propuestas indie con mec\u00e1nicas diferentes",
            "joyas independientes que buscan espacio entre grandes lanzamientos",
        ]
        resumen = (
            "Tema editorial para descubrir juegos independientes con una propuesta clara. "
            "No debe presentarse como tendencia confirmada sin se\u00f1ales recientes o fuentes verificadas."
        )
        fuente = "Tema editorial de juegos indie"
        estilo = "indie"
    elif categoria == "nostalgia":
        temas = TEMAS_NOSTALGIA
        resumen = (
            "Tema nost\u00e1lgico para conectar con recuerdos de infancia, consolas viejas, "
            "juegos f\u00edsicos, multiplayer local y experiencias que muchos gamers de Puerto Rico y LatAm reconocen."
        )
        fuente = "Tema nost\u00e1lgico del proyecto"
        estilo = "nostalgia"
    elif categoria == "debate":
        temas = TEMAS_COMUNIDAD
        resumen = (
            "Tema de debate de comunidad. No se presenta como noticia confirmada; sirve para provocar comentarios, "
            "opiniones y conversaci\u00f3n gamer sin inventar datos."
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
            "Tema de tecnolog\u00eda explicado desde el punto de vista gamer, con lenguaje simple y enfocado en por qu\u00e9 importa."
        )
        fuente = "Tema editorial de tecnolog\u00eda"
        estilo = "technology"
    else:
        temas = [
            f"juegos de {ANIO_NOTICIAS}",
            "lanzamientos esperados",
            "servicios de suscripci\u00f3n gaming",
            "actualidad de consolas",
        ]
        resumen = (
            "Tema gamer general para convertir actualidad, opini\u00f3n o cultura de videojuegos en un post claro y conversacional."
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
    base = ["gaming", "tecnologia", "anime", "indie", "debate", "nostalgia"]
    if "noticia" in texto or "noticias" in texto or "actualidad" in texto:
        base = ["gaming", "tecnologia", "anime", "indie", "debate", "nostalgia"]
    if "anime" in texto:
        base = ["anime", "gaming", "tecnologia", "debate", "nostalgia", "indie"]
    elif "debate" in texto:
        base = ["debate", "gaming", "anime", "tecnologia", "nostalgia", "indie"]
    elif "nostalgia" in texto or "retro" in texto:
        base = ["nostalgia", "gaming", "anime", "debate", "tecnologia", "indie"]

    categorias = []
    while len(categorias) < cantidad:
        categorias.extend(base)
    return categorias[:cantidad]


def crear_varios_posts(cantidad, pregunta):
    cantidad = max(2, min(cantidad, 8))
    texto = pregunta.lower()
    exclusiones = detectar_exclusiones_usuario(texto)
    noticias = [
        item for item in filtrar_noticias_verificadas(buscar_noticias())
        if item_cumple_exclusiones(item, exclusiones)
    ]
    noticias = seleccionar_noticias_variadas(noticias, min(cantidad * 2, 8), texto)
    titulos_usados = set()
    posts = []
    items_generados = []
    st.session_state.news_by_number = {}

    estilos = {
        "gaming": "noticia",
        "indie": "indie",
        "tecnologia": "tecnologia",
        "nostalgia": "nostalgia",
        "anime": "anime",
        "debate": "debate",
    }

    for indice, categoria in enumerate(categorias_para_posts(cantidad, texto), start=1):
        item = seleccionar_noticia_para_categoria(noticias, categoria, titulos_usados)
        if not item:
            item = crear_item_editorial_categoria(categoria, titulos_usados)
        item = dict(item)
        categoria_real = categoria_de_item(item)
        if item_es_contexto_editorial(item):
            categoria_real = categoria
        if categoria_real not in estilos:
            categoria_real = categoria

        st.session_state.generated_items[item["id"]] = item
        st.session_state.news_by_number[indice] = item
        st.session_state.last_item_id = item["id"]
        items_generados.append(item)

        estilo_post = estilos.get(categoria_real, "noticia")
        if (
            not noticia_verificada_para_publicar(item)
            and categoria_real in ["gaming", "indie", "tecnologia", "anime"]
        ):
            estilo_post = "debate"

        post = generate_social_post(item, estilo_post)
        etiqueta = etiqueta_publicacion_limpia(categoria_real)
        if not noticia_verificada_para_publicar(item) and categoria_real in ["gaming", "indie", "tecnologia", "anime"]:
            etiqueta = f"{etiqueta}/Editorial"

        posts.append(
            f"PUBLICACIÓN {indice} - {reparar_texto_roto(etiqueta.upper())}\n\n{post}"
        )

    respuesta = "\n\n---\n\n".join(posts)
    respuesta = limpiar_gramatica_post_final(reparar_texto_roto(limpiar_texto_publicable_final(respuesta)))
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
        return "\u00bfPara cu?l marca quieres el calendario: Gamer Cave o Daviet Gaming"

    if marca == "Daviet Gaming":
        return """
### Calendario semanal de Daviet Gaming

**Lunes:** noticia reciente de gaming, PC o tecnolog\u00eda explicada de forma sencilla.

**Martes:** hardware, accesorios, setup o una funci?n ?til para gamers.

**Mi?rcoles:** anime, cultura geek o recomendaci?n relacionada con gaming.

**Jueves:** nostalgia, opini\u00f3n personal o experiencia gamer.

**Viernes:** noticia hot convertida en una pregunta para conversaci\u00f3n.

**S?bado:** recomendaci?n, comparaci?n o tema para compartir con la comunidad.

**Domingo:** resumen ligero, recuerdo gamer o adelanto de la pr?xima semana.
"""

    return """
### Calendario semanal de El Gamer Cave

**Lunes:** noticia oficial de gaming o tecnolog\u00eda.

**Martes:** nostalgia gamer: consolas viejas, juegos f\u00edsicos, Game Boy, GameCube o Pok\u00e9mon.

**Mi?rcoles:** debate de comunidad: f\u00edsico vs digital, online vs local, remakes vs originales.

**Jueves:** post emocional: recuerdos de infancia, jugar con primos, controles prestados o memory cards.

**Viernes:** pregunta r?pida para comentarios.

**S?bado:** recomendaci?n o comparaci?n gamer.

**Domingo:** post ligero de recuerdos, ranking o "?te acuerdas de...".
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
        "debate": "Usarlo para abrir conversaci\u00f3n con dos lados claros y sin imponer conclusi?n.",
        "nostalgia": "Conectarlo con recuerdos gamer, consolas viejas, juegos f\u00edsicos y comunidad.",
        "tecnologia": "Explicarlo desde c\u00f3mo afecta la experiencia gamer, PC, hardware o servicios.",
        "anime": "Cruzar anime y cultura geek con gaming, hype, fandom o adaptaci\u00f3n.",
        "indie": "Presentarlo como descubrimiento: qu\u00e9 lo hace diferente y por qu\u00e9 vale mirarlo.",
    }
    return angulos.get(bucket, "Convertirlo en post simple, ?til y f\u00e1cil de comentar.")



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


def detectar_content_angle(item):
    item = item or {}
    scores = _puntuar_categorias(item)
    categoria = _categoria_ganadora(scores)
    if categoria == "tecnologia":
        texto = _texto_categoria_desde_item(item)
        if any(p in texto for p in ["hardware", "gpu", "rtx", "nvidia", "amd", "intel", "cpu", "processor", "steam deck", "handheld"]):
            return "hardware"
        return "technology"
    if categoria == "gaming":
        return "news"
    return categoria


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
                "Se?al de conversaci\u00f3n detectada en comunidad. "
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
                "verification_level": "se\u00f1al de comunidad; no confirma noticia",
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
    angulo = categoria_de_item(item)
    texto = f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}".lower()
    if angulo == "anime" or "anime" in texto or "manga" in texto or "crunchyroll" in texto:
        return "anime"
    if angulo in ["tecnologia", "hardware", "technology"] or any(p in texto for p in ["nvidia", "rtx", "gpu", "hardware", "pc gaming", "steam deck", "unreal engine", "unity"]):
        return "tecnologia"
    if angulo == "indie" or any(p in texto for p in SENALES_INDIE):
        return "indie"
    if angulo == "nostalgia" or detectar_angulo_nostalgia(item):
        return "nostalgia"
    if angulo == "debate" or any(p in texto for p in ["precio", "suscripcion", "suscripci\u00f3n", "digital", "fisico", "f\u00edsico", "game pass", "ps plus", "microtransacciones"]):
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
            return "Convertirlo en pregunta de comunidad con dos lados claros, sin imponer conclusi?n."
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


def crear_hashtags(texto, limite=None):
    texto = reparar_texto_roto(str(texto or "")).lower()
    brand = get_brand_voice()
    defaults = [tag.lower() for tag in brand.get("default_hashtags", ["#gaming", "#nostalgia", "#geek", "#puertorico", "#latam"])]
    if brand.get("brand") == "Daviet Gaming":
        marca_tag = "#davietgaming"
    elif brand.get("brand") == "El Gamer Cave":
        marca_tag = "#elgamercave"
    else:
        marca_tag = defaults[0] if defaults else "#gaming"

    topic_tags = []
    if "nintendo" in texto or "mario" in texto or "zelda" in texto or "kirby" in texto:
        topic_tags.extend(["#nintendo", "#nintendoswitch"])
    if "playstation" in texto or "ps2" in texto or "ps1" in texto:
        topic_tags.extend(["#playstation", "#ps5"])
    if "xbox" in texto:
        topic_tags.extend(["#xbox", "#xboxseriesx"])
    if "diablo" in texto or "blizzard" in texto:
        topic_tags.extend(["#diablo", "#blizzard"])
    if "kingdom hearts" in texto:
        topic_tags.extend(["#kingdomhearts", "#squareenix"])
    if "call of duty" in texto:
        topic_tags.extend(["#callofduty", "#cod"])
    if "pokemon" in texto or "pokémon" in texto or "pok\u00e9mon" in texto:
        topic_tags.append("#pokemon")
    if "pc" in texto or "steam" in texto:
        topic_tags.extend(["#pcgaming", "#steam"])
    if "hardware" in texto or "nvidia" in texto or "rtx" in texto or "gpu" in texto or "tecnología" in texto or "technology" in texto:
        topic_tags.extend(["#gamingtech", "#hardware", "#pcgaming"])
    if "anime" in texto or "manga" in texto or "crunchyroll" in texto:
        topic_tags.extend(["#anime", "#manga", "#otaku", "#geekculture"])
    if "indie" in texto or "demo" in texto:
        topic_tags.extend(["#indiegames", "#indiegaming"])
    if "nostalgia" in texto or "retro" in texto or "fisico" in texto or "físico" in texto:
        topic_tags.extend(["#nostalgia", "#retrogaming"])
    if brand.get("brand") == "Daviet Gaming":
        if "noticia" in texto or "news" in texto or "anuncio" in texto or "lanzamiento" in texto:
            topic_tags.extend(["#gamingnews", "#noticiasgaming", "#gamerslatam"])
        if "setup" in texto or "pc gaming" in texto or "gaming pc" in texto:
            topic_tags.extend(["#setupgamer", "#gamingpc"])
        if "msi" in texto:
            topic_tags.append("#msi")
        if "frieren" in texto:
            topic_tags.extend(["#frieren", "#animegaming"])

    genericos = [tag for tag in defaults if tag != marca_tag]
    hashtags = [marca_tag] + topic_tags + genericos
    hashtags = list(dict.fromkeys(tag.lower() for tag in hashtags))
    return limitar_hashtags_texto(" ".join(hashtags), limite)


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


def reparar_texto_roto(texto):
    if not texto:
        return ""
    texto = str(texto)

    for _ in range(3):
        if not any(marca in texto for marca in ["\u00c3", "\u00c2", "\u00e2", "\u00f0"]):
            break
        try:
            reparado = texto.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if reparado == texto:
            break
        texto = reparado

    reemplazos = {
        "\u00c3\u00a1": "\u00e1", "\u00c3\u00a9": "\u00e9", "\u00c3\u00ad": "\u00ed",
        "\u00c3\u00b3": "\u00f3", "\u00c3\u00ba": "\u00fa", "\u00c3\u00b1": "\u00f1",
        "\u00c3\u0081": "\u00c1", "\u00c3\u0089": "\u00c9", "\u00c3\u008d": "\u00cd",
        "\u00c3\u0093": "\u00d3", "\u00c3\u009a": "\u00da", "\u00c3\u0091": "\u00d1",
        "\u00c2\u00bf": "\u00bf", "\u00c2\u00a1": "\u00a1", "\u00c2\u00b7": "\u00b7", "\u00c2": "",
        "\u00e2\u20ac\u0153": '"', "\u00e2\u20ac\u009d": '"',
        "\u00e2\u20ac\u02dc": "'", "\u00e2\u20ac\u2122": "'",
        "\u00e2\u20ac\u201c": "-", "\u00e2\u20ac\u201d": "-", "\u00e2\u20ac\u00a6": "...",
        "\u00f0\u0178\u017d\u00ae": "\U0001f3ae",
        "\u00f0\u0178\u2018\u2021": "\U0001f447",
        "\u00f0\u0178\u201c\u00a1": "\U0001f4e1",
        "PUBLICACI\u00c3\u0093N": "PUBLICACI\u00d3N",
        "TECNOLOG\u00c3\u008dA": "TECNOLOG\u00cdA",
        "TECNOLOG\u00c3\u00adA": "TECNOLOG\u00cdA",
        "Preg\u00c3\u00bantame": "Preg\u00fantame",
    }
    for malo, bueno in reemplazos.items():
        texto = texto.replace(malo, bueno)

    arreglos_perdidos = {
        "PUBLICACI?N": "PUBLICACI\u00d3N",
        "TECNOLOG?A": "TECNOLOG\u00cdA",
        "tecnolog?a": "tecnolog\u00eda",
        "informaci?n": "informaci\u00f3n",
        "publicaci?n": "publicaci\u00f3n",
        "conversaci?n": "conversaci\u00f3n",
        "adaptaci?n": "adaptaci\u00f3n",
        "serializaci?n": "serializaci\u00f3n",
        "qu?": "qu\u00e9",
        "c?mo": "c\u00f3mo",
        "est?n": "est\u00e1n",
        "est?": "est\u00e1",
        "m?s": "m\u00e1s",
        "f?sicos": "f\u00edsicos",
        "f?sico": "f\u00edsico",
        "cl?sicos": "cl\u00e1sicos",
        "cl?sico": "cl\u00e1sico",
        "Pok?mon": "Pok\u00e9mon",
        "pok?mon": "pok\u00e9mon",
        "se?ales": "se\u00f1ales",
        "se?al": "se\u00f1al",
        "todav?a": "todav\u00eda",
        "Todav?a": "Todav\u00eda",
        "t?tulo": "t\u00edtulo",
        "Sin t?tulo": "Sin t\u00edtulo",
        "nost?lgico": "nost\u00e1lgico",
        "nost?lgica": "nost\u00e1lgica",
        "opini?n": "opini\u00f3n",
        "discusi?n": "discusi\u00f3n",
        "atenci?n": "atenci\u00f3n",
        "com?n": "com\u00fan",
        "t?cnica": "t\u00e9cnica",
        "fr?a": "fr\u00eda",
    }
    for malo, bueno in arreglos_perdidos.items():
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
    texto_lower = str(pregunta or "").lower()
    for malo, bueno in [
        ("?", "a"), ("?", "e"), ("?", "i"), ("?", "o"), ("?", "u"),
        ("Ãƒ?", "a"), ("ÃƒÂ©", "e"), ("ÃƒÂ­", "i"), ("ÃƒÂ³", "o"), ("ÃƒÂº", "u"),
    ]:
        texto_lower = texto_lower.replace(malo, bueno)
    frases = [
        "dame un", "dame una", "dame uno", "hazme uno", "hazme una",
        "dame un post", "dame una publicacion",
        "dame post", "dame un caption", "dame una noticia para post",
        "creame un post", "crea un post", "crear un post",
        "hazme un post", "haz un post", "post para instagram", "post para facebook",
        "caption para tiktok", "caption para reel", "publicacion",
        "instagram", "facebook", "hazme", "creame", "crea", "crear",
        "hacer", "hace", "haz", "dame", "post", "caption",
    ]
    for frase in sorted(frases, key=len, reverse=True):
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
        "para la marca", "para marca", "para mi marca", "para mi pagina",
        "otra noticia", "otra", "noticia", "noticias", "actual", "reciente",
        "para", "la marca", "marca",
    ]
    for item in ruido:
        texto_lower = texto_lower.replace(item, " ")

    limpio = " ".join(texto_lower.split()).strip(" .,:;-")
    vacios = {
        "", "un", "una", "uno", "unos", "unas", "nuevo", "nueva",
        "redes", "publicar", "hot", "viral", "del dia", "del d\u00eda",
        "tema", "algo", "para mi",
    }
    return "" if limpio in vacios else limpio


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
        texto += " La idea es explicarlo claro y convertirlo en un post ?til para redes."

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


def detalle_contextual_para_post(titulo, texto_base, estilo):
    """Segundo parrafo especifico y seguro: no mezcla juegos ni usa notas internas."""
    titulo_limpio = limpiar_texto_publicable_final(titulo)
    base = limpiar_texto_publicable_final(texto_base)
    texto = f"{titulo_limpio} {base}".lower()
    categoria = _estilo_a_categoria(estilo)
    if categoria == "gaming":
        categoria = _categoria_ganadora(_puntuar_categorias({"title": titulo_limpio, "summary": base}))

    frases = re.split(r"(<=[.!])\s+", base)
    for frase in frases[1:]:
        frase = limpiar_texto_publicable_final(frase)
        if (
            len(frase) >= 45
            and not parece_texto_ingles(frase)
            and not linea_no_publicable(frase)
            and frase.lower() not in titulo_limpio.lower()
        ):
            return recortar_texto(frase, 220)

    if categoria == "tecnologia":
        return "El punto es explicarlo desde lo que cambia para quien juega: rendimiento, precio, acceso, comodidad o valor real."
    if categoria == "indie":
        return "Funciona mejor como descubrimiento: qué lo hace diferente, por qué vale mirarlo y qué detalle puede enganchar a la comunidad."
    if categoria == "anime":
        return "Aquí manda el fandom: qué se mostró, por qué genera curiosidad y si hay hype real o dudas razonables."
    if categoria == "debate":
        return "La conversación funciona mejor cuando presenta dos lados claros y deja espacio para que la comunidad opine."
    if categoria == "nostalgia":
        return "La nostalgia se siente más real cuando conecta con una escena concreta: consola, control, cartucho, disco o gente con quien jugaste."
    if any(p in texto for p in ["precio", "subscription", "suscripcion", "suscripción"]):
        return "Para muchos gamers, la pregunta real es si esto vale el dinero y el tiempo."
    return "La conversación funciona mejor cuando el dato principal queda claro sin exagerar ni inventar detalles."





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


def pregunta_engagement(titulo, estilo):
    texto = limpiar_texto_publicable_final(titulo).lower()
    if estilo == "debate":
        return "\U0001f447 \u00bfT\u00fa c\u00f3mo lo ves: buena movida o mala decisi\u00f3n?"
    if estilo == "tecnologia":
        return "\U0001f447 \u00bfEsto te parece \u00fatil para gamers o puro ruido t\u00e9cnico?"
    if estilo == "indie":
        return "\U0001f447 \u00bfLo pondr\u00edas en tu radar o esperas m\u00e1s gameplay primero?"
    if estilo == "anime":
        return "\U0001f447 \u00bfEste tema te da hype o prefieres esperar m\u00e1s informaci\u00f3n?"
    if "precio" in texto or "suscripci\u00f3n" in texto or "game pass" in texto or "ps plus" in texto:
        return "\U0001f447 \u00bfLo pagar\u00edas o esperar\u00edas una mejor oferta?"
    if "remake" in texto or "remaster" in texto:
        return "\U0001f447 \u00bfTe emociona este regreso o prefieres juegos nuevos?"
    if "digital" in texto or "f\u00edsico" in texto or "fisico" in texto:
        return "\U0001f447 \u00bfT\u00fa eres team f\u00edsico o team digital?"
    if "anime" in texto or "manga" in texto:
        return "\U0001f447 \u00bfEste tema te da hype o lo dejar\u00edas pasar?"
    if estilo in ["nostalgia", "emocional"]:
        return "\U0001f447 \u00bfQu\u00e9 recuerdo gamer te vino a la mente?"
    if any(p in texto for p in ["actualizaci\u00f3n", "update", "parche", "temporada"]):
        return "\U0001f447 \u00bfEsto te anima a volver o lo dejar\u00edas pasar?"
    if any(p in texto for p in ["lanzamiento", "estreno", "preventa"]):
        return "\U0001f447 \u00bfLo pondr\u00edas en tu lista o esperar\u00edas m\u00e1s detalles?"
    return "\U0001f447 \u00bfEsto te interesa o lo dejar\u00edas pasar?"


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


def etiqueta_publicacion_limpia(categoria):
    etiquetas = {
        "gaming": "Gaming/Noticia",
        "indie": "Indie/En movimiento",
        "tecnologia": "Tecnología",
        "technology": "Tecnología",
        "hardware": "Tecnología",
        "nostalgia": "Nostalgia",
        "anime": "Anime",
        "debate": "Debate",
        "emocional": "Nostalgia/Comunidad",
        "noticia": "Gaming/Noticia",
        "news": "Gaming/Noticia",
    }
    return etiquetas.get(str(categoria or "").lower(), "Gaming/Noticia")


def limpiar_gramatica_post_final(texto):
    texto = reparar_texto_roto(str(texto or ""))
    reemplazos = {
        "TECNOLOG\u00edA": "TECNOLOG\u00cdA",
        "PUBLICACI\u00f3N": "PUBLICACI\u00d3N",
        "?los": "\u00bfLos", "?el": "\u00bfEl", "?la": "\u00bfLa",
        "?esto": "\u00bfEsto", "?este": "\u00bfEste", "?qu?": "\u00bfQu\u00e9",
        "?cu?l": "\u00bfCu\u00e1l", "?t?": "\u00bfT\u00fa", "?para": "\u00bfPara",
        "?sobre": "\u00bfSobre", "??": "\U0001f3ae",
    }
    for malo, bueno in reemplazos.items():
        texto = texto.replace(malo, bueno)

    texto = re.sub(r"\b([A-Z\u00c1\u00c9\u00cd\u00d3\u00da\u00d1 ]+)\u00edA\b", lambda m: m.group(0).replace("\u00edA", "\u00cdA"), texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    texto = re.sub(r"[ \t]{2,}", " ", texto)

    lineas = []
    for linea in texto.splitlines():
        limpia = linea.rstrip()
        if limpia.startswith("\u00bf") and not limpia.endswith("?"):
            limpia += "?"
        lineas.append(limpia)
    return "\n".join(lineas).strip()


def crear_post_limpio(titulo, resumen, estilo, nostalgia, hashtags):
    """Generador final de caption: especifico, en espanol y listo para copiar."""
    estilo = estilo or "news"
    titulo_original = limpiar_texto_publicable_final(titulo)
    titulo_es = titulo_publico_en_espanol(titulo_original, estilo)
    titulos_genericos = {
        "Novedad gamer para comentar",
        "Anime nuevo para comentar",
        "Juego para poner en el radar",
        "Tecnología gamer para mirar con calma",
    }
    if titulo_es in titulos_genericos and resumen:
        titulo_contextual = titulo_publico_en_espanol(f"{titulo_original} {resumen}", estilo)
        if titulo_contextual not in titulos_genericos:
            titulo_es = titulo_contextual
    texto_base = resumen_publico_en_espanol(titulo_original, resumen, estilo)
    texto_base = limpiar_primer_parrafo_repetido(texto_base, titulo_es)
    detalle = detalle_contextual_para_post(titulo_es, texto_base, estilo)
    pregunta = pregunta_engagement(titulo_es, estilo)
    brand = get_brand_voice().get("brand", "")

    if not texto_base or len(texto_base) < 35:
        texto_base = (
            "Este tema puede abrir una conversación útil, pero debe manejarse con cuidado para no venderlo como noticia confirmada. "
            "Lo mejor es enfocarlo como opinión o pregunta para la comunidad."
        )

    if estilo == "debate" and any(p in f"{titulo_es} {texto_base}".lower() for p in ["físico", "fisico", "digital"]):
        cuerpo = (
            "Por un lado está la comodidad de lo moderno: descargas rápidas, juegos siempre disponibles "
            "y menos espacio ocupado.\n\n"
            "Pero también está esa parte que muchos extrañan: tener el juego en la mano, prestarlo, "
            "ver la portada, leer el manual y sentir que de verdad era tuyo."
        )
        if detalle:
            cuerpo += f"\n\n{detalle}"
    elif estilo in ["nostalgia", "emocional"]:
        cuerpo = (
            f"{texto_base}\n\n"
            "La nostalgia pega más fuerte cuando no se siente forzada: una consola, un control, un cartucho, "
            "un disco o esa tarde jugando con panas puede decir más que cualquier dato técnico."
        )
        if detalle and detalle.lower() not in cuerpo.lower():
            cuerpo += f"\n\n{detalle}"
    else:
        cuerpo = texto_base
        if detalle and detalle.lower() not in cuerpo.lower():
            cuerpo += f"\n\n{detalle}"

    if nostalgia and estilo not in ["noticia", "news"] and nostalgia.lower() not in cuerpo.lower():
        cuerpo += f"\n\nTambién conecta con {nostalgia}"

    if brand == "Daviet Gaming":
        if estilo in ["tecnologia", "hardware", "technology"]:
            subtitulo = "Tecnología explicada sin complicarla"
        elif estilo == "anime":
            subtitulo = "Anime y cultura geek para comentar"
        elif estilo == "debate":
            subtitulo = "Un tema para prender conversación"
        elif estilo == "indie":
            subtitulo = "Un juego para tener en el radar"
        else:
            subtitulo = "Una noticia para mirar con calma"
        salida = f"🎮 {titulo_es}\n\n{subtitulo}\n\n{cuerpo}\n\n{pregunta}\n\n{hashtags}"
    else:
        salida = f"🎮 {titulo_es}\n\n{cuerpo}\n\n{pregunta}\n\n{hashtags}"

    return limpiar_gramatica_post_final(salida)


def generate_social_post(item, estilo=None):
    item = dict(item or {})
    titulo = limpiar_html(item.get("title", "Tema gamer"))
    resumen = limpiar_html(item.get("summary", ""))
    angulo = detectar_content_angle(item)
    item["content_angle"] = angulo
    item["nostalgia_angle"] = detectar_angulo_nostalgia(item)
    if item.get("id"):
        st.session_state.generated_items[item["id"]] = dict(item)
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
    limpio = reparar_texto_roto(str(texto or ""))
    limpio = re.sub(r"https?://\S+", "", limpio)
    limpio = re.sub(r"\bThe post\b.*?\bappeared first on\b.*?(?:\.|\n|$)", "", limpio, flags=re.IGNORECASE | re.DOTALL)
    limpio = re.sub(r"\bappeared first on\b.*?(?:\.|\n|$)", "", limpio, flags=re.IGNORECASE | re.DOTALL)
    limpio = re.sub(r"\n{3,}", "\n\n", limpio)
    limpio = re.sub(r"[ \t]{2,}", " ", limpio)
    return reparar_texto_roto(limpio).strip()

def parece_texto_ingles(texto):
    texto_bajo = f" {limpiar_texto_publicable_final(limpiar_html(texto)).lower()} "
    if not texto_bajo.strip():
        return False
    frases_ingles = [
        "release date", "hands-on", "available today", "coming soon", "coming to",
        "is about", "appeared first", "the post", "official podcast",
        "new trailer", "teaser trailer", "anime adaptation", "getting an anime",
        "could come sooner", "could inherit", "by default", "physical gaming crown",
        "monthly games", "free play days", "public betas", "apple platforms",
        "deep dive", "first-ever", "mass layoffs", "foreign-worker visas",
        "plot hole", "weekly shonen jump", "patron vote", "joins the",
        "turns tough", "powerful friends", "drown you in", "unveils new visual",
    ]
    if any(frase in texto_bajo for frase in frases_ingles):
        return True

    palabras = [
        "the", "and", "with", "for", "from", "this", "that", "players",
        "player", "update", "patch", "available", "coming", "launches",
        "launch", "release", "date", "report", "details", "official",
        "episode", "expect", "caused", "today", "november", "july",
        "acclaimed", "fantasy", "getting", "adaptation", "announced",
        "announces", "revealed", "reveals", "alongside", "teaser",
        "trailer", "could", "inherit", "physical", "digital", "crown",
        "default", "monthly", "games", "free", "days", "refutes", "notion",
        "foreign", "worker", "workers", "visas", "behind", "mass", "layoffs",
        "breaking", "concludes", "serialization", "hands-on", "president",
        "weighs", "recommendation", "recommended", "drops", "increases",
        "ends", "after", "weekly", "shonen", "jump", "feature", "fired",
        "platforms", "builds", "transformative", "style", "joins", "turns",
        "tough", "bosses", "friends", "will", "drown", "mythics", "news",
        "sooner", "think", "unveils", "visual", "vote", "following",
    ]
    tokens = re.findall(r"[a-z][a-z'-]+", texto_bajo)
    hits = sum(1 for token in tokens if token in palabras)
    if "'s" in texto_bajo and hits >= 1:
        return True
    return hits >= 3


def extraer_tema_para_titulo(titulo):
    limpio = limpiar_texto_publicable_final(limpiar_html(titulo))
    if not limpio:
        return "tema gamer"

    limpio = re.sub(r"^(?:the post|post|news|noticia)\s+", "", limpio, flags=re.IGNORECASE).strip()
    limpio = re.sub(
        r"^(?:pre[- ]?order|preventa|review|preview|hands[- ]on|trailer|teaser|update|patch)\s*[:\-]\s*",
        "",
        limpio,
        flags=re.IGNORECASE,
    ).strip()

    for patron in [
        r"(?:manga|anime)\s+'([^']+)'",
        r"(?:manga|anime)\s+\"([^\"]+)\"",
        r"'([^']{3,80})'",
        r"\"([^\"]{3,80})\"",
    ]:
        match = re.search(patron, limpio, flags=re.IGNORECASE)
        if match:
            return normalizar_titulo_gamer(match.group(1).strip())

    bajo = limpio.lower()
    acciones = [
        " is getting ", " gets ", " will get ", " getting ", " receives ",
        " announced ", " announces ", " revealed ", " reveals ", " unveils ",
        " launches ", " launch ", " drops ", " joins ", " turns ", " becomes ",
        " concludes ", " ends ", " ending ", " refutes ", " responds ", " details ",
        " update ", " version ", " coming ", " release date ",
    ]
    for separador in acciones:
        if separador in bajo:
            posible = limpio[:bajo.find(separador)].strip(" -:.,")
            if 3 <= len(posible) <= 80:
                return normalizar_titulo_gamer(posible)

    for separador in [" - ", " ? ", " ? ", ":"]:
        if separador in limpio:
            posible = limpio.split(separador, 1)[0].strip(" -:.,")
            if 3 <= len(posible) <= 80 and not re.fullmatch(r"(?i)(pre[- ]?order|review|preview|update|trailer|teaser)", posible):
                return normalizar_titulo_gamer(posible)

    return normalizar_titulo_gamer(limpio[:80].strip(" -:.,") or "tema gamer")

def titulo_publico_en_espanol(titulo, estilo):
    original = limpiar_texto_publicable_final(limpiar_html(titulo))
    if not original:
        return "Tema gamer para comentar"

    tema = normalizar_titulo_gamer(extraer_tema_para_titulo(original))
    bajo = original.lower()
    categoria_detectada = _categoria_ganadora(_puntuar_categorias({"title": original, "summary": ""}))
    tema_generico = {
        "anime": "Anime nuevo",
        "tecnologia": "Tecnología gamer",
        "indie": "Juego independiente",
        "debate": "Tema de industria",
        "nostalgia": "Clásico gamer",
        "gaming": "Novedad gamer",
    }
    tema_publico = tema
    if parece_texto_ingles(tema_publico) and re.search(
        r"\b(will|could|from|joins|turns|with|after|before|following|into|new|update|news|classic|classics|announces|reveals|unveils|available|today|report|details|version|refutes|notion|getting|release|date)\b",
        tema_publico.lower(),
    ):
        tema_publico = tema_generico.get(categoria_detectada, "Novedad gamer")

    if not parece_texto_ingles(original):
        limpio = normalizar_titulo_gamer(original)
        if estilo in ["nostalgia", "emocional"] and re.search(r"\b20\d{2}\b", limpio):
            limpio = re.sub(r"\b(?:de\s+)?20\d{2}\b", "", limpio, flags=re.IGNORECASE)
            limpio = re.sub(r"\s{2,}", " ", limpio).strip(" -:")
            return f"{limpio}: recuerdos que todav\u00eda conectan"
        return limpio

    for patron, plantilla in ACCION_PATRONES_TITULO:
        if re.search(patron, bajo, flags=re.IGNORECASE):
            return plantilla.format(tema=tema_publico)

    if parece_texto_ingles(tema_publico):
        if categoria_detectada == "anime":
            return "Anime nuevo para comentar"
        if categoria_detectada == "tecnologia":
            return "Tecnología gamer para mirar con calma"
        if categoria_detectada == "indie":
            return "Juego independiente para poner en el radar"
        if categoria_detectada == "debate":
            return "Tema de industria para debatir"
        if categoria_detectada == "nostalgia":
            return "Recuerdo gamer para comentar"
        return "Novedad gamer para comentar"

    categoria = _estilo_a_categoria(estilo)
    if categoria == "debate":
        return f"{tema_publico} abre debate gamer"
    if categoria == "nostalgia":
        return f"{tema_publico}: recuerdos gamer"
    if estilo == "corto":
        return f"{tema_publico}: tema r\u00e1pido para comentar"
    if categoria == "anime":
        return f"{tema_publico}: tema anime para comentar"
    if categoria == "tecnologia":
        return f"{tema_publico}: tecnología gamer para mirar con calma"
    if categoria == "indie":
        return f"{tema_publico}: juego para poner en el radar"
    return f"{tema_publico}: noticia para comentar"


def titulo_visible_seguro(item, estilo="news", bucket=None):
    """Titulo final para UI: nunca deja un headline entero en ingles."""
    item = item or {}
    original = item.get("title", "") if isinstance(item, dict) else str(item)
    titulo = titulo_publico_en_espanol(original, estilo)
    titulo = limpiar_texto_publicable_final(titulo)
    bajo = titulo.lower()
    marcas_espanol = [
        "vuelve", "conversaci\u00f3n", "termina", "serializaci\u00f3n", "responde",
        "despidos", "debate", "jugadores", "noticia", "tema", "adaptaci\u00f3n",
        "lanzamiento", "detalles", "comunidad", "recuerdos",
    ]
    palabras_ingles_visibles = [
        " could ", " inherit ", " crown", " by default", " hands-on", " available",
        " today", " announced", " revealed", " finally", " addresses", " release date",
        " coming", " getting", " trailer", " report", " details", " version",
    ]
    if any(p in bajo for p in marcas_espanol) and not any(p in f" {bajo} " for p in palabras_ingles_visibles):
        return titulo
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


def limpiar_para_ui(texto):
    """Texto seguro para mostrar en tarjetas: sin mojibake ni HTML raro."""
    return limpiar_texto_publicable_final(reparar_texto_roto(texto))


def estado_verificacion_item(item):
    item = item or {}
    nivel = str(item.get("verification_level", "")).lower()
    fuente = str(item.get("source", "")).lower()
    confianza = str(item.get("confidence_level", "")).lower()

    if any(p in nivel for p in ["fuente oficial", "verificada", "3 fuentes", "2 fuentes"]):
        return ("Verde", "verificada")
    if any(p in nivel for p in ["fuente confiable", "senal de comunidad", "se\u00f1al de comunidad", "no confirma noticia"]):
        return ("Amarillo", "usar como contexto/debate")
    if "oficial" in fuente and confianza not in ["low", "manual", "editorial"]:
        return ("Verde", "fuente oficial")
    if "confiable" in fuente or "trusted" in confianza or confianza in ["medium-high", "community_signal"]:
        return ("Amarillo", "fuente confiable o se\u00f1al editorial")

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
    bajo = f"{titulo} {resumen}".lower()
    categoria = _estilo_a_categoria(estilo)
    if categoria == "gaming":
        categoria = _categoria_ganadora(_puntuar_categorias({"title": titulo, "summary": resumen}))

    if resumen_limpio and not parece_texto_ingles(resumen_limpio):
        resumen_limpio = limpiar_primer_parrafo_repetido(resumen_limpio, tema)
        if not caption_necesita_regenerarse(resumen_limpio, {"title": titulo, "summary": resumen}, estilo):
            return recortar_texto(resumen_limpio, 260)

    traducido = traducir_basico_en_espanol(resumen_limpio)
    if traducido and not parece_texto_ingles(traducido):
        traducido = limpiar_primer_parrafo_repetido(traducido, tema)
        if not caption_necesita_regenerarse(traducido, {"title": titulo, "summary": resumen}, estilo):
            return recortar_texto(traducido, 260)

    if categoria == "debate":
        return (
            f"{tema} puede abrir una conversación real entre jugadores. "
            "Conviene presentar el dato confirmado, enseñar por qué divide opiniones y dejar que la comunidad tome postura."
        )
    if categoria == "nostalgia":
        return (
            f"{tema} conecta con recuerdos gamer, consolas viejas, juegos físicos "
            "y momentos que muchos todavía reconocen sin tener que tratarlo como noticia actual."
        )
    if categoria == "anime":
        return (
            f"{tema} se mueve dentro de la conversación anime/geek. "
            "Lo importante es explicar qué se confirmó, qué puede generar hype y qué duda queda para el fandom."
        )
    if categoria == "tecnologia":
        return (
            f"{tema} toca tecnología relacionada al gaming. "
            "El enfoque debe ser qué cambia para el jugador común: rendimiento, acceso, precio, comodidad o experiencia."
        )
    if categoria == "indie":
        return (
            f"{tema} puede funcionar como descubrimiento gamer. "
            "El punto es explicar qué lo hace diferente, qué se sabe por la fuente y por qué podría entrar en el radar."
        )
    if "layoff" in bajo or "despido" in bajo or "workers" in bajo:
        return (
            f"{tema} toca cambios en la industria. "
            "Más que convertirlo en pelea de marcas, vale mirar cómo puede afectar estudios, proyectos y jugadores."
        )
    return (
        f"{tema} vuelve al radar de la comunidad gamer. "
        "Vale mirarlo con calma para ver si realmente cambia algo para quienes juegan o siguen la industria."
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
    return limpiar_gramatica_post_final(salida)


def quitar_prefijos_editoriales(linea):
    """Convierte notas tipo 'Titulo:' o 'Post:' en caption limpio."""
    texto = str(linea or "").strip()
    patrones = [
        r"^(t[i\u00ed]tulo|titulo)\s*:\s*",
        r"^(subt[i\u00ed]tulo|subtitulo)\s*:\s*",
        r"^(post|caption|publicaci[o\u00f3]n)\s*:\s*",
        r"^(cierre|pregunta|cta)\s*:\s*",
        r"^(hashtags)\s*:\s*",
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
        "aparece como señal reciente",
        "aparece como senal reciente",
        "el feed no trae suficiente detalle",
        "conviene usarlo como punto de entrada",
        "la clave es explicar el dato concreto",
        "qué pregunta puede mover comentarios reales",
        "que pregunta puede mover comentarios reales",
        "lo importante es explicar",
        "abre conversación sin inventar datos",
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
        if re.search(r"https://|www\.", linea, flags=re.IGNORECASE):
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


def caption_necesita_regenerarse(texto, item=None, estilo="news"):
    """Detecta captions que suenan a plantilla o mezclan el tema con otra categoria."""
    item = item or {}
    texto_limpio = limpiar_texto_publicable_final(reparar_texto_roto(texto))
    bajo = texto_limpio.lower()
    titulo = limpiar_texto_publicable_final(limpiar_html(item.get("title", ""))).lower()
    resumen = limpiar_texto_publicable_final(limpiar_html(item.get("summary", ""))).lower()
    fuente = limpiar_texto_publicable_final(limpiar_html(item.get("source", ""))).lower()
    contexto = f"{titulo} {resumen} {fuente}"

    frases_de_plantilla = [
        "es un tema reciente dentro del mundo gamer",
        "lo importante es explicar que paso",
        "lo importante es explicar qué pasó",
        "que conversaci\u00f3n puede abrir",
        "qué conversación puede abrir",
        "lo interesante es mirar por que esto importa",
        "lo interesante es mirar por qué esto importa",
        "este tipo de tema conecta con la comunidad porque cada gamer",
        "puede servir para descubrir algo fuera de los lanzamientos gigantes",
        "aparece como señal reciente",
        "aparece como senal reciente",
        "el feed no trae suficiente detalle",
        "conviene usarlo como punto de entrada",
        "la clave es explicar el dato concreto",
        "qué pregunta puede mover comentarios reales",
        "que pregunta puede mover comentarios reales",
        "tema reciente dentro del mundo gamer",
        "noticia para comentar es un tema",
    ]
    if sum(1 for frase in frases_de_plantilla if frase in bajo) >= 2:
        return True

    categoria_real = _categoria_ganadora(_puntuar_categorias(item))
    if categoria_real != "indie" and any(p in bajo for p in ["indies", "juegos independientes", "demos"]):
        return True
    if categoria_real not in ["nostalgia", "debate"] and any(p in bajo for p in ["juegos fisicos", "juegos físicos", "caja", "manual", "prestarlo"]):
        return True
    if categoria_real != "tecnologia" and any(p in bajo for p in ["ruido tecnico", "ruido técnico", "cambio util", "cambio útil"]):
        return True
    if ("anime" in contexto or "manga" in contexto) and "dudas de adaptacion" in bajo and "adapt" not in contexto:
        return True
    if estilo in ["indie"] and categoria_real != "indie":
        return True
    return False


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

    if caption_tiene_ingles_visible(texto) or caption_necesita_regenerarse(texto, item, estilo):
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
    texto = limpiar_gramatica_post_final(reparar_texto_roto(texto))
    texto = re.sub(r"\n{3,}", "\n\n", texto).strip()
    return texto


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


def formatear_noticias(noticias, texto_usuario="", cantidad=5):
    cantidad = max(1, min(cantidad, 8))
    exclusiones = detectar_exclusiones_usuario(texto_usuario)
    noticias = seleccionar_noticias_variadas(noticias, cantidad, texto_usuario)
    if not noticias:
        extra = "\n\nTambien aplique tu filtro de exclusion, por eso quite esos temas de la lista." if exclusiones else ""
        return (
            f"No encontre noticias que pasen la verificacion automatica del ano {ANIO_NOTICIAS}.\n\n"
            "Estoy filtrando solo fuentes oficiales o noticias confirmadas por varias fuentes."
            f"{extra}"
        )

    respuesta = f"Busque y filtre noticias verificadas del ano {ANIO_NOTICIAS}.\n\n"
    if exclusiones:
        respuesta += "Tambien quite de la lista lo que pediste evitar.\n\n"
    respuesta += f"Rango usado: {FECHA_INICIO} hasta {FECHA_FINAL}\n\n"
    st.session_state.news_by_number = {}

    for numero, item in enumerate(noticias[:cantidad], start=1):
        item = dict(item)
        st.session_state.generated_items[item["id"]] = item
        st.session_state.last_item_id = item["id"]
        st.session_state.news_by_number[numero] = item

        titulo_visible = titulo_visible_seguro(item, "news")
        estado, detalle = estado_verificacion_item(item)
        resumen = resumen_publico_en_espanol(item.get("title", ""), item.get("summary", ""), "news")

        respuesta += f"### Noticia {numero}: {titulo_visible}\n\n"
        respuesta += f"**Fecha:** {item.get('date', '')}\n\n"
        respuesta += f"**Fuente:** {item.get('source', 'fuente')}\n\n"
        respuesta += f"**Estado:** {estado} - {detalle}\n\n"
        respuesta += f"{resumen}\n\n"
        if item.get("nostalgia_angle"):
            respuesta += f"**Conexion nostalgica:** {reparar_texto_roto(item['nostalgia_angle'])}\n\n"
        respuesta += f"Para usarla: **post de la noticia {numero}**\n\n---\n\n"
    return respuesta


def crear_opciones_post_recientes():
    noticias = filtrar_noticias_verificadas(buscar_noticias())
    titulos_usados = set()
    st.session_state.news_by_number = {}
    respuesta = f"### Opciones de post para {ANIO_NOTICIAS}\n\n"
    respuesta += (
        "Te dejo ideas ya filtradas autom\u00e1ticamente. Las noticias pasan por verificaci\u00f3n; "
        "debate y nostalgia se manejan como contenido editorial, no como noticia confirmada.\n\n"
    )

    for numero, categoria in enumerate(["gaming", "tecnologia", "nostalgia", "anime", "debate"], start=1):
        item = seleccionar_noticia_para_categoria(noticias, categoria, titulos_usados)
        if not item:
            item = crear_item_editorial_categoria(categoria, titulos_usados)
        item = dict(item)

        st.session_state.generated_items[item["id"]] = item
        st.session_state.news_by_number[numero] = item
        st.session_state.last_item_id = item["id"]

        titulo = titulo_publico_en_espanol(item.get("title", "Noticia gamer"), "news")
        fuente = item.get("source", "Fuente no disponible")
        fecha = item.get("date", "")
        angulo = item.get("content_angle", "noticia")
        nostalgia = item.get("nostalgia_angle", "")

        if angulo == "nostalgia" or nostalgia:
            idea = "post nost\u00e1lgico con conexi\u00f3n a recuerdos gamer"
        elif angulo == "debate":
            idea = "post de debate para generar comentarios"
        elif angulo == "anime":
            idea = "post de anime conectado con cultura gamer y comunidad"
        elif angulo in ["hardware", "technology"]:
            idea = "post de tecnolog\u00eda explicado para gamers"
        else:
            idea = "post informativo con pregunta para la comunidad"

        respuesta += f"**{numero}. {titulo}**\n\n"
        respuesta += f"- **Fuente:** {fuente}\n"
        respuesta += f"- **Fecha:** {fecha}\n"
        respuesta += f"- **Verificaci?n:** {item.get('verification_level', 'idea editorial / no es noticia confirmada')}\n"
        if item.get("verification_sources"):
            respuesta += f"- **Fuentes revisadas:** {', '.join(item['verification_sources'])}\n"
        respuesta += f"- **Idea:** {idea}\n"
        respuesta += f"- **\u00e1ngulo:** {angulo}\n"
        if nostalgia:
            respuesta += f"- **Conexi?n nost\u00e1lgica:** {reparar_texto_roto(nostalgia)}\n"
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
        "\u00bfPara cu?l marca lo hago\n\n"
        "Puedes responder: **Gamer Cave** o **Daviet Gaming**."
    )


def crear_lista_comandos():
    return """### Comandos ?tiles

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


def reparar_texto_roto(texto):
    if texto is None:
        return ""
    texto = str(texto)
    for _ in range(3):
        if not any(marca in texto for marca in ["Ã", "Â", "â", "ð"]):
            break
        try:
            reparado = texto.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if reparado == texto:
            break
        texto = reparado
    for malo, bueno in MOJIBAKE_FIXES_FINAL.items():
        texto = texto.replace(malo, bueno)
    texto = texto.replace("\ufffd", "")
    return texto


def limpiar_texto_publicable_final(texto):
    limpio = reparar_texto_roto(limpiar_html(texto) if "<" in str(texto or "") else str(texto or ""))
    limpio = re.sub(r"https?://\S+", "", limpio)
    limpio = re.sub(r"\bThe post\b.*?\bappeared first on\b.*?(?:\.|\n|$)", "", limpio, flags=re.IGNORECASE | re.DOTALL)
    limpio = re.sub(r"\bappeared first on\b.*?(?:\.|\n|$)", "", limpio, flags=re.IGNORECASE | re.DOTALL)
    limpio = re.sub(r"\s+([.,;:!?])", r"\1", limpio)
    limpio = re.sub(r"[ \t]{2,}", " ", limpio)
    limpio = re.sub(r"\n{3,}", "\n\n", limpio)
    return reparar_texto_roto(limpio).strip()


def _texto_item_final(item):
    item = item or {}
    return limpiar_texto_publicable_final(
        f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}"
    ).lower()


def _categoria_final_item(item, preferida=None):
    texto = _texto_item_final(item)
    fuente = str((item or {}).get("source", "")).lower()
    if any(p in fuente for p in ["anime", "myanimelist", "crunchyroll"]) or any(
        p in texto for p in ["anime", "manga", "shonen", "otaku", "serialization", "serializacion", "serializaci\u00f3n"]
    ):
        return "anime"
    if any(p in texto for p in ["gpu", "rtx", "nvidia", "amd", "intel", "hardware", "ios", "macos", "apple", "steam deck", "cloud gaming", "ray tracing", "unreal engine", "godot"]):
        return "tecnologia"
    if any(p in texto for p in ["indie", "independent", "independiente", "steam next fest", "next fest", "small team", "solo developer"]):
        return "indie"
    if any(p in texto for p in ["layoff", "layoffs", "despidos", "workers", "price", "precio", "delay", "retraso", "cancel", "microtransaction", "subscription", "suscripci", "physical", "digital", "f\u00edsico", "fisico", "exclusiva", "review bombing"]):
        return "debate"
    if any(p in texto for p in ["preservation", "preservaci", "classic", "cl\u00e1sico", "clasico", "retro", "remake", "remaster", "anniversary", "aniversario", "gamecube", "game boy", "ps1", "ps2", "xbox 360", "cartucho", "manual"]):
        return "nostalgia"
    if preferida in ["gaming", "tecnologia", "anime", "indie", "debate", "nostalgia"]:
        return preferida
    return "gaming"


def categoria_de_item(item):
    return _categoria_final_item(item)


def detectar_content_angle(item):
    categoria = _categoria_final_item(item)
    if categoria == "tecnologia":
        return "technology"
    if categoria == "gaming":
        return "news"
    return categoria


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


def titulo_publico_en_espanol(titulo, estilo="news"):
    original = limpiar_texto_publicable_final(titulo)
    if not original:
        return "Tema gamer para comentar"
    bajo = original.lower()
    tema = _tema_principal_final(original)

    reglas = [
        (r"diablo\s*(4|iv).*drown.*mythics", "Diablo 4 recibe una actualizaci\u00f3n cargada de Mythics"),
        (r"kingdom hearts\s*4.*news.*sooner", "Kingdom Hearts 4 podr\u00eda tener novedades pronto"),
        (r"castlevania.*bosses.*friends", "Castlevania convierte jefes dif\u00edciles en aliados poderosos"),
        (r"thief:\s*gold.*gog.*preservation", "Thief: Gold entra al programa de preservaci\u00f3n de GOG"),
        (r"blue box.*manga.*ends|ao no hako.*concludes", "Blue Box termina su serializaci\u00f3n"),
        (r"tetsuryo.*visual.*trailer", "Tetsuryo Meet With Tetsudou Musume muestra nuevo visual y tr\u00e1iler"),
        (r"pre[- ]?order.*sinking city 2", "The Sinking City 2 abre su preventa"),
        (r"public betas.*ios.*macos", "Apple lanza betas p\u00fablicas de iOS y macOS"),
        (r"space dragons.*retro", "Space Dragons mezcla gameplay moderno con estilo retro"),
        (r"6 classics.*sneg|six classics.*sneg", "Seis cl\u00e1sicos de SNEG quedan bajo la lupa"),
        (r"microsoft.*refutes.*xbox.*layoffs", "Microsoft responde a dudas sobre despidos en Xbox"),
        (r"anime adaptation|getting an anime", f"{tema} tendr\u00e1 adaptaci\u00f3n al anime"),
        (r"unveils.*visual|new visual|trailer|teaser", f"{tema} muestra nuevo material"),
        (r"release date|launches|coming soon|coming in", f"{tema} pone su lanzamiento en el radar"),
        (r"update|patch|version|details", f"{tema} trae nuevos detalles para jugadores"),
        (r"preservation|classic|collection|remaster|remake", f"{tema} conecta con preservaci\u00f3n y nostalgia"),
        (r"layoffs|workers|fired|visas", f"{tema} abre conversaci\u00f3n sobre la industria"),
        (r"physical|digital", "Juegos f\u00edsicos vs digitales vuelve al debate"),
    ]
    for patron, salida in reglas:
        if re.search(patron, bajo, flags=re.IGNORECASE):
            return limpiar_texto_publicable_final(salida)

    if parece_texto_ingles(original):
        categoria = _categoria_final_item({"title": original, "summary": ""}, _estilo_a_categoria(estilo))
        if categoria == "anime":
            return f"{tema}: tema anime para comentar" if not parece_texto_ingles(tema) else "Anime nuevo para comentar"
        if categoria == "tecnologia":
            return f"{tema}: tecnolog\u00eda gamer bajo la lupa" if not parece_texto_ingles(tema) else "Tecnolog\u00eda gamer bajo la lupa"
        if categoria == "indie":
            return f"{tema}: indie para poner en el radar" if not parece_texto_ingles(tema) else "Juego indie para poner en el radar"
        if categoria == "nostalgia":
            return f"{tema}: nostalgia gamer para comentar" if not parece_texto_ingles(tema) else "Nostalgia gamer para comentar"
        if categoria == "debate":
            return f"{tema}: tema para debatir" if not parece_texto_ingles(tema) else "Tema gamer para debatir"
        return f"{tema}: noticia gamer para comentar" if not parece_texto_ingles(tema) else "Noticia gamer para comentar"

    return normalizar_titulo_gamer(original)


def titulo_visible_seguro(item, estilo="news", bucket=None):
    return titulo_publico_en_espanol((item or {}).get("title", ""), bucket or estilo)


def parece_texto_ingles(texto):
    texto_bajo = f" {limpiar_texto_publicable_final(texto).lower()} "
    if not texto_bajo.strip():
        return False
    frases = [
        "release date", "available today", "coming soon", "getting an anime",
        "anime adaptation", "new trailer", "teaser trailer", "public betas",
        "mass layoffs", "foreign-worker", "weekly shonen jump", "patron vote",
        "drown you in", "unveils new visual", "could come sooner",
    ]
    if any(frase in texto_bajo for frase in frases):
        return True
    tokens = re.findall(r"[a-z][a-z'-]+", texto_bajo)
    palabras = {
        "the", "and", "with", "for", "from", "this", "that", "players",
        "update", "patch", "available", "coming", "launch", "release",
        "date", "details", "announced", "revealed", "unveils", "trailer",
        "could", "will", "joins", "following", "physical", "digital",
        "workers", "layoffs", "ends", "after", "weekly", "today",
    }
    return sum(1 for token in tokens if token in palabras) >= 3


def limpiar_pedido_post(pregunta):
    texto = limpiar_texto_publicable_final(pregunta).lower()
    texto = quitar_marca_de_texto(texto)
    frases = [
        "hazme un post", "hazme una publicacion", "hazme una publicaci\u00f3n",
        "creame un post", "cr\u00e9ame un post", "crea un post", "crear un post",
        "dame un post", "dame una noticia", "post para instagram", "post para facebook",
        "caption", "publicacion", "publicaci\u00f3n", "instagram", "facebook",
        "hazme", "creame", "cr\u00e9ame", "crear", "crea", "dame", "post",
        "noticia", "noticias", "actual", "reciente", "hot", "viral",
    ]
    for frase in sorted(frases, key=len, reverse=True):
        texto = texto.replace(frase, " ")
    for sep in [" sobre ", " de "]:
        if sep in f" {texto} ":
            texto = texto.split(sep, 1)[-1]
    limpio = " ".join(texto.split()).strip(" .,:;-")
    if limpio in {"", "un", "una", "uno", "tema", "algo", "nuevo", "nueva"}:
        return ""
    return limpio


def crear_hashtags(texto, limite=None):
    limite = limite or obtener_limite_hashtags()
    texto = limpiar_texto_publicable_final(texto).lower()
    brand = get_brand_voice().get("brand", "El Gamer Cave")
    marca = "#davietgaming" if brand == "Daviet Gaming" else "#elgamercave"
    tags = [marca]
    reglas = [
        (["anime", "manga", "crunchyroll", "shonen"], ["#anime", "#manga", "#otaku"]),
        (["nintendo", "mario", "zelda", "kirby", "pokemon", "pok\u00e9mon"], ["#nintendo", "#nintendoswitch"]),
        (["playstation", "ps5", "ps plus"], ["#playstation", "#ps5"]),
        (["xbox", "game pass"], ["#xbox", "#xboxseriesx"]),
        (["pc", "steam", "gpu", "nvidia", "amd", "intel", "hardware"], ["#pcgaming", "#gamingtech"]),
        (["indie", "independent", "next fest"], ["#indiegames", "#indiegaming"]),
        (["retro", "nostalgia", "classic", "remake", "remaster", "gamecube", "game boy"], ["#nostalgia", "#retrogaming"]),
        (["diablo"], ["#diablo"]),
        (["kingdom hearts"], ["#kingdomhearts"]),
        (["call of duty"], ["#callofduty"]),
    ]
    for claves, nuevos in reglas:
        if any(clave in texto for clave in claves):
            tags.extend(nuevos)
    tags.extend(["#gaming", "#videojuegos", "#gamers", "#geekculture"])
    return limitar_hashtags_texto(" ".join(dict.fromkeys(tags)), limite)


def _resumen_fuente_util(resumen):
    resumen = limpiar_texto_publicable_final(resumen)
    if not resumen or len(resumen) < 40:
        return ""
    if parece_texto_ingles(resumen):
        return ""
    if linea_no_publicable(resumen) or caption_necesita_regenerarse(resumen):
        return ""
    return recortar_texto(resumen, 230)


def resumen_publico_en_espanol(titulo, resumen, estilo="news"):
    titulo_es = titulo_publico_en_espanol(titulo, estilo)
    tema = _tema_principal_final(titulo)
    fuente_util = _resumen_fuente_util(resumen)
    texto = f"{titulo} {resumen}".lower()
    categoria = _categoria_final_item({"title": titulo, "summary": resumen}, _estilo_a_categoria(estilo))

    if fuente_util:
        return fuente_util

    if "diablo" in texto and ("update" in texto or "actualizaci" in texto or "mythic" in texto):
        return "La noticia apunta a una actualizaci\u00f3n de Diablo 4 con recompensas o cambios pensados para mantener a los jugadores pendientes de la temporada."
    if "kingdom hearts" in texto:
        return "El tema mueve hype porque Kingdom Hearts 4 lleva tiempo generando preguntas y cada se\u00f1al nueva prende teor\u00edas entre los fans."
    if "castlevania" in texto:
        return "La novedad de Castlevania suena interesante porque toca algo bien gamer: cambiar la forma en que enfrentas jefes y convertirlos en parte de la aventura."
    if "thief" in texto and "gog" in texto:
        return "Que Thief: Gold entre a preservaci\u00f3n importa porque mantiene vivo un cl\u00e1sico de PC y ayuda a que nuevas generaciones lo puedan descubrir."
    if "blue box" in texto or "ao no hako" in texto:
        return "El cierre de Blue Box marca un momento importante para su fandom, especialmente para quienes siguieron la historia semana tras semana."
    if "tetsuryo" in texto:
        return "El nuevo material de Tetsuryo Meet With Tetsudou Musume ayuda a medir el hype: visuales, tono y fecha son parte de lo que el fandom va a comentar."
    if "sinking city 2" in texto:
        return "La preventa de The Sinking City 2 pone el juego otra vez en el radar para quienes siguen el horror, la investigaci\u00f3n y las propuestas m\u00e1s oscuras."
    if "apple" in texto or "ios" in texto or "macos" in texto:
        return "Las betas de Apple importan si afectan rendimiento, compatibilidad o herramientas que tambi\u00e9n usa la comunidad gamer y creadora."
    if "space dragons" in texto:
        return "Space Dragons llama la atenci\u00f3n porque mezcla una vibra retro con gameplay moderno, algo que puede conectar con fans de lo cl\u00e1sico y lo nuevo."
    if "sneg" in texto:
        return "Los cl\u00e1sicos de SNEG funcionan como excusa perfecta para hablar de preservaci\u00f3n, nostalgia y juegos que no deber\u00edan perderse."
    if "microsoft" in texto and ("layoff" in texto or "despido" in texto or "visa" in texto):
        return "La respuesta de Microsoft toca un tema sensible: despidos, industria y c\u00f3mo las compa\u00f1\u00edas explican decisiones que afectan a muchos trabajadores."

    if categoria == "anime":
        return f"{titulo_es} mueve conversaci\u00f3n entre fans de anime y cultura geek porque puede traer hype, dudas o teor\u00edas sobre lo que viene."
    if categoria == "tecnologia":
        return f"{titulo_es} vale mirarlo desde el lado gamer: qu\u00e9 cambia en rendimiento, acceso, precio o experiencia real para quienes juegan."
    if categoria == "indie":
        return f"{titulo_es} puede funcionar como descubrimiento para la comunidad si tiene una propuesta clara, una mec\u00e1nica distinta o una demo que enganche."
    if categoria == "debate":
        return f"{titulo_es} abre una conversaci\u00f3n donde hay m\u00e1s de un lado para mirar, sin convertirlo en pelea de plataformas."
    if categoria == "nostalgia":
        return f"{titulo_es} conecta con esa parte de la comunidad que todav\u00eda valora cl\u00e1sicos, recuerdos y experiencias de otras generaciones."
    return f"{titulo_es} llega como una novedad para mirar con calma y comentar qu\u00e9 puede significar para la comunidad gamer."


def detalle_contextual_para_post(titulo, texto_base, estilo="news"):
    texto = f"{titulo} {texto_base}".lower()
    categoria = _categoria_final_item({"title": titulo, "summary": texto_base}, _estilo_a_categoria(estilo))
    if "diablo" in texto:
        return "La pregunta real es si estos cambios dan razones para volver o si solo alimentan el grind de siempre."
    if "kingdom hearts" in texto:
        return "Con esta saga, cualquier detalle abre teor\u00edas: mundos, personajes, fecha y cu\u00e1nto Square Enix quiere ense\u00f1ar antes del lanzamiento."
    if "castlevania" in texto:
        return "Ese tipo de mec\u00e1nica puede ser buena conversaci\u00f3n porque cambia la relaci\u00f3n entre reto, estrategia y nostalgia."
    if "thief" in texto or "preservaci" in texto:
        return "La preservaci\u00f3n no es solo guardar juegos viejos; tambi\u00e9n es permitir que sigan disponibles, jugables y con contexto."
    if "blue box" in texto or "ao no hako" in texto:
        return "Cuando una serie termina, el debate casi siempre va por el cierre, el legado y si el anime puede llevar esa emoci\u00f3n a m\u00e1s gente."
    if categoria == "tecnologia":
        return "Lo mejor es bajarlo a tierra: si no mejora c\u00f3mo jugamos, creamos o usamos la tecnolog\u00eda, es solo ruido."
    if categoria == "indie":
        return "Los indies suelen crecer por recomendaci\u00f3n de comunidad, por eso conviene enfocarse en qu\u00e9 lo hace distinto."
    if categoria == "anime":
        return "Anime y gaming se cruzan mucho en nuestra comunidad cuando hay hype, adaptaciones o fandoms comparando expectativas."
    if categoria == "nostalgia":
        return "La nostalgia pega m\u00e1s fuerte cuando se siente concreta: una consola, un control, un cartucho, un disco o una tarde jugando con panas."
    if categoria == "debate":
        return "La conversaci\u00f3n funciona mejor cuando presenta dos lados claros y deja que la comunidad cuente su experiencia."
    return "La clave est\u00e1 en conectar el dato con una pregunta que la comunidad realmente quiera contestar."


def pregunta_engagement(titulo, estilo="news"):
    texto = limpiar_texto_publicable_final(titulo).lower()
    categoria = _categoria_final_item({"title": titulo, "summary": ""}, _estilo_a_categoria(estilo))
    if "diablo" in texto:
        return "\U0001f447 \u00bfEsto te anima a volver a Diablo 4 o ya lo dejaste pasar?"
    if "kingdom hearts" in texto:
        return "\U0001f447 \u00bfQu\u00e9 tendr\u00eda que ense\u00f1ar Kingdom Hearts 4 para subirte el hype?"
    if "castlevania" in texto:
        return "\U0001f447 \u00bfTe gusta cuando un juego convierte jefes en aliados o prefieres el reto cl\u00e1sico?"
    if "thief" in texto or "preservaci" in texto:
        return "\U0001f447 \u00bfQu\u00e9 cl\u00e1sico te gustar\u00eda ver mejor preservado?"
    if "blue box" in texto or "ao no hako" in texto:
        return "\U0001f447 \u00bfT\u00fa eres de leer el manga completo o esperar el anime?"
    if categoria == "tecnologia":
        return "\U0001f447 \u00bfEsto te parece \u00fatil para gamers o puro ruido t\u00e9cnico?"
    if categoria == "indie":
        return "\U0001f447 \u00bfLo pondr\u00edas en tu radar o esperas m\u00e1s gameplay primero?"
    if categoria == "anime":
        return "\U0001f447 \u00bfEste tema te da hype o prefieres esperar m\u00e1s informaci\u00f3n?"
    if categoria == "nostalgia":
        return "\U0001f447 \u00bfQu\u00e9 recuerdo gamer te vino a la mente?"
    if categoria == "debate":
        return "\U0001f447 \u00bfT\u00fa c\u00f3mo lo ves: buena movida o mala decisi\u00f3n?"
    return "\U0001f447 \u00bfEsto te interesa o lo dejar\u00edas pasar?"


def limpiar_gramatica_post_final(texto):
    texto = reparar_texto_roto(str(texto or ""))
    texto = texto.replace("Tecnolog\u00edA", "Tecnolog\u00eda").replace("TECNOLOG\u00edA", "TECNOLOG\u00cdA")
    texto = texto.replace("PUBLICACI\u00f3N", "PUBLICACI\u00d3N")
    texto = texto.replace("ano ", "a\u00f1o ").replace("del ano", "del a\u00f1o")
    texto = texto.replace("Busque y filtre", "Busqu\u00e9 y filtr\u00e9")
    texto = texto.replace("Conexion", "Conexi\u00f3n").replace("conexion", "conexi\u00f3n")
    texto = re.sub(r"[ \t]{2,}", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    lineas = []
    for linea in texto.splitlines():
        limpia = linea.rstrip()
        if limpia.startswith("?"):
            limpia = "\u00bf" + limpia[1:]
        if limpia.startswith("\u00bf") and not limpia.endswith("?"):
            limpia += "?"
        lineas.append(limpia)
    return "\n".join(lineas).strip()


def linea_no_publicable(linea):
    texto = limpiar_texto_publicable_final(linea).strip().lower()
    if not texto:
        return False
    prefijos = [
        "fuente:", "fuentes:", "link:", "fecha:", "confianza:", "id para feedback:",
        "referencia interna", "referencia usada", "sugerencia visual:", "prompt:",
        "acci\u00f3n:", "accion:", "verificaci\u00f3n:", "verificacion:", "nota interna:",
    ]
    frases = [
        "lo importante es explicar", "lo interesante es mirar", "la clave es explicar",
        "aparece como se\u00f1al reciente", "el feed no trae suficiente detalle",
        "conviene usarlo como punto de entrada", "puede servir para descubrir algo fuera",
        "qu\u00e9 pregunta puede mover comentarios reales", "abre conversaci\u00f3n sin inventar datos",
        "tema reciente dentro del mundo gamer", "noticia para comentar es un tema",
    ]
    return any(texto.startswith(p) for p in prefijos) or any(f in texto for f in frases)


def caption_necesita_regenerarse(texto, item=None, estilo="news"):
    item = item or {}
    texto_limpio = limpiar_texto_publicable_final(texto)
    bajo = texto_limpio.lower()
    if any(
        frase in bajo
        for frase in [
            "lo importante es explicar", "lo interesante es mirar", "este tipo de tema conecta",
            "puede servir para descubrir algo fuera", "el feed no trae suficiente detalle",
            "conviene usarlo como punto de entrada", "tema reciente dentro del mundo gamer",
        ]
    ):
        return True
    categoria = _categoria_final_item(item, _estilo_a_categoria(estilo))
    if categoria != "indie" and any(p in bajo for p in ["indies", "juegos independientes", "demos"]):
        return True
    if categoria not in ["nostalgia", "debate"] and any(p in bajo for p in ["juegos f\u00edsicos", "manual", "prestarlo", "cartucho"]):
        return True
    if categoria != "tecnologia" and "ruido t\u00e9cnico" in bajo:
        return True
    return False


def limpiar_lineas_para_caption(texto):
    limpio = limpiar_texto_publicable_final(texto)
    lineas = []
    for linea in limpio.splitlines():
        if re.search(r"https?://|www\.", linea, flags=re.IGNORECASE):
            continue
        if linea_no_publicable(linea):
            continue
        linea = quitar_prefijos_editoriales(linea).strip()
        lineas.append(linea)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lineas)).strip()


def asegurar_hashtags_editoriales(texto, titulo_original="", resumen_original=""):
    lineas = texto.strip().splitlines()
    cuerpo = [linea for linea in lineas if not linea.strip().startswith("#")]
    hashtags = crear_hashtags(f"{titulo_original} {resumen_original}", 5)
    return f"{'\n'.join(cuerpo).strip()}\n\n{hashtags}".strip()


def asegurar_pregunta_final(texto, titulo_original="", estilo="news"):
    lineas = texto.strip().splitlines()
    if not lineas:
        return texto
    hashtags = ""
    if lineas[-1].strip().startswith("#"):
        hashtags = lineas.pop().strip()
    cuerpo = "\n".join(lineas).strip()
    if "?" not in cuerpo and "\u00bf" not in cuerpo:
        cuerpo = f"{cuerpo}\n\n{pregunta_engagement(titulo_original or cuerpo, estilo)}"
    return f"{cuerpo}\n\n{hashtags}".strip() if hashtags else cuerpo


def crear_post_limpio(titulo, resumen, estilo, nostalgia="", hashtags=""):
    estilo = estilo or "news"
    titulo_es = titulo_publico_en_espanol(titulo, estilo)
    resumen_es = resumen_publico_en_espanol(titulo, resumen, estilo)
    detalle = detalle_contextual_para_post(titulo_es, resumen_es, estilo)
    pregunta = pregunta_engagement(titulo_es, estilo)
    hashtags = limitar_hashtags_texto(hashtags or crear_hashtags(f"{titulo} {resumen}", 5), 5)

    partes = [f"\U0001f3ae {titulo_es}", resumen_es]
    if detalle and detalle.lower() not in resumen_es.lower():
        partes.append(detalle)
    partes.extend([pregunta, hashtags])
    return limpiar_gramatica_post_final("\n\n".join(partes))


def aplicar_reglas_editoriales_fuertes(post, item=None, estilo="news"):
    item = item or {}
    titulo = limpiar_html(item.get("title", "Tema gamer"))
    resumen = limpiar_html(item.get("summary", ""))
    texto = limpiar_lineas_para_caption(post)
    if caption_necesita_regenerarse(texto, item, estilo) or parece_texto_ingles(texto):
        texto = crear_post_limpio(titulo, resumen, estilo, item.get("nostalgia_angle", ""), crear_hashtags(f"{titulo} {resumen}", 5))
    texto = limpiar_lineas_para_caption(texto)
    texto = asegurar_hashtags_editoriales(texto, titulo, resumen)
    texto = asegurar_pregunta_final(texto, titulo, estilo)
    return limpiar_gramatica_post_final(texto)


def generate_social_post(item, estilo=None):
    item = dict(item or {})
    categoria = _categoria_final_item(item)
    estilo = estilo or st.session_state.get("post_style", "all")
    if estilo == "all":
        estilo = {
            "gaming": "news",
            "tecnologia": "tecnologia",
            "anime": "anime",
            "indie": "indie",
            "debate": "debate",
            "nostalgia": "nostalgia",
        }.get(categoria, "news")
    estilo = estilo_seguro_para_item(item, estilo)
    titulo = limpiar_html(item.get("title", "Tema gamer"))
    resumen = limpiar_html(item.get("summary", ""))
    item["content_angle"] = categoria if categoria != "gaming" else "news"
    item["nostalgia_angle"] = detectar_angulo_nostalgia(item)
    if item.get("id"):
        st.session_state.generated_items[item["id"]] = dict(item)
        st.session_state.last_item_id = item["id"]
    post = crear_post_limpio(titulo, resumen, estilo, item.get("nostalgia_angle", ""), crear_hashtags(f"{titulo} {resumen}", 5))
    post = aplicar_reglas_editoriales_fuertes(post, item, estilo)
    st.session_state.last_post_text = post
    st.session_state.last_post_title = titulo_publico_en_espanol(titulo, estilo)
    return post


def categorias_para_posts(cantidad, texto):
    texto = limpiar_texto_publicable_final(texto).lower()
    if "anime" in texto and cantidad <= 2:
        base = ["anime", "gaming", "debate", "nostalgia", "tecnologia", "indie"]
    elif "tecnologia" in texto or "tecnolog\u00eda" in texto:
        base = ["tecnologia", "gaming", "anime", "debate", "nostalgia", "indie"]
    elif "nostalgia" in texto or "retro" in texto:
        base = ["nostalgia", "gaming", "anime", "debate", "tecnologia", "indie"]
    elif "debate" in texto:
        base = ["debate", "gaming", "anime", "tecnologia", "nostalgia", "indie"]
    else:
        base = ["gaming", "anime", "tecnologia", "indie", "debate", "nostalgia"]
    salida = []
    while len(salida) < cantidad:
        salida.extend(base)
    return salida[:cantidad]


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


def seleccionar_noticias_variadas(noticias, cantidad, texto_usuario=""):
    cantidad = max(1, min(cantidad, 8))
    exclusiones = detectar_exclusiones_usuario(texto_usuario)
    disponibles = [
        dict(item) for item in filtrar_noticias_verificadas(noticias)
        if item_cumple_exclusiones(item, exclusiones)
    ]
    disponibles.sort(key=lambda item: str(item.get("date", "")), reverse=True)
    seleccionadas = []
    titulos_usados = set()
    fuentes_usadas = {}
    plataformas_usadas = {}

    def puede_usarse(item):
        titulo = limpiar_texto_publicable_final(item.get("title", ""))
        key = titulo.lower()
        if not key or key in titulos_usados:
            return False
        fuente = item.get("source", "")
        plataforma = plataforma_de_item(item)
        if cantidad >= 4 and fuentes_usadas.get(fuente, 0) >= 1:
            return False
        if cantidad >= 4 and plataforma != "general" and plataformas_usadas.get(plataforma, 0) >= 1:
            return False
        if tema_repetido(titulo) or tema_muy_similar(titulo):
            return False
        return True

    def agregar(item):
        titulo = limpiar_texto_publicable_final(item.get("title", ""))
        fuente = item.get("source", "")
        plataforma = plataforma_de_item(item)
        titulos_usados.add(titulo.lower())
        fuentes_usadas[fuente] = fuentes_usadas.get(fuente, 0) + 1
        plataformas_usadas[plataforma] = plataformas_usadas.get(plataforma, 0) + 1
        seleccionadas.append(dict(item))

    for categoria in categorias_para_posts(cantidad, texto_usuario or ""):
        item = seleccionar_noticia_para_categoria([x for x in disponibles if puede_usarse(x)], categoria, titulos_usados)
        if item:
            agregar(item)
        if len(seleccionadas) >= cantidad:
            break

    for item in disponibles:
        if len(seleccionadas) >= cantidad:
            break
        if puede_usarse(item):
            agregar(item)
    return seleccionadas[:cantidad]


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


def etiqueta_publicacion_limpia(categoria):
    etiquetas = {
        "gaming": "Gaming/Noticia",
        "news": "Gaming/Noticia",
        "noticia": "Gaming/Noticia",
        "tecnologia": "Tecnolog\u00eda",
        "technology": "Tecnolog\u00eda",
        "hardware": "Tecnolog\u00eda",
        "anime": "Anime",
        "indie": "Indie/En movimiento",
        "debate": "Debate",
        "nostalgia": "Nostalgia",
        "emocional": "Nostalgia",
    }
    return etiquetas.get(str(categoria or "").lower(), "Gaming/Noticia")


def crear_varios_posts(cantidad, pregunta):
    cantidad = max(2, min(cantidad, 8))
    texto = limpiar_texto_publicable_final(pregunta).lower()
    noticias = buscar_noticias()
    seleccionadas = seleccionar_noticias_variadas(noticias, cantidad, texto)
    categorias = categorias_para_posts(cantidad, texto)
    usados = set()
    posts = []
    items_generados = []
    st.session_state.news_by_number = {}

    for indice in range(1, cantidad + 1):
        categoria_objetivo = categorias[indice - 1]
        item = None
        for candidato in seleccionadas:
            key = candidato.get("id") or candidato.get("title", "")
            if key in usados:
                continue
            if _categoria_final_item(candidato, categoria_objetivo) == categoria_objetivo:
                item = candidato
                break
        if not item:
            for candidato in seleccionadas:
                key = candidato.get("id") or candidato.get("title", "")
                if key not in usados:
                    item = candidato
                    break
        if not item:
            item = crear_item_editorial_categoria(categoria_objetivo, set())

        key = item.get("id") or item.get("title", "")
        usados.add(key)
        categoria_real = _categoria_final_item(item, categoria_objetivo)
        estilo = {
            "gaming": "news",
            "tecnologia": "tecnologia",
            "anime": "anime",
            "indie": "indie",
            "debate": "debate",
            "nostalgia": "nostalgia",
        }.get(categoria_real, "news")
        st.session_state.generated_items[item["id"]] = dict(item)
        st.session_state.news_by_number[indice] = dict(item)
        st.session_state.last_item_id = item["id"]
        items_generados.append(dict(item))
        posts.append(f"PUBLICACI\u00d3N {indice} - {etiqueta_publicacion_limpia(categoria_real).upper()}\n\n{generate_social_post(item, estilo)}")

    respuesta = "\n\n---\n\n".join(posts)
    st.session_state.last_post_text = respuesta
    st.session_state.last_post_title = f"{cantidad}_posts_gamer_signal"
    st.session_state.last_post_items = items_generados
    return limpiar_gramatica_post_final(respuesta)


def estado_verificacion_item(item):
    item = item or {}
    if item.get("source_official"):
        return ("Verde", "fuente oficial")
    if item.get("verification_count", 0) >= 2:
        return ("Verde", "confirmada por varias fuentes")
    if item.get("source_trusted"):
        return ("Amarillo", "fuente confiable; revisar contexto antes de publicar como noticia fuerte")
    if item.get("is_community_signal"):
        return ("Amarillo", "se\u00f1al de comunidad; usar como debate o nostalgia")
    return ("Rojo", "no usar como noticia confirmada")


def formatear_noticias(noticias, texto_usuario="", cantidad=5):
    cantidad = max(1, min(cantidad, 8))
    noticias = seleccionar_noticias_variadas(noticias, cantidad, texto_usuario)
    if not noticias:
        return (
            f"No encontr\u00e9 noticias verificadas nuevas del a\u00f1o {ANIO_NOTICIAS} con ese filtro.\n\n"
            "Puedo crear contenido editorial de debate o nostalgia, pero no lo presentar\u00e9 como noticia confirmada."
        )
    st.session_state.news_by_number = {}
    respuesta = f"Busqu\u00e9 y filtr\u00e9 noticias verificadas del a\u00f1o {ANIO_NOTICIAS}.\n\n"
    respuesta += f"Rango usado: {FECHA_INICIO} hasta {FECHA_FINAL}\n\n"
    for numero, item in enumerate(noticias, start=1):
        item = dict(item)
        categoria = _categoria_final_item(item)
        st.session_state.generated_items[item["id"]] = item
        st.session_state.news_by_number[numero] = item
        st.session_state.last_item_id = item["id"]
        titulo = titulo_visible_seguro(item, categoria)
        estado, detalle = estado_verificacion_item(item)
        resumen = resumen_publico_en_espanol(item.get("title", ""), item.get("summary", ""), categoria)
        respuesta += f"### Noticia {numero}: {titulo}\n\n"
        respuesta += f"**Fecha:** {item.get('date', '')}\n\n"
        respuesta += f"**Fuente:** {item.get('source', 'fuente')}\n\n"
        respuesta += f"**Estado:** {estado} - {detalle}\n\n"
        respuesta += f"{resumen}\n\n"
        respuesta += f"Para usarla: **post de la noticia {numero}**\n\n---\n\n"
    return limpiar_gramatica_post_final(respuesta)


def crear_opciones_post_recientes():
    noticias = seleccionar_noticias_variadas(buscar_noticias(), 5, "opciones de post variadas")
    st.session_state.news_by_number = {}
    respuesta = f"### Opciones de post recientes\n\n"
    if not noticias:
        return "No encontr\u00e9 opciones verificadas nuevas ahora mismo. Puedes pedirme un post de nostalgia o debate editorial."
    for numero, item in enumerate(noticias, start=1):
        categoria = _categoria_final_item(item)
        st.session_state.generated_items[item["id"]] = dict(item)
        st.session_state.news_by_number[numero] = dict(item)
        st.session_state.last_item_id = item["id"]
        respuesta += f"**{numero}. {titulo_visible_seguro(item, categoria)}**\n\n"
        respuesta += f"- Categor\u00eda: {etiqueta_publicacion_limpia(categoria)}\n"
        respuesta += f"- Fuente: {item.get('source', '')}\n"
        respuesta += f"- Para usarla: **post de la noticia {numero}**\n\n"
    return limpiar_gramatica_post_final(respuesta)


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


def parece_texto_ingles(texto):
    limpio = limpiar_texto_publicable_final(limpiar_html(texto))
    bajo = f" {limpio.lower()} "
    if not bajo.strip():
        return False
    frases = [
        "release date", "hands-on", "available today", "coming soon", "coming to",
        "is about", "appeared first", "the post", "official podcast",
        "new trailer", "teaser trailer", "anime adaptation", "getting an anime",
        "could come sooner", "could inherit", "by default", "physical gaming crown",
        "monthly games", "free play days", "public betas", "apple platforms",
        "deep dive", "first-ever", "mass layoffs", "foreign-worker visas",
        "plot hole", "weekly shonen jump", "patron vote", "joins the",
        "turns tough", "powerful friends", "drown you in", "unveils new visual",
        "concludes serialization", "ends serialization",
        "will ", " could ", " is ", " are ", " from ", " with ",
    ]
    if any(frase in bajo for frase in frases):
        return True
    tokens = re.findall(r"[a-z][a-z'-]+", bajo)
    hits = sum(1 for token in tokens if token in PALABRAS_INGLES_GENERALES)
    if "'s" in bajo and hits >= 1:
        return True
    return hits >= 3


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


def _categoria_final_item(item, preferida=None):
    preferida = _estilo_a_categoria(preferida)
    scores = _puntuar_categorias_final(item or {})
    categoria = _categoria_ganadora(scores)
    if categoria == "gaming" and preferida in ["anime", "tecnologia", "indie", "debate", "nostalgia"]:
        return preferida
    return categoria


def categoria_de_item(item):
    return _categoria_final_item(item)


def detectar_content_angle(item):
    categoria = _categoria_final_item(item)
    return "news" if categoria == "gaming" else categoria


def detectar_accion_titulo(titulo, resumen=""):
    texto = limpiar_texto_publicable_final(f"{titulo} {resumen}").lower()
    for accion, patron in ACCIONES_TITULO_GENERALES:
        if re.search(patron, texto, flags=re.IGNORECASE):
            return accion
    return "noticia"


def _limpiar_tema_extraido(tema):
    tema = limpiar_texto_publicable_final(tema)
    tema = re.sub(r"^(manga|anime|game|juego|the post)\s+", "", tema, flags=re.IGNORECASE).strip()
    tema = re.sub(r"\s+(manga|anime|game|juego|news|update|patch|trailer|teaser)$", "", tema, flags=re.IGNORECASE).strip()
    tema = tema.strip(" -:.,'\"")
    if not tema:
        return "Tema gamer"
    return normalizar_titulo_gamer(tema)


def extraer_tema_para_titulo(titulo):
    limpio = limpiar_texto_publicable_final(limpiar_html(titulo))
    if not limpio:
        return "Tema gamer"
    limpio = re.sub(
        r"^(?:pre[- ]?order|preventa|review|preview|hands[- ]on|trailer|teaser|update|patch)\s*[:\-]\s*",
        "",
        limpio,
        flags=re.IGNORECASE,
    ).strip()
    patrones_cita = [
        r"(?:manga|anime)\s+'([^']{2,90})'",
        r'(?:manga|anime)\s+"([^"]{2,90})"',
        r"'([^']{2,90})'",
        r'"([^"]{2,90})"',
    ]
    for patron in patrones_cita:
        match = re.search(patron, limpio, flags=re.IGNORECASE)
        if match:
            return _limpiar_tema_extraido(match.group(1))

    bajo = limpio.lower()
    separadores_accion = [
        " release date", " is getting", " gets ", " will get", " could get",
        " could come", " news could", " news ", " update ", " patch ",
        " joins ", " turns ", " becomes ", " concludes ", " ends ",
        " unveils ", " reveals ", " revealed ", " announces ", " announced ",
        " launches ", " launch ", " coming ", " drops ", " increases ",
        " refutes ", " responds ", " available ", " hands-on", " hands on",
        " deep dive", " report", " details", " builds ",
    ]
    for sep in separadores_accion:
        idx = bajo.find(sep)
        if idx > 1:
            posible = limpio[:idx].strip(" -:.,")
            if 2 <= len(posible) <= 90:
                return _limpiar_tema_extraido(posible)

    for sep in [" - ", " | ", ":"]:
        if sep in limpio:
            posible = limpio.split(sep, 1)[0].strip(" -:.,")
            if 2 <= len(posible) <= 90:
                return _limpiar_tema_extraido(posible)
    return _limpiar_tema_extraido(limpio[:90])


def titulo_publico_en_espanol(titulo, estilo="news"):
    original = limpiar_texto_publicable_final(limpiar_html(titulo))
    if not original:
        return "Tema gamer para comentar"
    tema = extraer_tema_para_titulo(original)
    accion = detectar_accion_titulo(original)
    categoria = _categoria_final_item({"title": original, "summary": ""}, estilo)
    tema_usable = not parece_texto_ingles(tema) and len(tema) > 1

    if not parece_texto_ingles(original) and accion == "noticia":
        return normalizar_titulo_gamer(original)

    if not tema_usable:
        tema = {
            "anime": "Anime nuevo",
            "tecnologia": "Tecnolog\u00eda gamer",
            "indie": "Juego independiente",
            "debate": "Tema de industria",
            "nostalgia": "Tema retro",
        }.get(categoria, "Novedad gamer")

    plantillas = {
        "cierre_serializacion": "{tema} termina una etapa importante",
        "adaptacion_anime": "{tema} tendr\u00e1 adaptaci\u00f3n al anime",
        "avance": "{tema} muestra nuevo avance",
        "actualizacion": "{tema} recibe nuevos detalles",
        "preventa": "{tema} abre etapa de preventa",
        "lanzamiento": "{tema} apunta a nuevo lanzamiento",
        "preservacion": "{tema} entra en conversaci\u00f3n por preservaci\u00f3n gamer",
        "industria": "{tema} abre debate sobre la industria",
        "tecnologia": "{tema}: tecnolog\u00eda gamer bajo la lupa",
        "fisico_digital": "Juegos f\u00edsicos vs digitales vuelve al debate",
        "impresiones": "{tema} deja nuevas impresiones para comentar",
        "mecanica": "{tema} presenta una mec\u00e1nica para comentar",
        "noticia": "{tema}: noticia gamer para comentar",
    }
    titulo_es = plantillas.get(accion, plantillas["noticia"]).format(tema=tema)
    if categoria == "anime" and accion == "noticia":
        titulo_es = f"{tema}: tema anime para comentar"
    elif categoria == "indie" and accion == "noticia":
        titulo_es = f"{tema}: indie para poner en el radar"
    elif categoria == "tecnologia" and accion == "noticia":
        titulo_es = f"{tema}: tecnolog\u00eda gamer bajo la lupa"
    elif categoria == "debate" and accion == "noticia":
        titulo_es = f"{tema}: tema para debatir"
    elif categoria == "nostalgia" and accion == "noticia":
        titulo_es = f"{tema}: nostalgia gamer para comentar"
    return limpiar_texto_publicable_final(titulo_es)


def titulo_visible_seguro(item, estilo="news", bucket=None):
    item = item or {}
    categoria = bucket or item.get("content_angle") or estilo
    titulo = titulo_publico_en_espanol(item.get("title", ""), categoria)
    if parece_texto_ingles(titulo):
        return {
            "anime": "Tema anime para comentar",
            "tecnologia": "Tecnolog\u00eda gamer bajo la lupa",
            "indie": "Juego independiente para poner en el radar",
            "debate": "Tema gamer para debatir",
            "nostalgia": "Nostalgia gamer para comentar",
        }.get(_estilo_a_categoria(categoria), "Noticia gamer para comentar")
    return limpiar_texto_publicable_final(titulo)


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


def resumen_publico_en_espanol(titulo, resumen, estilo="news"):
    titulo_es = titulo_publico_en_espanol(titulo, estilo)
    accion = detectar_accion_titulo(titulo, resumen)
    categoria = _categoria_final_item({"title": titulo, "summary": resumen}, estilo)
    resumen_limpio = limpiar_texto_publicable_final(limpiar_html(resumen))

    frase_real = _frase_real_del_resumen(resumen_limpio, titulo_es)
    if frase_real:
        return frase_real

    traducido = traducir_basico_en_espanol(resumen_limpio)
    frase_traducida = _frase_real_del_resumen(traducido, titulo_es)
    if frase_traducida:
        return frase_traducida

    if accion == "actualizacion":
        return "La noticia apunta a cambios o contenido nuevo que puede afectar c\u00f3mo la comunidad sigue jugando."
    if accion == "avance":
        return "El material nuevo sirve para mirar tono, propuesta y si el hype realmente se sostiene."
    if accion == "cierre_serializacion":
        return "Marca un punto importante para su fandom y abre espacio para hablar de cierre, legado y expectativas."
    if accion == "adaptacion_anime":
        return "La adaptaci\u00f3n puede mover conversaci\u00f3n entre fans por c\u00f3mo se llevar\u00e1 el material original a otro formato."
    if accion == "preservacion":
        return "Importa porque la preservaci\u00f3n ayuda a que juegos y experiencias de otras generaciones no se pierdan."
    if accion == "industria":
        return "Toca decisiones de industria que pueden afectar estudios, trabajadores, proyectos y confianza de la comunidad."
    if accion == "tecnologia" or categoria == "tecnologia":
        return "Vale mirarlo desde el lado gamer: rendimiento, acceso, compatibilidad, precio o experiencia real."
    if categoria == "indie":
        return "Puede servir como descubrimiento si tiene una propuesta clara, una mec\u00e1nica distinta o una demo que enganche."
    if categoria == "anime":
        return "Se mueve dentro de la conversaci\u00f3n anime/geek y puede generar hype, dudas o teor\u00edas del fandom."
    if categoria == "nostalgia":
        return "Conecta con recuerdos, cl\u00e1sicos y esa parte de la comunidad que todav\u00eda valora otras generaciones."
    if categoria == "debate":
        return "Tiene m\u00e1s de un lado para mirar, y por eso funciona mejor cuando se presenta sin pelea de plataformas."
    return "Llega como una novedad para mirar con calma y comentar qu\u00e9 puede significar para la comunidad gamer."


def detalle_contextual_para_post(titulo, texto_base, estilo="news"):
    accion = detectar_accion_titulo(titulo, texto_base)
    categoria = _categoria_final_item({"title": titulo, "summary": texto_base}, estilo)
    if accion == "actualizacion":
        return "La pregunta real es si estos cambios dan razones para volver, seguir jugando o simplemente mirar desde lejos."
    if accion == "avance":
        return "Cuando sale nuevo material, la comunidad suele fijarse en detalles peque\u00f1os: tono, fecha, gameplay y si el hype se sostiene."
    if accion == "preservacion":
        return "Preservar no es solo guardar juegos viejos; tambi\u00e9n es mantener viva una parte importante de la historia gamer."
    if accion == "industria":
        return "Este tipo de tema conviene hablarlo con calma, mirando el impacto real sin convertirlo en guerra de marcas."
    if accion == "fisico_digital":
        return "Ah\u00ed el debate se pone bueno porque cada jugador tiene una historia distinta con discos, cartuchos, descargas y bibliotecas digitales."
    if categoria == "tecnologia":
        return "Lo mejor es bajarlo a tierra: si no mejora c\u00f3mo jugamos, creamos o usamos la tecnolog\u00eda, es solo ruido."
    if categoria == "indie":
        return "Los indies suelen crecer por recomendaci\u00f3n de comunidad, por eso conviene enfocarse en qu\u00e9 lo hace distinto."
    if categoria == "anime":
        return "Anime y gaming se cruzan mucho cuando hay hype, adaptaciones, fandoms comparando expectativas o teor\u00edas."
    if categoria == "nostalgia":
        return "La nostalgia se siente m\u00e1s real cuando conecta con una escena concreta: consola, control, cartucho, disco o gente con quien jugaste."
    if categoria == "debate":
        return "La conversaci\u00f3n funciona mejor cuando presenta dos lados claros y deja espacio para que la comunidad opine."
    return "El valor est\u00e1 en conectar el dato con una pregunta que la comunidad realmente quiera contestar."


def pregunta_engagement(titulo, estilo="news"):
    accion = detectar_accion_titulo(titulo)
    categoria = _categoria_final_item({"title": titulo, "summary": ""}, estilo)
    if accion == "actualizacion":
        return "\U0001f447 \u00bfEsto te anima a volver o lo dejar\u00edas pasar?"
    if accion == "avance":
        return "\U0001f447 \u00bfEste avance te subi\u00f3 el hype o necesitas ver m\u00e1s?"
    if accion == "lanzamiento" or accion == "preventa":
        return "\U0001f447 \u00bfLo pondr\u00edas en tu lista o esperar\u00edas m\u00e1s detalles?"
    if accion == "preservacion":
        return "\U0001f447 \u00bfQu\u00e9 cl\u00e1sico te gustar\u00eda ver mejor preservado?"
    if accion == "fisico_digital":
        return "\U0001f447 \u00bfT\u00fa eres team f\u00edsico o team digital?"
    if categoria == "tecnologia":
        return "\U0001f447 \u00bfEsto te parece \u00fatil para gamers o puro ruido t\u00e9cnico?"
    if categoria == "indie":
        return "\U0001f447 \u00bfLo pondr\u00edas en tu radar o esperas m\u00e1s gameplay primero?"
    if categoria == "anime":
        return "\U0001f447 \u00bfEste tema te da hype o prefieres esperar m\u00e1s informaci\u00f3n?"
    if categoria == "nostalgia":
        return "\U0001f447 \u00bfQu\u00e9 recuerdo gamer te vino a la mente?"
    if categoria == "debate":
        return "\U0001f447 \u00bfT\u00fa c\u00f3mo lo ves: buena movida o mala decisi\u00f3n?"
    return "\U0001f447 \u00bfEsto te interesa o lo dejar\u00edas pasar?"


def limpiar_gramatica_post_final(texto):
    texto = reparar_texto_roto(str(texto or ""))
    reemplazos = {
        "Preg\u00c3\u00bantame": "Preg\u00fantame",
        "PUBLICACI?N": "PUBLICACI\u00d3N",
        "TECNOLOG?A": "TECNOLOG\u00cdA",
        "Tecnolog?a": "Tecnolog\u00eda",
        "tecnolog?a": "tecnolog\u00eda",
        "Verificaci?n": "Verificaci\u00f3n",
        "verificaci?n": "verificaci\u00f3n",
        "Conexi?n": "Conexi\u00f3n",
        "conexi?n": "conexi\u00f3n",
        "espec?fica": "espec\u00edfica",
        "confirmaci?n": "confirmaci\u00f3n",
        "Acci?n": "Acci\u00f3n",
        "guard?": "guard\u00e9",
        "?til": "\u00fatil",
        "f?sicos": "f\u00edsicos",
        "pr?xima": "pr\u00f3xima",
        "Miercoles": "Mi\u00e9rcoles",
        "Mi?rcoles": "Mi\u00e9rcoles",
        "S?bado": "S\u00e1bado",
        "r?pida": "r\u00e1pida",
        "recomendaci?n": "recomendaci\u00f3n",
    }
    for malo, bueno in reemplazos.items():
        texto = texto.replace(malo, bueno)
    texto = re.sub(r"\bano\b", "a\u00f1o", texto)
    texto = re.sub(r"\bBusque y filtre\b", "Busqu\u00e9 y filtr\u00e9", texto)
    texto = re.sub(r"[ \t]{2,}", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    lineas = []
    for linea in texto.splitlines():
        limpia = linea.rstrip()
        if limpia.startswith("?"):
            limpia = "\u00bf" + limpia[1:]
        if limpia.startswith("\u00bf") and not limpia.endswith("?"):
            limpia += "?"
        lineas.append(limpia)
    return "\n".join(lineas).strip()


def linea_no_publicable(linea):
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
    frases = [
        "lo importante es aterrizarlo a la comunidad",
        "lo importante es explicar",
        "lo interesante es mirar",
        "la clave es explicar",
        "que conversacion puede abrir",
        "qu\u00e9 conversaci\u00f3n puede abrir",
        "que pregunta puede mover comentarios reales",
        "qu\u00e9 pregunta puede mover comentarios reales",
        "este tipo de tema conecta con la comunidad porque cada gamer",
        "puede servir para descubrir algo fuera",
        "aparece como se\u00f1al reciente",
        "el feed no trae suficiente detalle",
        "conviene usarlo como punto de entrada",
        "tema reciente dentro del mundo gamer",
        "no se presenta como noticia confirmada",
        "referencia gamer cave usada",
    ]
    return any(texto.startswith(p) for p in prefijos) or any(f in texto for f in frases)


def caption_necesita_regenerarse(texto, item=None, estilo="news"):
    item = item or {}
    bajo = limpiar_texto_publicable_final(texto).lower()
    frases_malas = [
        "lo importante es explicar", "lo interesante es mirar",
        "puede servir para descubrir algo fuera", "el feed no trae suficiente detalle",
        "tema reciente dentro del mundo gamer", "la clave es explicar",
        "este tipo de tema conecta con la comunidad porque cada gamer",
    ]
    if any(frase in bajo for frase in frases_malas):
        return True
    categoria = _categoria_final_item(item, estilo)
    if categoria != "indie" and any(p in bajo for p in ["indies", "juegos independientes", "demos"]):
        return True
    if categoria not in ["nostalgia", "debate"] and any(p in bajo for p in ["juegos f\u00edsicos", "manual", "prestarlo", "cartucho"]):
        return True
    if categoria != "tecnologia" and any(p in bajo for p in ["ruido t\u00e9cnico", "cambio \u00fatil"]):
        return True
    return parece_texto_ingles("\n".join(line for line in str(texto).splitlines() if not line.startswith("#")))


def limpiar_lineas_para_caption(texto):
    limpio = limpiar_texto_publicable_final(texto)
    lineas = []
    for linea in limpio.splitlines():
        if re.search(r"https?://|www\.", linea, flags=re.IGNORECASE):
            continue
        linea = quitar_prefijos_editoriales(linea).strip()
        if linea_no_publicable(linea):
            continue
        lineas.append(linea)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lineas)).strip()


def crear_hashtags(texto, limite=None):
    limite = limite or obtener_limite_hashtags()
    texto = limpiar_texto_publicable_final(texto).lower()
    brand = get_brand_voice().get("brand", "El Gamer Cave")
    hashtags = ["#davietgaming" if brand == "Daviet Gaming" else "#elgamercave"]
    reglas = [
        (["anime", "manga", "crunchyroll", "shonen"], ["#anime", "#manga", "#otaku"]),
        (["nintendo", "switch", "mario", "zelda", "kirby", "pokemon", "pok\u00e9mon"], ["#nintendo", "#nintendoswitch"]),
        (["playstation", "ps5", "ps plus"], ["#playstation", "#ps5"]),
        (["xbox", "game pass"], ["#xbox", "#xboxseriesx"]),
        (["pc", "steam", "gpu", "nvidia", "amd", "intel", "hardware"], ["#pcgaming", "#gamingtech"]),
        (["indie", "independent", "next fest"], ["#indiegames", "#indiegaming"]),
        (["retro", "nostalgia", "classic", "clasico", "cl\u00e1sico", "remake", "remaster"], ["#nostalgia", "#retrogaming"]),
    ]
    for claves, nuevos in reglas:
        if any(clave in texto for clave in claves):
            hashtags.extend(nuevos)
    hashtags.extend(["#gaming", "#videojuegos", "#gamers", "#geekculture"])
    return limitar_hashtags_texto(" ".join(dict.fromkeys(hashtags)), limite)


def crear_post_limpio(titulo, resumen, estilo, nostalgia="", hashtags=""):
    estilo = estilo or "news"
    titulo_es = titulo_publico_en_espanol(titulo, estilo)
    resumen_es = resumen_publico_en_espanol(titulo, resumen, estilo)
    detalle = detalle_contextual_para_post(titulo, resumen or resumen_es, estilo)
    pregunta = pregunta_engagement(titulo, estilo)
    hashtags = limitar_hashtags_texto(hashtags or crear_hashtags(f"{titulo} {resumen}", 5), 5)
    partes = [f"\U0001f3ae {titulo_es}", resumen_es]
    if detalle and detalle.lower() not in resumen_es.lower():
        partes.append(detalle)
    if nostalgia and _estilo_a_categoria(estilo) in ["nostalgia", "debate"]:
        nostalgia = limpiar_texto_publicable_final(nostalgia)
        if nostalgia and nostalgia.lower() not in " ".join(partes).lower():
            partes.append(nostalgia)
    partes.extend([pregunta, hashtags])
    return limpiar_gramatica_post_final("\n\n".join(partes))


def aplicar_reglas_editoriales_fuertes(post, item=None, estilo="news"):
    item = item or {}
    titulo = limpiar_html(item.get("title", "Tema gamer"))
    resumen = limpiar_html(item.get("summary", ""))
    texto = limpiar_lineas_para_caption(post)
    if caption_necesita_regenerarse(texto, item, estilo):
        texto = crear_post_limpio(titulo, resumen, estilo, item.get("nostalgia_angle", ""), crear_hashtags(f"{titulo} {resumen}", 5))
        texto = limpiar_lineas_para_caption(texto)
    texto = asegurar_hashtags_editoriales(texto, titulo, resumen)
    texto = asegurar_pregunta_final(texto, titulo, estilo)
    return limpiar_gramatica_post_final(texto)


def generate_social_post(item, estilo=None):
    item = dict(item or {})
    categoria = _categoria_final_item(item)
    estilo = estilo or st.session_state.get("post_style", "all")
    if estilo == "all":
        estilo = {
            "gaming": "news",
            "tecnologia": "tecnologia",
            "anime": "anime",
            "indie": "indie",
            "debate": "debate",
            "nostalgia": "nostalgia",
        }.get(categoria, "news")
    estilo = estilo_seguro_para_item(item, estilo)
    titulo = limpiar_html(item.get("title", "Tema gamer"))
    resumen = limpiar_html(item.get("summary", ""))
    item["content_angle"] = categoria if categoria != "gaming" else "news"
    item["nostalgia_angle"] = detectar_angulo_nostalgia(item)
    if item.get("id"):
        st.session_state.generated_items[item["id"]] = dict(item)
        st.session_state.last_item_id = item["id"]
    post = crear_post_limpio(titulo, resumen, estilo, item.get("nostalgia_angle", ""), crear_hashtags(f"{titulo} {resumen}", 5))
    post = aplicar_reglas_editoriales_fuertes(post, item, estilo)
    st.session_state.last_post_text = post
    st.session_state.last_post_title = titulo_publico_en_espanol(titulo, estilo)
    return post


def categorias_para_posts(cantidad, texto):
    texto = limpiar_texto_publicable_final(texto).lower()
    if "anime" in texto and cantidad <= 2:
        base = ["anime", "gaming", "tecnologia", "indie", "debate", "nostalgia"]
    elif "tecnologia" in texto or "tecnolog\u00eda" in texto:
        base = ["tecnologia", "gaming", "anime", "indie", "debate", "nostalgia"]
    elif "nostalgia" in texto or "retro" in texto:
        base = ["nostalgia", "gaming", "anime", "tecnologia", "debate", "indie"]
    elif "debate" in texto:
        base = ["debate", "gaming", "anime", "tecnologia", "indie", "nostalgia"]
    else:
        base = ["gaming", "anime", "tecnologia", "indie", "debate", "nostalgia"]
    salida = []
    while len(salida) < cantidad:
        salida.extend(base)
    return salida[:cantidad]


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


def seleccionar_noticias_variadas(noticias, cantidad, texto_usuario=""):
    cantidad = max(1, min(cantidad, 8))
    exclusiones = detectar_exclusiones_usuario(texto_usuario)
    disponibles = [
        dict(item) for item in filtrar_noticias_verificadas(noticias)
        if item_cumple_exclusiones(item, exclusiones)
    ]
    disponibles.sort(key=lambda item: str(item.get("date", "")), reverse=True)
    seleccionadas = []
    titulos_usados = set()
    fuentes_usadas = {}
    plataformas_usadas = {}

    def puede_usarse(item, estricto=True):
        titulo = limpiar_texto_publicable_final(item.get("title", ""))
        key = titulo.lower().strip()
        if not key or key in titulos_usados:
            return False
        if tema_repetido(titulo) or tema_muy_similar(titulo):
            return False
        if estricto and cantidad >= 4:
            fuente = item.get("source", "")
            plataforma = plataforma_de_item(item)
            if fuentes_usadas.get(fuente, 0) >= 1:
                return False
            if plataforma != "general" and plataformas_usadas.get(plataforma, 0) >= 1:
                return False
        return True

    def agregar(item):
        titulo = limpiar_texto_publicable_final(item.get("title", ""))
        fuente = item.get("source", "")
        plataforma = plataforma_de_item(item)
        titulos_usados.add(titulo.lower().strip())
        fuentes_usadas[fuente] = fuentes_usadas.get(fuente, 0) + 1
        plataformas_usadas[plataforma] = plataformas_usadas.get(plataforma, 0) + 1
        seleccionadas.append(dict(item))

    for categoria in categorias_para_posts(cantidad, texto_usuario or ""):
        for item in disponibles:
            if puede_usarse(item) and _categoria_final_item(item, categoria) == categoria:
                agregar(item)
                break
        if len(seleccionadas) >= cantidad:
            break

    for estricto in [True, False]:
        for item in disponibles:
            if len(seleccionadas) >= cantidad:
                break
            if puede_usarse(item, estricto):
                agregar(item)
    return seleccionadas[:cantidad]


def etiqueta_publicacion_limpia(categoria):
    etiquetas = {
        "gaming": "Gaming/Noticia",
        "news": "Gaming/Noticia",
        "noticia": "Gaming/Noticia",
        "tecnologia": "Tecnolog\u00eda",
        "technology": "Tecnolog\u00eda",
        "hardware": "Tecnolog\u00eda",
        "anime": "Anime",
        "indie": "Indie/En movimiento",
        "debate": "Debate",
        "nostalgia": "Nostalgia",
        "emocional": "Nostalgia",
    }
    return etiquetas.get(str(categoria or "").lower(), "Gaming/Noticia")


def crear_varios_posts(cantidad, pregunta):
    cantidad = max(2, min(cantidad, 8))
    texto = limpiar_texto_publicable_final(pregunta).lower()
    noticias = buscar_noticias()
    seleccionadas = seleccionar_noticias_variadas(noticias, cantidad, texto)
    categorias = categorias_para_posts(cantidad, texto)
    usados = set()
    posts = []
    items_generados = []
    st.session_state.news_by_number = {}

    for indice in range(1, cantidad + 1):
        categoria_objetivo = categorias[indice - 1]
        item = None
        for candidato in seleccionadas:
            key = candidato.get("id") or candidato.get("title", "")
            if key not in usados and _categoria_final_item(candidato, categoria_objetivo) == categoria_objetivo:
                item = candidato
                break
        if not item:
            for candidato in seleccionadas:
                key = candidato.get("id") or candidato.get("title", "")
                if key not in usados:
                    item = candidato
                    break
        if not item:
            item = crear_item_editorial_categoria(categoria_objetivo, set())

        key = item.get("id") or item.get("title", "")
        usados.add(key)
        categoria_real = _categoria_final_item(item, categoria_objetivo)
        estilo = {
            "gaming": "news",
            "tecnologia": "tecnologia",
            "anime": "anime",
            "indie": "indie",
            "debate": "debate",
            "nostalgia": "nostalgia",
        }.get(categoria_real, "news")
        st.session_state.generated_items[item["id"]] = dict(item)
        st.session_state.news_by_number[indice] = dict(item)
        st.session_state.last_item_id = item["id"]
        items_generados.append(dict(item))
        posts.append(f"PUBLICACI\u00d3N {indice} - {etiqueta_publicacion_limpia(categoria_real).upper()}\n\n{generate_social_post(item, estilo)}")

    respuesta = "\n\n---\n\n".join(posts)
    st.session_state.last_post_text = respuesta
    st.session_state.last_post_title = f"{cantidad}_posts_gamer_signal"
    st.session_state.last_post_items = items_generados
    return limpiar_gramatica_post_final(respuesta)


def estado_verificacion_item(item):
    item = item or {}
    nivel = str(item.get("verification_level", "")).lower()
    fuente = str(item.get("source", "")).lower()
    confianza = str(item.get("confidence_level", "")).lower()
    if item.get("source_official") or "oficial" in fuente:
        return ("Verde", "fuente oficial")
    if item.get("verification_count", 0) >= 2 or any(p in nivel for p in ["verificada", "2 fuentes", "3 fuentes"]):
        return ("Verde", "verificada")
    if item.get("source_trusted") or "confiable" in fuente or confianza in ["medium-high", "trusted"]:
        return ("Amarillo", "fuente confiable; revisar contexto antes de publicarla como noticia fuerte")
    if item.get("is_community_signal"):
        return ("Amarillo", "se\u00f1al de comunidad; usar como debate o nostalgia")
    return ("Rojo", "no usar como noticia confirmada")


def formatear_noticias(noticias, texto_usuario="", cantidad=5):
    cantidad = max(1, min(cantidad, 8))
    noticias = seleccionar_noticias_variadas(noticias, cantidad, texto_usuario)
    if not noticias:
        return (
            f"No encontr\u00e9 noticias verificadas nuevas del a\u00f1o {ANIO_NOTICIAS} con ese filtro.\n\n"
            "Puedo crear contenido editorial de debate o nostalgia, pero no lo presentar\u00e9 como noticia confirmada."
        )
    st.session_state.news_by_number = {}
    respuesta = f"Busqu\u00e9 y filtr\u00e9 noticias verificadas del a\u00f1o {ANIO_NOTICIAS}.\n\n"
    respuesta += f"Rango usado: {FECHA_INICIO} hasta {FECHA_FINAL}\n\n"
    for numero, item in enumerate(noticias, start=1):
        item = dict(item)
        categoria = _categoria_final_item(item)
        st.session_state.generated_items[item["id"]] = item
        st.session_state.news_by_number[numero] = item
        st.session_state.last_item_id = item["id"]
        titulo = titulo_visible_seguro(item, categoria)
        estado, detalle = estado_verificacion_item(item)
        resumen = resumen_publico_en_espanol(item.get("title", ""), item.get("summary", ""), categoria)
        respuesta += f"### Noticia {numero}: {titulo}\n\n"
        respuesta += f"**Fecha:** {item.get('date', '')}\n\n"
        respuesta += f"**Fuente:** {item.get('source', 'fuente')}\n\n"
        respuesta += f"**Estado:** {estado} - {detalle}\n\n"
        respuesta += f"{resumen}\n\n"
        respuesta += f"Para usarla: **post de la noticia {numero}**\n\n---\n\n"
    return limpiar_gramatica_post_final(respuesta)


def crear_opciones_post_recientes():
    noticias = seleccionar_noticias_variadas(buscar_noticias(), 5, "opciones de post variadas")
    st.session_state.news_by_number = {}
    if not noticias:
        return "No encontr\u00e9 opciones verificadas nuevas ahora mismo. Puedes pedirme un post de nostalgia o debate editorial."
    respuesta = "### Opciones de post recientes\n\n"
    for numero, item in enumerate(noticias, start=1):
        categoria = _categoria_final_item(item)
        st.session_state.generated_items[item["id"]] = dict(item)
        st.session_state.news_by_number[numero] = dict(item)
        st.session_state.last_item_id = item["id"]
        respuesta += f"**{numero}. {titulo_visible_seguro(item, categoria)}**\n\n"
        respuesta += f"- Categor\u00eda: {etiqueta_publicacion_limpia(categoria)}\n"
        respuesta += f"- Fuente: {item.get('source', '')}\n"
        respuesta += f"- Para usarla: **post de la noticia {numero}**\n\n"
    return limpiar_gramatica_post_final(respuesta)


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


def reparar_texto_roto(texto):
    if texto is None:
        return ""
    texto = str(texto)
    for _ in range(3):
        if not any(marca in texto for marca in ["\u00c3", "\u00c2", "\u00e2", "\u00f0"]):
            break
        try:
            reparado = texto.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if reparado == texto:
            break
        texto = reparado
    reemplazos = {
        "PUBLICACI?N": "PUBLICACI\u00d3N",
        "TECNOLOG?A": "TECNOLOG\u00cdA",
        "Preg?ntame": "Preg\u00fantame",
        "verificaci?n": "verificaci\u00f3n",
        "Verificaci?n": "Verificaci\u00f3n",
        "conversaci?n": "conversaci\u00f3n",
        "informaci?n": "informaci\u00f3n",
        "publicaci?n": "publicaci\u00f3n",
        "adaptaci?n": "adaptaci\u00f3n",
        "serializaci?n": "serializaci\u00f3n",
        "tecnolog?a": "tecnolog\u00eda",
        "Tecnolog?a": "Tecnolog\u00eda",
        "espa?ol": "espa\u00f1ol",
        "ingl?s": "ingl\u00e9s",
        "qu?": "qu\u00e9",
        "Qu?": "Qu\u00e9",
        "c?mo": "c\u00f3mo",
        "C?mo": "C\u00f3mo",
        "cu?l": "cu\u00e1l",
        "t?": "t\u00fa",
        "m?s": "m\u00e1s",
        "est?": "est\u00e1",
        "est?n": "est\u00e1n",
        "todav?a": "todav\u00eda",
        "f?sicos": "f\u00edsicos",
        "f?sico": "f\u00edsico",
        "t?cnico": "t\u00e9cnico",
        "cl?sicos": "cl\u00e1sicos",
        "nost?lgico": "nost\u00e1lgico",
        "se?al": "se\u00f1al",
        "a\u00f1o": "a\u00f1o",
        "\u00e2\u20ac\u2122": "'",
        "\u00e2\u20ac\u02dc": "'",
        "\u00e2\u20ac\u0153": '"',
        "\u00e2\u20ac\ufffd": '"',
        "\u00e2\u20ac\u201c": "-",
        "\u00e2\u20ac\u00a6": "...",
    }
    for malo, bueno in reemplazos.items():
        texto = texto.replace(malo, bueno)
    texto = re.sub(r"([A-Za-z])\u00fas\b", r"\1's", texto)
    return texto.replace("\ufffd", "")


def limpiar_texto_publicable_final(texto):
    base = str(texto or "")
    if "<" in base and ">" in base:
        base = limpiar_html(base)
    base = html_unescape(base)
    base = reparar_texto_roto(base)
    base = re.sub(r"https?://\S+", "", base)
    base = re.sub(r"\bThe post\b.*?\bappeared first on\b.*?(?:\.|\n|$)", "", base, flags=re.IGNORECASE | re.DOTALL)
    base = re.sub(r"\bappeared first on\b.*?(?:\.|\n|$)", "", base, flags=re.IGNORECASE | re.DOTALL)
    base = base.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    base = base.replace("\u2013", "-").replace("\u2014", "-")
    base = re.sub(r"\s+([.,;:!?])", r"\1", base)
    base = re.sub(r"[ \t]{2,}", " ", base)
    base = re.sub(r"\n{3,}", "\n\n", base)
    return base.strip()


def parece_texto_ingles(texto):
    limpio = limpiar_texto_publicable_final(texto)
    bajo = f" {limpio.lower()} "
    if not bajo.strip():
        return False
    frases = [
        "release date", "available today", "coming soon", "coming to",
        "getting an anime", "anime adaptation", "new trailer", "teaser trailer",
        "new visual", "public betas", "mass layoffs", "foreign-worker",
        "weekly shonen jump", "patron vote", "drown you in", "unveils",
        "could come sooner", "joins the", "turns tough", "physical gaming",
        "hands-on", "deep dive", "concludes serialization", "ends serialization",
        "gameplay mechanic", "changes rewards", "new information",
        "a conversation about", "changing retail strategies",
        "will ", " could ", " is ", " are ",
    ]
    if any(frase in bajo for frase in frases):
        return True
    tokens = re.findall(r"[a-z][a-z'-]+", bajo)
    hits = sum(1 for token in tokens if token in PALABRAS_INGLES_VISIBLES)
    return hits >= 3 or ("'s" in bajo and hits >= 1)


def _texto_item_editorial(item):
    item = item or {}
    return limpiar_texto_publicable_final(
        f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}"
    ).lower()


def _categoria_final_item(item, preferida=None):
    item = item or {}
    texto = _texto_item_editorial(item)
    fuente = str(item.get("source", "")).lower()
    preferida = _estilo_a_categoria(preferida)
    explicita = _estilo_a_categoria(item.get("content_angle") or item.get("editorial_category"))
    categorias_validas = ["gaming", "tecnologia", "anime", "indie", "debate", "nostalgia"]

    if item_es_contexto_editorial(item) and explicita in categorias_validas:
        return explicita
    if item_es_contexto_editorial(item) and preferida in categorias_validas:
        return preferida

    scores = {
        "gaming": 1,
        "tecnologia": 0,
        "anime": 0,
        "indie": 0,
        "debate": 0,
        "nostalgia": 0,
    }
    if any(p in fuente for p in ["anime", "myanimelist", "crunchyroll", "anime corner"]) or any(
        p in texto for p in ["anime", "manga", "shonen", "otaku", "serializacion", "serializaci\u00f3n", "serialization"]
    ):
        scores["anime"] += 4
    if re.search(r"\b(gpu|rtx|nvidia|amd|intel|hardware|ios|macos|apple|ram|cloud gaming|unreal engine|godot|tecnolog[ií]a|tech)\b", texto):
        scores["tecnologia"] += 4
    if re.search(r"\b(indie|independent|independiente|steam next fest|next fest|demo|early access|solo developer)\b", texto):
        scores["indie"] += 4
    if re.search(r"\b(layoff|layoffs|despidos|workers|fired|price|precio|delay|retraso|cancel|microtransaction|subscription|suscripci[oó]n|review bombing|physical|digital|f[ií]sico|cartucho|disco|manual)\b", texto):
        scores["debate"] += 4
    if any(p in texto for p in ["preservation", "preservaci", "classic", "clasico", "cl\u00e1sico", "retro", "remake", "remaster", "anniversary", "aniversario", "gamecube", "game boy", "ps1", "ps2", "xbox 360", "cartucho", "manual"]):
        scores["nostalgia"] += 4

    return max(scores, key=scores.get)


def categoria_de_item(item):
    return _categoria_final_item(item)


def detectar_content_angle(item):
    categoria = _categoria_final_item(item)
    if categoria == "tecnologia":
        return "technology"
    if categoria == "gaming":
        return "news"
    return categoria


def detectar_accion_titulo(titulo, resumen=""):
    texto = limpiar_texto_publicable_final(f"{titulo} {resumen}").lower()
    for accion, patron in PATRONES_ACCION_TITULO:
        if re.search(patron, texto, flags=re.IGNORECASE):
            return accion
    return "noticia"


def _limpiar_tema_titulo(tema):
    tema = limpiar_texto_publicable_final(tema)
    tema = re.sub(r"^(manga|anime|game|juego|the post|review|preview)\s+", "", tema, flags=re.IGNORECASE)
    tema = re.sub(r"\s+(manga|anime|game|juego|news|update|patch|trailer|teaser)$", "", tema, flags=re.IGNORECASE)
    tema = tema.strip(" -:.,'\"")
    if not tema:
        return "Tema gamer"
    return normalizar_titulo_gamer(tema)


def extraer_tema_para_titulo(titulo):
    limpio = limpiar_texto_publicable_final(titulo)
    if not limpio:
        return "Tema gamer"

    for patron in [
        r"(?:manga|anime)\s+'([^']{2,90})'",
        r'(?:manga|anime)\s+"([^"]{2,90})"',
        r"'([^']{2,90})'",
        r'"([^"]{2,90})"',
        r"\bwith\s+([A-Z][A-Za-z0-9:' \-]{2,70})$",
    ]:
        match = re.search(patron, limpio, flags=re.IGNORECASE)
        if match:
            return _limpiar_tema_titulo(match.group(1))

    bajo = limpio.lower()
    separadores_accion = [
        " release date", " is getting", " gets ", " will get", " could get",
        " could come", " news could", " update ", " patch ", " joins ",
        " turns ", " becomes ", " concludes ", " ends ", " unveils ",
        " reveals ", " revealed ", " announces ", " announced ", " launches ",
        " launch ", " coming ", " drops ", " increases ", " refutes ",
        " responds ", " available ", " hands-on", " hands on", " deep dive",
        " report", " details", " builds ", " goes ", " adds ",
    ]
    for sep in separadores_accion:
        idx = bajo.find(sep)
        if idx > 1:
            return _limpiar_tema_titulo(limpio[:idx])

    for sep in [" - ", " | ", ":"]:
        if sep in limpio:
            parte = limpio.split(sep, 1)[0]
            if 2 <= len(parte.strip()) <= 90:
                return _limpiar_tema_titulo(parte)
    return _limpiar_tema_titulo(limpio[:85])


def titulo_publico_en_espanol(titulo, estilo="news"):
    original = limpiar_texto_publicable_final(titulo)
    if not original:
        return "Tema gamer para comentar"
    tema = extraer_tema_para_titulo(original)
    accion = detectar_accion_titulo(original)
    categoria = _categoria_final_item({"title": original, "summary": ""}, estilo)
    if not parece_texto_ingles(original) and accion == "noticia":
        return normalizar_titulo_gamer(original)
    if parece_texto_ingles(tema) or len(tema) < 2:
        tema = {
            "anime": "Anime nuevo",
            "tecnologia": "Tecnolog\u00eda gamer",
            "indie": "Juego indie",
            "debate": "Tema de industria",
            "nostalgia": "Tema retro",
        }.get(categoria, "Novedad gamer")

    plantillas = {
        "cierre_serializacion": "{tema} termina una etapa importante",
        "adaptacion_anime": "{tema} tendr\u00e1 adaptaci\u00f3n al anime",
        "avance": "{tema} muestra nuevo material",
        "actualizacion": "{tema} recibe una actualizaci\u00f3n para comentar",
        "preventa": "{tema} abre etapa de preventa",
        "lanzamiento": "{tema} pone su lanzamiento en el radar",
        "senal": "{tema}: novedades posibles para comentar",
        "preservacion": "{tema} conecta con preservaci\u00f3n y nostalgia",
        "industria": "{tema} abre conversaci\u00f3n sobre la industria",
        "fisico_digital": "Juegos f\u00edsicos vs digitales vuelve al debate",
        "tecnologia": "{tema}: tecnolog\u00eda gamer bajo la lupa",
        "mecanica": "{tema} presenta una mec\u00e1nica para comentar",
        "noticia": "{tema}: noticia gamer para comentar",
    }
    salida = plantillas.get(accion, plantillas["noticia"]).format(tema=tema)
    if categoria == "anime" and accion == "noticia":
        salida = f"{tema}: tema anime para comentar"
    elif categoria == "tecnologia" and accion == "noticia":
        salida = f"{tema}: tecnolog\u00eda gamer bajo la lupa"
    elif categoria == "indie" and accion == "noticia":
        salida = f"{tema}: indie para poner en el radar"
    elif categoria == "debate" and accion == "noticia":
        salida = f"{tema}: tema para debatir"
    elif categoria == "nostalgia" and accion == "noticia":
        salida = f"{tema}: nostalgia gamer para comentar"
    return limpiar_texto_publicable_final(salida)


def titulo_visible_seguro(item, estilo="news", bucket=None):
    return titulo_publico_en_espanol((item or {}).get("title", ""), bucket or estilo)


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


def _resumen_fuente_util(resumen, titulo_es=""):
    resumen = limpiar_texto_publicable_final(resumen)
    if resumen.lower().startswith("tema editorial"):
        return ""
    if len(resumen) < 50 or parece_texto_ingles(resumen):
        return ""
    if linea_no_publicable(resumen) or any(frase in resumen.lower() for frase in FRASES_PLANTILLA_BLOQUEADAS):
        return ""
    if titulo_es and resumen.lower().startswith(titulo_es.lower()):
        return ""
    return recortar_texto(resumen, 260)


def resumen_publico_en_espanol(titulo, resumen, estilo="news"):
    titulo_es = titulo_publico_en_espanol(titulo, estilo)
    tema = extraer_tema_para_titulo(titulo)
    accion = detectar_accion_titulo(titulo, resumen)
    categoria = _categoria_final_item({"title": titulo, "summary": resumen}, estilo)

    fuente_util = _resumen_fuente_util(resumen, titulo_es)
    if fuente_util:
        return fuente_util
    traducido = traducir_basico_en_espanol(resumen)
    fuente_traducida = _resumen_fuente_util(traducido, titulo_es)
    if fuente_traducida:
        return fuente_traducida

    if accion == "actualizacion":
        return f"La noticia gira alrededor de una actualizaci\u00f3n para {tema}. La conversaci\u00f3n est\u00e1 en si esos cambios dan razones para volver, seguir jugando o mirar desde lejos."
    if accion == "avance":
        return f"El nuevo material de {tema} sirve para medir la expectativa: tono, visuales, jugabilidad y qu\u00e9 tanto convence a la comunidad."
    if accion == "mecanica":
        return f"La noticia se enfoca en una mec\u00e1nica de {tema}. Ese tipo de cambio puede mover conversaci\u00f3n porque afecta reto, estrategia y forma de jugar."
    if accion == "senal":
        return f"Alrededor de {tema} hay una se\u00f1al que puede prender la emoci\u00f3n, pero conviene tratarla con cuidado hasta que exista una confirmaci\u00f3n clara."
    if accion == "cierre_serializacion":
        return f"El cierre de {tema} marca un momento importante para su fandom. Cuando una historia termina, casi siempre empieza el debate sobre legado, final y adaptaci\u00f3n."
    if accion == "adaptacion_anime":
        return f"La adaptaci\u00f3n de {tema} puede mover conversaci\u00f3n entre fans por c\u00f3mo llevar\u00e1 el material original a otro formato."
    if accion == "preservacion":
        return f"{tema} entra en una conversaci\u00f3n importante: preservar juegos tambi\u00e9n es mantener viva una parte de la historia gamer."
    if accion == "industria":
        return f"{tema} toca decisiones de industria que pueden afectar estudios, trabajadores, proyectos y confianza de la comunidad."
    if accion == "fisico_digital":
        return "El debate f\u00edsico vs digital sigue vivo porque mezcla comodidad, propiedad, nostalgia y la forma en que cada gamer guarda sus juegos."
    if categoria == "tecnologia":
        return f"{tema} vale mirarlo desde el lado gamer: rendimiento, acceso, precio, compatibilidad o experiencia real."
    if categoria == "anime":
        return f"{tema} cruza anime y cultura geek con una pregunta simple: si realmente hay emoci\u00f3n o si conviene esperar m\u00e1s informaci\u00f3n."
    if categoria == "indie":
        return f"{tema} puede entrar en el radar si tiene una propuesta clara, una mec\u00e1nica distinta o una demo que la comunidad quiera recomendar."
    if categoria == "nostalgia":
        return f"{tema} conecta con recuerdos, cl\u00e1sicos y esa parte de la comunidad que todav\u00eda valora otras generaciones."
    if categoria == "debate":
        return f"{tema} tiene m\u00e1s de un lado para mirar, por eso funciona mejor cuando se presenta sin pelea de plataformas."
    return f"{tema} llega como una novedad para mirar con calma y comentar qu\u00e9 puede significar para la comunidad gamer."


def detalle_contextual_para_post(titulo, texto_base, estilo="news"):
    accion = detectar_accion_titulo(titulo, texto_base)
    categoria = _categoria_final_item({"title": titulo, "summary": texto_base}, estilo)
    if accion == "actualizacion":
        return "La pregunta real es si esto cambia la experiencia o si se siente como m\u00e1s de lo mismo."
    if accion == "avance":
        return "Cuando sale nuevo material, la comunidad mira detalles peque\u00f1os: jugabilidad, fecha, tono y si la expectativa se sostiene."
    if accion == "mecanica":
        return "Cuando una mec\u00e1nica cambia c\u00f3mo enfrentamos un juego, la conversaci\u00f3n se va r\u00e1pido a si mejora el reto o rompe la experiencia."
    if accion == "senal":
        return "Para la comunidad, la pregunta no es solo si viene algo nuevo, sino cu\u00e1nto vale emocionarse antes de una confirmaci\u00f3n fuerte."
    if accion == "preservacion":
        return "La preservaci\u00f3n importa porque muchos juegos pierden acceso con el tiempo, aunque sigan siendo parte de la memoria gamer."
    if accion == "industria":
        return "Este tipo de tema conviene hablarlo con calma, mirando el impacto real sin convertirlo en guerra de marcas."
    if categoria == "tecnologia":
        return "Lo mejor es bajarlo a tierra: si no mejora c\u00f3mo jugamos, creamos o usamos la tecnolog\u00eda, es solo ruido."
    if categoria == "indie":
        return "Los indies crecen mucho por recomendaci\u00f3n de comunidad, por eso el gancho debe explicar qu\u00e9 lo hace diferente."
    if categoria == "anime":
        return "Anime y gaming se cruzan cuando hay emoci\u00f3n, adaptaciones, fandoms comparando expectativas o teor\u00edas."
    if categoria == "nostalgia":
        return "La nostalgia pega m\u00e1s cuando se siente concreta: una consola, un control, un cartucho, un disco o una tarde jugando con panas."
    if categoria == "debate":
        return "La conversaci\u00f3n funciona mejor cuando presenta dos lados claros y deja que la comunidad cuente su experiencia."
    return "El valor est\u00e1 en conectar el dato con una pregunta que la comunidad realmente quiera contestar."


def pregunta_engagement(titulo, estilo="news"):
    accion = detectar_accion_titulo(titulo)
    categoria = _categoria_final_item({"title": titulo, "summary": ""}, estilo)
    if accion == "actualizacion":
        return "\U0001f447 \u00bfEsto te anima a volver o lo dejar\u00edas pasar?"
    if accion == "avance":
        return "\U0001f447 \u00bfEste avance te subi\u00f3 la emoci\u00f3n o necesitas ver m\u00e1s?"
    if accion == "mecanica":
        return "\U0001f447 \u00bfTe gusta cuando un juego cambia sus mec\u00e1nicas o prefieres lo cl\u00e1sico?"
    if accion == "senal":
        return "\U0001f447 \u00bfEsto te emociona o prefieres esperar confirmaci\u00f3n oficial?"
    if accion in ["lanzamiento", "preventa"]:
        return "\U0001f447 \u00bfLo pondr\u00edas en tu lista o esperar\u00edas m\u00e1s detalles?"
    if accion == "preservacion":
        return "\U0001f447 \u00bfQu\u00e9 cl\u00e1sico te gustar\u00eda ver mejor preservado?"
    if accion == "fisico_digital":
        return "\U0001f447 \u00bfT\u00fa prefieres juegos f\u00edsicos o digitales?"
    if categoria == "tecnologia":
        return "\U0001f447 \u00bfEsto te parece \u00fatil para gamers o puro ruido t\u00e9cnico?"
    if categoria == "anime":
        return "\U0001f447 \u00bfEste tema te emociona o prefieres esperar m\u00e1s informaci\u00f3n?"
    if categoria == "indie":
        return "\U0001f447 \u00bfLo pondr\u00edas en tu radar o esperas ver m\u00e1s jugabilidad primero?"
    if categoria == "nostalgia":
        return "\U0001f447 \u00bfQu\u00e9 recuerdo gamer te vino a la mente?"
    if categoria == "debate":
        return "\U0001f447 \u00bfT\u00fa c\u00f3mo lo ves: buena movida o mala decisi\u00f3n?"
    return "\U0001f447 \u00bfEsto te interesa o lo dejar\u00edas pasar?"


def limpiar_gramatica_post_final(texto):
    texto = limpiar_texto_publicable_final(texto)
    texto = texto.replace("Tecnolog\u00edA", "Tecnolog\u00eda").replace("TECNOLOG\u00edA", "TECNOLOG\u00cdA")
    texto = texto.replace("PUBLICACI\u00f3N", "PUBLICACI\u00d3N")
    texto = texto.replace("Busque y filtre", "Busqu\u00e9 y filtr\u00e9")
    texto = re.sub(r"\bdel ano\b", "del a\u00f1o", texto)
    texto = re.sub(r"\bano\b", "a\u00f1o", texto)
    texto = re.sub(r"[ \t]{2,}", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    lineas = []
    for linea in texto.splitlines():
        limpia = linea.rstrip()
        if limpia.startswith("?"):
            limpia = "\u00bf" + limpia[1:]
        if limpia.startswith("\u00bf") and not limpia.endswith("?"):
            limpia += "?"
        lineas.append(limpia)
    return "\n".join(lineas).strip()


def quitar_prefijos_editoriales(linea):
    texto = str(linea or "").strip()
    for patron in [
        r"^(t[i\u00ed]tulo|titulo)\s*:\s*",
        r"^(subt[i\u00ed]tulo|subtitulo)\s*:\s*",
        r"^(post|caption|publicaci[o\u00f3]n)\s*:\s*",
        r"^(cierre|pregunta|cta)\s*:\s*",
        r"^(hashtags)\s*:\s*",
    ]:
        texto = re.sub(patron, "", texto, flags=re.IGNORECASE).strip()
    return texto


def linea_no_publicable(linea):
    texto = limpiar_texto_publicable_final(linea).strip().lower()
    if not texto:
        return False
    prefijos = [
        "fuente:", "fuentes:", "link:", "fecha:", "confianza:", "id para feedback:",
        "referencia interna", "referencia usada", "sugerencia visual:", "prompt:",
        "acci\u00f3n:", "accion:", "verificaci\u00f3n:", "verificacion:", "nota interna:",
        "\u00e1ngulo recomendado:", "angulo recomendado:",
    ]
    return any(texto.startswith(prefijo) for prefijo in prefijos) or any(
        frase in texto for frase in FRASES_PLANTILLA_BLOQUEADAS
    )


def caption_necesita_regenerarse(texto, item=None, estilo="news"):
    item = item or {}
    texto_limpio = limpiar_texto_publicable_final(texto)
    bajo = texto_limpio.lower()
    if any(frase in bajo for frase in FRASES_PLANTILLA_BLOQUEADAS):
        return True
    categoria = _categoria_final_item(item, estilo)
    if categoria != "indie" and any(p in bajo for p in ["indies", "juegos independientes", "demos"]):
        return True
    if categoria not in ["nostalgia", "debate"] and any(p in bajo for p in ["juegos f\u00edsicos", "manual", "prestarlo", "cartucho"]):
        return True
    if categoria != "tecnologia" and any(p in bajo for p in ["ruido t\u00e9cnico", "cambio \u00fatil"]):
        return True
    cuerpo = "\n".join(linea for linea in texto_limpio.splitlines() if not linea.strip().startswith("#"))
    return parece_texto_ingles(cuerpo)


def limpiar_lineas_para_caption(texto):
    lineas = []
    for linea in limpiar_texto_publicable_final(texto).splitlines():
        if re.search(r"https?://|www\.", linea, flags=re.IGNORECASE):
            continue
        linea = quitar_prefijos_editoriales(linea).strip()
        if linea_no_publicable(linea):
            continue
        lineas.append(linea)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lineas)).strip()


def crear_hashtags(texto, limite=None):
    limite = limite or obtener_limite_hashtags()
    texto = limpiar_texto_publicable_final(texto).lower()
    brand = get_brand_voice().get("brand", "El Gamer Cave")
    tags = ["#davietgaming" if brand == "Daviet Gaming" else "#elgamercave"]
    reglas = [
        (["anime", "manga", "crunchyroll", "shonen", "otaku"], ["#anime", "#manga", "#otaku"]),
        (["nintendo", "switch", "mario", "zelda", "kirby", "pokemon", "pok\u00e9mon"], ["#nintendo", "#nintendoswitch"]),
        (["playstation", "ps5", "ps plus"], ["#playstation", "#ps5"]),
        (["xbox", "game pass"], ["#xbox", "#xboxseriesx"]),
        (["pc", "steam", "gpu", "nvidia", "amd", "intel", "hardware", "tecnologia", "tecnología"], ["#pcgaming", "#gamingtech"]),
        (["indie", "independent", "next fest"], ["#indiegames", "#indiegaming"]),
        (["retro", "nostalgia", "classic", "clasico", "cl\u00e1sico", "remake", "remaster", "gamecube", "game boy"], ["#nostalgia", "#retrogaming"]),
    ]
    for claves, nuevos in reglas:
        if any(clave in texto for clave in claves):
            tags.extend(nuevos)
    tags.extend(["#gaming", "#videojuegos", "#gamers", "#geekculture"])
    return limitar_hashtags_texto(" ".join(dict.fromkeys(tags)), limite)


def asegurar_hashtags_editoriales(texto, titulo_original="", resumen_original=""):
    cuerpo = [linea for linea in texto.strip().splitlines() if not linea.strip().startswith("#")]
    cuerpo_texto = "\n".join(cuerpo).strip()
    hashtags = crear_hashtags(f"{titulo_original} {resumen_original}", 5)
    return f"{cuerpo_texto}\n\n{hashtags}".strip()


def asegurar_pregunta_final(texto, titulo_original="", estilo="news"):
    lineas = texto.strip().splitlines()
    if not lineas:
        return texto
    hashtag_line = ""
    if lineas[-1].strip().startswith("#"):
        hashtag_line = lineas.pop().strip()
    cuerpo = "\n".join(lineas).strip()
    if "?" not in cuerpo and "\u00bf" not in cuerpo:
        cuerpo = f"{cuerpo}\n\n{pregunta_engagement(titulo_original or cuerpo, estilo)}"
    return f"{cuerpo}\n\n{hashtag_line}".strip() if hashtag_line else cuerpo


def limpiar_pedido_post(pregunta):
    texto = limpiar_texto_publicable_final(pregunta).lower()
    texto = quitar_marca_de_texto(texto)
    texto = re.sub(r"\b(daviet gaming|gamer cave|el gamer cave|gamer signal|instagram|facebook)\b", " ", texto)
    frases = [
        "hazme un post", "hazme una publicacion", "hazme una publicaci\u00f3n",
        "creame un post", "cr\u00e9ame un post", "crea un post", "crear un post",
        "dame un post", "dame una noticia", "post para", "caption para",
        "caption", "publicacion", "publicaci\u00f3n", "hazme", "creame",
        "cr\u00e9ame", "crear", "crea", "dame", "post", "noticia", "noticias",
        "actual", "reciente", "hot", "viral", "del dia", "del d\u00eda",
    ]
    for frase in sorted(frases, key=len, reverse=True):
        texto = texto.replace(frase, " ")
    texto = re.sub(r"\b(sobre|de|para|un|una|el|la|los|las)\b", " ", texto)
    limpio = " ".join(texto.split()).strip(" .,:;-")
    if limpio in {"", "tema", "algo", "nuevo", "nueva", "redes", "publicar"}:
        return ""
    return limpio


def crear_post_limpio(titulo, resumen, estilo, nostalgia="", hashtags=""):
    titulo_es = titulo_publico_en_espanol(titulo, estilo)
    resumen_es = resumen_publico_en_espanol(titulo, resumen, estilo)
    detalle = detalle_contextual_para_post(titulo, resumen or resumen_es, estilo)
    pregunta = pregunta_engagement(titulo, estilo)
    hashtags = limitar_hashtags_texto(hashtags or crear_hashtags(f"{titulo} {resumen}", 5), 5)
    partes = [f"\U0001f3ae {titulo_es}", resumen_es]
    if detalle and detalle.lower() not in resumen_es.lower():
        partes.append(detalle)
    if nostalgia and _estilo_a_categoria(estilo) in ["nostalgia", "debate"]:
        nostalgia = limpiar_texto_publicable_final(nostalgia)
        if nostalgia and nostalgia.lower() not in " ".join(partes).lower():
            partes.append(nostalgia)
    partes.extend([pregunta, hashtags])
    return limpiar_gramatica_post_final("\n\n".join(partes))


def aplicar_reglas_editoriales_fuertes(post, item=None, estilo="news"):
    item = item or {}
    titulo = limpiar_html(item.get("title", "Tema gamer"))
    resumen = limpiar_html(item.get("summary", ""))
    texto = limpiar_lineas_para_caption(post)
    if caption_necesita_regenerarse(texto, item, estilo):
        texto = crear_post_limpio(
            titulo,
            resumen,
            estilo,
            item.get("nostalgia_angle", ""),
            crear_hashtags(f"{titulo} {resumen}", 5),
        )
        texto = limpiar_lineas_para_caption(texto)
    texto = asegurar_hashtags_editoriales(texto, titulo, resumen)
    texto = asegurar_pregunta_final(texto, titulo, estilo)
    return limpiar_gramatica_post_final(texto)


def generate_social_post(item, estilo=None):
    item = dict(item or {})
    categoria = _categoria_final_item(item)
    estilo = estilo or st.session_state.get("post_style", "all")
    if estilo == "all":
        estilo = {
            "gaming": "news",
            "tecnologia": "tecnologia",
            "anime": "anime",
            "indie": "indie",
            "debate": "debate",
            "nostalgia": "nostalgia",
        }.get(categoria, "news")
    estilo = estilo_seguro_para_item(item, estilo)
    titulo = limpiar_html(item.get("title", "Tema gamer"))
    resumen = limpiar_html(item.get("summary", ""))
    item["content_angle"] = categoria if categoria != "gaming" else "news"
    item["nostalgia_angle"] = detectar_angulo_nostalgia(item)
    if item.get("id"):
        st.session_state.generated_items[item["id"]] = dict(item)
        st.session_state.last_item_id = item["id"]
    post = crear_post_limpio(titulo, resumen, estilo, item.get("nostalgia_angle", ""), crear_hashtags(f"{titulo} {resumen}", 5))
    post = aplicar_reglas_editoriales_fuertes(post, item, estilo)
    st.session_state.last_post_text = post
    st.session_state.last_post_title = titulo_publico_en_espanol(titulo, estilo)
    return post


def categorias_para_posts(cantidad, texto):
    texto = limpiar_texto_publicable_final(texto).lower()
    if "anime" in texto and cantidad <= 2:
        base = ["anime", "gaming", "debate", "nostalgia", "tecnologia", "indie"]
    elif "tecnologia" in texto or "tecnolog\u00eda" in texto:
        base = ["tecnologia", "gaming", "anime", "debate", "nostalgia", "indie"]
    elif "nostalgia" in texto or "retro" in texto:
        base = ["nostalgia", "gaming", "anime", "debate", "tecnologia", "indie"]
    elif "debate" in texto:
        base = ["debate", "gaming", "anime", "tecnologia", "nostalgia", "indie"]
    else:
        base = ["gaming", "anime", "tecnologia", "indie", "debate", "nostalgia"]
    salida = []
    while len(salida) < cantidad:
        salida.extend(base)
    return salida[:cantidad]


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


def seleccionar_noticias_variadas(noticias, cantidad, texto_usuario=""):
    cantidad = max(1, min(cantidad, 8))
    exclusiones = detectar_exclusiones_usuario(texto_usuario)
    disponibles = [
        dict(item) for item in filtrar_noticias_verificadas(noticias)
        if item_cumple_exclusiones(item, exclusiones)
    ]
    disponibles.sort(key=lambda item: str(item.get("date", "")), reverse=True)
    seleccionadas = []
    titulos_usados = set()
    fuentes_usadas = {}
    plataformas_usadas = {}

    def puede_usarse(item):
        titulo = limpiar_texto_publicable_final(item.get("title", ""))
        key = titulo.lower()
        if not key or key in titulos_usados:
            return False
        if tema_repetido(titulo) or tema_muy_similar(titulo):
            return False
        fuente = item.get("source", "")
        plataforma = plataforma_de_item(item)
        if cantidad >= 4 and fuentes_usadas.get(fuente, 0) >= 1:
            return False
        if cantidad >= 4 and plataforma != "general" and plataformas_usadas.get(plataforma, 0) >= 1:
            return False
        return True

    def agregar(item):
        titulo = limpiar_texto_publicable_final(item.get("title", ""))
        fuente = item.get("source", "")
        plataforma = plataforma_de_item(item)
        titulos_usados.add(titulo.lower())
        fuentes_usadas[fuente] = fuentes_usadas.get(fuente, 0) + 1
        plataformas_usadas[plataforma] = plataformas_usadas.get(plataforma, 0) + 1
        seleccionadas.append(dict(item))

    for categoria in categorias_para_posts(cantidad, texto_usuario or ""):
        for item in disponibles:
            if puede_usarse(item) and _categoria_final_item(item) == categoria:
                agregar(item)
                break
        if len(seleccionadas) >= cantidad:
            break

    for item in disponibles:
        if len(seleccionadas) >= cantidad:
            break
        if puede_usarse(item):
            agregar(item)
    return seleccionadas[:cantidad]


def crear_item_editorial_categoria(categoria, titulos_usados):
    temas_por_categoria = {
        "gaming": ["lanzamientos que dividen a la comunidad", "juegos que vuelven al radar", "actualidad gamer para comentar"],
        "anime": ["anime de temporada que mueve conversaci\u00f3n", "manga y anime que cruzan con cultura gamer", "adaptaciones que el fandom mira con cuidado"],
        "tecnologia": ["tecnolog\u00eda que s\u00ed cambia la experiencia gamer", "hardware y servicios que afectan c\u00f3mo jugamos", "IA y herramientas dentro del gaming"],
        "indie": ["indies con propuestas diferentes", "demos que pueden crecer por recomendaci\u00f3n", "juegos peque\u00f1os que merecen radar"],
        "debate": TEMAS_COMUNIDAD,
        "nostalgia": TEMAS_NOSTALGIA,
    }
    temas = temas_por_categoria.get(categoria, temas_por_categoria["gaming"])
    titulo = next((tema for tema in temas if tema.lower() not in titulos_usados), temas[0])
    titulos_usados.add(titulo.lower())
    resumenes = {
        "gaming": "Tema editorial gamer para comentar lanzamientos, actualidad u opinión sin presentarlo como noticia confirmada.",
        "anime": "Tema editorial anime/geek para abrir conversación de fandom sin presentarlo como noticia confirmada.",
        "tecnologia": "Tema editorial de tecnología gamer para hablar de experiencia, acceso, rendimiento o servicios.",
        "indie": "Tema editorial indie para descubrir propuestas pequeñas sin presentarlas como tendencia confirmada.",
        "debate": "Tema editorial de debate para presentar dos lados sin convertirlo en pelea de plataformas.",
        "nostalgia": "Tema editorial nostálgico para conectar recuerdos concretos de consolas, juegos y comunidad.",
    }
    resumen = resumenes.get(categoria, resumenes["gaming"])
    item = {
        "id": str(uuid.uuid4()),
        "title": limpiar_texto_publicable_final(titulo),
        "summary": resumen,
        "source": "Tema editorial Gamer Signal",
        "link": "",
        "date": str(ahora_en_puerto_rico().date()),
        "source_official": False,
        "source_trusted": False,
        "content_angle": categoria,
        "editorial_category": categoria,
        "nostalgia_angle": detectar_angulo_nostalgia({"title": titulo, "summary": resumen}),
        "confidence_level": "editorial",
        "verification_count": 0,
        "verification_sources": [],
        "verification_level": "idea editorial / no es noticia confirmada",
    }
    st.session_state.generated_items[item["id"]] = item
    st.session_state.last_item_id = item["id"]
    return item


def crear_varios_posts(cantidad, pregunta):
    cantidad = max(2, min(cantidad, 8))
    texto = limpiar_texto_publicable_final(pregunta).lower()
    noticias = seleccionar_noticias_variadas(buscar_noticias(), min(cantidad * 2, 8), texto)
    categorias = categorias_para_posts(cantidad, texto)
    usados = set()
    titulos_editoriales = set()
    posts = []
    items_generados = []
    st.session_state.news_by_number = {}

    for indice, categoria_objetivo in enumerate(categorias, start=1):
        item = None
        for candidato in noticias:
            key = candidato.get("id") or candidato.get("title", "")
            if key in usados:
                continue
            if _categoria_final_item(candidato) == categoria_objetivo:
                item = dict(candidato)
                break
        if not item:
            item = crear_item_editorial_categoria(categoria_objetivo, titulos_editoriales)

        key = item.get("id") or item.get("title", "")
        usados.add(key)
        categoria_real = _categoria_final_item(item, categoria_objetivo)
        estilo = {
            "gaming": "news",
            "tecnologia": "tecnologia",
            "anime": "anime",
            "indie": "indie",
            "debate": "debate",
            "nostalgia": "nostalgia",
        }.get(categoria_real, "news")
        st.session_state.generated_items[item["id"]] = dict(item)
        st.session_state.news_by_number[indice] = dict(item)
        st.session_state.last_item_id = item["id"]
        items_generados.append(dict(item))
        etiqueta = etiqueta_publicacion_limpia(categoria_real)
        if item_es_contexto_editorial(item):
            etiqueta = f"{etiqueta}/Editorial"
        posts.append(f"PUBLICACI\u00d3N {indice} - {etiqueta.upper()}\n\n{generate_social_post(item, estilo)}")

    respuesta = "\n\n---\n\n".join(posts)
    st.session_state.last_post_text = respuesta
    st.session_state.last_post_title = f"{cantidad}_posts_gamer_signal"
    st.session_state.last_post_items = items_generados
    return limpiar_gramatica_post_final(respuesta)


def estado_verificacion_item(item):
    item = item or {}
    fuente = str(item.get("source", "")).lower()
    confianza = str(item.get("confidence_level", "")).lower()
    nivel = str(item.get("verification_level", "")).lower()
    if item.get("source_official") or "oficial" in fuente:
        return ("Verde", "fuente oficial")
    if item.get("verification_count", 0) >= 2 or "verificada" in nivel:
        return ("Verde", "verificada por varias fuentes")
    if item.get("source_trusted") or "confiable" in fuente or confianza in ["medium-high", "trusted"]:
        return ("Amarillo", "fuente confiable; revisar contexto antes de publicarla como noticia fuerte")
    if item.get("is_community_signal"):
        return ("Amarillo", "se\u00f1al de comunidad; usar como debate o nostalgia")
    return ("Rojo", "no usar como noticia confirmada")


def formatear_noticias(noticias, texto_usuario="", cantidad=5):
    cantidad = max(1, min(cantidad, 8))
    noticias = seleccionar_noticias_variadas(noticias, cantidad, texto_usuario)
    if not noticias:
        return (
            f"No encontr\u00e9 noticias verificadas nuevas del a\u00f1o {ANIO_NOTICIAS} con ese filtro.\n\n"
            "Puedo crear contenido editorial de debate o nostalgia, pero no lo presentar\u00e9 como noticia confirmada."
        )
    st.session_state.news_by_number = {}
    respuesta = f"Busqu\u00e9 y filtr\u00e9 noticias verificadas del a\u00f1o {ANIO_NOTICIAS}.\n\n"
    respuesta += f"Rango usado: {FECHA_INICIO} hasta {FECHA_FINAL}\n\n"
    for numero, item in enumerate(noticias, start=1):
        item = dict(item)
        categoria = _categoria_final_item(item)
        st.session_state.generated_items[item["id"]] = item
        st.session_state.news_by_number[numero] = item
        st.session_state.last_item_id = item["id"]
        titulo = titulo_visible_seguro(item, categoria)
        estado, detalle = estado_verificacion_item(item)
        resumen = resumen_publico_en_espanol(item.get("title", ""), item.get("summary", ""), categoria)
        respuesta += f"### Noticia {numero}: {titulo}\n\n"
        respuesta += f"**Fecha:** {item.get('date', '')}\n\n"
        respuesta += f"**Fuente:** {item.get('source', 'fuente')}\n\n"
        respuesta += f"**Estado:** {estado} - {detalle}\n\n"
        respuesta += f"{resumen}\n\n"
        respuesta += f"Para usarla: **post de la noticia {numero}**\n\n---\n\n"
    return limpiar_gramatica_post_final(respuesta)


def crear_opciones_post_recientes():
    noticias = seleccionar_noticias_variadas(buscar_noticias(), 5, "opciones de post variadas")
    st.session_state.news_by_number = {}
    if not noticias:
        return "No encontr\u00e9 opciones verificadas nuevas ahora mismo. Puedes pedirme un post de nostalgia o debate editorial."
    respuesta = "### Opciones de post recientes\n\n"
    for numero, item in enumerate(noticias, start=1):
        categoria = _categoria_final_item(item)
        st.session_state.generated_items[item["id"]] = dict(item)
        st.session_state.news_by_number[numero] = dict(item)
        st.session_state.last_item_id = item["id"]
        respuesta += f"**{numero}. {titulo_visible_seguro(item, categoria)}**\n\n"
        respuesta += f"- Categor\u00eda: {etiqueta_publicacion_limpia(categoria)}\n"
        respuesta += f"- Fuente: {item.get('source', '')}\n"
        respuesta += f"- Para usarla: **post de la noticia {numero}**\n\n"
    return limpiar_gramatica_post_final(respuesta)


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
            titulo = html_escape(limpiar_para_ui(titulo_visible_seguro(item, "news")))
            fuente = html_escape(limpiar_para_ui(item.get("source", "fuente")))
            color, verificacion = estado_verificacion_item(item)
            color = limpiar_para_ui(color)
            verificacion = limpiar_para_ui(verificacion)
            angulo = html_escape(limpiar_para_ui(item.get("angle", fallback)))
            contenido = (
                f'<div class="daily-radar-item"><strong>{titulo}</strong><br>{fuente}</div>'
                f'<div class="daily-radar-angle">Verificaci\u00f3n: {html_escape(color)} - {html_escape(verificacion)}</div>'
                f'<div class="daily-radar-angle">{angulo}</div>'
            )
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
            titulo = html_escape(limpiar_para_ui(titulo_visible_seguro(item, "news", bucket)))
            fuente = html_escape(limpiar_para_ui(item.get("source", "fuente")))
            color, verificacion = estado_verificacion_item(item)
            color = limpiar_para_ui(color)
            verificacion = limpiar_para_ui(verificacion)
            contenido = (
                f'<div class="daily-radar-item"><strong>{titulo}</strong><br>{fuente}</div>'
                f'<div class="daily-radar-angle">Verificaci\u00f3n: {html_escape(color)} - {html_escape(verificacion)}</div>'
                f'<div class="daily-radar-angle">{html_escape(limpiar_para_ui(angulo_para_bucket(bucket)))}</div>'
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
