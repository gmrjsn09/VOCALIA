import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Acepta la URL con o sin comillas (en el archivo .env o en las variables del servidor)
DATABASE_URL = (os.getenv("DATABASE_URL") or "").strip().strip('"').strip("'")
if not DATABASE_URL:
    raise RuntimeError("Falta DATABASE_URL en el archivo .env")

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