import streamlit as st
import pandas as pd
import re
from sqlalchemy.orm import joinedload
from src.database.config import SessionLocal
from src.database.models import Vaga, Candidato, Inscricao, UF

def extrair_score_txt(texto):
    if not texto: return None
    match = re.search(r'(\d+)%', texto)
    return f"{match.group(1)}%" if match else None

def render_admin_portal():
    with st.sidebar:
        st.divider()
        if st.button("Sair do Sistema", key="logout_sidebar", type="primary", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()

    st.title("🎯 Painel de Controle RH IA")
    
    db = SessionLocal()
    try:
        inscricoes = db.query(Inscricao).options(
            joinedload(Inscricao.candidato),
            joinedload(Inscricao.vaga).joinedload(Vaga.uf)
        ).all()

        tabs = st.tabs(["👥 Candidatos", "🔍 Análise Profunda", "📊 Dashboard", "➕ Controle de Vagas"])

        with tabs[0]:
            st.subheader("📋 Lista Geral de Inscritos")
            if inscricoes:
                dados_tab = []
                for i in inscricoes:
                    sc = extrair_score_txt(i.feedback_ia) or f"{i.candidato.score_ia or 0}%"
                    gen = "Masculino" if i.candidato.genero in ['M', 'Masculino'] else "Feminino"
                    dados_tab.append({
                        "Candidato": i.candidato.nome,
                        "Vaga": i.vaga.titulo,
                        "Cidade": i.vaga.cidade,
                        "Gênero": gen,
                        "Score IA": sc
                    })
                # hide_index=True remove a primeira coluna de IDs automáticos
                st.dataframe(pd.DataFrame(dados_tab), width="stretch", hide_index=True)
            else:
                st.info("Nenhum candidato inscrito.")

        with tabs[1]:
            st.subheader("🔍 Detalhamento Individual")
            if inscricoes:
                opcoes = {f"{i.candidato.nome} ({i.vaga.titulo})": i for i in inscricoes}
                sel = st.selectbox("Selecione para analisar:", list(opcoes.keys()))
                ins = opcoes[sel]
                
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**📍 Local:** {ins.vaga.cidade} ({ins.vaga.uf.sigla if ins.vaga.uf else 'N/A'})")
                    gen_f = "Masculino" if ins.candidato.genero in ['M', 'Masculino'] else "Feminino"
                    st.write(f"**👤 Gênero:** {gen_f}")
                with c2:
                    st.write(f"**📞 Contato:** {ins.candidato.celular}")
                    st.write(f"**📧 Email:** {ins.candidato.email}")
                
                st.divider()
                col_res, col_ia = st.columns(2)
                with col_res:
                    st.info(f"**📝 Resumo do Candidato:**\n\n{ins.candidato.resumo or 'N/A'}")
                with col_ia:
                    st.success(f"**🧠 Parecer da IA:**\n\n{ins.feedback_ia or 'Aguardando...'}")
            else:
                st.warning("Sem dados para análise profunda.")

        with tabs[2]:
            from src.admin.comp_candidatos import render_analytics_dashboard
            render_analytics_dashboard()

        with tabs[3]:
            from src.admin.comp_vagas import render_vagas_manager
            render_vagas_manager()
            
    finally:
        db.close()
