import streamlit as st
import traceback
from src.database import init_db
from src.admin.auth import check_password
from src.admin.views import render_admin_portal
from src.candidate.views import render_candidate_portal

st.set_page_config(page_title="Sistema de Vagas", page_icon="🎯", layout="wide")

def main():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063376.png", width=80)
    st.sidebar.title("🚀 Navegação")
    portal = st.sidebar.selectbox("Selecione o Portal:", ["Candidato: Buscar Vagas", "Admin: Painel de Controle"])
    st.sidebar.markdown("---")
    
    # Apelo Comercial solicitado
    st.sidebar.success("🤖 IA Mistral-Nemo 7.1 GB ativada!")

    try:
        init_db()
        if portal == "Candidato: Buscar Vagas":
            render_candidate_portal()
        else:
            if check_password():
                render_admin_portal()
    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"❌ DEBUG ERROR:\n{error_msg}")
        st.error(f"Ocorreu um erro inesperado. Verifique os logs.")

if __name__ == "__main__":
    main()
