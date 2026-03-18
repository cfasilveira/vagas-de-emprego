import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1. Busca das Secrets do Streamlit Cloud
DATABASE_URL = st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", ""))

if not DATABASE_URL:
    st.error("🚨 DATABASE_URL não configurada nas Secrets!")
    st.stop()

# 2. Correção de protocolo
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    # 3. Engine com SSL obrigatório para o Supabase
    engine = create_engine(
        DATABASE_URL,
        connect_args={"sslmode": "require"},
        pool_pre_ping=True
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Testa a conexão
    with engine.connect() as conn:
        pass
except Exception as e:
    st.error(f"❌ Erro de Conexão com o Banco: {e}")
    st.stop()

class Base(DeclarativeBase):
    pass
