import streamlit as st
import re
from src.database.config import SessionLocal
from src.database.models import Candidato, Vaga, UF
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
            escolha = st.radio("Selecione:", [v.titulo for v in vagas], label_visibility="collapsed")
            vaga_sel = next(v for v in vagas if v.titulo == escolha)

        with col_detalhe:
            st.subheader("📄 Detalhes da Vaga")
            st.markdown(f"### {vaga_sel.titulo}")
            st.write(f"**📍 Local:** {vaga_sel.cidade} - {vaga_sel.uf.sigla}")
            st.write(f"**Descrição:** {vaga_sel.descricao}")
            if st.button("✅ Quero me candidatar", use_container_width=True):
                st.session_state.abrir_formulario = True
                st.session_state.vaga_id_selecionada = vaga_sel.id

        if st.session_state.get("abrir_formulario") and st.session_state.get("vaga_id_selecionada") == vaga_sel.id:
            st.divider()
            with st.form("candidatura", clear_on_submit=True):
                nome = st.text_input("Nome Completo")
                email = st.text_input("E-mail")
                f1, f2 = st.columns([0.7, 0.3])
                with f1: cid_in = st.text_input("Sua Cidade")
                with f2: uf_in = st.selectbox("UF", db.query(UF).all(), format_func=lambda x: x.sigla)
                celular = st.text_input("Celular")
                genero = st.selectbox("Gênero", ["Masculino", "Feminino"])
                resumo = st.text_area("Resumo Profissional", height=150)
                
                if st.form_submit_button("Finalizar Candidatura", use_container_width=True):
                    if not nome or not validar_email(email) or len(resumo) < 15:
                        st.error("Preencha todos os campos corretamente.")
                    else:
                        # 1. Salva imediatamente para liberar o candidato
                        novo_candidato = Candidato(
                            nome=nome, 
                            email=email.lower(), 
                            celular=celular, 
                            genero=genero, 
                            resumo=resumo, 
                            vaga_id=vaga_sel.id, 
                            score_ia=0, 
                            parecer_ia="Processando análise..."
                        )
                        db.add(novo_candidato)
                        db.commit()
                        db.refresh(novo_candidato)
                        
                        st.success("✅ Inscrição recebida! Você já pode fechar esta página.")
                        
                        # 2. Processa a IA logo após o commit (ainda no fluxo, mas após salvar)
                        # Em um app de alta escala usaríamos Celery/Redis, aqui fazemos o "pós-save"
                        try:
                            analise = AIService().analisar_candidato(vaga_sel.titulo, vaga_sel.descricao, resumo)
                            score = 0
                            if "SCORE:" in analise.upper():
                                try:
                                    score = int(''.join(filter(str.isdigit, analise.upper().split("SCORE:")[1].split("%")[0])))
                                except: score = 0
                            
                            novo_candidato.score_ia = score
                            novo_candidato.parecer_ia = analise
                            db.commit()
                        except:
                            pass # Evita que erro na IA trave a experiência do usuário
                        
                        st.session_state.abrir_formulario = False
                        st.rerun()
    finally:
        db.close()
