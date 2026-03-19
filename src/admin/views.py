import streamlit as st
import pandas as pd
import re
from sqlalchemy.orm import joinedload
from src.database.config import SessionLocal
from src.database.models import Vaga, Candidato, Inscricao, UF

def extrair_score(texto):
    if not texto: return None
    match = re.search(r'(\d+)%', texto)
    return f"{match.group(1)}%" if match else None

def render_admin_portal():
    with st.sidebar:
        st.divider()
        if st.button("🔴 Sair do Sistema", key="logout_sidebar", width="stretch"):
            st.session_state.is_admin = False
            st.rerun()

    st.title("🎯 Painel de Controle RH IA")
    
    db = SessionLocal()
    try:
        inscricoes = db.query(Inscricao).options(
            joinedload(Inscricao.candidato),
            joinedload(Inscricao.vaga).joinedload(Vaga.uf)
        ).all()

        # Alteração cirúrgica: 'Cadastrar Vaga' -> 'Controle de Vagas'
        tabs = st.tabs(["👥 Candidatos", "🔍 Análise Profunda", "📊 Dashboard", "➕ Controle de Vagas"])

        with tabs[0]:
            dados = []
            for i in inscricoes:
                sc_txt = extrair_score(i.feedback_ia)
                dados.append({
                    "Candidato": i.candidato.nome, "Vaga": i.vaga.titulo,
                    "Cidade": i.vaga.cidade or "N/I", "UF": i.vaga.uf.sigla if i.vaga.uf else "N/A",
                    "Score": sc_txt or f"{i.candidato.score_ia or 0}%"
                })
            st.dataframe(pd.DataFrame(dados), width="stretch")

        with tabs[1]:
            st.subheader("🔍 Análise Profunda")
            if inscricoes:
                opcoes = {f"{i.candidato.nome} ({i.vaga.titulo})": i for i in inscricoes}
                sel = st.selectbox("Selecione:", list(opcoes.keys()))
                ins = opcoes[sel]
                st.write(f"**📍 Localização:** {ins.vaga.cidade or 'Remoto'} - {ins.vaga.uf.sigla if ins.vaga.uf else ''}")
                st.write(f"**📞 Contato:** {ins.candidato.celular}")
                c_res, c_ia = st.columns(2)
                with c_res: st.info(f"**📝 Resumo:**\n\n{ins.resumo_submetido or 'N/A'}")
                with c_ia:
                    score_f = extrair_score(ins.feedback_ia) or f"{ins.candidato.score_ia or 0}%"
                    st.success(f"**🧠 Avaliação IA (Aderência: {score_f}):**\n\n{ins.feedback_ia or 'Pendente'}")
            else: st.warning("Sem dados.")

        with tabs[2]:
            from src.admin.comp_vagas import render_dashboard
            render_dashboard(inscricoes)

        with tabs[3]:
            from src.admin.comp_vagas import render_vagas_manager
            render_vagas_manager()
            
    finally:
        db.close()
