import streamlit as st
from .forms import render_vaga_form
from .comp_candidatos import render_inscritos_list, render_analytics_dashboard
from .comp_vagas import render_raw_database_tables

def render_admin_portal():
    """
    Função principal chamada pelo main.py.
    Orquestra as abas do painel administrativo.
    """
    # 1. Configuração da Sidebar (Logout)
    with st.sidebar:
        st.header("🔐 Painel Admin")
        st.divider()
        if st.button("🚪 Encerrar Sessão", type="primary", width='stretch'):
            st.session_state.is_admin = False
            st.rerun()
    
    # 2. FAIL FIRST: Interface de Navegação por Abas
    # Se algum componente falhar, apenas a aba dele apresentará erro
    tab1, tab2, tab3, tab4 = st.tabs([
        "📢 Publicar Vaga", 
        "👥 Candidatos", 
        "📈 Dashboard", 
        "🔍 Tabelas"
    ])
    
    with tab1:
        render_vaga_form()
    
    with tab2:
        render_inscritos_list()
        
    with tab3:
        render_analytics_dashboard()
        
    with tab4:
        render_raw_database_tables()
