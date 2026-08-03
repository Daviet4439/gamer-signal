# Gamer Signal

Gamer Signal es una app en Streamlit para buscar noticias gamer/geek, organizar radar diario y crear posts para Gamer Cave y Daviet Gaming.

## Ollama Cloud

La generación y clasificación de noticias usa `https://ollama.com/api/chat` con el modelo `gpt-oss:20b`.

En Streamlit Community Cloud abre **App settings > Secrets** y agrega:

```toml
OLLAMA_API_KEY = "tu_clave_nueva_de_ollama"
```

La clave nunca debe añadirse a `app.py`, GitHub ni a `.streamlit/config.toml`.

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
