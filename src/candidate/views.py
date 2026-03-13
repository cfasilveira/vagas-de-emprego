import streamlit as st
import re
from src.database.config import SessionLocal
from src.database.models import Candidato, Vaga
from src.ai_service import AIService

def validar_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def render_candidate_portal():
    st.title("🚀 Portal de Oportunidades")
    db = SessionLocal()
    try:
        vagas = db.query(Vaga).filter(Vaga.ativa == True).all()
        if not vagas:
            st.warning("No momento não há vagas abertas.")
            return

        col_detalhe, col_lista = st.columns([0.6, 0.4])
        with col_lista:
            st.subheader("📌 Vagas Abertas")
            vaga_nomes = [v.titulo for v in vagas]
            escolha = st.radio("Selecione:", vaga_nomes, label_visibility="collapsed")
            vaga_sel = next(v for v in vagas if v.titulo == escolha)

        with col_detalhe:
            st.subheader("📄 Detalhes da Vaga")
            st.markdown(f"### {vaga_sel.titulo}")
            
            # Cidade e UF na mesma linha
            c1, c2 = st.columns(2)
            c1.write(f"**📍 Cidade:** {vaga_sel.cidade}")
            c2.write(f"**🚩 UF:** {vaga_sel.uf.sigla}")
            
            st.write(f"**Descrição:** {vaga_sel.descricao}")
            if st.button("✅ Quero me candidatar", width="stretch"):
                st.session_state.vaga_id_selecionada = vaga_sel.id
                st.session_state.abrir_formulario = True

        if st.session_state.get("abrir_formulario") and st.session_state.get("vaga_id_selecionada") == vaga_sel.id:
            st.divider()
            with st.form("cadastro_candidatura", clear_on_submit=True):
                st.subheader("📝 Sua Inscrição")
                nome = st.text_input("Nome Completo")
                email = st.text_input("E-mail")
                
                # Cidade e UF na mesma linha no formulário
                f1, f2 = st.columns([0.7, 0.3])
                with f1: cid_in = st.text_input("Sua Cidade", value=vaga_sel.cidade)
                with f2: uf_in = st.text_input("UF", value=vaga_sel.uf.sigla, disabled=True)
                
                celular = st.text_input("Celular (Obrigatório)")
                genero = st.selectbox("Gênero", ["Masculino", "Feminino"])
                resumo = st.text_area("Resumo Profissional / Currículo", height=150)
                
                if st.form_submit_button("Finalizar Candidatura"):
                    if not nome or not validar_email(email) or not celular or len(resumo) < 15:
                        st.error("Verifique os campos obrigatórios.")
                    else:
                        with st.spinner("Analisando perfil..."):
                            ai = AIService()
                            analise = ai.analisar_candidato(vaga_sel.titulo, vaga_sel.descricao, resumo)
                            score = 0
                            if "SCORE:" in analise.upper():
                                try: score = int(''.join(filter(str.isdigit, analise.upper().split("SCORE:")[1].split("%")[0])))
                                except: score = 0

                            novo = Candidato(
                                nome=nome, email=email.lower(), celular=celular, # Corrigido aqui
                                genero=genero, resumo=resumo, vaga_id=vaga_sel.id,
                                score_ia=score, parecer_ia=analise
                            )
                            db.add(novo)
                            db.commit()
                            st.success("Candidatura enviada com sucesso!")
                            st.session_state.abrir_formulario = False
                            st.rerun()
    finally:
        db.close()
