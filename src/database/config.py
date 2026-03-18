import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1. Tenta ler das Secrets do Streamlit ou do ambiente
DATABASE_URL = st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", "")).strip()

if not DATABASE_URL:
    st.error("🚨 A variável 'DATABASE_URL' não foi encontrada!")
    DATABASE_URL = "sqlite:///./vagas.db"
else:
    # 2. Corrige o protocolo para SQLAlchemy 2.0
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Configura a Engine com SSL obrigatório para o Supabase
try:
    # O segredo para o Streamlit Cloud é o sslmode=require
    engine = create_engine(
        DATABASE_URL,
        connect_args={"sslmode": "require"} if "supabase" in DATABASE_URL or "aws" in DATABASE_URL else {},
        pool_pre_ping=True
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Testa a conexão silenciosamente
    with engine.connect() as conn:
        pass
except Exception as e:
    st.error(f"❌ Erro de Conexão: {e}")
    st.stop()

class Base(DeclarativeBase):
    pass
