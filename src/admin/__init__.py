import streamlit as st
import pandas as pd
from .auth import login_required
from .forms import form_cadastro_vaga
from src.database.config import get_db
from src.database.repository import VagaRepository

@login_required
def render_admin_panel():
    st.title("🛡️ Painel de Controle")
    
    tab1, tab2 = st.tabs(["📢 Cadastrar Vaga", "📊 Gestão de Vagas"])
    
    with tab1:
        form_cadastro_vaga()
    
    with tab2:
        st.subheader("Vagas Publicadas no Sistema")
        
        with next(get_db()) as db:
            vagas = VagaRepository.listar_vagas(db)
            
            if not vagas:
                st.info("Nenhuma vaga cadastrada até o momento.")
            else:
                # Transformamos os dados em um DataFrame para uma visualização limpa
                dados = []
                for v in vagas:
                    dados.append({
                        "ID": v.id,
                        "Título": v.nome,
                        "Local": v.localidade,
                        "Data Limite": v.data_termino,
                        "Salário": f"R$ {v.salario:,.2f}"
                    })
                
                df = pd.DataFrame(dados)
                
                # Exibição da Tabela Interativa
                st.dataframe(
                    df, 
                    width='stretch', 
                    hide_index=True,
                    column_config={
                        "Data Limite": st.column_config.DateColumn("Prazo Final"),
                        "ID": st.column_config.NumberColumn("Cód")
                    }
                )
                
                st.caption(f"Total de {len(vagas)} oportunidades ativas.")

        if st.sidebar.button("Encerrar Sessão"):
            st.session_state.clear()
            st.rerun()
