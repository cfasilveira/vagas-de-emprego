import streamlit as st
from .handlers import realizar_inscricao # Importa a lógica de salvar no banco

def exibir_cards_vagas(vagas):
    """Renderiza a lista de vagas em formato de cards."""
    for vaga in vagas:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"🚀 {vaga.nome}")
                st.caption(f"📍 {vaga.localidade} | 📅 Prazo: {vaga.data_termino}")
            with col2:
                st.write(f"### R$ {vaga.salario:,.2f}")
                if st.button("Candidate-se", key=f"btn_{vaga.id}"):
                    # Salva a vaga escolhida no estado da sessão
                    st.session_state.vaga_selecionada = {
                        "id": vaga.id, 
                        "nome": vaga.nome, 
                        "descricao": vaga.descricao
                    }
                    st.rerun()
            
            with st.expander("Ver detalhes da vaga"):
                st.write(vaga.descricao)
                st.write(f"**Benefícios:** {vaga.beneficios}")

def render_formulario_inscricao():
    """Renderiza o formulário de candidatura (Resolve o ImportError)."""
    vaga = st.session_state.vaga_selecionada
    
    # Botão para voltar à lista
    if st.button("⬅️ Voltar para a lista de vagas"):
        del st.session_state.vaga_selecionada
        st.rerun()

    st.markdown(f"### 📝 Inscrição para: {vaga['nome']}")
    st.info("Preencha seus dados abaixo. Seu resumo será analisado por nossa IA.")

    with st.form("form_candidatura", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        documento = st.text_input("Documento (CPF)")
        email = st.text_input("E-mail")
        celular = st.text_input("Celular")
        genero = st.selectbox("Gênero", ["M", "F", "Não informar"])
        resumo = st.text_area("Resumo da sua experiência e por que você é ideal para esta vaga:", height=200)
        
        enviar = st.form_submit_button("🚀 Enviar Candidatura")
        
        if enviar:
            if not nome or not email or not resumo or not documento:
                st.warning("Por favor, preencha todos os campos obrigatórios.")
            else:
                # Monta o dicionário conforme esperado pelo handlers.py
                dados_candidato = {
                    "nome": nome,
                    "documento": documento,
                    "email": email,
                    "celular": celular,
                    "genero": genero[0], # Pega apenas a primeira letra (M/F/N)
                    "resumo": resumo
                }
                
                # Chama o handler para salvar no banco de dados
                sucesso = realizar_inscricao(vaga['id'], dados_candidato)
                
                if sucesso:
                    st.success("✅ Candidatura enviada com sucesso! Nossa IA está processando seu perfil.")
                    # Aqui é onde entraremos com a chamada da IA no próximo passo
                else:
                    st.error("Erro ao processar candidatura. Verifique os logs.")
