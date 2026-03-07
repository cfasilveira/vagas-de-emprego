import streamlit as st
from .handlers import realizar_inscricao
from src.database.config import get_db
from src.database.models import Vaga

def render_candidate_portal():
    st.header("🎯 Portal de Oportunidades")
    
    if "vaga_id" in st.session_state:
        render_formulario_inscricao()
        return

    with get_db() as db:
        vagas = db.query(Vaga).filter(Vaga.ativo == True).all()
        if not vagas:
            st.info("Nenhuma vaga aberta no momento.")
            return

        for v in vagas:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(v.titulo)
                    # Localização Completa: Cidade - UF
                    st.write(f"📍 {v.cidade} - {v.uf.sigla if v.uf else ''} | 💰 R$ {v.salario:,.2f}")
                
                with col2:
                    if st.button("Quero me candidatar", key=f"btn_{v.id}", width='stretch'):
                        st.session_state.vaga_id = v.id
                        st.rerun()

                exp = st.expander("Ver Detalhes")
                exp.write(v.descricao if v.descricao else "Sem descrição.")

def render_formulario_inscricao():
    vaga_id = st.session_state.vaga_id
    if st.button("⬅️ Voltar para Vagas"):
        del st.session_state.vaga_id
        st.rerun()

    st.divider()
    st.subheader(f"📝 Inscrição: Vaga #{vaga_id}")
    
    with st.form("form_inscricao", clear_on_submit=True):
        col_n, col_e = st.columns(2)
        nome = col_n.text_input("Nome Completo")
        email = col_e.text_input("E-mail")
        
        col_d, col_t, col_g = st.columns([2, 2, 1])
        doc = col_d.text_input("CPF")
        tel = col_t.text_input("Celular / WhatsApp", placeholder="(00) 00000-0000")
        gen = col_g.selectbox("Gênero", ["Masculino", "Feminino"])
        
        pitch = st.text_area("Seu Pitch (Por que contratar você?)")
        
        if st.form_submit_button("Confirmar Candidatura", type="primary"):
            if not (nome and email and doc and tel and pitch):
                st.error("Preencha todos os campos obrigatórios!")
                return
                
            dados = {
                'nome': nome, 'email': email, 'documento': doc, 
                'telefone': tel, 'genero': gen, 'resumo': pitch
            }
            if realizar_inscricao(vaga_id, dados):
                st.success("✅ Candidatura enviada com sucesso!")
                del st.session_state.vaga_id
                st.rerun()
