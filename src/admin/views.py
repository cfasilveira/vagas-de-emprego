import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
import re
from src.database.config import get_db, engine
from src.database.models import Vaga, Candidato, Inscricao, UF

def calcular_match(resumo_cand, desc_vaga):
    """Calcula match ignorando pontuação e palavras irrelevantes."""
    if not resumo_cand or not desc_vaga:
        return 0.0
    
    # Limpeza básica: apenas letras e números
    def limpar(texto):
        t = re.sub(r'[^\w\s]', '', texto.lower())
        # Filtra palavras curtas (conectores comuns)
        return set(p for p in t.split() if len(p) > 2)

    set_cand = limpar(resumo_cand)
    set_vaga = limpar(desc_vaga)
    
    if not set_vaga:
        return 0.0
        
    intersecao = set_cand.intersection(set_vaga)
    # Proporção de palavras da vaga encontradas no currículo
    score = (len(intersecao) / len(set_vaga)) * 100
    return round(min(score * 1.5, 100.0), 1)

def render_admin_portal():
    st.title("🎯 Painel de Controle RH IA")
    
    with st.sidebar:
        st.header("⚙️ Configurações")
        if st.button("🚪 Sair", type="primary", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()

    tabs = st.tabs(["📢 gestão de vagas", "👥 detalhes candidatos", "📊 dashboard analytics"])

    with get_db() as db:
        ufs_banco = db.query(UF).order_by(UF.sigla).all()
        lista_siglas = [u.sigla.strip().upper() for u in ufs_banco]

        # --- ABA 0: GESTÃO ---
        with tabs[0]:
            st.subheader("visualização de candidatos")
            query_tabela = text("""
                SELECT 
                    c.nome as candidato, 
                    v.titulo as vaga, 
                    UPPER(u.sigla) as uf, 
                    c.telefone as celular,
                    c.email,
                    c.resumo as descricao_candidato,
                    v.descricao as requisito_vaga
                FROM candidatos c
                JOIN inscricoes i ON c.id = i.candidato_id
                JOIN vagas v ON i.vaga_id = v.id
                JOIN ufs u ON v.uf_id = u.id
            """)
            with engine.connect() as conn:
                df_tabela = pd.read_sql(query_tabela, conn)
            
            if not df_tabela.empty:
                df_tabela.columns = [c.lower() for c in df_tabela.columns]
                
                # Cálculo do Match
                df_tabela['match %'] = df_tabela.apply(
                    lambda x: calcular_match(x['descricao_candidato'], x['requisito_vaga']), axis=1
                )
                
                vaga_sel = st.selectbox("filtrar por vaga:", ["todas"] + list(df_tabela['vaga'].unique()), key="f_vaga")
                df_exibir = df_tabela if vaga_sel == "todas" else df_tabela[df_tabela['vaga'] == vaga_sel]
                
                # Exibindo TODOS os dados solicitados
                colunas_finais = ['candidato', 'vaga', 'uf', 'celular', 'email', 'descricao_candidato', 'match %']
                st.dataframe(df_exibir[colunas_finais], use_container_width=True, hide_index=True)
            else:
                st.info("nenhuma inscrição encontrada.")

        # --- ABA 1 E 2 (MANTIDAS) ---
        with tabs[1]:
            st.subheader("análise profunda")
            dados_ia = (db.query(Candidato, Inscricao, Vaga)
                        .join(Inscricao, Candidato.id == Inscricao.candidato_id)
                        .join(Vaga, Inscricao.vaga_id == Vaga.id)
                        .all())
            if dados_ia:
                for c_obj, i_obj, v_obj in dados_ia:
                    with st.expander(f"👤 {c_obj.nome} - {v_obj.titulo}"):
                        st.write(f"**resumo:** {c_obj.resumo}")
                        st.info(f"🧠 feedback ia: {i_obj.feedback_ia}")

        with tabs[2]:
            st.subheader("indicadores estratégicos")
            if lista_siglas:
                uf_sel = st.selectbox("📍 selecione o estado:", lista_siglas, key="f_uf")
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
                    c1, c2 = st.columns(2)
                    with c1:
                        df_bar = df_an.groupby("vaga")["inscritos"].sum().reset_index()
                        st.plotly_chart(px.bar(df_bar, x="vaga", y="inscritos", color_discrete_sequence=['#00CC96']), use_container_width=True)
                    with c2:
                        v_pizza = st.selectbox("vaga:", df_an["vaga"].unique(), key="p_vaga")
                        df_p = df_an[df_an["vaga"] == v_pizza]
                        st.plotly_chart(px.pie(df_p, values="inscritos", names="genero", color_discrete_map={'masculino':'#636EFA', 'feminino':'#EF553B'}), use_container_width=True)
