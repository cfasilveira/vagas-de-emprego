import streamlit as st
from src.database.config import get_db
from src.database.models import Vaga, UF

def render_vaga_form():
    st.subheader("📢 Publicar Nova Oportunidade")
    
    # 1. Busca as UFs de forma segura
    try:
        with get_db() as db:
            lista_ufs = db.query(UF).order_by(UF.sigla).all()
            opcoes_uf = {f"{u.sigla} - {u.nome}": u.id for u in lista_ufs}
    except Exception as e:
        st.error(f"Erro ao carregar estados: {e}")
        opcoes_uf = {}

    if not opcoes_uf:
        st.warning("⚠️ Nenhuma UF encontrada no banco. Por favor, rode o script de seed.")
        return

    # 2. Formulário Streamlit
    with st.form("form_vaga", clear_on_submit=True):
        titulo = st.text_input("Título da Vaga*", placeholder="Ex: Desenvolvedor Fullstack")
        cidade = st.text_input("Cidade*", placeholder="Ex: Goiânia")
        uf_selecionada = st.selectbox("Estado/UF*", options=list(opcoes_uf.keys()))
        salario = st.number_input("Salário (R$)", min_value=0.0, step=100.0)
        prazo = st.date_input("Prazo de Inscrição")
        descricao = st.text_area("Descrição Detalhada e Requisitos*")
        
        if st.form_submit_button("✅ Salvar e Publicar Vaga"):
            if not (titulo and descricao and cidade):
                st.error("Preencha todos os campos obrigatórios!")
                return

            try:
                with get_db() as db:
                    nova_vaga = Vaga(
                        titulo=titulo, 
                        cidade=cidade,
                        uf_id=opcoes_uf[uf_selecionada],
                        salario=salario,
                        descricao=descricao,
                        data_termino=prazo,
                        ativo=True
                    )
                    db.add(nova_vaga)
                    db.commit()
                    st.success("Vaga publicada com sucesso!")
                    st.rerun()
            except Exception as e:
                st.error(f"☢️ Erro ao persistir dados: {e}")
