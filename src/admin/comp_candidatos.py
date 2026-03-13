import streamlit as st
from src.database.config import get_db
from src.database.models import Candidato, Vaga

def render_inscritos_list():
    st.subheader("👥 Candidatos por Vaga")
    with get_db() as db:
        vagas = db.query(Vaga).all()
        if not vagas:
            st.info("Nenhuma vaga cadastrada.")
            return
            
        v_sel = st.selectbox("Selecione a Vaga:", vagas, format_func=lambda x: x.titulo)
        cands = db.query(Candidato).filter(Candidato.vaga_id == v_sel.id).all()
        
        for c in cands:
            with st.expander(f"{c.nome} - Score: {c.score_ia}%"):
                st.write(f"**📍 Localização:** {c.vaga.cidade} / {c.vaga.uf.sigla}")
                st.write(f"**Resumo:** {c.resumo}")
                st.info(f"**Parecer IA:** {c.parecer_ia}")
                st.write(f"**Contato:** {c.email} | {c.celular}") # Corrigido aqui
