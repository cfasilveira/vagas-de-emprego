import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from contextlib import contextmanager

# 1. Busca a Secret do HF
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vagas.db")

# 2. Ajuste de protocolo para SQLAlchemy 2.0
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Diagnóstico (Aparecerá nos Logs do Hugging Face)
if "supabase" in DATABASE_URL:
    print("🚀 INFO: Conectando ao banco externo (Supabase)")
else:
    print("⚠️ WARNING: Usando banco de dados LOCAL (vagas.db)")

# 4. Configuração de SSL para Supabase
if "localhost" not in DATABASE_URL and "sqlite" not in DATABASE_URL:
    if "?" not in DATABASE_URL:
        DATABASE_URL += "?sslmode=require"
    elif "sslmode" not in DATABASE_URL:
        DATABASE_URL += "&sslmode=require"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
