# -*- coding: utf-8 -*-
"""Motor editorial final de Gamer Signal.

Este modulo instala una capa final sobre app.py sin depender de APIs de IA.
La regla principal es no crear parches por franquicia o titular especifico:
todo sale de senales, categorias, acciones, facts procesados y QA.
"""

from __future__ import annotations

import re
import uuid
from datetime import date
from difflib import SequenceMatcher
from html import unescape as html_unescape


MAIN_CATEGORIES = [
    "gaming",
    "tecnologia",
    "game_development",
    "anime",
    "geek",
    "industria",
    "indie",
]

FILLER_PHRASES = [
    "lo importante es explicar",
    "lo interesante es mirar",
    "tema reciente dentro del mundo gamer",
    "puede servir para descubrir algo fuera",
    "el feed no trae suficiente detalle",
    "conviene usarlo como punto de entrada",
    "la clave es explicar",
    "este tipo de tema conecta con la comunidad porque cada gamer",
    "que conversacion puede abrir",
    "qué conversación puede abrir",
    "qué pregunta puede mover comentarios reales",
    "que pregunta puede mover comentarios reales",
    "noticia para comentar es un tema",
    "la clave es bajarlo a tierra",
    "lo importante es aterrizarlo a la comunidad",
    "aparece como señal reciente",
]

ENGLISH_WORDS = {
    "the", "and", "with", "for", "from", "this", "that", "into", "after",
    "before", "players", "player", "update", "patch", "available", "today",
    "coming", "launch", "launches", "release", "date", "details", "announced",
    "revealed", "reveals", "unveils", "trailer", "teaser", "could", "will",
    "joins", "following", "physical", "digital", "workers", "layoffs", "ends",
    "concludes", "gets", "getting", "hands", "deep", "dive", "first", "ever",
    "mass", "refutes", "behind", "powerful", "friends", "bosses", "drown",
    "mythics", "news", "new", "gameplay", "mechanic", "changes", "rewards",
    "progression", "classic", "stealth", "part", "program", "fans", "may",
    "information", "soon", "tough", "conversation", "about", "changing",
    "retail", "strategies", "games", "game", "adds", "drops", "arrives",
    "delayed", "delay", "preorder", "pre-order", "open", "beta", "public",
}

ACTION_PATTERNS = [
    ("cierre", r"\b(concludes|ends|final chapter|termina|finaliza|cierra|serialization|serializacion|serialización)\b"),
    ("adaptacion", r"\b(getting an anime|anime adaptation|adaptacion al anime|adaptación al anime)\b"),
    ("avance", r"\b(trailer|teaser|new visual|visual|gameplay|hands[- ]on|preview|avance|trailer|tráiler)\b"),
    ("actualizacion", r"\b(update|patch|version|temporada|season|actualizacion|actualización|new details|nuevos detalles)\b"),
    ("preventa", r"\b(pre[- ]?order|preventa|reserva)\b"),
    ("lanzamiento", r"\b(release date|launch|launches|coming soon|coming in|llega|lanzamiento|estreno)\b"),
    ("senal", r"\b(could come|news could|sooner than|may get|might get|podria|podría|rumor|leak)\b"),
    ("preservacion", r"\b(preservation|preservacion|preservación|classic|clasico|clásico|collection|remaster|remake)\b"),
    ("industria", r"\b(layoff|layoffs|despidos|workers|fired|visas|studio closes|acquisition|adquisicion|adquisición|industria)\b"),
    ("fisico_digital", r"\b(physical|digital|fisico|fisicos|físico|físicos|cartucho|disco|manual|ownership|propiedad)\b"),
    ("tecnologia", r"\b(gpu|rtx|nvidia|amd|intel|hardware|ios|macos|apple|ram|cloud|unreal engine|godot|unity|engine)\b"),
    ("mecanica", r"\b(turns tough|bosses|powerful friends|mechanic|mecanica|mecánica|builds|system)\b"),
]

CATEGORY_SIGNALS = {
    "anime": [
        "anime", "manga", "shonen", "shojo", "otaku", "crunchyroll",
        "myanimelist", "anime corner", "serialization", "serializacion",
        "serialización", "temporada anime",
    ],
    "tecnologia": [
        "gpu", "rtx", "nvidia", "amd", "intel", "hardware", "ios", "macos",
        "apple", "ram", "cloud gaming", "steam deck", "tecnologia", "tecnología",
        "driver", "performance", "rendimiento", "pc gaming",
    ],
    "game_development": [
        "unreal engine", "unity", "godot", "developer", "desarrollador",
        "devlog", "sdk", "engine", "programacion", "programación", "toolkit",
        "modding", "mods",
    ],
    "indie": [
        "indie", "independent", "independiente", "steam next fest", "next fest",
        "demo", "early access", "solo developer", "small team",
    ],
    "industria": [
        "layoff", "layoffs", "despidos", "workers", "visas", "studio closes",
        "acquisition", "adquisicion", "adquisición", "merger", "lawsuit",
        "demanda", "union", "sindicato", "industry", "industria",
    ],
    "geek": [
        "movie", "pelicula", "película", "series", "comic", "cómic", "dc",
        "marvel", "star wars", "collectible", "cosplay", "figure", "figura",
        "cultura geek",
    ],
    "gaming": [
        "game", "juego", "playstation", "xbox", "nintendo", "switch", "ps5",
        "steam", "game pass", "dlc", "update", "patch", "trailer", "gameplay",
        "release", "launch", "console", "consola",
    ],
}


