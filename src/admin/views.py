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

        with tabs[0]: # LISTAGEM DE VAGAS
            vagas = db.query(Vaga).all()
            if vagas:
                filtro = st.selectbox("Filtrar por Título:", ["Todas"] + [v.titulo for v in vagas])
                dados = [v for v in vagas if filtro == "Todas" or v.titulo == filtro]
                tabela_vagas = []
                agora = datetime.now(UTC)
                for v in dados:
                    scores = [c.score_ia for c in v.candidatos if c.score_ia is not None]
                    media = sum(scores) / len(scores) if scores else 0
                    dias_ativa = (agora - v.data_criacao).days
                    tabela_vagas.append({
                        "ID": v.id, "Título": v.titulo, "Cidade": v.cidade, "UF": v.uf.sigla,
                        "Média Score": f"{media:.1f}%", "Tempo Ativa": f"{dias_ativa} dias",
                        "Expiração": v.data_expiracao.strftime('%d/%m/%y') if v.data_expiracao else "N/A"
                    })
                st.dataframe(pd.DataFrame(tabela_vagas), use_container_width=True, hide_index=True)

        with tabs[1]:
            render_inscritos_list()
        
        with tabs[2]: # NOVA VAGA
            with st.form("nova_vaga", clear_on_submit=True):
                st.subheader("Cadastrar Nova Vaga")
                t = st.text_input("Título")
                col_cid, col_uf = st.columns([0.7, 0.3])
                with col_cid: c = st.text_input("Cidade")
                with col_uf: u = st.selectbox("UF", db.query(UF).all(), format_func=lambda x: x.sigla)
                d = st.text_area("Descrição")
                exp = st.date_input("Data de Expiração")
                if st.form_submit_button("Salvar"):
                    if t and d:
                        db.add(Vaga(titulo=t, cidade=c, descricao=d, uf_id=u.id, data_expiracao=exp))
                        db.commit()
                        st.success("Vaga salva!")
                        st.rerun()

        with tabs[3]: # BI REFORMULADO
            st.subheader("Análise de Performance")
            vagas_all = db.query(Vaga).all()
            cands_all = db.query(Candidato).all()

            if vagas_all:
                total_v = len(vagas_all)
                total_c = len(cands_all)
                
                # Cálculos de KPI
                df_vagas = pd.DataFrame([{"UF": v.uf.sigla, "Titulo": v.titulo} for v in vagas_all])
                uf_mais_vagas = df_vagas["UF"].value_counts(normalize=True).idxmax()
                perc_uf_vagas = df_vagas["UF"].value_counts(normalize=True).max() * 100

                if total_c > 0:
                    df_cands = pd.DataFrame([{"UF": c.vaga.uf.sigla, "Vaga": c.vaga.titulo} for c in cands_all])
                    uf_mais_cands = df_cands["UF"].value_counts(normalize=True).idxmax()
                    perc_uf_cands = df_cands["UF"].value_counts(normalize=True).max() * 100
                    
                    vaga_counts = df_cands["Vaga"].value_counts(normalize=True)
                    vaga_mais_disp = vaga_counts.idxmax()
                    perc_vaga_mais = vaga_counts.max() * 100
                    vaga_menos_disp = vaga_counts.idxmin()
                    perc_vaga_menos = vaga_counts.min() * 100
                else:
                    uf_mais_cands, perc_uf_cands = "N/A", 0
                    vaga_mais_disp, perc_vaga_mais = "N/A", 0
                    vaga_menos_disp, perc_vaga_menos = "N/A", 0

                # Linha 1: KPIs Gerais
                k1, k2, k3 = st.columns(3)
                k1.metric("Total Vagas", total_v)
                k2.metric("Total Candidatos", total_c)
                v_enc = len([v for v in vagas_all if not v.ativa])
                k3.metric("% Vagas Preenchidas", f"{(v_enc/total_v*100):.1f}%")
                
                st.write("---")
                
                # Linha 2: Blocos Geográfico e de Disputa
                col_geo, col_disp = st.columns(2)
                
                with col_geo:
                    st.write("**📍 Por Região (UF)**")
                    kg1, kg2 = st.columns(2)
                    kg1.metric("Mais Vagas", f"{uf_mais_vagas}", f"{perc_uf_vagas:.0f}%")
                    kg2.metric("Mais Candidatos", f"{uf_mais_cands}", f"{perc_uf_cands:.0f}%")
                
                with col_disp:
                    st.write("**🔥 Por Ocupação (Vagas)**")
                    kd1, kd2 = st.columns(2)
                    kd1.metric("Maior Procura", f"{vaga_mais_disp[:12]}...", f"{perc_vaga_mais:.0f}%")
                    kd2.metric("Menor Procura", f"{vaga_menos_disp[:12]}...", f"{perc_vaga_menos:.0f}%")
                
                st.divider()

            if cands_all:
                df = pd.DataFrame([{
                    "Data": c.data.date(), "Score": c.score_ia, 
                    "Vaga": c.vaga.titulo, "Genero": c.genero, "UF": c.vaga.uf.sigla,
                    "Celular": c.celular
                } for c in cands_all])

                vagas_sel = st.multiselect("Filtrar Dashboard por Vaga:", options=df['Vaga'].unique())
                if vagas_sel: df = df[df['Vaga'].isin(vagas_sel)]

                col_l, col_r = st.columns(2)
                with col_l:
                    df_qual = df.groupby("Vaga")["Score"].mean().reset_index()
                    st.plotly_chart(px.bar(df_qual, x="Vaga", y="Score", title="Score Médio por Vaga"), use_container_width=True)
                with col_r:
                    df_gen = df.groupby("Genero").size().reset_index(name="Qtd")
                    st.plotly_chart(px.pie(df_gen, values="Qtd", names="Genero", title="Distribuição de Gênero"), use_container_width=True)
            else:
                st.info("Aguardando novos candidatos para gerar gráficos.")
    finally:
        db.close()
