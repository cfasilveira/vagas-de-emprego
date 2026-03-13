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

        with tabs[0]:
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
                
                df_v = pd.DataFrame(tabela_vagas)
                st.dataframe(df_v, use_container_width=True, hide_index=True)

        with tabs[1]:
            render_inscritos_list()
        
        with tabs[2]:
            with st.form("nova_vaga", clear_on_submit=True):
                st.subheader("Cadastrar Nova Vaga")
                t = st.text_input("Título")
                
                # Campos Cidade e UF na mesma linha (Solicitação Imagem 1)
                col_cid, col_uf = st.columns([0.7, 0.3])
                with col_cid:
                    c = st.text_input("Cidade")
                with col_uf:
                    u = st.selectbox("UF", db.query(UF).all(), format_func=lambda x: x.sigla)
                
                d = st.text_area("Descrição")
                exp = st.date_input("Data de Expiração")
                
                if st.form_submit_button("Salvar"):
                    if t and d:
                        db.add(Vaga(titulo=t, cidade=c, descricao=d, uf_id=u.id, data_expiracao=exp))
                        db.commit()
                        st.success("Vaga salva com sucesso!")
                        st.rerun()
                    else:
                        st.error("Preencha o título e a descrição.")

        with tabs[3]:
            st.subheader("Análise de Dados")
            vagas_all = db.query(Vaga).all()
            cands_all = db.query(Candidato).all()

            # Seção de KPIs (Solicitação Imagem 2)
            if vagas_all:
                total_v = len(vagas_all)
                total_c = len(cands_all)
                vagas_encerradas = len([v for v in vagas_all if not v.ativa])
                perc_preenchidas = (vagas_encerradas / total_v * 100) if total_v > 0 else 0
                
                # Lógica para UF com maior/menor preenchimento
                df_preenchimento = pd.DataFrame([{"UF": v.uf.sigla, "Status": v.ativa} for v in vagas_all])
                uf_stats = df_preenchimento[df_preenchimento['Status'] == False]['UF'].value_counts()
                
                maior_uf = uf_stats.idxmax() if not uf_stats.empty else "N/A"
                menor_uf = uf_stats.idxmin() if not uf_stats.empty else "N/A"

                kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
                kpi1.metric("Total Vagas", total_v)
                kpi2.metric("Total Candidatos", total_c)
                kpi3.metric("% Preenchidas", f"{perc_preenchidas:.1f}%")
                kpi4.metric("UF Destaque (+)", maior_uf)
                kpi5.metric("UF Destaque (-)", menor_uf)
                st.divider()

            vagas_selecionadas = st.multiselect(
                "Filtrar Dashboard por Vaga:", 
                options=[v.titulo for v in vagas_all],
                default=[]
            )

            if cands_all:
                df_c = pd.DataFrame([
                    {"Genero": c.genero, "Vaga": c.vaga.titulo, "UF": c.vaga.uf.sigla} 
                    for c in cands_all
                ])

                if vagas_selecionadas:
                    df_c = df_c[df_c['Vaga'].isin(vagas_selecionadas)]

                if not df_c.empty:
                    col1, col2 = st.columns(2)
                    with col1: 
                        st.plotly_chart(px.bar(df_c.groupby("UF").count().reset_index(), x="UF", y="Vaga", title="Inscritos por UF"), use_container_width=True)
                    with col2: 
                        st.plotly_chart(px.pie(df_c, names="Genero", hole=0.4, title="Distribuição por Gênero"), use_container_width=True)
                else:
                    st.info("Nenhum dado encontrado para os filtros selecionados.")
    finally:
        db.close()
