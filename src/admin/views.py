import streamlit as st
import pandas as pd
import plotly.express as px
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

        with tabs[0]:
            vagas = db.query(Vaga).all()
            if vagas:
                filtro = st.selectbox("Filtrar por Título:", ["Todas"] + [v.titulo for v in vagas])
                dados = [v for v in vagas if filtro == "Todas" or v.titulo == filtro]
                df_v = pd.DataFrame([{
                    "ID": v.id, "Título": v.titulo, "Cidade": v.cidade, "UF": v.uf.sigla,
                    "Expiração": v.data_expiracao.strftime('%d/%m/%y') if v.data_expiracao else "N/A"
                } for v in dados])
                st.dataframe(df_v, width="stretch", hide_index=True)

        with tabs[1]:
            render_inscritos_list()
        
        # ... (Mantendo tabs[2] e [3] com a sintaxe width="stretch" corrigida)
        with tabs[2]:
            with st.form("nova_vaga"):
                t, c, d = st.text_input("Título"), st.text_input("Cidade"), st.text_area("Descrição")
                u = st.selectbox("UF", db.query(UF).all(), format_func=lambda x: x.sigla)
                exp = st.date_input("Data de Expiração")
                if st.form_submit_button("Salvar"):
                    db.add(Vaga(titulo=t, cidade=c, descricao=d, uf_id=u.id, data_expiracao=exp))
                    db.commit()
                    st.rerun()

        with tabs[3]:
            cands = db.query(Candidato).all()
            if cands:
                df_c = pd.DataFrame([{"Genero": c.genero, "Vaga": c.vaga.titulo, "UF": c.vaga.uf.sigla} for c in cands])
                col1, col2 = st.columns(2)
                with col1: st.plotly_chart(px.bar(df_c.groupby("UF").count().reset_index(), x="UF", y="Vaga"), width="stretch")
                with col2: st.plotly_chart(px.pie(df_c, names="Genero", hole=0.4), width="stretch")
    finally:
        db.close()
