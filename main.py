import streamlit as st
from src.candidate.views import render_candidate_portal
from src.admin.auth import render_login_page
from src.admin.views import render_admin_portal

st.set_page_config(page_title="RH IA", page_icon="🎯", layout="wide")

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

def main():
    with st.sidebar:
        st.title("🚀 Navegação")
        # Mantendo os nomes originais conforme solicitado
        escolha = st.radio("Ir para:", ["Portal do Candidato", "Área Administrativa"])
        st.divider()

    if escolha == "Portal do Candidato":
        render_candidate_portal()
    else:
        if not st.session_state.is_admin:
            render_login_page()
        else:
            render_admin_portal()

if __name__ == "__main__":
    main()
