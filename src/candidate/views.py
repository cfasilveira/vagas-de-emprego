import streamlit as st
import threading
import re
from src.database.config import SessionLocal
from src.database.models import Candidato, Vaga, Inscricao, UF
from src.utils.ai_handler import calcular_match_ia
from sqlalchemy import or_

def apenas_numeros(valor):
    if not valor: return ""
    return "".join(filter(str.isdigit, str(valor)))

def validar_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def processar_ia_background(inscricao_id, resumo, descricao_vaga):
    db = SessionLocal()
    try:
        resultado = calcular_match_ia(resumo, descricao_vaga)
        insc = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
        if insc:
            insc.feedback_ia = resultado
            db.commit()
    except Exception as e:
        print(f"Erro IA Background: {e}")
    finally:
        db.close()

def render_candidate_portal():
    st.title("🚀 portal de oportunidades")
    db = SessionLocal()
    try:
        ufs = db.query(UF).order_by(UF.sigla).all()
        vagas = db.query(Vaga).filter(or_(Vaga.ativo == True, Vaga.ativo == None)).all()
        if not vagas:
            st.warning("No momento não há vagas abertas.")
            return

        col_detalhe, col_lista = st.columns([0.6, 0.4])
        with col_lista:
            st.subheader("📌 vagas abertas")
            vaga_nomes = [f"{v.titulo} ({v.cidade or 'Remoto'})" for v in vagas]
            escolha = st.radio("Selecione:", vaga_nomes, label_visibility="collapsed")
            idx = vaga_nomes.index(escolha)
            vaga_sel = vagas[idx]

        with col_detalhe:
            st.subheader("📄 detalhes da vaga")
            st.markdown(f"### {vaga_sel.titulo}")
            st.write(f"**Descrição:** {vaga_sel.descricao}")
            if st.button("✅ quero me candidatar agora", use_container_width=True):
                st.session_state.vaga_id_selecionada = vaga_sel.id
                st.session_state.abrir_formulario = True

        if st.session_state.get("abrir_formulario") and st.session_state.get("vaga_id_selecionada") == vaga_sel.id:
            st.divider()
            with st.form("cadastro_candidatura"):
                st.subheader("📝 sua inscrição")
                c1, c2 = st.columns(2)
                with c1:
                    nome = st.text_input("nome completo")
                    email = st.text_input("e-mail")
                    cpf_i = st.text_input("cpf (11 números)")
                    genero_ext = st.selectbox("gênero", ["Feminino", "Masculino"])
                with c2:
                    tel_i = st.text_input("telefone (DDD + número)")
                    cid = st.text_input("cidade")
                    uf_s = st.selectbox("estado", ufs, format_func=lambda x: f"{x.sigla}")
                    cep_i = st.text_input("cep (8 números)")
                
                resumo = st.text_area("resumo profissional", height=100)
                if st.form_submit_button("finalizar"):
                    cpf_l, cep_l, tel_l = apenas_numeros(cpf_i), apenas_numeros(cep_i), apenas_numeros(tel_i)
                    
                    # --- VALIDAÇÃO INTELIGENTE ---
                    alertas = []
                    if len(nome.split()) < 2: alertas.append("Digite nome e sobrenome.")
                    if not validar_email(email): alertas.append("E-mail inválido.")
                    if len(cpf_l) != 11: alertas.append(f"CPF deve ter 11 dígitos (enviado: {len(cpf_l)}).")
                    if len(cep_l) != 8: alertas.append(f"CEP deve ter 8 dígitos (enviado: {len(cep_l)}).")
                    if len(tel_l) < 10 or len(tel_l) > 11: alertas.append(f"Telefone inválido. Use DDD + Número (ex: 62988887777). Enviado: {len(tel_l)} dígitos.")
                    if len(resumo) < 15: alertas.append("Resumo muito curto.")

                    if alertas:
                        st.warning("⚠️ **Verifique os seguintes campos:**")
                        for msg in alertas: st.error(msg)
                    else:
                        try:
                            cand = db.query(Candidato).filter(Candidato.email == email).first()
                            if not cand:
                                cand = Candidato(nome=nome, email=email, cpf=cpf_l, genero=genero_ext[0], 
                                               telefone=tel_l, resumo=resumo, logradouro="Pendente", 
                                               numero="0", bairro="Pendente", cidade=cid, cep=cep_l, 
                                               uf_residencia_id=uf_s.id)
                                db.add(cand)
                                db.flush()
                            
                            nova_insc = Inscricao(candidato_id=cand.id, vaga_id=vaga_sel.id, 
                                                resumo_submetido=resumo, feedback_ia="Analisando...")
                            db.add(nova_insc)
                            db.commit()

                            threading.Thread(target=processar_ia_background, 
                                           args=(nova_insc.id, resumo, vaga_sel.descricao)).start()
                            
                            st.balloons()
                            st.success("Inscrição confirmada!")
                            st.session_state.abrir_formulario = False
                        except Exception as e:
                            db.rollback()
                            # Aqui o sistema "delata" o erro técnico de forma legível
                            st.error(f"Erro de Banco: {str(e).split(']')[0].split(')')[-1] if ']' in str(e) else 'Dados incompatíveis'}")
    finally:
        db.close()
