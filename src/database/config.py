import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.logger import log_error

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    log_error("DATABASE_URL não configurada no ambiente!")
    sys.exit(1) # Fail Fast: O sistema nem inicia sem banco

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
