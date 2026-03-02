import streamlit as st
from src.database.config import get_db
from src.database.models import Inscricao
from .forms import render_vaga_form

def render_admin_portal():
    # CSS Curto para botão redondo
    st.markdown("<style>[data-testid='stSidebar'] button {border-radius: 50px !important;}</style>", unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛡️ Admin")
        if st.button("🚪 Sair", type="primary", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()

    tab1, tab2 = st.tabs(["📝 Nova Vaga", "👥 Candidatos"])
    with tab1: render_vaga_form()
    with tab2: render_inscritos()

def render_inscritos():
    with next(get_db()) as db:
        inscricoes = db.query(Inscricao).all()
        if not inscricoes: return st.info("Sem inscritos.")

        for inc in inscricoes:
            with st.expander(f"👤 {inc.candidato.nome} | {inc.vaga.titulo}"):
                st.write(f"📍 {inc.vaga.cidade}-{inc.vaga.uf.sigla} | 📧 {inc.candidato.email}")
