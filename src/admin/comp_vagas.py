import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.database.config import get_db
from src.database.models import Inscricao, Vaga, Candidato

def render_raw_database_tables():
    """Visualização tabular crua com limpeza rigorosa para compatibilidade PyArrow."""
    st.subheader("🔍 Consulta Direta ao Banco")
    tabela_sel = st.selectbox("Escolha a Tabela para Auditoria", ["Vagas", "Candidatos", "Inscrições"])
    
    with get_db() as db:
        model_map = {"Vagas": Vaga, "Candidatos": Candidato, "Inscrições": Inscricao}
        try:
            registros = db.query(model_map[tabela_sel]).all()
            
            # FAIL FIRST: Se não há dados, para a execução aqui
            if not registros:
                return st.warning(f"A tabela '{tabela_sel}' não possui registros no momento.")

            dados_limpos = []
            for reg in registros:
                if reg is None: continue
                
                item = {}
                # Extração segura de atributos do SQLAlchemy
                for chave, valor in vars(reg).items():
                    if chave.startswith('_'): 
                        continue
                    
                    # Formatação Fail First: Garante que o Streamlit/Arrow aceite o tipo de dado
                    if valor is None:
                        item[chave] = "-"
                    elif isinstance(valor, (datetime, date)):
                        item[chave] = valor.isoformat()
                    # Se for objeto de classe (Vaga/Candidato), usa o __repr__ do models.py
                    elif "src.database.models" in str(type(valor)):
                        item[chave] = str(valor)
                    else:
                        item[chave] = valor
                dados_limpos.append(item)
            
            # Verificação final antes de enviar ao DataFrame
            if not dados_limpos:
                return st.error("Erro interno no processamento dos dados da tabela.")

            df = pd.DataFrame(dados_limpos)
            
            # Renderização moderna Streamlit 2026
            st.dataframe(df, width='stretch')
            
            st.caption(f"Exibindo {len(dados_limpos)} registro(s) da tabela {tabela_sel}.")
            
        except Exception as e:
            st.error(f"Erro técnico ao renderizar consulta direta: {e}")
