import streamlit as st
import pandas as pd
import plotly.express as px
import re
from sqlalchemy import func
from src.database.config import get_db
from src.database.models import Inscricao, Vaga, Candidato, UF

def extrair_score(fb):
    if not fb: return 0
    match = re.search(r"(?:SCORE|MATCH).*?(\d+)", fb.upper())
    if not match: match = re.search(r"(\d+)\s*%", fb)
    return int(match.group(1)) if match else 0

def render_inscritos_list():
    st.subheader("🏆 Ranking & Central de Contatos")
    with get_db() as db:
        vagas = db.query(Vaga).filter(Vaga.ativo == True).all()
        if not vagas: return st.info("Sem vagas ativas.")
        
        v_map = {f"{v.titulo} ({v.cidade})": v.id for v in vagas}
        v_sel = st.selectbox("Filtrar por Vaga:", list(v_map.keys()))
        v_id = v_map[v_sel]
        
        inscs = db.query(Inscricao).filter(Inscricao.vaga_id == v_id, Inscricao.ativo == True).all()
        if not inscs: return st.warning("Nenhum candidato ativo.")

        dados = [{"Nome": i.candidato.nome, "Score": extrair_score(i.feedback_ia), 
                  "Email": i.candidato.email, "Celular": i.candidato.celular,
                  "Feedback": i.feedback_ia, "obj": i} for i in inscs]
        
        df = pd.DataFrame(dados).sort_values("Score", ascending=False)
        st.plotly_chart(px.bar(df.head(10), x='Score', y='Nome', orientation='h', color='Score', text_auto=True), width='stretch')

        for _, r in df.iterrows():
            with st.expander(f"⭐ {r['Score']}% - {r['Nome']}"):
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.write(f"**📧 Email:** {r['Email']}")
                    st.write(f"**📞 Celular:** {r['Celular']}")
                with c2:
                    st.markdown(f"**🤖 Análise:**\n{r['Feedback']}")
                if st.button("Dispensar", key=f"d_{r['obj'].id}"):
                    r['obj'].ativo = False
                    db.commit(); st.rerun()

def render_analytics_dashboard():
    st.subheader("📊 BI de Recrutamento Real-time")
    with get_db() as db:
        # --- KPIs ---
        total_cand = db.query(Candidato).count()
        total_vagas = db.query(Vaga).count()
        vagas_ativas = db.query(Vaga).filter(Vaga.ativo == True).count()
        total_inscricoes = db.query(Inscricao).count()

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Candidatos", total_cand)
        k2.metric("Vagas Totais", total_vagas)
        k3.metric("Vagas Ativas", vagas_ativas)
        k4.metric("Inscrições", total_inscricoes)

        st.divider()
        col_esq, col_dir = st.columns(2)

        with col_esq:
            # --- Gráfico de Gênero ---
            res_g = db.query(Candidato.genero, func.count(Candidato.id)).group_by(Candidato.genero).all()
            if res_g:
                df_g = pd.DataFrame(res_g, columns=['Gênero', 'Qtd'])
                df_g['Gênero'] = df_g['Gênero'].replace({'M': 'Masculino', 'F': 'Feminino'})
                st.plotly_chart(px.pie(df_g, values='Qtd', names='Gênero', hole=.4, title="Diversidade"), width='stretch')

            # --- Vagas mais Disputadas ---
            res_disp = db.query(Vaga.titulo, func.count(Inscricao.id).label('total')).\
                join(Inscricao).group_by(Vaga.titulo).order_by(func.count(Inscricao.id).desc()).limit(5).all()
            if res_disp:
                df_d = pd.DataFrame(res_disp, columns=['Vaga', 'Inscrições'])
                st.plotly_chart(px.bar(df_d, x='Inscrições', y='Vaga', orientation='h', title="Top 5 Vagas Disputadas"), width='stretch')

        with col_dir:
            # --- Candidatos por UF ---
            res_uf = db.query(UF.sigla, func.count(Inscricao.id)).\
                join(Vaga, Vaga.uf_id == UF.id).join(Inscricao, Inscricao.vaga_id == Vaga.id).\
                group_by(UF.sigla).all()
            if res_uf:
                df_uf = pd.DataFrame(res_uf, columns=['UF', 'Candidatos'])
                st.plotly_chart(px.bar(df_uf, x='UF', y='Candidatos', title="Distribuição Geográfica"), width='stretch')
            
            # --- Histórico de Inscrições ---
            res_data = db.query(func.date(Inscricao.data), func.count(Inscricao.id)).group_by(func.date(Inscricao.data)).all()
            if res_data:
                df_data = pd.DataFrame(res_data, columns=['Data', 'Qtd'])
                st.plotly_chart(px.line(df_data, x='Data', y='Qtd', title="Volume de Candidaturas"), width='stretch')
