import streamlit as st
import pandas as pd
import re
import plotly.express as px
from src.database.config import get_db
from src.database.models import Inscricao, Candidato, Vaga, UF
from sqlalchemy import func

def extrair_score(fb):
    if not fb: return 0
    # Procura por "SCORE: X%" ou apenas "X%"
    match = re.search(r"(\d+)\s*%", fb)
    return int(match.group(1)) if match else 0

def render_inscritos_list():
    st.subheader("🏆 Ranking & Central de Contatos")
    
    with get_db() as db:
        vagas = db.query(Vaga).all()
        if not vagas:
            st.info("Nenhuma vaga encontrada no sistema.")
            return

        # Seletor de Vagas para Filtragem
        opcoes = {f"{v.titulo} ({v.cidade}-{v.uf.sigla if v.uf else ''})": v.id for v in vagas}
        vaga_selecionada = st.selectbox("Selecione a Vaga para listar os candidatos:", list(opcoes.keys()))
        v_id = opcoes[vaga_selecionada]

        # Busca inscritos apenas desta vaga
        inscs = db.query(Inscricao).filter(Inscricao.vaga_id == v_id).all()
        
        if not inscs:
            st.warning("Nenhum candidato inscrito para esta vaga ainda.")
            return

        dados = []
        for i in inscs:
            dados.append({
                "Score": extrair_score(i.feedback_ia),
                "Nome": i.candidato.nome,
                "Pitch": i.candidato.resumo or "Sem resumo",
                "IA": i.feedback_ia,
                "Email": i.candidato.email,
                "Telefone": i.candidato.telefone or ""
            })
        
        df = pd.DataFrame(dados).sort_values(by="Score", ascending=False)
        
        for _, row in df.iterrows():
            with st.expander(f"[{row['Score']}%] {row['Nome']}"):
                c1, c2 = st.columns(2)
                c1.info(f"**Pitch:**\n\n{row['Pitch']}")
                c2.success(f"**Análise da IA:**\n\n{row['IA']}")
                
                st.divider()
                col_a, col_b = st.columns(2)
                col_a.write(f"📧 {row['Email']}")
                if row['Telefone']:
                    clean_tel = re.sub(r'\D', '', row['Telefone'])
                    col_b.link_button(f"📲 WhatsApp: {row['Telefone']}", f"https://wa.me/55{clean_tel}")

def render_analytics_dashboard():
    st.subheader("📊 BI Operacional")
    with get_db() as db:
        c1, c2, c3 = st.columns(3)
        c1.metric("Candidatos", db.query(Candidato).count())
        c2.metric("Vagas", db.query(Vaga).count())
        c3.metric("Inscrições", db.query(Inscricao).count())
        
        col_l, col_r = st.columns(2)
        res_uf = db.query(UF.sigla, func.count(Inscricao.id)).select_from(UF).join(Vaga).join(Inscricao).group_by(UF.sigla).all()
        if res_uf:
            df_uf = pd.DataFrame(res_uf, columns=['UF', 'Total'])
            col_l.plotly_chart(px.bar(df_uf, x='UF', y='Total', title="Candidatos por UF"))
        
        res_gen = db.query(Candidato.genero, func.count(Candidato.id)).group_by(Candidato.genero).all()
        if res_gen:
            df_gen = pd.DataFrame(res_gen, columns=['Gênero', 'Qtd'])
            col_r.plotly_chart(px.pie(df_gen, names='Gênero', values='Qtd', title="Gênero (M/F)"))
