import streamlit as st
import pandas as pd
import plotly.express as px
import re
from src.database.config import get_db
from src.database.models import Inscricao, Candidato, Vaga, UF
from sqlalchemy import func

def extrair_score(fb):
    if not fb: return 0
    match = re.search(r"(\d+)\s*%", fb)
    return int(match.group(1)) if match else 0

def render_analytics_dashboard():
    st.subheader("📊 BI Operacional - Painéis de Performance")
    with get_db() as db:
        # --- 1. KPIs GLOBAIS (Não alteradas) ---
        st.markdown("### 💼 Painel de Vagas (Global)")
        v1, v2, v3, v4 = st.columns(4)
        
        total_vagas = db.query(Vaga).count()
        total_cands = db.query(Candidato).count()
        vagas_com_insc = db.query(Inscricao.vaga_id).distinct().count()
        perc_insc = (vagas_com_insc / total_vagas * 100) if total_vagas > 0 else 0
        vaga_top = db.query(Vaga.titulo, func.count(Vaga.id)).group_by(Vaga.titulo).order_by(func.count(Vaga.id).desc()).first()
        
        v1.metric("Vagas Oferecidas", total_vagas)
        v2.metric("Total Candidatos", total_cands)
        v3.metric("% Vagas c/ Inscrição", f"{perc_insc:.1f}%")
        if vaga_top:
            v4.metric("Vaga mais Frequente", f"{vaga_top[0]}", f"{vaga_top[1]} ocorrências")

        st.divider()

        # --- 2. FILTRO POR UF ---
        ufs = db.query(UF).order_by(UF.sigla).all()
        lista_uf = ["Todas"] + [u.sigla for u in ufs]
        uf_sel = st.selectbox("📍 Filtrar Gráficos por UF:", lista_uf)

        # Queries cirúrgicas: definimos explicitamente o caminho do JOIN
        # Candidato -> Vaga -> UF
        q_cands = db.query(Candidato.genero, Candidato.score_ia, Vaga.titulo).select_from(Candidato).join(Vaga).join(UF)
        q_vagas = db.query(Vaga.titulo).select_from(Vaga).join(UF)
        
        if uf_sel != "Todas":
            q_cands = q_cands.filter(UF.sigla == uf_sel)
            q_vagas = q_vagas.filter(UF.sigla == uf_sel)

        df_cands = pd.read_sql(q_cands.statement, db.bind)
        df_vagas = pd.read_sql(q_vagas.statement, db.bind)

        # --- 3. GRÁFICOS (Filtro UF aplicado + Estilo Limpo) ---
        col_l, col_r = st.columns(2)

        with col_l:
            if not df_cands.empty:
                df_score = df_cands.groupby("titulo")["score_ia"].mean().reset_index()
                fig1 = px.bar(df_score, x="titulo", y="score_ia", text_auto='.0f', title="Média de Score por Vaga")
                fig1.update_traces(textposition="outside", marker_color="#00CC96")
                fig1.update_layout(yaxis=dict(showgrid=False, showticklabels=False, title=""),
                                 xaxis=dict(showgrid=False, title=""), plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig1, width="stretch")
            
            if not df_vagas.empty:
                df_rank = df_vagas["titulo"].value_counts().reset_index()
                df_rank.columns = ["Vaga", "Qtd"]
                fig2 = px.bar(df_rank, x="Qtd", y="Vaga", orientation='h', text_auto=True, title="Ranking de Vagas")
                fig2.update_traces(textposition="outside")
                fig2.update_layout(xaxis=dict(showgrid=False, showticklabels=False, title=""),
                                 yaxis=dict(showgrid=False, title=""), plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig2, width="stretch")

        with col_r:
            if not df_cands.empty:
                df_gen = df_cands["genero"].value_counts().reset_index()
                df_gen.columns = ["Gênero", "Qtd"]
                df_gen["Gênero"] = df_gen["Gênero"].replace({"M": "Masculino", "F": "Feminino"})
                fig3 = px.pie(df_gen, names="Gênero", values="Qtd", title="Gênero", hole=.3)
                st.plotly_chart(fig3, width="stretch")

            # Evolução Temporal (Global - Independente do filtro)
            df_time = pd.read_sql(db.query(Candidato.data).statement, db.bind)
            if not df_time.empty:
                df_time["data"] = pd.to_datetime(df_time["data"]).dt.date
                df_evol = df_time.groupby("data").size().reset_index(name="Qtd")
                fig4 = px.line(df_evol, x="data", y="Qtd", title="Tendência Global")
                fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
                st.plotly_chart(fig4, width="stretch")

def render_inscritos_list():
    # Função original preservada integralmente para não quebrar a listagem
    st.subheader("🏆 Ranking de Aderência (IA)")
    with get_db() as db:
        vagas = db.query(Vaga).all()
        if not vagas: return
        opcoes = {f"{v.titulo} ({v.cidade})": v.id for v in vagas}
        sel = st.selectbox("Selecione a Vaga para o Ranking:", list(opcoes.keys()))
        v_id = opcoes[sel]
        inscs = db.query(Inscricao).filter(Inscricao.vaga_id == v_id).all()
        if not inscs:
            st.info("Nenhum inscrito.")
            return
        dados = [{"Score": extrair_score(i.feedback_ia), "Nome": i.candidato.nome, "IA": i.feedback_ia, "Contato": i.candidato.celular} for i in inscs]
        df = pd.DataFrame(dados).sort_values(by="Score", ascending=False)
        for _, row in df.iterrows():
            with st.expander(f"⭐ {row['Score']}% - {row['Nome']}"):
                st.write(row['IA'])
                if row['Contato']:
                    st.link_button("WhatsApp", f"https://wa.me/55{re.sub(r'\D', '', row['Contato'])}")
