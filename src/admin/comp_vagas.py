import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.config import get_db
from src.database.models import Vaga, Candidato, Inscricao, UF
import re

def extrair_score_num(texto):
    if not texto: return 0
    match = re.search(r'(\d+)%', texto)
    return int(match.group(1)) if match else 0

def render_dashboard(inscricoes):
    st.subheader("📊 Estatísticas Estratégicas")
    
    with get_db() as db:
        # KPIs GLOBAIS (Não afetados pelo filtro) [cite: 28]
        total_vagas_global = db.query(Vaga).count()
        total_cand_global = db.query(Candidato).count()
        vagas_com_ins_global = db.query(Inscricao.vaga_id).distinct().count()
        perc_inscritas = (vagas_com_ins_global / total_vagas_global * 100) if total_vagas_global > 0 else 0

        st.markdown("### 📋 Painel de Vagas (Consolidado)")
        v1, v2, v3 = st.columns(3)
        v1.metric("Total de Vagas Oferecidas", total_vagas_global)
        v2.metric("Total de Candidatos", total_cand_global)
        v3.metric("% Vagas com Inscrição", f"{perc_inscritas:.1f}%")

        st.divider()

        # FILTRO DE UF (Afeta apenas os gráficos)
        ufs_db = db.query(UF).all()
        lista_ufs = ["Todas"] + [u.sigla for u in ufs_db]
        uf_filtro = st.selectbox("Filtrar Gráficos por UF:", options=lista_ufs)

        ins_filtradas = [
            i for i in inscricoes 
            if uf_filtro == "Todas" or (i.vaga.uf and i.vaga.uf.sigla == uf_filtro)
        ]

        st.markdown(f"### 📈 Detalhamento Visual - UF: {uf_filtro}")
        col_esq, col_dir = st.columns(2)

        with col_esq:
            # Score por vaga (Limpo, sem grades)
            if ins_filtradas:
                df_score = pd.DataFrame([
                    {"Vaga": i.vaga.titulo, "Score": extrair_score_num(i.feedback_ia)} 
                    for i in ins_filtradas
                ]).groupby("Vaga").mean().reset_index()
                fig_score = px.bar(df_score, x="Vaga", y="Score", text_auto=True, title="Média de Score por Vaga")
                fig_score.update_traces(textposition="outside", marker_color="#003366")
                fig_score.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, yaxis_visible=False, plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_score, use_container_width=True)
            
            # Ranking de Vagas (Barras Horizontais)
            if ins_filtradas:
                df_ranking = pd.DataFrame([{"Vaga": i.vaga.titulo} for i in ins_filtradas]).value_counts().reset_index(name="Candidatos")
                fig_rank = px.bar(df_ranking, x="Candidatos", y="Vaga", orientation='h', text_auto=True, title="Ranking de Inscritos")
                fig_rank.update_traces(textposition="outside", marker_color="#28a745")
                fig_rank.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, xaxis_visible=False, plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_rank, use_container_width=True)

        with col_dir:
            # Gênero (Pizza) [cite: 30]
            if ins_filtradas:
                df_gen = pd.DataFrame([
                    {"Gênero": "Masculino" if i.candidato.genero == "M" else "Feminino"} 
                    for i in ins_filtradas
                ]).value_counts().reset_index(name="Total")
                fig_gen = px.pie(df_gen, values="Total", names="Gênero", title="Distribuição por Gênero", hole=0.3)
                st.plotly_chart(fig_gen, use_container_width=True)

            # Temporal (Linha - Global) [cite: 30]
            vagas_all = db.query(Vaga).all()
            df_vagas_tempo = pd.DataFrame([{"Data": v.data.date() if hasattr(v, 'data') and v.data else "2026-03-01"} for v in vagas_all])
            df_vagas_tempo = df_vagas_tempo.groupby("Data").size().cumsum().reset_index(name="Total")
            fig_time = px.line(df_vagas_tempo, x="Data", y="Total", title="Crescimento Total de Vagas")
            fig_time.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis_showgrid=False, yaxis_showgrid=False)
            st.plotly_chart(fig_time, use_container_width=True)

def render_vagas_manager():
    st.subheader("⚙️ Controle de Vagas")
    with get_db() as db:
        # RECUPERADO: Formulário de Cadastro [cite: 20, 29]
        with st.expander("➕ Cadastrar Nova Vaga", expanded=False):
            with st.form("form_nova_vaga", clear_on_submit=True):
                titulo = st.text_input("Título da Vaga*")
                descricao = st.text_area("Descrição/Requisitos*")
                salario = st.number_input("Salário (R$)", min_value=0.0, format="%.2f", step=100.0)
                
                col_cid, col_uf = st.columns([3, 1])
                cidade = col_cid.text_input("Cidade")
                ufs_db = db.query(UF).all()
                opcoes_uf = {u.sigla: u.id for u in ufs_db}
                uf_sel = col_uf.selectbox("UF", options=list(opcoes_uf.keys()))

                if st.form_submit_button("Salvar Vaga", type="primary", width="stretch"):
                    if titulo and descricao:
                        nova = Vaga(titulo=titulo, descricao=descricao, salario=salario, 
                                    cidade=cidade, uf_id=opcoes_uf[uf_sel], ativo=True)
                        db.add(nova)
                        db.commit()
                        st.success("Vaga cadastrada!")
                        st.rerun()

        st.divider()
        # RECUPERADO: Lista de Gestão [cite: 4, 5, 26, 27]
        vagas = db.query(Vaga).all()
        for v in vagas:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                status = "🟢" if v.ativo else "🔴"
                c1.write(f"{status} **{v.titulo}**")
                c2.write(f"R$ {v.salario:,.2f}" if v.salario else "R$ 0,00")
                if c3.button("Pausar/Ativar", key=f"p_{v.id}", width="stretch"):
                    v.ativo = not v.ativo
                    db.commit()
                    st.rerun()
                if c4.button("🗑️", key=f"d_{v.id}", type="secondary", width="stretch"):
                    db.delete(v)
                    db.commit()
                    st.rerun()
