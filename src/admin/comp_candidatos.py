import streamlit as st
import pandas as pd
import plotly.express as px
import re
from src.database.config import get_db
from src.database.models import Inscricao, Candidato, Vaga, UF
from sqlalchemy import func

def render_analytics_dashboard():
    st.subheader("📊 BI Operacional - Painéis de Performance")
    with get_db() as db:
        # --- PAINEL 1: VAGAS ---
        st.markdown("### 💼 Painel de Vagas")
        v1, v2, v3, v4 = st.columns(4)
        
        total_vagas = db.query(Vaga).count()
        total_cands = db.query(Candidato).count()
        vagas_com_insc = db.query(Inscricao.vaga_id).distinct().count()
        perc_insc = (vagas_com_insc / total_vagas * 100) if total_vagas > 0 else 0
        
        # Vaga que mais aparece
        vaga_top = db.query(Vaga.titulo, func.count(Vaga.id)).group_by(Vaga.titulo).order_by(func.count(Vaga.id).desc()).first()
        
        v1.metric("Vagas Oferecidas", total_vagas)
        v2.metric("Total Candidatos", total_cands)
        v3.metric("% Vagas c/ Inscrição", f"{perc_insc:.1f}%")
        if vaga_top:
            v4.metric("Vaga mais Frequente", f"{vaga_top[0]}", f"{vaga_top[1]} ocorrências", delta_color="normal")

        st.divider()

        # --- PAINEL 2: UFs ---
        st.markdown("### 📍 Painel de UFs")
        u1, u2, u3, u4 = st.columns(4)
        
        # Queries para UFs
        uf_vagas = db.query(UF.sigla, func.count(Vaga.id)).join(Vaga).group_by(UF.sigla).order_by(func.count(Vaga.id).desc()).all()
        uf_cands = db.query(UF.sigla, func.count(Candidato.id)).select_from(UF).join(Vaga).join(Candidato).group_by(UF.sigla).order_by(func.count(Candidato.id).desc()).all()

        if uf_vagas:
            u1.metric("UF c/ Mais Vagas", f"{uf_vagas[0][0]}", f"{uf_vagas[0][1]} vagas")
            u3.metric("UF c/ Menos Vagas", f"{uf_vagas[-1][0]}", f"{uf_vagas[-1][1]} vagas")
        
        if uf_cands:
            u2.metric("UF c/ Mais Candidatos", f"{uf_cands[0][0]}", f"{uf_cands[0][1]} total")
            u4.metric("UF c/ Menos Candidatos", f"{uf_cands[-1][0]}")

def extrair_score(fb):
    if not fb: return 0
    match = re.search(r"(\d+)\s*%", fb)
    return int(match.group(1)) if match else 0

def render_inscritos_list():
    st.subheader("🏆 Ranking de Aderência (IA)")
    with get_db() as db:
        vagas = db.query(Vaga).all()
        if not vagas:
            st.warning("Cadastre uma vaga para ver o ranking.")
            return

        opcoes = {f"{v.titulo} ({v.cidade})": v.id for v in vagas}
        sel = st.selectbox("Filtrar por Vaga:", list(opcoes.keys()))
        v_id = opcoes[sel]

        inscs = db.query(Inscricao).filter(Inscricao.vaga_id == v_id).all()
        if not inscs:
            st.info("Nenhum inscrito para esta vaga.")
            return

        dados = []
        for i in inscs:
            dados.append({
                "Score": extrair_score(i.feedback_ia),
                "Nome": i.candidato.nome,
                "IA": i.feedback_ia,
                "Contato": i.candidato.celular
            })
        
        df = pd.DataFrame(dados).sort_values(by="Score", ascending=False)
        for _, row in df.iterrows():
            with st.expander(f"⭐ {row['Score']}% - {row['Nome']}"):
                st.write(f"**Análise Comportamental:**\n\n{row['IA']}")
                if row['Contato']:
                    st.link_button(f"Falar com Candidato (WhatsApp)", f"https://wa.me/55{re.sub(r'\D', '', row['Contato'])}")
