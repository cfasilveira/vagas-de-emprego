import streamlit as st
from datetime import date
from src.database.config import get_db
from src.database.models import Vaga
from src.security import SecurityGate

def render_vaga_form():
    """
    Interface de Cadastro de Vagas (Aba 1).
    Agora com proteção contra duplicidade de registros.
    """
    st.subheader("📢 Publicar Nova Oportunidade")
    
    with st.form("form_cadastro_vaga", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            nome = st.text_input("Título da Vaga*", placeholder="Ex: Desenvolvedor Fullstack")
            localidade = st.text_input("Localidade*", placeholder="Ex: Remoto ou Goiânia - GO")
            
        with col2:
            salario = st.number_input("Salário (R$)", min_value=0.0, step=500.0, format="%.2f")
            data_termino = st.date_input("Prazo de Inscrição", min_value=date.today())

        descricao = st.text_area("Descrição Detalhada e Requisitos*", height=150)
        
        st.markdown("---")
        submit = st.form_submit_button("✅ Salvar e Publicar Vaga")

        if submit:
            # 1. Validação de Campos Obrigatórios
            if not nome or not localidade or not descricao:
                return st.error("❗ Por favor, preencha todos os campos obrigatórios (*).")

            # 2. Validação de Segurança (Injection Proof)
            if not SecurityGate.validate_input(nome) or not SecurityGate.validate_input(descricao):
                return st.error("❌ Caracteres não permitidos detectados nos campos de texto.")

            try:
                with next(get_db()) as db:
                    # --- FAIL FIRST: VERIFICAÇÃO DE DUPLICIDADE ---
                    vaga_repetida = db.query(Vaga).filter(
                        Vaga.nome == nome,
                        Vaga.localidade == localidade,
                        Vaga.salario == salario
                    ).first()

                    if vaga_repetida:
                        return st.warning(f"⚠️ A vaga '{nome}' para '{localidade}' já está cadastrada.")

                    # 3. Inserção Segura
                    nova_vaga = Vaga(
                        nome=nome,
                        localidade=localidade,
                        salario=salario,
                        data_termino=data_termino,
                        descricao=descricao
                    )
                    db.add(nova_vaga)
                    db.commit()
                    st.success(f"🚀 Vaga '{nome}' publicada com sucesso!")
                    
            except Exception as e:
                st.error(f"☢️ Erro ao persistir dados: {str(e)}")
