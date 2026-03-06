import streamlit as st
import traceback
from src.database import init_db  # Corrigido: Importa do pacote database, não do config
from src.logger import log_audit
from src.admin.auth import check_password
from src.admin.views import render_admin_portal
from src.candidate.views import render_candidate_portal

st.set_page_config(page_title="Sistema de Vagas", page_icon="🎯", layout="wide")

def main():
    # 1. Barra Lateral (Sempre visível)
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063376.png", width=80)
    st.sidebar.title("🚀 Navegação")
    portal = st.sidebar.selectbox("Selecione o Portal:", ["Candidato: Buscar Vagas", "Admin: Painel de Controle"])
    st.sidebar.markdown("---")
    
    # Lógica de Status de IA na Sidebar Global (Exorcizando o Qwen)
    if st.session_state.get('is_admin'):
        st.sidebar.success("🤖 Mistral-Nemo (12B) Ativo")
    else:
        st.sidebar.info("🤖 Engine de Recrutamento Ativa")

    # 2. Lógica de Portais (Protegida)
    try:
        init_db()  # Agora ele vai encontrar a função
        if portal == "Candidato: Buscar Vagas":
            render_candidate_portal()
        else:
            if check_password():
                render_admin_portal()
    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"❌ DEBUG BOOT ERROR:\n{error_msg}")
        st.error("Erro na conexão com o banco de dados.")
        st.info("Verifique se o container 'db' está rodando.")

if __name__ == "__main__":
    main()
