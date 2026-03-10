import streamlit as st
from src.database.config import get_db
from src.database.models import Vaga, Candidato, Inscricao

def render_candidate_portal():
    st.markdown("""
        <style>
        .vaga-card {
            background-color: #ffffff; padding: 25px; border-radius: 15px;
            border: 1px solid #e6e9ef; box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            margin-bottom: 25px;
        }
        div.stButton > button {
            background-color: #00CC96 !important; color: white !important;
            font-weight: bold !important; border-radius: 8px !important; width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if "vaga_selecionada_id" not in st.session_state:
        st.session_state.vaga_selecionada_id = None

    if st.session_state.vaga_selecionada_id:
        v_id = st.session_state.vaga_selecionada_id
        with get_db() as db:
            vaga = db.query(Vaga).filter(Vaga.id == v_id).first()
            
            st.button("⬅️ Voltar", on_click=lambda: st.session_state.update({"vaga_selecionada_id": None}))
            st.subheader(f"Inscrição: {vaga.titulo}")
            
            with st.form("form_inscricao_completo"):
                c1, c2 = st.columns(2)
                with c1:
                    nome = st.text_input("Nome Completo")
                    email = st.text_input("E-mail")
                    cpf = st.text_input("CPF (apenas números)")
                with c2:
                    telefone = st.text_input("Celular (com DDD)")
                    genero = st.selectbox("Gênero", ["Feminino", "Masculino"])
                    endereco = st.text_input("Endereço Completo")
                
                resumo = st.text_area("Resumo Profissional / Competências")
                
                if st.form_submit_button("Confirmar Candidatura"):
                    if nome and email and cpf and resumo:
                        novo_c = Candidato(
                            nome=nome, email=email, documento=cpf, 
                            telefone=telefone, endereco=endereco,
                            genero=genero, resumo=resumo
                        )
                        db.add(novo_c)
                        db.flush()
                        db.add(Inscricao(candidato_id=novo_c.id, vaga_id=vaga.id, feedback_ia="Aguardando análise."))
                        db.commit()
                        st.success("✅ Candidatura enviada com sucesso!")
                        st.session_state.vaga_selecionada_id = None
                        st.rerun()
                    else:
                        st.error("Preencha os campos obrigatórios: Nome, Email, CPF e Resumo.")
    else:
        st.title("💼 Vagas em Aberto")
        with get_db() as db:
            vagas = db.query(Vaga).filter(Vaga.ativo == True).all()
            for vaga in vagas:
                with st.container():
                    st.markdown(f"""
                        <div class="vaga-card">
                            <h2 style='margin:0;'>{vaga.titulo}</h2>
                            <p style='color: #666;'>📍 {vaga.cidade if vaga.cidade else 'Remoto'}</p>
                            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #00CC96;">
                                {vaga.descricao}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Candidatar", key=f"btn_{vaga.id}"):
                        st.session_state.vaga_selecionada_id = vaga.id
                        st.rerun()
