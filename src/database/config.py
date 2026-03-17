import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from contextlib import contextmanager

# Busca a Secret do Hugging Face
DATABASE_URL = os.getenv("DATABASE_URL")

# DIAGNÓSTICO VISUAL NO STREAMLIT
if not DATABASE_URL:
    st.error("❌ ERRO CRÍTICO: Secret 'DATABASE_URL' não encontrada no Hugging Face!")
    st.info("Verifique se o nome na aba 'Variables and Secrets' está exatamente como DATABASE_URL (maiúsculo).")
    # Fallback para não quebrar o build, mas as vagas não aparecerão
    DATABASE_URL = "sqlite:///./vagas.db"
else:
    # Ajuste automático do prefixo exigido pelo SQLAlchemy
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Mostra sucesso apenas para você confirmar a conexão (pode remover depois)
    if "db_connected" not in st.session_state:
        st.toast("🚀 Conectado ao banco Supabase!")
        st.session_state.db_connected = True

# Criação da Engine
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        # O Supabase exige SSL para conexões externas
        connect_args={"sslmode": "require"} if "supabase" in DATABASE_URL else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    st.error(f"❌ Erro ao conectar no banco: {e}")

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
