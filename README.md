# Gamer Signal

Gamer Signal es una app en Streamlit para buscar noticias gamer/geek, organizar radar diario y crear posts para Gamer Cave y Daviet Gaming.

## Ejecutar local

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Subir a Streamlit Cloud

1. Sube estos archivos a un repositorio de GitHub.
2. Entra a https://share.streamlit.io/
3. Crea una app nueva.
4. Selecciona el repo.
5. Main file path: `app.py`
6. Deploy.

## Nota

En Streamlit Cloud la memoria guardada en archivos puede reiniciarse cuando la app duerme o se redeploya. Para memoria permanente se recomienda luego conectar una base de datos gratis como Supabase.
