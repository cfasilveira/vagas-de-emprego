import streamlit as st
import secrets
import time
from src.logger import log_audit, log_error

def login_required(func):
    """Decorator de Segurança: Só executa a função se estiver autenticado."""
    def wrapper(*args, **kwargs):
        if not st.session_state.get("is_admin"):
            render_login()
            return
        return func(*args, **kwargs)
    return wrapper

def render_login():
    st.warning("🔒 Acesso Restrito ao Sistema Central")
    user = st.text_input("ID de Operador", key="admin_user")
    password = st.text_input("Chave de Acesso", type="password", key="admin_pass")
    
    if st.button("Validar Credenciais"):
        time.sleep(1) # Defesa anti-brute force
        if user == "admin" and password == "seguranca2026":
            st.session_state.is_admin = True
            st.session_state.session_token = secrets.token_hex(32)
            log_audit(f"LOGIN: Sessão segura iniciada para {user}")
            st.rerun()
        else:
            log_error(f"ALERTA: Falha de autenticação detectada.")
            st.error("Acesso Negado.")
