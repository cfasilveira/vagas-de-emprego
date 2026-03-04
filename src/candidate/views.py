import streamlit as st
from src.database.config import get_db
from src.database.models import Vaga
from .handlers import realizar_inscricao

def render_candidate_portal():
    st.header("🎯 Portal do Candidato")
    try:
        with get_db() as db:
            # O lazy='joined' no models.py garante que vaga.uf funcione aqui
            vagas = db.query(Vaga).filter(Vaga.ativo == True).all()
            
            if "vaga_selecionada" in st.session_state:
                render_formulario_inscricao()
            else:
                exibir_cards_vagas(vagas)
    except Exception as e:
        st.error(f"Erro ao carregar vagas: {e}")

def exibir_cards_vagas(vagas):
    if not vagas:
        return st.info("No momento, não temos vagas abertas.")

    for vaga in vagas:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"🚀 {vaga.titulo}")
                # Aqui vaga.uf.sigla agora funciona sempre!
                st.caption(f"📍 {vaga.cidade} - {vaga.uf.sigla} | 📅 Prazo: {vaga.data_termino}")
            with col2:
                st.write(f"### R$ {vaga.salario:,.2f}")
                if st.button("Candidate-se", key=f"btn_{vaga.id}"):
                    st.session_state.vaga_selecionada = {"id": vaga.id, "titulo": vaga.titulo, "descricao": vaga.descricao}
                    st.rerun()
            with st.expander("Ver detalhes"):
                st.write(vaga.descricao)

def render_formulario_inscricao():
    # ... (restante do código do formulário permanece igual) ...
    vaga = st.session_state.vaga_selecionada
    if st.button("⬅️ Voltar"):
        del st.session_state.vaga_selecionada
        st.rerun()
    st.write(f"Inscrição para: {vaga['titulo']}")
    # (Omitido por brevidade, mas deve seguir o padrão original)
