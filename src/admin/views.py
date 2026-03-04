import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import func
from src.database.config import get_db
from src.database.models import Inscricao, Vaga, Candidato, UF
from .forms import render_vaga_form

def render_inscritos():
    st.subheader("👥 Candidatos Inscritos")
    with get_db() as db:
        inscricoes = db.query(Inscricao).filter(Inscricao.ativo == True).all()
        if not inscricoes: 
            return st.info("Sem candidatos ativos no momento.")
        for inc in inscricoes:
            with st.expander(f"👤 {inc.candidato.nome} | {inc.vaga.titulo}"):
                st.write(f"**📧 E-mail:** {inc.candidato.email} | **⚤ Gênero:** {inc.candidato.genero}")
                st.write(f"**📝 Resumo:** {inc.candidato.resumo}")
                if inc.feedback_ia: st.info(f"🤖 **Análise IA:** {inc.feedback_ia}")
                if st.button("🗑️ Remover", key=f"del_insc_{inc.id}"):
                    inc.ativo = False
                    db.commit()
                    st.rerun()

def render_dashboard():
    st.header("📈 Dashboard de Recrutamento")
    with get_db() as db:
        total_insc = db.query(Inscricao).filter(Inscricao.ativo == True).count()
        vagas_atv = db.query(Vaga).filter(Vaga.ativo == True).count()
        c1, c2, c3 = st.columns(3)
        c1.metric("Inscritos Ativos", total_insc)
        c2.metric("Vagas Abertas", vagas_atv)
        c3.metric("Média Cand/Vaga", f"{total_insc/max(vagas_atv, 1):.1f}")

        col_esq, col_dir = st.columns(2)
        with col_esq:
            st.write("**📍 Por Estado**")
            estados = db.query(UF.sigla, func.count(Inscricao.id)).select_from(UF)\
                .join(Vaga, Vaga.uf_id == UF.id).join(Inscricao, Inscricao.vaga_id == Vaga.id)\
                .filter(Inscricao.ativo == True).group_by(UF.sigla).all()
            if estados:
                df = pd.DataFrame(estados, columns=['UF', 'Inscritos'])
                st.bar_chart(df.set_index('UF'))

        with col_dir:
            st.write("**⚤ Gênero**")
            generos = db.query(Candidato.genero, func.count(Inscricao.id)).select_from(Candidato)\
                .join(Inscricao, Inscricao.candidato_id == Candidato.id)\
                .filter(Inscricao.ativo == True).group_by(Candidato.genero).all()
            if generos:
                df_g = pd.DataFrame(generos, columns=['G', 'Qtd'])
                st.plotly_chart(px.pie(df_g, values='Qtd', names='G', hole=.4), use_container_width=True)

def render_consulta_direta():
    st.subheader("🔍 Consulta Direta ao Banco")
    tabela = st.selectbox("Escolha a Tabela", ["Vagas", "Candidatos", "Inscrições"])
    with get_db() as db:
        model_map = {"Vagas": Vaga, "Candidatos": Candidato, "Inscrições": Inscricao}
        dados = db.query(model_map[tabela]).all()
        if dados:
            # Converte para lista de dicts limpando campos internos do SQLAlchemy
            limpo = [{k: v for k, v in d.__dict__.items() if not k.startswith('_')} for d in dados]
            st.dataframe(pd.DataFrame(limpo), use_container_width=True)

def render_admin_portal():
    with st.sidebar:
        st.divider()
        if st.button("🚪 Sair do Admin", type="primary", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Nova Vaga", "👥 Candidatos", "📈 Dashboard", "🔍 Tabelas"])
    with tab1: render_vaga_form()
    with tab2: render_inscritos()
    with tab3: render_dashboard()
    with tab4: render_consulta_direta()
