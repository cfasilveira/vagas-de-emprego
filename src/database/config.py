import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from contextlib import contextmanager

DATABASE_URL = "sqlite:///./vagas.db"

# Ajuste de protocolo para nuvem
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "sqlite:///./vagas.db"

# Ativa SSL apenas se for banco externo (nuvem)
if "localhost" not in DATABASE_URL and "@db:" not in DATABASE_URL:
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
