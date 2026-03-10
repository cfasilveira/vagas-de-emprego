import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from sqlalchemy.orm import joinedload
from src.database.config import SessionLocal, engine
from src.database.models import Vaga, Candidato, Inscricao, UF

def render_admin_portal():
    st.title("🎯 Painel de Controle RH IA")
    
    with st.sidebar:
        st.header("⚙️ Configurações")
        if st.button("🚪 Sair", type="primary", width='stretch'):
            st.session_state.is_admin = False
            st.rerun()

    tabs = st.tabs(["📢 gestão de vagas", "👥 detalhes candidatos", "📊 dashboard analytics"])
    db = SessionLocal()

    try:
        with tabs[0]:
            st.subheader("visualização de candidatos")
            query = text("""
                SELECT c.nome, v.titulo as vaga, UPPER(u.sigla) as uf, 
                       c.telefone, c.email, i.feedback_ia
                FROM inscricoes i
                JOIN candidatos c ON i.candidato_id = c.id
                JOIN vagas v ON i.vaga_id = v.id
                JOIN ufs u ON v.uf_id = u.id
            """)
            with engine.connect() as conn:
                df = pd.read_sql(query, conn)
            
            if not df.empty:
                df['match %'] = df['feedback_ia'].str.split('\n').str[0]
                st.dataframe(df[['nome', 'vaga', 'uf', 'telefone', 'email', 'match %']], 
                             width='stretch', hide_index=True)
            else:
                st.info("Nenhuma inscrição encontrada.")

        with tabs[1]:
            st.subheader("🔍 Análise Profunda do Candidato")
            # Carrega relações necessárias: Candidato, Vaga e a UF da Vaga
            inscritos = db.query(Inscricao).options(
                joinedload(Inscricao.candidato), 
                joinedload(Inscricao.vaga).joinedload(Vaga.uf)
            ).all()
            
            if inscritos:
                opcoes = {f"{i.candidato.nome} - {i.vaga.titulo}": i.id for i in inscritos}
                sel = st.selectbox("Selecione para ver detalhes:", list(opcoes.keys()))
                insc = next(i for i in inscritos if i.id == opcoes[sel])
                
                c1, c2 = st.columns([0.3, 0.7])
                with c1:
                    nota = insc.feedback_ia.split("\n")[0] if insc.feedback_ia else "---"
                    st.metric("Aderência", nota)
                    st.write(f"**Contato:** {insc.candidato.telefone}")
                    # EXIBIÇÃO DA UF AQUI:
                    st.write(f"**Local:** {insc.candidato.cidade} / {insc.vaga.uf.sigla.upper()}")
                
                with c2:
                    st.markdown("### 🧠 Avaliação da IA")
                    if insc.feedback_ia and "\n" in insc.feedback_ia:
                        st.info(insc.feedback_ia.split("\n", 1)[1])
                    else:
                        st.info("⏳ A IA está realizando a análise profunda. Aguarde alguns instantes e atualize a página.")

                with st.expander("Ver Resumo Original"):
                    st.text_area("Texto:", insc.resumo_submetido, height=150, disabled=True)

        with tabs[2]:
            st.subheader("📊 indicadores estratégicos")
            ufs = db.query(UF).all()
            if ufs:
                uf_sel = st.selectbox("📍 filtrar por UF:", [u.sigla for u in ufs])
                sql_an = text("SELECT lower(v.titulo) as vaga, lower(c.genero) as genero, count(i.id) as inscritos FROM inscricoes i JOIN vagas v ON i.vaga_id = v.id JOIN candidatos c ON i.candidato_id = c.id JOIN ufs u ON v.uf_id = u.id WHERE UPPER(u.sigla) = :uf_param GROUP BY v.titulo, c.genero")
                with engine.connect() as conn:
                    df_an = pd.read_sql(sql_an, conn, params={"uf_param": uf_sel})
                
                if not df_an.empty:
                    col_b, col_p = st.columns(2)
                    with col_b:
                        df_bar = df_an.groupby("vaga")["inscritos"].sum().reset_index()
                        st.plotly_chart(px.bar(df_bar, x="vaga", y="inscritos", color_discrete_sequence=['#00CC96']), width='stretch')
                    with col_p:
                        v_sel = st.selectbox("vaga detalhada:", df_an["vaga"].unique())
                        df_p = df_an[df_an["vaga"] == v_sel].copy()
                        df_p['genero'] = df_p['genero'].map({'m': 'Masculino', 'f': 'Feminino'})
                        st.plotly_chart(px.pie(df_p, values="inscritos", names="genero", hole=0.4), width='stretch')
    finally:
        db.close()
