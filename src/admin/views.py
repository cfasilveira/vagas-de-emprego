import streamlit as st
from src.database.config import get_db
from src.database.models import Inscricao, UF
from .forms import render_vaga_form

def render_admin_portal():
    st.markdown("<style>[data-testid='stSidebar'] button {border-radius: 50px !important;}</style>", unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛡️ Admin")
        if st.button("🚪 Sair", type="primary", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["📝 Nova Vaga", "👥 Candidatos", "📊 Gestão de Vagas"])
    
    with tab1: 
        render_vaga_form()
    
    with tab2: 
        render_inscritos()

    with tab3:
        render_lista_vagas()

def render_inscritos():
    with next(get_db()) as db:
        inscricoes = db.query(Inscricao).all()
        if not inscricoes: 
            return st.info("No momento não temos candidatos inscritos.")

        for inc in inscricoes:
            with st.expander(f"👤 {inc.candidato.nome} | {inc.vaga.titulo}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**📍 Local:** {inc.vaga.cidade}-{inc.vaga.uf.sigla}")
                    st.write(f"**📧 E-mail:** {inc.candidato.email}")
                    st.write(f"**⚤ Gênero:** {inc.candidato.genero}")
                with col2:
                    st.write(f"**📞 Celular:** {inc.candidato.celular}")
                    st.write(f"**🆔 Doc:** {inc.candidato.documento}")
                
                st.divider()
                st.write("**📝 Resumo do Candidato:**")
                st.write(inc.candidato.resumo)
                
                if inc.feedback_ia:
                    st.info(f"🤖 Análise IA: {inc.feedback_ia}")

def render_lista_vagas():
    from src.database.models import Vaga
    with next(get_db()) as db:
        vagas = db.query(Vaga).all()
        if not vagas:
            return st.warning("Nenhuma vaga cadastrada no sistema.")
        
        for v in vagas:
            st.text(f"ID: {v.id} | {v.titulo} ({v.cidade}/{v.uf.sigla})")
