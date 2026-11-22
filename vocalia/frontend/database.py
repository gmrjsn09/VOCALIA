import os
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Lee primero de st.secrets (Streamlit Cloud) y si no existe, del .env local
DATABASE_URL = st.secrets.get("DATABASE_URL") if "DATABASE_URL" in st.secrets else os.getenv("DATABASE_URL")
DATABASE_URL = (DATABASE_URL or "").strip().strip('"').strip("'")

if not DATABASE_URL:
    raise RuntimeError("Falta DATABASE_URL en Secrets o .env")

# Algunos proveedores entregan "postgres://", SQLAlchemy necesita "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Usa el driver instalado: psycopg (v3) si existe; si no, psycopg2
_args = {"connect_timeout": 10}
if DATABASE_URL.startswith("postgresql://"):
    try:
        import psycopg  # noqa: F401
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
        _args["prepare_threshold"] = None  # compatible con el pooler de Supabase
    except ImportError:
        pass

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=5,
                       pool_recycle=300, connect_args=_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()