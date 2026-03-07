import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.database.config import get_db
from src.database.models import Vaga, Candidato, Inscricao

def render_vagas_manager():
    st.subheader("⚙️ Painel Operacional de Vagas")
    with get_db() as db:
        vagas = db.query(Vaga).all()
        if not vagas:
            st.info("Nenhuma vaga cadastrada.")
            return

        for v in vagas:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                status = "🟢" if v.ativo else "🔴"
                col1.write(f"{status} **{v.titulo}**")
                col2.write(f"R$ {v.salario:,.2f}")
                
                if col3.button("Pausar/Ativar", key=f"st_{v.id}"):
                    v.ativo = not v.ativo
                    db.commit()
                    st.rerun()
                
                if col4.button("🗑️ Remover", key=f"del_{v.id}", type="secondary"):
                    db.delete(v)
                    db.commit()
                    st.rerun()

def render_raw_database_tables():
    st.subheader("🔍 Auditoria de Dados")
    tabela = st.selectbox("Tabela:", ["Vagas", "Candidatos", "Inscrições"])
    with get_db() as db:
        modelos = {"Vagas": Vaga, "Candidatos": Candidato, "Inscrições": Inscricao}
        regs = db.query(modelos[tabela]).all()
        if regs:
            limpos = [{k: (str(v) if hasattr(v, '__table__') or isinstance(v, (datetime, date)) else v) 
                        for k, v in vars(r).items() if not k.startswith('_')} for r in regs]
            st.dataframe(pd.DataFrame(limpos), use_container_width=True)
