import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, UTC
from src.database.config import SessionLocal
from src.database.models import Vaga, Candidato, UF
from .comp_candidatos import render_inscritos_list

def render_admin_portal():
    st.title("🎯 Painel Administrativo")
    db = SessionLocal()
    try:
        with st.sidebar:
            if st.button("🚪 Sair", type="primary"):
                st.session_state.is_admin = False
                st.rerun()

        tabs = st.tabs(["📢 Vagas", "👥 Candidatos", "➕ Nova Vaga", "📊 BI"])

        with tabs[0]: # LISTAGEM COM FILTRO RESTAURADO
            vagas = db.query(Vaga).all()
            if vagas:
                agora = datetime.now(UTC)
                filtro_lista = st.selectbox("Filtrar por Título:", ["Todas"] + [v.titulo for v in vagas])
                vagas_filtradas = [v for v in vagas if filtro_lista == "Todas" or v.titulo == filtro_lista]
                
                tabela = []
                for v in vagas_filtradas:
                    scores = [c.score_ia for c in v.candidatos if c.score_ia is not None]
                    media = sum(scores) / len(scores) if scores else 0
                    tabela.append({
                        "ID": v.id, "Título": v.titulo, "Cidade": v.cidade, "UF": v.uf.sigla,
                        "Score Médio": f"{media:.1f}%", 
                        "Tempo": f"{(agora - v.data_criacao).days} dias",
                        "Expiração": v.data_expiracao.strftime('%d/%m/%y') if v.data_expiracao else "N/A"
                    })
                st.dataframe(pd.DataFrame(tabela), width="stretch", hide_index=True)

        with tabs[1]:
            render_inscritos_list()
        
        with tabs[2]:
            with st.form("n_vaga", clear_on_submit=True):
                st.subheader("Cadastrar Nova Vaga")
                t = st.text_input("Título")
                c_cid, c_uf = st.columns([0.7, 0.3])
                with c_cid: c = st.text_input("Cidade")
                with c_uf: u = st.selectbox("UF", db.query(UF).all(), format_func=lambda x: x.sigla)
                d = st.text_area("Descrição")
                exp = st.date_input("Data de Expiração")
                if st.form_submit_button("Salvar"):
                    db.add(Vaga(titulo=t, cidade=c, descricao=d, uf_id=u.id, data_expiracao=exp))
                    db.commit()
                    st.success("Vaga salva!")
                    st.rerun()

        with tabs[3]: # BI COM FILTROS CORRIGIDOS
            cands = db.query(Candidato).all()
            vagas_all = db.query(Vaga).all()
            if cands:
                df = pd.DataFrame([{
                    "Score": c.score_ia, "Genero": c.genero, 
                    "Vaga": c.vaga.titulo, "UF": c.vaga.uf.sigla
                } for c in cands])
                
                vagas_sel = st.multiselect("Filtrar Dashboard por Vaga:", options=df['Vaga'].unique())
                df_filtered = df[df['Vaga'].isin(vagas_sel)] if vagas_sel else df.copy()
                
                k1, k2, k3 = st.columns(3)
                k1.metric("Total Vagas", len(vagas_all))
                k2.metric("Candidatos (Filtro)", len(df_filtered))
                k3.metric("Média Score (Filtro)", f"{df_filtered['Score'].mean():.1f}%")

                st.divider()
                c1, c2 = st.columns(2)
                with c1:
                    df_score = df_filtered.groupby("Vaga")["Score"].mean().reset_index()
                    fig1 = px.bar(df_score, x="Vaga", y="Score", title="Performance por Vaga", text_auto='.1f')
                    fig1.update_traces(textposition='outside')
                    fig1.update_layout(yaxis={'visible': False}, xaxis={'title': None}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    fig1.update_xaxes(showgrid=False); fig1.update_yaxes(showgrid=False)
                    st.plotly_chart(fig1, width="stretch")
                with c2:
                    fig2 = px.pie(df_filtered, names="Genero", title="Distribuição de Gênero")
                    st.plotly_chart(fig2, width="stretch")
                
                st.divider()
                c3, c4 = st.columns(2)
                with c3:
                    # Filtra UFs baseado nas vagas que contém os candidatos filtrados
                    df_v_uf = df_filtered.groupby("UF").size().reset_index(name="Qtd")
                    fig3 = px.bar(df_v_uf, x="UF", y="Qtd", title="Distribuição Geográfica (Filtro)", text_auto=True, color_discrete_sequence=['#00CC96'])
                    fig3.update_traces(textposition='outside')
                    fig3.update_layout(yaxis={'visible': False}, xaxis={'title': None}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    fig3.update_xaxes(showgrid=False); fig3.update_yaxes(showgrid=False)
                    st.plotly_chart(fig3, width="stretch")
                with c4:
                    df_c_uf = df_filtered.groupby("UF").size().reset_index(name="Candidatos")
                    fig4 = px.bar(df_c_uf, x="UF", y="Candidatos", title="Candidatos por UF", text_auto=True, color_discrete_sequence=['#636EFA'])
                    fig4.update_traces(textposition='outside')
                    fig4.update_layout(yaxis={'visible': False}, xaxis={'title': None}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    fig4.update_xaxes(showgrid=False); fig4.update_yaxes(showgrid=False)
                    st.plotly_chart(fig4, width="stretch")
            else:
                st.info("Aguardando dados para gerar o BI.")
    finally:
        db.close()
