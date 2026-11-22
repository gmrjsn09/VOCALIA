# Vocacional IA · UCV Chiclayo

Orientación vocacional basada en las 23 carreras de la UCV sede Chiclayo.
Todo en Python: interfaz Streamlit + API FastAPI (integrada en la misma app) + PostgreSQL (Supabase) + Gemini.

## Estructura
- `vocalia/frontend/app.py`: interfaz de Streamlit (archivo principal).
- `vocalia/frontend/main.py`: API (FastAPI). Corre dentro de la app, no necesita servidor aparte.
- `vocalia/frontend/cuestionario.py`: preguntas, carreras de la UCV y cálculo de puntajes.
- `vocalia/frontend/database.py`: conexión a la base de datos.
- `vocalia/backend/`: scripts de apoyo (`prueba.py` prueba la conexión, `ver_datos.py` muestra los datos).

Las tablas y las 23 carreras se crean solas al iniciar la app.

## Variables de entorno
En local van en un archivo `.env` (en `vocalia/frontend/` o `vocalia/backend/`); en Streamlit Cloud, en *Secrets*:

```
DATABASE_URL = "postgresql://..."
GEMINI_API_KEY = "..."
GEMINI_MODEL = "gemini-2.5-flash"
ADMIN_EMAILS = "correo-del-administrador@ejemplo.com"
```

## Ejecutar en local
```
cd vocalia/frontend
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Cloud
Main file path: `vocalia/frontend/app.py`. Completa los *Secrets* con las variables de arriba.