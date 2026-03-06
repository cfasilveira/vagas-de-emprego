import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.database.config import get_db
from src.database.models import Vaga, Candidato, Inscricao

def render_vagas_manager():
    st.subheader("⚙️ Painel Operacional de Vagas")
    with get_db() as db:
        vagas = db.query(Vaga).all()
        for v in vagas:
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"{'🟢' if v.ativo else '🔴'} **{v.titulo}**")
            col2.write(f"R$ {v.salario:,.2f}")
            if col3.button("Pausar/Ativar", key=f"v_{v.id}", width='stretch'):
                v.ativo = not v.ativo
                db.commit(); st.rerun()

def render_raw_database_tables():
    st.subheader("🔍 Auditoria de Dados")
    tabela = st.selectbox("Tabela:", ["Vagas", "Candidatos", "Inscrições"])
    with get_db() as db:
        modelos = {"Vagas": Vaga, "Candidatos": Candidato, "Inscrições": Inscricao}
        regs = db.query(modelos[tabela]).all()
        if regs:
            limpos = [{k: (str(v) if hasattr(v, '__table__') or isinstance(v, (datetime, date)) else v) 
                        for k, v in vars(r).items() if not k.startswith('_')} for r in regs]
            st.dataframe(pd.DataFrame(limpos), width='stretch')
