# Vocacional IA
Backend: FastAPI + PostgreSQL + Gemini. Frontend: Streamlit (todo Python).

## Backend
cd backend && pip install -r requirements.txt
copia .env.example a .env y completa los datos
(opcional) ejecuta schema.sql en tu base de Render
uvicorn main:app --reload

## Frontend
cd frontend && pip install -r requirements.txt
streamlit run app.py
