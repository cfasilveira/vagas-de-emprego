import streamlit as st

def render_candidato_card(cand):
    """Renderiza o card do candidato com Fail First (Aba 3)."""
    nome_vaga = cand.vaga.nome if cand.vaga else "Vaga Removida"
    
    with st.expander(f"👤 {cand.nome_completo} | Vaga: {nome_vaga}"):
        col1, col2 = st.columns(2)
        with col1: st.write(f"**📧 E-mail:** {cand.email}")
        with col2: st.write(f"**📱 Celular:** {cand.celular}")
        
        st.markdown("---")
        st.info(cand.resumo_experiencia or "Sem resumo disponível.")
        
        st.markdown("**🤖 Análise da IA:**")
        
        # --- FAIL FIRST ---
        if not cand.feedback_ia:
            return st.info("⏳ O feedback da IA ainda não foi gerado.")

        feedback = cand.feedback_ia
        if "Erro" in feedback or "indisponível" in feedback.lower():
            return st.warning(f"⚠️ {feedback}")

