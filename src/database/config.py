import os
import streamlit as st
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from contextlib import contextmanager

# 1. Tenta buscar a Secret
DATABASE_URL = os.getenv("DATABASE_URL")

# --- BLOCO DE DIAGNÓSTICO ---
if not DATABASE_URL:
    st.error("🚨 ERRO: A Secret 'DATABASE_URL' não foi encontrada no Hugging Face!")
    st.info("Acesse Settings -> Variables and Secrets e verifique o nome.")
    st.stop()  # Trava o app aqui

# Ajuste do prefixo para SQLAlchemy 2.0
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 2. Tenta conectar e "Grita" o erro específico
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        # O Supabase exige SSL
        connect_args={"sslmode": "require"} if "supabase" in DATABASE_URL else {}
    )
    # Testa a conexão de verdade agora
    with engine.connect() as conn:
        pass 
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
except Exception as e:
    st.error("❌ FALHA NA CONEXÃO COM O SUPABASE")
    st.warning(f"Detalhe técnico do erro: {e}")
    
    # Dicas baseadas no tipo de erro
    if "password authentication failed" in str(e):
        st.info("💡 Dica: A senha na Secret está errada ou os caracteres especiais (como @) não foram escapados com %40.")
    elif "could not translate host name" in str(e):
        st.info("💡 Dica: O endereço da URL (host) parece estar incorreto.")
    
    st.stop() # Não deixa o app continuar se o banco estiver quebrado

# --- FIM DO DIAGNÓSTICO ---

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
