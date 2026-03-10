import streamlit as st
from src.database.config import SessionLocal
from src.database.models import Candidato, Vaga, Inscricao, UF
from sqlalchemy import or_

def limpar_dados(valor):
    if not valor: return ""
    return "".join(filter(str.isdigit, str(valor)))

def render_candidate_portal():
    st.title("🚀 portal de oportunidades")
    
    db = SessionLocal()
    
    try:
        # 1. Carga de Dados
        ufs = db.query(UF).order_by(UF.sigla).all()
        vagas = db.query(Vaga).filter(or_(Vaga.ativo == True, Vaga.ativo == None)).all()
        
        if not vagas:
            st.warning("No momento não há vagas abertas.")
            return

        # 2. Layout em Duas Colunas
        col_detalhe, col_lista = st.columns([0.6, 0.4])

        with col_lista:
            st.subheader("📌 vagas abertas")
            # Criando "Cards" de seleção
            vaga_nomes = [f"{v.titulo} ({v.cidade or 'Remoto'})" for v in vagas]
            escolha = st.radio("Selecione para ver detalhes:", vaga_nomes, label_visibility="collapsed")
            
            # Recupera o objeto da vaga selecionada
            idx = vaga_nomes.index(escolha)
            vaga_sel = vagas[idx]

        with col_detalhe:
            st.subheader("📄 detalhes da vaga")
            st.markdown(f"### {vaga_sel.titulo}")
            st.caption(f"📍 {vaga_sel.cidade or 'Remoto'} | 💰 R$ {vaga_sel.salario:,.2f}")
            st.write("---")
            st.markdown(f"**Descrição e Requisitos:**\n\n{vaga_sel.descricao}")
            
            if st.button("✅ quero me candidatar agora", use_container_width=True):
                st.session_state.vaga_id_selecionada = vaga_sel.id
                st.session_state.abrir_formulario = True

        # 3. Modal/Formulário de Cadastro (Abaixo das colunas se ativado)
        if st.session_state.get("abrir_formulario") and st.session_state.get("vaga_id_selecionada") == vaga_sel.id:
            st.success(f"Ótima escolha! Complete seus dados para a vaga: **{vaga_sel.titulo}**")
            
            with st.form("cadastro_candidatura"):
                c1, c2 = st.columns(2)
                with c1:
                    nome = st.text_input("nome completo")
                    email = st.text_input("e-mail")
                    cpf = st.text_input("cpf (apenas números)")
                    genero_ext = st.selectbox("gênero", ["Feminino", "Masculino"])
                
                with c2:
                    tel = st.text_input("telefone (DDD)")
                    cid = st.text_input("sua cidade")
                    uf_sel = st.selectbox("estado", ufs, format_func=lambda x: f"{x.sigla} - {x.nome}")
                    cep = st.text_input("cep")

                resumo = st.text_area("seu resumo profissional para esta vaga", height=150, 
                                     placeholder="Fale sobre suas experiências com as tecnologias da vaga...")
                
                btn_finalizar = st.form_submit_button("enviar candidatura")

                if btn_finalizar:
                    cpf_limpo = limpar_dados(cpf)
                    gen_map = {"Feminino": "F", "Masculino": "M"}
                    
                    if not nome or not email or len(cpf_limpo) != 11:
                        st.error("Verifique os campos obrigatórios e o CPF (11 dígitos).")
                    elif not resumo:
                        st.error("O resumo é essencial para a análise da IA.")
                    else:
                        try:
                            # Busca/Cria Candidato
                            cand = db.query(Candidato).filter(Candidato.email == email).first()
                            if not cand:
                                cand = Candidato(
                                    nome=nome, email=email, cpf=cpf_limpo, 
                                    genero=gen_map.get(genero_ext), telefone=limpar_dados(tel),
                                    resumo=resumo, logradouro="Pendente", numero="0", bairro="Pendente",
                                    cidade=cid, cep=limpar_dados(cep), uf_residencia_id=uf_sel.id
                                )
                                db.add(cand)
                                db.flush()

                            # Cria Inscrição
                            insc = Inscricao(
                                candidato_id=cand.id, vaga_id=vaga_sel.id,
                                resumo_submetido=resumo, feedback_ia="Processando..."
                            )
                            db.add(insc)
                            db.commit()
                            
                            st.balloons()
                            st.success(f"Inscrição realizada com sucesso, {nome}!")
                            st.session_state.abrir_formulario = False
                        except Exception as e:
                            db.rollback()
                            st.error(f"Erro ao salvar: {e}")

    finally:
        db.close()
