import streamlit as st
from src.database.config import get_db
from src.database.models import Administrador
from src.security import Security

def render_login_page():
    st.subheader("🔐 Acesso Administrativo")
    
    with st.container(border=True):
        user = st.text_input("Usuário", key="admin_user")
        password = st.text_input("Senha", type="password", key="admin_pass")
        
        if st.button("Entrar", type="primary", width="stretch"):
            with get_db() as db:
                admin = db.query(Administrador).filter(Administrador.login == user).first()
                
                if admin and Security.verificar_senha(password, admin.senha_hash):
                    st.session_state.is_admin = True
                    st.success("Logado com sucesso!")
                    st.rerun()
                else:
                    st.error("Credenciais Inválidas.")
