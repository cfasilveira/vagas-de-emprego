import streamlit as st
import secrets
import time
from src.logger import log_audit, log_error
from src.security import SecurityGate, generate_handshake_token # Integração com security.py

def check_password():
    """Interface de ligação com o main.py."""
    if st.session_state.get("is_admin"):
        return True
    
    render_login()
    return False

def render_login():
    st.warning("🔒 Acesso Restrito ao Sistema Central")
    
    user = st.text_input("ID de Operador", key="admin_user")
    password = st.text_input("Chave de Acesso", type="password", key="admin_pass")
    
    if st.button("Validar Credenciais"):
        # Validação via SecurityGate antes de processar
        if not SecurityGate.validate_input(user):
            log_error(f"BLOQUEIO: Tentativa de injeção detectada no usuário: {user}")
            st.error("Caracteres inválidos detectados.")
            return

        time.sleep(1) # Defesa anti-brute force
        
        # Credenciais conforme seu script original
        if user == "admin" and password == "seguranca2026":
            st.session_state.is_admin = True
            st.session_state.session_token = generate_handshake_token() # Uso do security.py
            log_audit(f"LOGIN: Sessão segura iniciada para {user}")
            st.rerun()
        else:
            log_error(f"ALERTA: Falha de autenticação para o usuário {user}.")
            st.error("Acesso Negado.")

def login_required(func):
    """Decorator para uso futuro em funções específicas."""
    def wrapper(*args, **kwargs):
        if not st.session_state.get("is_admin"):
            render_login()
            return
        return func(*args, **kwargs)
    return wrapper
