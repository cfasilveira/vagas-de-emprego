import streamlit as st
import pandas as pd
import plotly.express as px
import re
from sqlalchemy import text
from sqlalchemy.orm import joinedload
from src.database.config import SessionLocal, engine
from src.database.models import Vaga, Candidato, Inscricao, UF, TipoTrabalho

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
        # --- ABA 1: GESTÃO ---
        with tabs[0]:
            # Subseção 1: Vagas no Sistema (Para conferir o que você acabou de cadastrar)
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
            else:
                st.info("Nenhuma vaga cadastrada ainda.")

            st.divider()

            # Subseção 2: Candidatos Inscritos
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
                st.dataframe(df_cand[['nome', 'vaga', 'uf_candidato', 'telefone', 'email', 'match %']], 
                             width='stretch', hide_index=True)
            else:
                st.warning("Aguardando novas inscrições para exibir candidatos.")

        # --- ABA 2: DETALHES ---
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
                    else:
                        st.warning("⏳ IA processando...")
                    with st.expander("Ver Resumo Original"):
                        st.text_area("Texto:", insc.resumo_submetido, height=150, disabled=True)

        # --- ABA 3: ANALYTICS ---
        with tabs[2]:
            st.subheader("📊 indicadores estratégicos")
            ufs_db = db.query(UF).all()
            if ufs_db:
                uf_sel = st.selectbox("📍 filtrar por UF da Vaga:", [u.sigla for u in ufs_db])
                sql_an = text("""
                    SELECT lower(v.titulo) as vaga, lower(c.genero) as genero, count(i.id) as inscritos 
                    FROM inscricoes i 
                    JOIN vagas v ON i.vaga_id = v.id 
                    JOIN candidatos c ON i.candidato_id = c.id 
                    JOIN ufs u ON v.uf_id = u.id 
                    WHERE UPPER(u.sigla) = :uf_param 
                    GROUP BY v.titulo, c.genero
                """)
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

        # --- ABA 4: CADASTRO DE VAGAS ---
        with tabs[3]:
            st.subheader("📝 Cadastrar Nova Vaga")
            with st.form("nova_vaga_form", clear_on_submit=True):
                titulo = st.text_input("Título da Vaga*")
                descricao = st.text_area("Descrição da Vaga*", height=200)
                
                col1, col2 = st.columns(2)
                with col1:
                    cidade = st.text_input("Cidade")
                    salario = st.number_input("Salário", min_value=0.0, step=100.0)
                    quantidade = st.number_input("Quantidade de Vagas", min_value=1, value=1)
                
                with col2:
                    ufs = db.query(UF).order_by(UF.sigla).all()
                    tipos = db.query(TipoTrabalho).all()
                    uf_obj = st.selectbox("UF da Vaga", ufs, format_func=lambda x: x.sigla.upper())
                    tipo_obj = st.selectbox("Tipo de Trabalho", tipos, format_func=lambda x: x.nome)
                    ativo_vaga = st.selectbox("Status da Vaga", [True, False], format_func=lambda x: "Ativa" if x else "Inativa")

                if st.form_submit_button("🚀 Salvar Vaga", type="primary", width='stretch'):
                    if not titulo or not descricao:
                        st.error("Por favor, preencha o Título e a Descrição.")
                    else:
                        nova_vaga = Vaga(
                            titulo=titulo,
                            descricao=descricao,
                            cidade=cidade,
                            salario=salario,
                            quantidade_vagas=quantidade,
                            uf_id=uf_obj.id,
                            tipo_trabalho_id=tipo_obj.id,
                            ativo=ativo_vaga
                        )
                        db.add(nova_vaga)
                        db.commit()
                        st.success(f"Vaga '{titulo}' cadastrada com sucesso!")
                        st.rerun()

    finally:
        db.close()
