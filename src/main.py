import streamlit as st
from src.database import init_db
from src.logger import log_audit

# Configuração de Página (Web Design Moderno)
st.set_page_config(page_title="Sistema de Vagas", layout="wide")

def main():
    try:
        # Health Check e Inicialização
        init_db()
        log_audit("Sistema iniciado e tabelas verificadas.")
        
        st.title("🎯 Portal de Vagas")
        st.sidebar.info("Sistema Modular Seguro")
        
        st.write("Bem-vindo. Selecione uma vaga ou acesse como administrador.")
        
    except Exception as e:
        st.error("Erro crítico de conexão. Verifique os logs do sistema.")
        log_error(f"Falha no boot: {str(e)}")

if __name__ == "__main__":
    main()
