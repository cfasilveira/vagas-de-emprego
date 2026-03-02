import streamlit as st
from src.database.config import get_db
from src.database.repository import VagaRepository
from .views import exibir_cards_vagas, render_formulario_inscricao

def render_candidate_portal():
    """
    Função principal que alterna entre a lista de vagas e o formulário de inscrição.
    """
    # 1. Verifica se o usuário já escolheu uma vaga para se candidatar
    if "vaga_selecionada" not in st.session_state:
        st.title("🎯 Oportunidades Disponíveis")
        st.markdown("---")
        
        # Busca as vagas no banco de dados
        try:
            with next(get_db()) as db:
                vagas = VagaRepository.listar_vagas(db)
                if not vagas:
                    st.info("No momento não temos vagas abertas.")
                else:
                    # Chama a view para renderizar os cards das vagas
                    exibir_cards_vagas(vagas)
        except Exception as e:
            st.error(f"Erro ao carregar vagas: {e}")
    
    # 2. Se houver uma vaga selecionada, renderiza o formulário (Corrige o erro da tela branca)
    else:
        # Esta chamada garante que o formulário apareça na tela
        render_formulario_inscricao()

# O Streamlit recarrega o script do topo, então o estado da sessão 
# controla o que o usuário vê em tempo real.