def install_editorial_engine(g):
    """Instala/override las funciones editoriales finales dentro de app.py."""

    st = g["st"]

    def call(name, default=None):
        return g.get(name, default)

    def _mojibake_score(texto):
        texto = str(texto or "")
        return sum(texto.count(marca) for marca in ["Ã", "Â", "â", "ð", "�", "?"])

    def reparar_texto_roto(texto):
        if texto is None:
            return ""
        texto = str(texto)
        mejor = texto
        for _ in range(3):
            if not any(marca in mejor for marca in ["Ã", "Â", "â", "ð"]):
                break
            try:
                candidato = mejor.encode("latin1", errors="strict").decode("utf-8", errors="strict")
            except (UnicodeEncodeError, UnicodeDecodeError):
                break
            if _mojibake_score(candidato) > _mojibake_score(mejor):
                break
            mejor = candidato
        reemplazos = {
            "PUBLICACI?N": "PUBLICACIÓN",
            "TECNOLOG?A": "TECNOLOGÍA",
            "Preg?ntame": "Pregúntame",
            "cu?l": "cuál",
            "Cu?l": "Cuál",
            "qu?": "qué",
            "Qu?": "Qué",
            "c?mo": "cómo",
            "C?mo": "Cómo",
            "t?": "tú",
            "m?s": "más",
            "est?": "está",
            "est?n": "están",
            "todav?a": "todavía",
            "f?sico": "físico",
            "f?sicos": "físicos",
            "cl?sico": "clásico",
            "cl?sicos": "clásicos",
            "nost?lgico": "nostálgico",
            "nost?lgica": "nostálgica",
            "se?al": "señal",
            "informaci?n": "información",
            "conversaci?n": "conversación",
            "publicaci?n": "publicación",
            "adaptaci?n": "adaptación",
            "serializaci?n": "serialización",
            "tecnolog?a": "tecnología",
            "Tecnolog?a": "Tecnología",
            "opini?n": "opinión",
            "Acci?n": "Acción",
            "guard?": "guardé",
            "â˜°": "☰",
            "â€™": "'",
            "â€˜": "'",
            "â€œ": '"',
            "â€�": '"',
            "â€“": "-",
            "â€”": "-",
            "â€¦": "...",
        }
        for malo, bueno in reemplazos.items():
            mejor = mejor.replace(malo, bueno)
        mejor = re.sub(r"\bdel ano\b", "del año", mejor, flags=re.IGNORECASE)
        mejor = re.sub(r"\bano\b", "año", mejor, flags=re.IGNORECASE)
        return mejor.replace("�", "").strip()

    def limpiar_texto_publicable_final(texto):
        base = reparar_texto_roto(texto)
        if "<" in base and ">" in base:
            limpiar_html = call("limpiar_html")
            if limpiar_html:
                try:
                    base = limpiar_html(base)
                except Exception:
                    base = re.sub(r"<[^>]+>", " ", base)
            else:
                base = re.sub(r"<[^>]+>", " ", base)
        base = html_unescape(base)
        base = reparar_texto_roto(base)
        base = re.sub(r"https?://\S+|www\.\S+", "", base)
        base = re.sub(r"\bThe post\b.*?\bappeared first on\b.*?(?:\.|\n|$)", "", base, flags=re.IGNORECASE | re.DOTALL)
        base = re.sub(r"\bappeared first on\b.*?(?:\.|\n|$)", "", base, flags=re.IGNORECASE | re.DOTALL)
        base = re.sub(r"\bfisicos\b", "físicos", base, flags=re.IGNORECASE)
        base = re.sub(r"\bfisico\b", "físico", base, flags=re.IGNORECASE)
        base = base.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
        base = base.replace("–", "-").replace("—", "-")
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
            "a conversation about", "changing retail strategies", "will ", " could ",
            " is ", " are ", " with ", " after ", " following ",
        ]
        if any(frase in bajo for frase in frases):
            return True
        tokens = re.findall(r"[a-z][a-z'-]+", bajo)
        hits = sum(1 for token in tokens if token in ENGLISH_WORDS)
        return hits >= 3 or ("'s" in bajo and hits >= 1)

    def _event_text(item):
        item = item or {}
        return limpiar_texto_publicable_final(
            f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}"
        )

    def _signal_count(texto, palabras):
        bajo = limpiar_texto_publicable_final(texto).lower()
        total = 0
        for palabra in palabras:
            p = palabra.lower()
            if " " in p:
                total += 2 if p in bajo else 0
            elif re.search(rf"\b{re.escape(p)}\b", bajo):
                total += 1
        return total

    def normalizar_evento(item):
        item = dict(item or {})
        titulo = limpiar_texto_publicable_final(item.get("title", "Tema gamer"))
        resumen = limpiar_texto_publicable_final(item.get("summary", ""))
        fuente = limpiar_texto_publicable_final(item.get("source", "Fuente"))
        fecha = limpiar_texto_publicable_final(item.get("date", ""))
        link = str(item.get("link", "") or "").strip()
        evento = {
            "id": item.get("id") or str(uuid.uuid5(uuid.NAMESPACE_URL, f"{fuente}|{link}|{titulo}|{fecha}")),
            "title": titulo,
            "summary": resumen,
            "source": fuente,
            "date": fecha,
            "link": link,
            "source_official": bool(item.get("source_official")) or "oficial" in fuente.lower(),
            "source_trusted": bool(item.get("source_trusted")),
            "is_community_signal": bool(item.get("is_community_signal")),
            "raw": item,
        }
        evento["text"] = _event_text(evento)
        return evento

    def crear_fact_sheet(item):
        evento = normalizar_evento(item)
        fecha_publicacion = evento.get("date") or ""
        fecha_evento = ""
        fecha_evento_verificada = False
        match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", f"{evento['title']} {evento['summary']}")
        if match:
            fecha_evento = match.group(1)
            fecha_evento_verificada = True
        elif fecha_publicacion:
            fecha_evento = fecha_publicacion
        recortar = call("recortar_texto", lambda t, n: str(t)[:n])
        facts = [f"Título procesado: {evento['title']}", f"Fuente procesada: {evento['source']}"]
        if fecha_publicacion:
            facts.append(f"Fecha de publicación RSS: {fecha_publicacion}")
        if evento["summary"]:
            facts.append(f"Resumen disponible: {recortar(evento['summary'], 220)}")
        return {
            "event": evento,
            "facts": facts,
            "publication_date": fecha_publicacion,
            "event_date": fecha_evento,
            "event_date_verified": fecha_evento_verificada,
            "sufficient_detail": len(evento["summary"]) >= 45,
            "processed_fields": ["title", "summary", "source", "date", "link"],
        }

    def detectar_accion_titulo(titulo, resumen=""):
        texto = limpiar_texto_publicable_final(f"{titulo} {resumen}").lower()
        for accion, patron in ACTION_PATTERNS:
            if re.search(patron, texto, flags=re.IGNORECASE):
                return accion
        return "noticia"

    def item_es_contexto_editorial(item):
        item = item or {}
        fuente = str(item.get("source", "")).lower()
        return (
            bool(item.get("is_editorial"))
            or "tema editorial" in fuente
            or "contexto" in fuente
            or str(item.get("confidence_level", "")).lower() == "editorial"
        )

    def clasificar_evento(item):
        evento = normalizar_evento(item)
        texto = evento["text"].lower()
        scores = {categoria: 0 for categoria in MAIN_CATEGORIES}
        for categoria, palabras in CATEGORY_SIGNALS.items():
            scores[categoria] += _signal_count(texto, palabras)
        if not any(scores.values()):
            scores["gaming"] = 1
        source = evento["source"].lower()
        if "anime" in source or "myanimelist" in source or "crunchyroll" in source:
            scores["anime"] += 4
        if "xbox" in source or "playstation" in source or "nintendo" in source or "gog" in source:
            scores["gaming"] += 3
        main = max(scores, key=scores.get)
        secondary = [
            categoria for categoria, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
            if categoria != main and score > 0
        ][:3]
        accion = detectar_accion_titulo(evento["title"], evento["summary"])
        formatos = []
        if accion in ["industria", "fisico_digital", "senal"]:
            formatos.append("debate")
        if accion == "preservacion" or _signal_count(texto, ["retro", "nostalgia", "classic", "clásico", "remake", "remaster", "gamecube", "game boy", "ps1", "ps2", "cartucho", "manual"]):
            formatos.append("nostalgia")
        if evento.get("is_community_signal"):
            formatos.append("opinion")
        if not formatos:
            formatos.append("news")
        return {
            "main_category": main,
            "secondary_categories": secondary,
            "editorial_formats": list(dict.fromkeys(formatos)),
            "action": accion,
            "category_scores": scores,
        }

    def _estilo_a_categoria_seguro(estilo):
        fn = call("_estilo_a_categoria")
        if fn:
            return fn(estilo)
        mapa = {"hardware": "tecnologia", "technology": "tecnologia", "noticia": "gaming", "news": "gaming"}
        return mapa.get(str(estilo or "").lower(), str(estilo or "").lower())

    def _categoria_final_item(item, preferida=None):
        item = item or {}
        preferida_cat = _estilo_a_categoria_seguro(preferida)
        if item_es_contexto_editorial(item):
            explicita = _estilo_a_categoria_seguro(item.get("editorial_category") or item.get("content_angle"))
            if explicita in ["gaming", "tecnologia", "anime", "indie", "debate", "nostalgia"]:
                return explicita
            if preferida_cat in ["gaming", "tecnologia", "anime", "indie", "debate", "nostalgia"]:
                return preferida_cat
        main = clasificar_evento(item)["main_category"]
        if main == "game_development":
            return "tecnologia"
        if main == "geek":
            texto = _event_text(item).lower()
            return "anime" if "anime" in texto or "manga" in texto else "gaming"
        if main == "industria":
            return "debate"
        return main if main in ["gaming", "tecnologia", "anime", "indie"] else "gaming"

    def categoria_de_item(item):
        return _categoria_final_item(item)

    def detectar_content_angle(item):
        clasificacion = clasificar_evento(item)
        if "nostalgia" in clasificacion["editorial_formats"]:
            return "nostalgia"
        if "debate" in clasificacion["editorial_formats"]:
            return "debate"
        categoria = _categoria_final_item(item)
        return "technology" if categoria == "tecnologia" else categoria

    def _normalizar_para_similitud(texto):
        texto = limpiar_texto_publicable_final(texto).lower()
        texto = re.sub(r"[^a-záéíóúñ0-9 ]+", " ", texto)
        stop = {"the", "a", "an", "of", "and", "para", "con", "sobre", "noticia", "post", "nuevo", "nueva", "gamer"}
        return " ".join(t for t in texto.split() if t not in stop)

    def _similitud_texto(a, b):
        a = _normalizar_para_similitud(a)
        b = _normalizar_para_similitud(b)
        if not a or not b:
            return 0.0
        set_a = set(a.split())
        set_b = set(b.split())
        jaccard = len(set_a & set_b) / max(1, len(set_a | set_b))
        return max(jaccard, SequenceMatcher(None, a, b).ratio())

    def _used_entries():
        try:
            return call("leer_json")(g["USED_FILE"], [])
        except Exception:
            return []

    def entrada_usada_aplica_a_marca(item, marca=None):
        marcas = item.get("brands") if isinstance(item, dict) else None
        if not marcas:
            return True
        if not isinstance(marcas, list):
            marcas = [str(marcas)]
        if marca:
            return marca in marcas or "ambas" in [m.lower() for m in marcas]
        return True

    def tema_repetido(topic, marca=None):
        topic_key = _normalizar_para_similitud(topic)
        if not topic_key:
            return False
        for item in _used_entries():
            if not entrada_usada_aplica_a_marca(item, marca):
                continue
            usado = _normalizar_para_similitud(item.get("topic", ""))
            if usado and (topic_key == usado or _similitud_texto(topic_key, usado) >= 0.82):
                return True
        return False

    def tema_muy_similar(topic, threshold=0.58, marca=None):
        topic_key = _normalizar_para_similitud(topic)
        if not topic_key:
            return False
        for item in _used_entries():
            if not entrada_usada_aplica_a_marca(item, marca):
                continue
            usado = _normalizar_para_similitud(item.get("topic", ""))
            if usado and _similitud_texto(topic_key, usado) >= threshold:
                return True
        return False

    def calcular_score_multidimensional(item):
        evento = normalizar_evento(item)
        clasificacion = clasificar_evento(item)
        texto = evento["text"].lower()
        score = {
            "gaming_relevance": min(10, clasificacion["category_scores"].get("gaming", 0) + 2),
            "tech_relevance": min(10, clasificacion["category_scores"].get("tecnologia", 0) + clasificacion["category_scores"].get("game_development", 0)),
            "debate_potential": 3,
            "geek_potential": min(10, clasificacion["category_scores"].get("anime", 0) + clasificacion["category_scores"].get("geek", 0)),
            "interaction_potential": 4,
            "novelty": 5,
            "source_reliability": 3,
            "similarity_penalty": 0,
        }
        if any(p in texto for p in ["precio", "price", "digital", "physical", "fisico", "físico", "despidos", "layoffs", "rumor", "delay", "retraso"]):
            score["debate_potential"] += 4
            score["interaction_potential"] += 2
        if any(p in texto for p in ["nostalgia", "retro", "classic", "clásico", "remake", "remaster", "preservation"]):
            score["interaction_potential"] += 2
        if evento["source_official"]:
            score["source_reliability"] = 10
        elif evento["source_trusted"]:
            score["source_reliability"] = 7
        elif evento["is_community_signal"]:
            score["source_reliability"] = 2
        try:
            ahora_en_puerto_rico = call("ahora_en_puerto_rico")
            fecha = date.fromisoformat(str(evento.get("date", ""))[:10])
            dias = max(0, (ahora_en_puerto_rico().date() - fecha).days) if ahora_en_puerto_rico else 3
            score["novelty"] = 10 if dias <= 1 else 8 if dias <= 3 else 6 if dias <= 10 else 3
        except Exception:
            score["novelty"] = 4
        if tema_repetido(evento["title"]) or tema_muy_similar(evento["title"]):
            score["similarity_penalty"] = 10
        for key in list(score):
            score[key] = max(0, min(10, int(score[key])))
        score["final_score"] = (
            score["gaming_relevance"]
            + score["tech_relevance"]
            + score["debate_potential"]
            + score["geek_potential"]
            + score["interaction_potential"]
            + score["novelty"]
            + score["source_reliability"]
            - score["similarity_penalty"]
        )
        return score

    def _limpiar_tema_titulo(tema):
        tema = limpiar_texto_publicable_final(tema)
        tema = re.sub(r"^(manga|anime|game|juego|review|preview|pre[- ]?order)\s+", "", tema, flags=re.IGNORECASE)
        tema = re.sub(r"\s+(manga|anime|game|juego|news|update|patch|trailer|teaser)$", "", tema, flags=re.IGNORECASE)
        tema = tema.strip(" -:.,'\"")
        normalizar = call("normalizar_titulo_gamer", lambda x: x)
        return normalizar(tema) if tema else "Tema gamer"

    def extraer_tema_para_titulo(titulo):
        limpio = limpiar_texto_publicable_final(titulo)
        if not limpio:
            return "Tema gamer"
        for patron in [
            r"(?:manga|anime)\s+'([^']{2,90})'",
            r'(?:manga|anime)\s+"([^"]{2,90})"',
            r"'([^']{2,90})'",
            r'"([^"]{2,90})"',
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
            " report", " details", " builds ", " goes ", " adds ", " opens ",
        ]
        for sep in separadores_accion:
            idx = bajo.find(sep)
            if idx > 1:
                return _limpiar_tema_titulo(limpio[:idx])
        if ": " in limpio:
            first, second = limpio.split(": ", 1)
            if first.lower() in ["pre-order", "preorder", "review", "preview", "xbox", "playstation", "nintendo"]:
                return _limpiar_tema_titulo(second[:80])
        for sep in [" - ", " | "]:
            if sep in limpio:
                parte = limpio.split(sep, 1)[0]
                if 2 <= len(parte.strip()) <= 90:
                    return _limpiar_tema_titulo(parte)
        return _limpiar_tema_titulo(limpio[:85])

    def _tema_parece_titulo_propio(tema):
        tema = limpiar_texto_publicable_final(tema)
        tokens = re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ0-9']+", tema)
        if not tokens or len(tokens) > 8:
            return False
        mayus = sum(1 for token in tokens if token[:1].isupper() or re.search(r"\d", token))
        return mayus >= max(1, len(tokens) // 2)

    def titulo_generico_o_pobre(titulo):
        titulo = limpiar_texto_publicable_final(titulo).strip()
        bajo = titulo.lower()
        if len(titulo) < 8:
            return True
        patrones = [
            r"^(xbox|playstation|nintendo|pc|gaming|anime|manga):?\s*(noticia|novedad|tema)\s+para\s+(comentar|la comunidad)",
            r"^(xbox|playstation|nintendo|pc):?\s*novedad\s+para\s+la\s+comunidad\s+gamer$",
            r"^juegos incluidos este mes para comentar$",
            r"^tema gamer para comentar$",
            r"^noticia gamer para comentar$",
            r"^novedad gamer$",
        ]
        if any(re.search(patron, bajo) for patron in patrones):
            return True
        palabras_reales = [
            p for p in re.findall(r"[a-záéíóúñ0-9]+", bajo)
            if p not in {"noticia", "novedad", "tema", "para", "comentar", "gamer", "gaming"}
        ]
        return len(palabras_reales) < 2

    def titulo_publico_en_espanol(titulo, estilo="news"):
        original = limpiar_texto_publicable_final(titulo)
        if not original:
            return "Tema gamer para comentar"
        if titulo_generico_o_pobre(original):
            categoria_generica = _estilo_a_categoria_seguro(estilo)
            return {
                "anime": "Tema anime para comentar",
                "tecnologia": "Tecnología gamer bajo la lupa",
                "indie": "Indie para poner en el radar",
                "debate": "Tema gamer para debatir",
                "nostalgia": "Nostalgia gamer para comentar",
            }.get(categoria_generica, "Tema gamer para comentar")
        tema = extraer_tema_para_titulo(original)
        accion = detectar_accion_titulo(original)
        categoria = _categoria_final_item({"title": original, "summary": ""}, estilo)
        normalizar = call("normalizar_titulo_gamer", lambda x: x)
        if not parece_texto_ingles(original) and accion == "noticia" and len(original) <= 88:
            return normalizar(original)
        if parece_texto_ingles(tema) and not _tema_parece_titulo_propio(tema):
            tema = {
                "anime": "Tema anime",
                "tecnologia": "Tecnología gamer",
                "indie": "Juego indie",
                "debate": "Tema de industria",
                "nostalgia": "Tema retro",
            }.get(categoria, "Novedad gamer")
        plantillas = {
            "cierre": "{tema} termina una etapa importante",
            "adaptacion": "{tema} tendrá adaptación al anime",
            "avance": "{tema} muestra nuevo material",
            "actualizacion": "{tema} recibe una actualización para comentar",
            "preventa": "{tema} abre etapa de preventa",
            "lanzamiento": "{tema} pone su lanzamiento en el radar",
            "senal": "{tema}: posible novedad para seguir de cerca",
            "preservacion": "{tema} conecta con preservación y nostalgia",
            "industria": "{tema} abre conversación sobre la industria",
            "fisico_digital": "Juegos físicos vs digitales vuelve al debate",
            "tecnologia": "{tema}: tecnología gamer bajo la lupa",
            "mecanica": "{tema} presenta una mecánica para comentar",
            "noticia": "{tema}: noticia gamer para comentar",
        }
        salida = plantillas.get(accion, plantillas["noticia"]).format(tema=tema)
        if categoria == "anime" and accion == "noticia":
            salida = f"{tema}: tema anime para comentar"
        elif categoria == "tecnologia" and accion == "noticia":
            salida = f"{tema}: tecnología gamer bajo la lupa"
        elif categoria == "indie" and accion == "noticia":
            salida = f"{tema}: indie para poner en el radar"
        elif categoria == "debate" and accion == "noticia":
            salida = f"{tema}: tema para debatir"
        elif categoria == "nostalgia" and accion == "noticia":
            salida = f"{tema}: nostalgia gamer para comentar"
        return limpiar_texto_publicable_final(salida)

    def titulo_visible_seguro(item, estilo="news", bucket=None):
        return titulo_publico_en_espanol((item or {}).get("title", ""), bucket or estilo)

    def _resumen_fuente_util(resumen, titulo_es=""):
        resumen = limpiar_texto_publicable_final(resumen)
        if not resumen or resumen.lower().startswith("tema editorial"):
            return ""
        if len(resumen) < 55 or parece_texto_ingles(resumen):
            return ""
        bajo = resumen.lower()
        if any(frase in bajo for frase in FILLER_PHRASES) or linea_no_publicable(resumen):
            return ""
        if titulo_es and bajo.startswith(titulo_es.lower()):
            return ""
        recortar = call("recortar_texto", lambda t, n: str(t)[:n])
        return recortar(resumen, 280)

    def resumen_publico_en_espanol(titulo, resumen, estilo="news"):
        titulo_es = titulo_publico_en_espanol(titulo, estilo)
        tema = extraer_tema_para_titulo(titulo)
        accion = detectar_accion_titulo(titulo, resumen)
        categoria = _estilo_a_categoria_seguro(estilo)
        if categoria not in ["gaming", "tecnologia", "anime", "indie", "debate", "nostalgia"]:
            categoria = _categoria_final_item({"title": titulo, "summary": resumen}, estilo)
        fuente_util = _resumen_fuente_util(resumen, titulo_es)
        if fuente_util:
            return fuente_util
        if resumen and "tema editorial" in limpiar_texto_publicable_final(resumen).lower():
            if categoria == "tecnologia":
                return "Cuando la tecnología cambia cómo jugamos, vale mirar lo que realmente afecta: rendimiento, acceso, servicios, precio o comodidad."
            if categoria == "anime":
                return "Anime y cultura geek se cruzan cuando hay emoción, expectativas, adaptaciones, teorías o fandom comparando lo que espera ver."
            if categoria == "indie":
                return "Los indies muchas veces crecen por recomendación: una mecánica distinta, una demo fuerte o un estilo visual que se queda en la mente."
            if categoria == "nostalgia":
                return "La nostalgia pega cuando trae recuerdos concretos: consolas viejas, juegos físicos, controles prestados y etapas que marcaron a muchos gamers."
            if categoria == "debate":
                return "Este tema funciona porque tiene dos lados claros y deja espacio para que la comunidad cuente cómo lo vive sin pelear por plataformas."
            return "Un buen tema gamer no necesita sonar complicado: solo debe sentirse claro, cercano y fácil de comentar."
        if accion == "actualizacion":
            return f"La información disponible apunta a una actualización de {tema}. El ángulo seguro es contar que hay cambios en camino y abrir conversación sobre si vale volver a jugarlo."
        if accion == "avance":
            return f"El nuevo material de {tema} sirve para medir expectativa: tono, visuales, jugabilidad y qué tanto convence a la comunidad."
        if accion == "mecanica":
            return f"La noticia se enfoca en una mecánica de {tema}. Ese tipo de cambio puede mover conversación porque afecta reto, estrategia y forma de jugar."
        if accion == "senal":
            return f"Alrededor de {tema} hay una señal que puede prender emoción, pero conviene tratarla con cuidado hasta que exista confirmación clara."
        if accion == "cierre":
            return f"El cierre de {tema} marca un momento importante para su fandom. Cuando una historia termina, empieza la conversación sobre legado, final y qué viene después."
        if accion == "adaptacion":
            return f"La adaptación de {tema} puede mover conversación entre fans por cómo llevará el material original a otro formato."
        if accion == "preservacion":
            return f"{tema} entra en una conversación importante: preservar juegos también es mantener viva una parte de la historia gamer."
        if accion == "industria":
            return f"{tema} toca decisiones de industria que pueden afectar estudios, trabajadores, proyectos y confianza de la comunidad."
        if accion == "fisico_digital":
            return "El debate físico vs digital sigue vivo porque mezcla comodidad, propiedad, nostalgia y la forma en que cada gamer guarda sus juegos."
        if categoria == "tecnologia":
            return f"{tema} vale mirarlo desde el lado gamer: rendimiento, acceso, precio, compatibilidad o experiencia real."
        if categoria == "anime":
            return f"{tema} cruza anime y cultura geek con una pregunta simple: si realmente hay emoción o si conviene esperar más información."
        if categoria == "indie":
            return f"{tema} puede entrar en el radar si tiene una propuesta clara, una mecánica distinta o una demo que la comunidad quiera recomendar."
        if categoria == "nostalgia":
            return f"{tema} conecta con recuerdos, clásicos y esa parte de la comunidad que todavía valora otras generaciones."
        if categoria == "debate":
            return f"{tema} tiene más de un lado para mirar, por eso funciona mejor cuando se presenta sin pelea de plataformas."
        return f"{tema} llega como una novedad para mirar con calma y comentar qué puede significar para la comunidad gamer."

    def detalle_contextual_para_post(titulo, texto_base, estilo="news"):
        accion = detectar_accion_titulo(titulo, texto_base)
        categoria = _estilo_a_categoria_seguro(estilo)
        if categoria not in ["gaming", "tecnologia", "anime", "indie", "debate", "nostalgia"]:
            categoria = _categoria_final_item({"title": titulo, "summary": texto_base}, estilo)
        if accion == "actualizacion":
            return "La pregunta real es si esto cambia la experiencia o si se siente como más de lo mismo."
        if accion == "avance":
            return "Cuando sale nuevo material, la comunidad mira detalles pequeños: jugabilidad, fecha, tono y si la expectativa se sostiene."
        if accion == "mecanica":
            return "Cuando una mecánica cambia cómo enfrentamos un juego, la conversación se va rápido a si mejora el reto o rompe la experiencia."
        if accion == "senal":
            return "Aquí lo mejor es mantener los pies en la tierra: comentar la posibilidad sin venderla como hecho cerrado."
        if accion == "preservacion":
            return "La preservación importa porque muchos juegos pierden acceso con el tiempo, aunque sigan siendo parte de la memoria gamer."
        if accion == "industria":
            return "Este tipo de tema conviene hablarlo con calma, mirando el impacto real sin convertirlo en guerra de marcas."
        if categoria == "tecnologia":
            return "Lo mejor es bajarlo a tierra: cómo afecta jugar, crear contenido, comprar hardware o usar servicios."
        if categoria == "indie":
            return "Los indies crecen mucho por recomendación de comunidad: cuando una idea se siente diferente, la gente la pasa de boca en boca."
        if categoria == "anime":
            return "Anime y gaming se cruzan cuando hay emoción, adaptaciones, fandoms comparando expectativas o teorías."
        if categoria == "nostalgia":
            return "La nostalgia pega más cuando se siente concreta: una consola, un control, un cartucho, un disco o una tarde jugando con panas."
        if categoria == "debate":
            return "La conversación funciona mejor cuando presenta dos lados claros y deja que la comunidad cuente su experiencia."
        return "El valor está en conectar el dato con una pregunta que la comunidad realmente quiera contestar."

    def pregunta_engagement(titulo, estilo="news"):
        accion = detectar_accion_titulo(titulo)
        categoria = _categoria_final_item({"title": titulo, "summary": ""}, estilo)
        if accion == "actualizacion":
            return "👇 ¿Esto te anima a volver o lo dejarías pasar?"
        if accion == "avance":
            return "👇 ¿Este avance te subió la emoción o necesitas ver más?"
        if accion == "mecanica":
            return "👇 ¿Te gusta cuando un juego cambia sus mecánicas o prefieres lo clásico?"
        if accion == "senal":
            return "👇 ¿Esto te emociona o prefieres esperar confirmación oficial?"
        if accion in ["lanzamiento", "preventa"]:
            return "👇 ¿Lo pondrías en tu lista o esperarías más detalles?"
        if accion == "preservacion":
            return "👇 ¿Qué clásico te gustaría ver mejor preservado?"
        if accion == "fisico_digital":
            return "👇 ¿Tú prefieres juegos físicos o digitales?"
        if categoria == "tecnologia":
            return "👇 ¿Esto te parece útil para gamers o todavía necesitas ver más?"
        if categoria == "anime":
            return "👇 ¿Este tema te emociona o prefieres esperar más información?"
        if categoria == "indie":
            return "👇 ¿Lo pondrías en tu radar o esperas ver más gameplay primero?"
        if categoria == "nostalgia":
            return "👇 ¿Qué recuerdo gamer te vino a la mente?"
        if categoria == "debate":
            return "👇 ¿Tú cómo lo ves: buena movida o mala decisión?"
        return "👇 ¿Esto te interesa o lo dejarías pasar?"

    def limpiar_gramatica_post_final(texto):
        texto = limpiar_texto_publicable_final(texto)
        texto = texto.replace("TecnologíA", "Tecnología").replace("TECNOLOGíA", "TECNOLOGÍA")
        texto = texto.replace("PUBLICACIóN", "PUBLICACIÓN")
        texto = texto.replace("Busque y filtre", "Busqué y filtré")
        texto = re.sub(r"[ \t]{2,}", " ", texto)
        texto = re.sub(r"\n{3,}", "\n\n", texto)
        lineas = []
        for linea in texto.splitlines():
            limpia = linea.rstrip()
            if limpia.startswith("?"):
                limpia = "¿" + limpia[1:]
            if limpia.startswith("¿") and not limpia.endswith("?"):
                limpia += "?"
            lineas.append(limpia)
        return "\n".join(lineas).strip()

    def quitar_prefijos_editoriales(linea):
        texto = str(linea or "").strip()
        for patron in [
            r"^(t[ií]tulo|titulo)\s*:\s*",
            r"^(subt[ií]tulo|subtitulo)\s*:\s*",
            r"^(post|caption|publicaci[oó]n)\s*:\s*",
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
            "acción:", "accion:", "verificación:", "verificacion:", "nota interna:",
            "ángulo recomendado:", "angulo recomendado:",
        ]
        return any(texto.startswith(prefijo) for prefijo in prefijos) or any(
            frase in texto for frase in FILLER_PHRASES
        )

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

    def caption_necesita_regenerarse(texto, item=None, estilo="news"):
        item = item or {}
        texto_limpio = limpiar_texto_publicable_final(texto)
        bajo = texto_limpio.lower()
        if any(frase in bajo for frase in FILLER_PHRASES):
            return True
        categoria = _categoria_final_item(item, estilo)
        if categoria != "indie" and any(p in bajo for p in ["indies", "juegos independientes", "demos"]):
            return True
        if categoria not in ["nostalgia", "debate"] and any(p in bajo for p in ["juegos físicos", "manual", "prestarlo", "cartucho"]):
            return True
        if categoria != "tecnologia" and any(p in bajo for p in ["ruido técnico", "cambio útil"]):
            return True
        cuerpo = "\n".join(linea for linea in texto_limpio.splitlines() if not linea.strip().startswith("#"))
        return parece_texto_ingles(cuerpo) and not _tema_parece_titulo_propio(cuerpo)

    def crear_hashtags(texto, limite=None):
        limite = 5 if limite is None else min(5, max(1, int(limite)))
        texto_limpio = limpiar_texto_publicable_final(texto).lower()
        brand = call("get_brand_voice")().get("brand", st.session_state.get("active_brand", "Gamer Cave"))
        marca = "#davietgaming" if brand == "Daviet Gaming" else "#elgamercave"
        tags = [marca]
        reglas = [
            (["anime", "manga", "crunchyroll", "shonen", "otaku"], ["#anime", "#manga"]),
            (["nintendo", "switch", "mario", "zelda", "kirby", "pokemon", "pokémon"], ["#nintendo", "#nintendoswitch"]),
            (["playstation", "ps5", "ps plus"], ["#playstation", "#ps5"]),
            (["xbox", "game pass"], ["#xbox", "#xboxseriesx"]),
            (["pc", "steam", "gpu", "nvidia", "amd", "intel", "hardware", "tecnologia", "tecnología", "unreal engine", "godot", "unity"], ["#pcgaming", "#gamingtech"]),
            (["indie", "independent", "independiente", "next fest"], ["#indiegames", "#indiegaming"]),
            (["retro", "nostalgia", "classic", "clasico", "clásico", "remake", "remaster", "gamecube", "game boy"], ["#nostalgia", "#retrogaming"]),
        ]
        for claves, nuevos in reglas:
            if any(clave in texto_limpio for clave in claves):
                tags.extend(nuevos)
        for clave, tag in [
            ("diablo", "#diablo"),
            ("kingdom hearts", "#kingdomhearts"),
            ("call of duty", "#callofduty"),
            ("pokemon", "#pokemon"),
            ("pokémon", "#pokemon"),
        ]:
            if clave in texto_limpio:
                tags.append(tag)
        tags.extend(["#gaming", "#videojuegos", "#gamers", "#geekculture"])
        salida = []
        for tag in tags:
            tag = tag.lower()
            if tag and tag not in salida:
                salida.append(tag)
            if len(salida) >= limite:
                break
        while len(salida) < limite:
            for tag in ["#gaming", "#videojuegos", "#gamers", "#geekculture"]:
                if tag not in salida:
                    salida.append(tag)
                    break
            else:
                break
        return " ".join(salida[:limite])

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
        if "?" not in cuerpo and "¿" not in cuerpo:
            cuerpo = f"{cuerpo}\n\n{pregunta_engagement(titulo_original or cuerpo, estilo)}"
        return f"{cuerpo}\n\n{hashtag_line}".strip() if hashtag_line else cuerpo

    def limpiar_pedido_post(pregunta):
        texto = limpiar_texto_publicable_final(pregunta).lower()
        quitar_marca = call("quitar_marca_de_texto", lambda x: x)
        texto = quitar_marca(texto)
        texto = re.sub(r"\b(daviet gaming|gamer cave|el gamer cave|gamer signal|instagram|facebook)\b", " ", texto)
        frases = [
            "hazme un post", "hazme una publicacion", "hazme una publicación",
            "creame un post", "créame un post", "crea un post", "crear un post",
            "dame un post", "dame una noticia", "dame un", "dame una",
            "post para", "caption para", "caption", "publicacion", "publicación",
            "hazme", "creame", "créame", "crear", "crea", "dame", "post",
            "noticia", "noticias", "actual", "reciente", "hot", "viral",
            "del dia", "del día",
        ]
        for frase in sorted(frases, key=len, reverse=True):
            texto = texto.replace(frase, " ")
        texto = re.sub(r"\b(sobre|de|para|un|una|el|la|los|las)\b", " ", texto)
        limpio = " ".join(texto.split()).strip(" .,:;-")
        if limpio in {"", "tema", "algo", "nuevo", "nueva", "redes", "publicar"}:
            return ""
        return limpio

    def brand_route_for_item(item, marca=None):
        marca_permitida = call("marca_permitida", lambda x: x or "Gamer Cave")
        marca = marca_permitida(marca or st.session_state.get("active_brand", "Gamer Cave"))
        clasificacion = clasificar_evento(item)
        scores = calcular_score_multidimensional(item)
        enfoque = (
            "opinión clara, reacción natural y utilidad para gamers de Puerto Rico/LatAm"
            if marca == "Daviet Gaming"
            else "comunidad, información clara y conversación sana"
        )
        return {"brand": marca, "focus": enfoque, "classification": clasificacion, "scores": scores}

    def seleccionar_angulo_editorial(item, estilo=None, marca=None):
        ruta = brand_route_for_item(item, marca)
        clasificacion = ruta["classification"]
        categoria = _categoria_final_item(item, estilo)
        formato = _estilo_a_categoria_seguro(estilo)
        if formato in ["nostalgia", "debate"]:
            return formato
        if "debate" in clasificacion["editorial_formats"] and ruta["scores"]["debate_potential"] >= 6:
            return "debate"
        if "nostalgia" in clasificacion["editorial_formats"]:
            return "nostalgia"
        if categoria == "tecnologia":
            return "tecnologia"
        if categoria == "anime":
            return "anime"
        if categoria == "indie":
            return "indie"
        return "news"

    def crear_post_limpio(titulo, resumen, estilo, nostalgia="", hashtags=""):
        titulo_es = titulo_publico_en_espanol(titulo, estilo)
        resumen_es = resumen_publico_en_espanol(titulo, resumen, estilo)
        detalle = detalle_contextual_para_post(titulo, resumen or resumen_es, estilo)
        pregunta = pregunta_engagement(titulo, estilo)
        hashtags = crear_hashtags(f"{titulo} {resumen}", 5)
        partes = [f"🎮 {titulo_es}", resumen_es]
        if detalle and detalle.lower() not in " ".join(partes).lower():
            partes.append(detalle)
        if nostalgia and _estilo_a_categoria_seguro(estilo) in ["nostalgia", "debate"]:
            nostalgia = limpiar_texto_publicable_final(nostalgia)
            if nostalgia and nostalgia.lower() not in " ".join(partes).lower():
                partes.append(nostalgia)
        partes.extend([pregunta, hashtags])
        return limpiar_gramatica_post_final("\n\n".join(partes))

    def categoria_de_publicacion(categoria, estilo, item):
        estilo_norm = _estilo_a_categoria_seguro(estilo)
        if estilo_norm in ["nostalgia", "debate"]:
            return estilo_norm
        clasificacion = clasificar_evento(item)
        if "nostalgia" in clasificacion["editorial_formats"] and categoria not in ["anime", "tecnologia", "indie"]:
            return "nostalgia"
        if "debate" in clasificacion["editorial_formats"] and categoria not in ["anime", "tecnologia", "indie"]:
            return "debate"
        return categoria

    def aplicar_reglas_editoriales_fuertes(post, item=None, estilo="news"):
        item = item or {}
        titulo = limpiar_texto_publicable_final(item.get("title", "Tema gamer"))
        resumen = limpiar_texto_publicable_final(item.get("summary", ""))
        texto = limpiar_lineas_para_caption(post)
        if caption_necesita_regenerarse(texto, item, estilo):
            texto = crear_post_limpio(titulo, resumen, estilo, item.get("nostalgia_angle", ""), crear_hashtags(f"{titulo} {resumen}", 5))
            texto = limpiar_lineas_para_caption(texto)
        texto = asegurar_hashtags_editoriales(texto, titulo, resumen)
        texto = asegurar_pregunta_final(texto, titulo, estilo)
        return limpiar_gramatica_post_final(texto)

    def generate_social_post(item, estilo=None):
        item = dict(item or {})
        fact_sheet = crear_fact_sheet(item)
        clasificacion = clasificar_evento(item)
        categoria = _categoria_final_item(item)
        estilo = estilo or st.session_state.get("post_style", "all")
        if estilo == "all":
            estilo = seleccionar_angulo_editorial(item)
        estilo_seguro = call("estilo_seguro_para_item", lambda _item, _estilo: _estilo)
        estilo = estilo_seguro(item, estilo)
        if estilo == "noticia":
            estilo = "news"
        titulo = fact_sheet["event"]["title"]
        resumen = fact_sheet["event"]["summary"]
        detectar_angulo_nostalgia = call("detectar_angulo_nostalgia", lambda _item: "")
        item.update({
            "id": fact_sheet["event"]["id"],
            "title": titulo,
            "summary": resumen,
            "content_angle": categoria,
            "editorial_format": estilo,
            "fact_sheet": fact_sheet,
            "classification": clasificacion,
            "score_result": calcular_score_multidimensional(item),
            "nostalgia_angle": detectar_angulo_nostalgia(item),
        })
        st.session_state.generated_items[item["id"]] = dict(item)
        st.session_state.last_item_id = item["id"]
        post = crear_post_limpio(titulo, resumen, estilo, item.get("nostalgia_angle", ""), crear_hashtags(f"{titulo} {resumen}", 5))
        post = aplicar_reglas_editoriales_fuertes(post, item, estilo)
        st.session_state.last_post_text = post
        st.session_state.last_post_title = titulo_publico_en_espanol(titulo, estilo)
        return post

    def categorias_para_posts(cantidad, texto):
        texto = limpiar_texto_publicable_final(texto).lower()
        pedidos = []
        if "anime" in texto or "manga" in texto:
            pedidos.append("anime")
        if "tecnologia" in texto or "tecnología" in texto or "pc" in texto or "hardware" in texto:
            pedidos.append("tecnologia")
        if "indie" in texto or "independiente" in texto:
            pedidos.append("indie")
        if "debate" in texto or "opinion" in texto or "opinión" in texto:
            pedidos.append("debate")
        if "nostalgia" in texto or "retro" in texto:
            pedidos.append("nostalgia")
        if "gaming" in texto or "juego" in texto or "noticia" in texto:
            pedidos.insert(0, "gaming")
        base = pedidos or ["gaming", "anime", "tecnologia", "indie", "debate", "nostalgia"]
        for extra in ["gaming", "anime", "tecnologia", "indie", "debate", "nostalgia"]:
            if extra not in base:
                base.append(extra)
        salida = []
        while len(salida) < cantidad:
            salida.extend(base)
        return salida[:cantidad]

    def _pasa_exclusiones_basicas(item, texto_usuario):
        texto = _event_text(item).lower()
        pedido = limpiar_texto_publicable_final(texto_usuario).lower()
        if not item_es_contexto_editorial(item) and titulo_generico_o_pobre(item.get("title", "")):
            return False
        exclusiones = []
        for patron in [r"no sea de ([a-z0-9 áéíóúñ]+)", r"que no sea de ([a-z0-9 áéíóúñ]+)", r"no de ([a-z0-9 áéíóúñ]+)"]:
            for match in re.finditer(patron, pedido):
                exclusiones.extend(match.group(1).split())
        exclusiones = [e.strip() for e in exclusiones if len(e.strip()) > 2]
        return not any(exclusion in texto for exclusion in exclusiones)

    def seleccionar_noticias_variadas(noticias, cantidad, texto_usuario=""):
        cantidad = max(1, min(cantidad, 8))
        disponibles = []
        for item in noticias or []:
            item = dict(item)
            if not _pasa_exclusiones_basicas(item, texto_usuario):
                continue
            if tema_repetido(item.get("title", "")) or tema_muy_similar(item.get("title", "")):
                continue
            estado, _detalle = estado_verificacion_item(item)
            if estado == "Rojo" and not item.get("is_community_signal"):
                continue
            item["classification"] = clasificar_evento(item)
            item["score_result"] = calcular_score_multidimensional(item)
            disponibles.append(item)
        disponibles.sort(key=lambda x: x.get("score_result", {}).get("final_score", 0), reverse=True)
        seleccionadas = []
        titulos = set()
        fuentes = {}
        plataformas = {}

        def puede_usarse(item):
            titulo = limpiar_texto_publicable_final(item.get("title", ""))
            key = _normalizar_para_similitud(titulo)
            if not key or key in titulos:
                return False
            fuente = item.get("source", "")
            plataforma_de_item = call("plataforma_de_item", lambda _item: "general")
            plataforma = plataforma_de_item(item)
            if cantidad >= 4 and fuentes.get(fuente, 0) >= 1:
                return False
            if cantidad >= 4 and plataforma != "general" and plataformas.get(plataforma, 0) >= 1:
                return False
            return True

        def agregar(item):
            titulo = limpiar_texto_publicable_final(item.get("title", ""))
            titulos.add(_normalizar_para_similitud(titulo))
            fuente = item.get("source", "")
            fuentes[fuente] = fuentes.get(fuente, 0) + 1
            plataforma_de_item = call("plataforma_de_item", lambda _item: "general")
            plataforma = plataforma_de_item(item)
            plataformas[plataforma] = plataformas.get(plataforma, 0) + 1
            seleccionadas.append(dict(item))

        for categoria in categorias_para_posts(cantidad, texto_usuario):
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
            "anime": ["anime de temporada que mueve conversación", "manga y anime que cruzan con cultura gamer", "adaptaciones que el fandom mira con cuidado"],
            "tecnologia": ["tecnología que sí cambia la experiencia gamer", "hardware y servicios que afectan cómo jugamos", "herramientas nuevas dentro del gaming"],
            "indie": ["indies con propuestas diferentes", "demos que pueden crecer por recomendación", "juegos pequeños que merecen radar"],
            "debate": g.get("TEMAS_COMUNIDAD", ["juegos físicos vs digitales", "precios y servicios"]),
            "nostalgia": g.get("TEMAS_NOSTALGIA", ["juegos físicos y recuerdos de infancia", "consolas viejas que marcaron época"]),
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
        ahora_en_puerto_rico = call("ahora_en_puerto_rico")
        detectar_angulo_nostalgia = call("detectar_angulo_nostalgia", lambda _item: "")
        item = {
            "id": str(uuid.uuid4()),
            "title": limpiar_texto_publicable_final(titulo),
            "summary": resumen,
            "source": "Tema editorial Gamer Signal",
            "link": "",
            "date": str(ahora_en_puerto_rico().date()) if ahora_en_puerto_rico else "",
            "source_official": False,
            "source_trusted": False,
            "is_editorial": True,
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

    def etiqueta_publicacion_limpia(categoria):
        return {
            "gaming": "Gaming/Noticia",
            "tecnologia": "Tecnología",
            "anime": "Anime",
            "indie": "Indie",
            "debate": "Debate",
            "nostalgia": "Nostalgia",
        }.get(categoria, "Gaming")

    def crear_varios_posts(cantidad, pregunta):
        cantidad = max(2, min(cantidad, 8))
        texto = limpiar_texto_publicable_final(pregunta).lower()
        noticias = seleccionar_noticias_variadas(g["buscar_noticias"](), min(cantidad * 3, 12), texto)
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
            estilo = seleccionar_angulo_editorial(item, categoria_real)
            st.session_state.generated_items[item["id"]] = dict(item)
            st.session_state.news_by_number[indice] = dict(item)
            st.session_state.last_item_id = item["id"]
            items_generados.append(dict(item))
            etiqueta = etiqueta_publicacion_limpia(categoria_de_publicacion(categoria_real, estilo, item))
            if item_es_contexto_editorial(item):
                etiqueta = f"{etiqueta}/Editorial"
            posts.append(f"PUBLICACIÓN {indice} - {etiqueta.upper()}\n\n{generate_social_post(item, estilo)}")
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
            return ("Amarillo", "señal de comunidad; usar como debate o nostalgia")
        return ("Rojo", "no usar como noticia confirmada")

    def formatear_noticias(noticias, texto_usuario="", cantidad=5):
        cantidad = max(1, min(cantidad, 8))
        noticias = seleccionar_noticias_variadas(noticias, cantidad, texto_usuario)
        if not noticias:
            return (
                f"No encontré noticias verificadas nuevas del año {g.get('ANIO_NOTICIAS', '')} con ese filtro.\n\n"
                "Puedo crear contenido editorial de debate o nostalgia, pero no lo presentaré como noticia confirmada."
            )
        st.session_state.news_by_number = {}
        respuesta = f"Busqué y filtré noticias verificadas del año {g.get('ANIO_NOTICIAS', '')}.\n\n"
        respuesta += f"Rango usado: {g.get('FECHA_INICIO', '')} hasta {g.get('FECHA_FINAL', '')}\n\n"
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
        noticias = seleccionar_noticias_variadas(g["buscar_noticias"](), 5, "opciones de post variadas")
        st.session_state.news_by_number = {}
        if not noticias:
            return "No encontré opciones verificadas nuevas ahora mismo. Puedes pedirme un post de nostalgia o debate editorial."
        respuesta = "### Opciones de post recientes\n\n"
        for numero, item in enumerate(noticias, start=1):
            categoria = _categoria_final_item(item)
            st.session_state.generated_items[item["id"]] = dict(item)
            st.session_state.news_by_number[numero] = dict(item)
            st.session_state.last_item_id = item["id"]
            respuesta += f"**{numero}. {titulo_visible_seguro(item, categoria)}**\n\n"
            respuesta += f"- Categoría: {etiqueta_publicacion_limpia(categoria)}\n"
            respuesta += f"- Fuente: {item.get('source', '')}\n"
            respuesta += f"- Estado: {estado_verificacion_item(item)[0]}\n"
            respuesta += f"- Para usarla: **post de la noticia {numero}**\n\n"
        return limpiar_gramatica_post_final(respuesta)

    replacements = {
        "reparar_texto_roto": reparar_texto_roto,
        "limpiar_texto_publicable_final": limpiar_texto_publicable_final,
        "parece_texto_ingles": parece_texto_ingles,
        "normalizar_evento": normalizar_evento,
        "crear_fact_sheet": crear_fact_sheet,
        "clasificar_evento": clasificar_evento,
        "calcular_score_multidimensional": calcular_score_multidimensional,
        "detectar_accion_titulo": detectar_accion_titulo,
        "item_es_contexto_editorial": item_es_contexto_editorial,
        "_categoria_final_item": _categoria_final_item,
        "categoria_de_item": categoria_de_item,
        "detectar_content_angle": detectar_content_angle,
        "entrada_usada_aplica_a_marca": entrada_usada_aplica_a_marca,
        "tema_repetido": tema_repetido,
        "tema_muy_similar": tema_muy_similar,
        "extraer_tema_para_titulo": extraer_tema_para_titulo,
        "titulo_generico_o_pobre": titulo_generico_o_pobre,
        "titulo_publico_en_espanol": titulo_publico_en_espanol,
        "titulo_visible_seguro": titulo_visible_seguro,
        "resumen_publico_en_espanol": resumen_publico_en_espanol,
        "detalle_contextual_para_post": detalle_contextual_para_post,
        "pregunta_engagement": pregunta_engagement,
        "limpiar_gramatica_post_final": limpiar_gramatica_post_final,
        "linea_no_publicable": linea_no_publicable,
        "limpiar_lineas_para_caption": limpiar_lineas_para_caption,
        "caption_necesita_regenerarse": caption_necesita_regenerarse,
        "crear_hashtags": crear_hashtags,
        "asegurar_hashtags_editoriales": asegurar_hashtags_editoriales,
        "asegurar_pregunta_final": asegurar_pregunta_final,
        "limpiar_pedido_post": limpiar_pedido_post,
        "brand_route_for_item": brand_route_for_item,
        "seleccionar_angulo_editorial": seleccionar_angulo_editorial,
        "crear_post_limpio": crear_post_limpio,
        "aplicar_reglas_editoriales_fuertes": aplicar_reglas_editoriales_fuertes,
        "generate_social_post": generate_social_post,
        "categorias_para_posts": categorias_para_posts,
        "seleccionar_noticias_variadas": seleccionar_noticias_variadas,
        "crear_item_editorial_categoria": crear_item_editorial_categoria,
        "etiqueta_publicacion_limpia": etiqueta_publicacion_limpia,
        "crear_varios_posts": crear_varios_posts,
        "estado_verificacion_item": estado_verificacion_item,
        "formatear_noticias": formatear_noticias,
        "crear_opciones_post_recientes": crear_opciones_post_recientes,
    }
    g.update(replacements)
    return replacements
