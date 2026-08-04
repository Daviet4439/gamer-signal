# Gamer Signal

Gamer Signal es una app en Streamlit para buscar noticias gamer/geek, organizar radar diario y crear posts para Gamer Cave y Daviet Gaming.

## Ollama Cloud

La generación y clasificación de noticias usa `https://ollama.com/api/chat` con el modelo `gpt-oss:20b`.

En Streamlit Community Cloud abre **App settings > Secrets** y agrega:

```toml
OLLAMA_API_KEY = "tu_clave_nueva_de_ollama"
```

La clave nunca debe añadirse a `app.py`, GitHub ni a `.streamlit/config.toml`.

## Aprendizaje persistente con Supabase

Los votos de los posts se guardan en la tabla `ejemplos_posts`. En los Secrets
de Streamlit Community Cloud agrega tambien:

```toml
SUPABASE_URL = "https://tu-proyecto.supabase.co"
SUPABASE_KEY = "tu_clave_de_supabase"
```

La estructura reproducible de la tabla esta en
`supabase/migrations/20260803_create_ejemplos_posts.sql`.

## App en la nube

- Publico: https://gamer-signal.streamlit.app/
- Dueño: https://gamer-signal.streamlit.app/?owner=daviet

## Ejecutar local

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Actualizar la app

Cuando hagas cambios, ejecuta:

```powershell
.\actualizar_app.ps1
```

Eso sube los cambios a GitHub y Streamlit actualiza el link automaticamente.
