import streamlit as st
from src.database.config import get_db
from src.database.models import Vaga

def render_vagas_table():
    """Renderiza a tabela de vagas cadastradas (Aba 2)."""
    try:
        with next(get_db()) as db:
            vagas = db.query(Vaga).all()
            if not vagas:
                return st.info("📭 Nenhuma vaga no sistema.")
            
            lista_vagas = [{
                "ID": v.id,
                "Título": v.nome,
                "Local": v.localidade,
                "Salário": f"R$ {v.salario:,.2f}"
            } for v in vagas]
            st.table(lista_vagas)
    except Exception as e:
        st.error(f"Erro ao carregar vagas: {e}")
