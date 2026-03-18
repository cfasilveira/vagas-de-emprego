import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from contextlib import contextmanager

# 1. Carrega as variáveis do arquivo .env (Onde definimos a URL local)
load_dotenv()

# 2. Busca a URL do ambiente. 
# Se não encontrar, usa o padrão que está no seu docker-compose.yml
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@db:5432/vagas_db")

# 3. Cria a Engine para o Postgres Local (sem SSL)
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True
)

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
