import streamlit as st
from .forms import render_vaga_form
from .comp_candidatos import render_inscritos_list, render_analytics_dashboard
from .comp_vagas import render_raw_database_tables, render_vagas_manager

def render_admin_portal():
    # Removido st.sidebar.success daqui para evitar duplicidade com main.py
    with st.sidebar:
        st.header("🔐 Painel Admin")
        st.divider()
        if st.button("🚪 Encerrar Sessão", type="primary", width='stretch'):
            st.session_state.clear()
            st.session_state.is_admin = False
            st.rerun()
    
    tabs = st.tabs([
        "📢 Publicar Vaga", 
        "🏆 Ranking & Contato", 
        "📊 Dashboard BI", 
        "⚙️ Gestão de Vagas", 
        "🔍 Auditoria Bruta"
    ])
    
    with tabs[0]: render_vaga_form()
    with tabs[1]: render_inscritos_list()
    with tabs[2]: render_analytics_dashboard()
    with tabs[3]: render_vagas_manager()
    with tabs[4]: render_raw_database_tables()
