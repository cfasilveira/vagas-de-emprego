import streamlit as st
from src.database import init_db
from src.logger import log_audit
from src.admin.auth import check_password  # Proteção de acesso
from src.admin.views import render_admin_portal  # Maestro das abas
from src.candidate import render_candidate_portal

# 1. Configuração ÚNICA de Página (Evita erro de re-chamada)
st.set_page_config(
    page_title="Sistema de Vagas Inteligente",
    page_icon="🎯",
    layout="wide"
)

def main():
    try:
        # 2. Inicialização do Banco de Dados
        init_db()
        
        # 3. Sidebar Personalizada
        st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063376.png", width=80)
        st.sidebar.title("🚀 Navegação")
        
        portal = st.sidebar.selectbox(
            "Selecione o Portal:",
            ["Candidato: Buscar Vagas", "Admin: Painel de Controle"]
        )
        
        st.sidebar.markdown("---")
        st.sidebar.info("🤖 IA Engine: Ollama (Mistral/Llama)")

        # 4. Roteamento com Validação de Segurança
        if portal == "Candidato: Buscar Vagas":
            render_candidate_portal()
        
        elif portal == "Admin: Painel de Controle":
            # Integração: Só chama o views.py se o login for bem-sucedido
            if check_password():
                render_admin_portal() 

    except Exception as e:
        st.error("Erro crítico na inicialização.")
        log_audit(f"Falha no boot: {str(e)}")

if __name__ == "__main__":
    main()
