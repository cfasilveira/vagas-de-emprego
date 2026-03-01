import streamlit as st
from src.database.config import get_db
from src.database.models import Vaga
from src.database.repository import VagaRepository
from src.validators import VagaSchema
from src.logger import log_audit, log_error

def form_cadastro_vaga():
    st.subheader("📢 Nova Oportunidade")
    with st.form("form_vaga", clear_on_submit=True):
        nome = st.text_input("Título", key="f_nome")
        local = st.text_input("Localidade", key="f_local")
        salario = st.number_input("Salário", min_value=0.0)
        data_fim = st.date_input("Data Limite")
        desc = st.text_area("Descrição")
        # ADICIONADO: Campo que o seu Schema exige
        bene = st.text_area("Benefícios (ex: VR, VT, Home Office)")

        if st.form_submit_button("Registrar no Sistema"):
            try:
                # 1. Validar com todos os campos exigidos pelo Schema
                VagaSchema(
                    nome=nome, 
                    descricao=desc, 
                    salario=salario, 
                    data_termino=str(data_fim),
                    beneficios=bene # Agora o Schema não vai mais reclamar
                )
                
                with next(get_db()) as db:
                    if VagaRepository.buscar_duplicada(db, nome, local, data_fim):
                        st.error("🚨 Duplicidade bloqueada pelo servidor.")
                        log_audit(f"BLOQUEIO: Vaga duplicada negada: {nome}")
                    else:
                        # 2. Salvar no Banco (Mapeando corretamente os campos)
                        vaga = Vaga(
                            nome=nome, 
                            localidade=local, 
                            salario=salario, 
                            data_termino=data_fim, 
                            descricao=desc,
                            beneficios=bene
                        )
                        VagaRepository.salvar(db, vaga)
                        st.success(f"Vaga '{nome}' publicada com sucesso!")
                        log_audit(f"DATABASE: Nova vaga inserida: {nome}")
            
            except Exception as e:
                # Melhoria: Mostra o erro real se algo ainda falhar
                st.error(f"Erro na validação: {str(e)}")
                log_error(f"Falha técnica: {str(e)}")
