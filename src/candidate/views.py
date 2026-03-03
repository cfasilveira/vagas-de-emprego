import streamlit as st
from .handlers import realizar_inscricao # Importa a lógica de salvar no banco

def exibir_cards_vagas(vagas):
    """Renderiza a lista de vagas em formato de cards com suporte à nova arquitetura."""
    for vaga in vagas:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                # CORREÇÃO: Mudar de .nome para .titulo
                st.subheader(f"🚀 {vaga.titulo}") 
                # CORREÇÃO: Acessar a relação relacional vaga.cidade e vaga.uf.sigla
                st.caption(f"📍 {vaga.cidade} - {vaga.uf.sigla} | 📅 Prazo: {vaga.data_termino}")
            with col2:
                st.write(f"### R$ {vaga.salario:,.2f}")
                if st.button("Candidate-se", key=f"btn_{vaga.id}"):
                    # Salva a vaga escolhida no estado da sessão usando os campos corretos
                    st.session_state.vaga_selecionada = {
                        "id": vaga.id, 
                        "titulo": vaga.titulo, # Mudar de nome para titulo
                        "descricao": vaga.descricao
                    }
                    st.rerun()
            
            with st.expander("Ver detalhes da vaga"):
                st.write(vaga.descricao)
                # O campo benefícios foi removido/integrado à descrição na nova modelagem
                # Se não houver o campo no banco, remova a linha abaixo para evitar novos erros
                # st.write(f"**Benefícios:** {vaga.beneficios}")

def render_formulario_inscricao():
    """Renderiza o formulário de candidatura."""
    vaga = st.session_state.vaga_selecionada
    
    # Botão para voltar à lista
    if st.button("⬅️ Voltar para a lista de vagas"):
        del st.session_state.vaga_selecionada
        st.rerun()

    # CORREÇÃO: Acessar vaga['titulo'] em vez de vaga['nome']
    st.markdown(f"### 📝 Inscrição para: {vaga['titulo']}")
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
                dados_candidato = {
                    "nome": nome,
                    "documento": documento,
                    "email": email,
                    "celular": celular,
                    "genero": genero[0],
                    "resumo": resumo
                }
                
                sucesso = realizar_inscricao(vaga['id'], dados_candidato)
                
                if sucesso:
                    st.success("✅ Candidatura enviada com sucesso! Nossa IA está processando seu perfil.")
                else:
                    st.error("Erro ao processar candidatura. Verifique os logs.")
