import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import func
from src.database.config import get_db
from src.database.models import Inscricao, Candidato, UF, Vaga

def render_inscritos_list():
    """Lista detalhada de candidatos com feedback da IA e remoção segura."""
    st.subheader("👥 Candidatos Inscritos")
    with get_db() as db:
        try:
            inscricoes = db.query(Inscricao).filter(Inscricao.ativo == True).all()
            
            # FAIL FIRST: Validação de dados antes de renderizar
            if not inscricoes:
                return st.info("Sem candidatos ativos no momento.")
                
            for inc in inscricoes:
                # O label do expander usa o __repr__ do model (Nome | Vaga)
                with st.expander(f"👤 {inc.candidato.nome} | {inc.vaga.titulo}"):
                    st.write(f"**📧 E-mail:** {inc.candidato.email} | **⚤ Gênero:** {inc.candidato.genero}")
                    st.write(f"**📝 Resumo:** {inc.candidato.resumo}")
                    
                    if inc.feedback_ia: 
                        st.info(f"🤖 **Análise IA:** {inc.feedback_ia}")
                    else:
                        st.warning("⚠️ IA: Análise pendente ou serviço indisponível.")
                    
                    if st.button("🗑️ Remover Candidato", key=f"del_insc_{inc.id}"):
                        try:
                            inc.ativo = False
                            db.commit()
                            st.success("Removido com sucesso!")
                            st.rerun()
                        except Exception as e:
                            db.rollback()
                            st.error(f"Erro ao persistir remoção: {e}")
        except Exception as e:
            st.error(f"Erro ao carregar lista de inscritos: {e}")

def render_analytics_dashboard():
    """Painel de BI com métricas e gráficos protegidos contra dados vazios."""
    st.header("📈 Dashboard de Recrutamento")
    with get_db() as db:
        try:
            total_insc = db.query(Inscricao).filter(Inscricao.ativo == True).count()
            vagas_atv = db.query(Vaga).filter(Vaga.ativo == True).count()
            
            # Métricas no topo
            c1, c2, c3 = st.columns(3)
            c1.metric("Inscritos Ativos", total_insc)
            c2.metric("Vagas Abertas", vagas_atv)
            divisor = max(vagas_atv, 1)
            c3.metric("Média Cand/Vaga", f"{total_insc/divisor:.1f}")

            col_esq, col_dir = st.columns(2)
            
            # Gráfico de Estados
            with col_esq:
                st.write("**📍 Por Estado**")
                estados = db.query(UF.sigla, func.count(Inscricao.id)).select_from(UF)\
                    .join(Vaga, Vaga.uf_id == UF.id).join(Inscricao, Inscricao.vaga_id == Vaga.id)\
                    .filter(Inscricao.ativo == True).group_by(UF.sigla).all()
                if estados:
                    df = pd.DataFrame(estados, columns=['UF', 'Inscritos'])
                    st.bar_chart(df.set_index('UF'))
                else:
                    st.info("Aguardando dados geográficos...")

            # Gráfico de Gênero
            with col_dir:
                st.write("**⚤ Gênero**")
                generos = db.query(Candidato.genero, func.count(Inscricao.id)).select_from(Candidato)\
                    .join(Inscricao, Inscricao.candidato_id == Candidato.id)\
                    .filter(Inscricao.ativo == True).group_by(Candidato.genero).all()
                if generos:
                    df_g = pd.DataFrame(generos, columns=['G', 'Qtd'])
                    if not df_g.empty and df_g['Qtd'].sum() > 0:
                        fig = px.pie(df_g, values='Qtd', names='G', hole=.4)
                        st.plotly_chart(fig, width='stretch')
                else:
                    st.info("Aguardando dados de gênero...")
        except Exception as e:
            st.error(f"Erro ao processar analytics: {e}")
