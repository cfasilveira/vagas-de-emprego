import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1. Pega a URL e limpa espaços invisíveis
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# 2. Mostra na tela para conferência (SÓ O INÍCIO POR SEGURANÇA)
if not DATABASE_URL:
    st.error("🚨 A variável 'DATABASE_URL' está VAZIA nos Logs do Sistema.")
    st.info("Acesse Settings -> Variables and Secrets e verifique se você clicou em 'Save' após o Replace.")
    DATABASE_URL = "sqlite:///./vagas.db"
else:
    st.success(f"✅ Variável encontrada! Começa com: {DATABASE_URL[:15]}...")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Engine
try:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"sslmode": "require"} if "supabase" in DATABASE_URL else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # Testa a conexão
    with engine.connect() as conn:
        st.toast("Conectado ao Supabase com sucesso!")
except Exception as e:
    st.error(f"❌ Erro técnico: {e}")
    st.stop()

class Base(DeclarativeBase):
    pass
