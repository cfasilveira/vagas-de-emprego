import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.logger import log_error
from contextlib import contextmanager

# Tenta pegar do ambiente (Docker), se não houver, usa o padrão local
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@db:5432/vagas_db")

try:
    engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_size=10,       # Mantém até 10 conexões prontas
    max_overflow=20     # Permite até 20 extras em picos de acesso
)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    log_error(f"Falha ao configurar o Engine do Banco: {e}")
    sys.exit(1)

# Padrão SQLAlchemy 2.0+
class Base(DeclarativeBase):
    pass

@contextmanager
def get_db():
    """Gerenciador de contexto robusto para evitar vazamento de sessões."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
