import streamlit as st
import pandas as pd
import plotly.express as px
import re
from sqlalchemy import text
from sqlalchemy.orm import joinedload
from src.database.config import SessionLocal, engine
from src.database.models import Vaga, Candidato, Inscricao, UF, TipoTrabalho
from datetime import datetime, UTC

def render_admin_portal():
    st.title("🎯 Painel de Controle RH IA")
    
    with st.sidebar:
        st.header("⚙️ Configurações")
        if st.button("🚪 Sair", type="primary", width='stretch'):
            st.session_state.is_admin = False
            st.rerun()

    tabs = st.tabs(["📢 gestão de vagas", "👥 detalhes candidatos", "📊 dashboard analytics", "➕ cadastrar vaga"])
    db = SessionLocal()

    try:
        # --- ABA 1: GESTÃO (MANTIDA) ---
        with tabs[0]:
            st.subheader("📋 Vagas no Sistema")
            query_vagas = text("""
                SELECT v.id, v.titulo, v.cidade, UPPER(u.sigla) as uf, t.nome as tipo, 
                       CASE WHEN v.ativo THEN 'Ativa' ELSE 'Inativa' END as status
                FROM vagas v
                JOIN ufs u ON v.uf_id = u.id
                JOIN tipos_trabalho t ON v.tipo_trabalho_id = t.id
                ORDER BY v.id DESC
            """)
            with engine.connect() as conn:
                df_vagas = pd.read_sql(query_vagas, conn)
            if not df_vagas.empty:
                st.dataframe(df_vagas, width='stretch', hide_index=True)

            st.divider()
            st.subheader("👥 Candidatos Inscritos")
            query_cand = text("""
                SELECT c.nome, v.titulo as vaga, UPPER(u_cand.sigla) as uf_candidato, 
                       c.telefone, c.email, i.feedback_ia
                FROM inscricoes i
                JOIN candidatos c ON i.candidato_id = c.id
                JOIN vagas v ON i.vaga_id = v.id
                JOIN ufs u_cand ON c.uf_residencia_id = u_cand.id
            """)
            with engine.connect() as conn:
                df_cand = pd.read_sql(query_cand, conn)
            
            if not df_cand.empty:
                df_cand['match %'] = df_cand['feedback_ia'].str.extract(r'(\d+%)').fillna("0%")
                st.dataframe(df_cand[['nome', 'vaga', 'uf_candidato', 'match %']], width='stretch', hide_index=True)

        # --- ABA 2: DETALHES (MANTIDA) ---
        with tabs[1]:
            st.subheader("🔍 Análise Profunda")
            inscritos = db.query(Inscricao).options(
                joinedload(Inscricao.candidato).joinedload(Candidato.uf_residencia),
                joinedload(Inscricao.vaga)
            ).all()
            
            if inscritos:
                opcoes = {f"{i.candidato.nome} - {i.vaga.titulo}": i.id for i in inscritos}
                sel = st.selectbox("Selecione para ver detalhes:", list(opcoes.keys()))
                insc = next(i for i in inscritos if i.id == opcoes[sel])
                
                c1, c2 = st.columns([0.3, 0.7])
                with c1:
                    match_val = re.search(r"(\d+%)", insc.feedback_ia) if insc.feedback_ia else None
                    st.metric("Aderência", match_val.group(1) if match_val else "---")
                    st.write(f"**Contato:** {insc.candidato.telefone}")
                    uf_sigla = insc.candidato.uf_residencia.sigla.upper() if insc.candidato.uf_residencia else "??"
                    st.write(f"**Local:** {insc.candidato.cidade} / {uf_sigla}")
                with c2:
                    st.markdown("### 🧠 Avaliação da IA")
                    if insc.feedback_ia:
                        st.info(insc.feedback_ia)

        # --- ABA 3: ANALYTICS (TÍTULOS ATUALIZADOS) ---
        with tabs[2]:
            st.subheader("📊 Dashboard Estratégico")
            
            col1, col2, col3, col4 = st.columns(4)
            t_vagas = db.query(Vaga).filter(Vaga.ativo == True).count()
            t_cands = db.query(Candidato).count()
            
            query_stats = text("SELECT feedback_ia, data, vaga_id, candidato_id FROM inscricoes")
            with engine.connect() as conn:
                rows = conn.execute(query_stats).fetchall()
                vals = [int(re.search(r'(\d+)', r[0]).group()) for r in rows if r[0] and re.search(r'(\d+)', r[0])]
                media = sum(vals)/len(vals) if vals else 0
                atendidas = len(set(r[2] for r in rows if r[0] and int(re.search(r'(\d+)', r[0]).group()) >= 70))
                perc_atendimento = (atendidas / t_vagas * 100) if t_vagas > 0 else 0
                tempos = [(datetime.now(UTC) - r[1].replace(tzinfo=UTC)).days for r in rows if r[1]]
                tempo_medio = sum(tempos)/len(tempos) if tempos else 0

            col1.metric("Match Médio", f"{media:.0f}%")
            col2.metric("Vagas Atendidas", f"{perc_atendimento:.0f}%")
            col3.metric("Tempo Médio", f"{tempo_medio:.1f} d")
            col4.metric("Candidatos", t_cands)

            st.divider()

            c_geo, c_pie = st.columns(2)
            
            with c_geo:
                st.markdown("### 📍 Analise Geografica")
                query_geo = text("""
                    SELECT UPPER(u.sigla) as uf, 
                           CASE WHEN c.genero = 'M' THEN 'Masculino' ELSE 'Feminino' END as perfil,
                           count(*) as total
                    FROM candidatos c JOIN ufs u ON c.uf_residencia_id = u.id GROUP BY u.sigla, c.genero
                """)
                with engine.connect() as conn:
                    df_geo = pd.read_sql(query_geo, conn)
                if not df_geo.empty:
                    st.plotly_chart(px.bar(df_geo, x='uf', y='total', color='perfil', barmode='group',
                                     color_discrete_map={'Masculino': '#636EFA', 'Feminino': '#EF553B'}), width='stretch')

            with c_pie:
                st.markdown("### 🎯 Analise Total por Genero")
                query_atendidos = text("""
                    SELECT CASE WHEN c.genero = 'M' THEN 'Masculino' ELSE 'Feminino' END as perfil, count(*) as total
                    FROM inscricoes i
                    JOIN candidatos c ON i.candidato_id = c.id
                    WHERE i.feedback_ia ~ '([7-9][0-9]|100)%'
                    GROUP BY c.genero
                """)
                with engine.connect() as conn:
                    df_pie = pd.read_sql(query_atendidos, conn)
                if not df_pie.empty:
                    st.plotly_chart(px.pie(df_pie, values='total', names='perfil', hole=0.4,
                                     color='perfil', color_discrete_map={'Masculino': '#636EFA', 'Feminino': '#EF553B'}), width='stretch')

            st.divider()
            st.markdown("### 🚑 Saúde e Tempo de Vaga")
            query_saude = text("""
                SELECT v.titulo, count(i.id) as inscritos, MIN(i.data) as criada_em
                FROM vagas v LEFT JOIN inscricoes i ON v.id = i.vaga_id
                WHERE v.ativo = True GROUP BY v.titulo
            """)
            with engine.connect() as conn:
                df_s = pd.read_sql(query_saude, conn)
            if not df_s.empty:
                df_s['criada_em'] = pd.to_datetime(df_s['criada_em'])
                df_s['Dias'] = (datetime.now(UTC) - df_s['criada_em'].fillna(datetime.now(UTC))).dt.days
                st.table(df_s[['titulo', 'inscritos', 'Dias']].sort_values('Dias', ascending=False))

        # --- ABA 4: CADASTRO (MANTIDA) ---
        with tabs[3]:
            st.subheader("📝 Cadastrar Nova Vaga")
            with st.form("nova_vaga", clear_on_submit=True):
                titulo = st.text_input("Título da Vaga*")
                descricao = st.text_area("Descrição*")
                c1, c2 = st.columns(2)
                with c1:
                    cidade = st.text_input("Cidade")
                    salario = st.number_input("Salário", min_value=0.0)
                    qtd = st.number_input("Vagas", min_value=1)
                with c2:
                    ufs_l = db.query(UF).order_by(UF.sigla).all()
                    tipos_l = db.query(TipoTrabalho).all()
                    u_obj = st.selectbox("UF", ufs_l, format_func=lambda x: x.sigla.upper())
                    t_obj = st.selectbox("Tipo", tipos_l, format_func=lambda x: x.nome)
                    ativa = st.selectbox("Status", [True, False], format_func=lambda x: "Ativa" if x else "Inativa")
                if st.form_submit_button("🚀 Salvar Vaga", width='stretch'):
                    if titulo and descricao:
                        nova = Vaga(titulo=titulo, descricao=descricao, cidade=cidade, salario=salario, 
                                    quantidade_vagas=qtd, uf_id=u_obj.id, tipo_trabalho_id=t_obj.id, ativo=ativa)
                        db.add(nova); db.commit()
                        st.success("Vaga salva!"); st.rerun()
    finally:
        db.close()
