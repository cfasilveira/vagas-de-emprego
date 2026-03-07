import streamlit as st
from src.database.config import get_db
from src.database.models import Vaga, UF

def render_publicar_vaga():
    st.subheader("📢 Anunciar Nova Oportunidade")
    
    with get_db() as db:
        ufs = db.query(UF).all()
        lista_ufs = {u.sigla: u.id for u in ufs}

        with st.form("form_vaga", clear_on_submit=True):
            col1, col2 = st.columns([2, 1])
            titulo = col1.text_input("Título da Vaga", placeholder="Ex: Desenvolvedor Python")
            salario = col2.number_input("Salário Oferecido (R$)", min_value=0.0, step=100.0)

            col3, col4 = st.columns(2)
            cidade = col3.text_input("Cidade")
            uf_sigla = col4.selectbox("Estado (UF)", list(lista_ufs.keys()))

            descricao = st.text_area("Descrição da Vaga e Requisitos")

            if st.form_submit_button("🚀 Publicar Vaga"):
                if not titulo or not descricao or not cidade:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                else:
                    nova_vaga = Vaga(
                        titulo=titulo,
                        descricao=descricao,
                        cidade=cidade,
                        salario=salario,
                        uf_id=lista_ufs[uf_sigla],
                        ativo=True
                    )
                    db.add(nova_vaga)
                    db.commit()
                    st.success(f"Vaga '{titulo}' publicada com sucesso!")
                    st.balloons()
