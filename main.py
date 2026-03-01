import streamlit as st
from src.database import init_db
from src.admin import render_admin_panel

# 1. Configuração de Identidade Visual e Segurança de Página
st.set_page_config(
    page_title="Portal de Vagas Segura",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # 2. Health Check e Boot do Banco (Fail Fast)
    try:
        init_db()
    except Exception as e:
        st.error("⚠️ Falha crítica na conexão com o Banco de Dados.")
        return

    # 3. Menu de Navegação Lateral
    st.sidebar.title("🚀 Navegação Principal")
    app_mode = st.sidebar.selectbox(
        "Selecione o Portal:",
        ["Candidato: Buscar Vagas", "Admin: Gestão Interna"]
    )

    # 4. Roteamento Inteligente
    if app_mode == "Candidato: Buscar Vagas":
        st.title("🎯 Oportunidades Disponíveis")
        st.info("O módulo de candidatura será ativado na Fase 4 (IA DeepSeek integration).")
        
    elif app_mode == "Admin: Gestão Interna":
        # Chama o pacote modular que subdividimos (auth + forms)
        render_admin_panel()

if __name__ == "__main__":
    main()
