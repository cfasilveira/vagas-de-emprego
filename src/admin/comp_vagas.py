import streamlit as st
import pandas as pd
from src.database.config import get_db
from src.database.models import Vaga, Candidato, Inscricao, UF

def render_dashboard(inscricoes):
    st.subheader("📊 Estatísticas Estratégicas")
    
    with get_db() as db:
        total_vagas = db.query(Vaga).count()
        total_cand = db.query(Candidato).count()
        vagas_com_ins = db.query(Inscricao.vaga_id).distinct().count()
        perc_inscritas = (vagas_com_ins / total_vagas * 100) if total_vagas > 0 else 0

        vagas_por_uf = {}
        for v in db.query(Vaga).all():
            sigla = v.uf.sigla if v.uf else 'N/A'
            vagas_por_uf[sigla] = vagas_por_uf.get(sigla, 0) + 1

        cand_por_uf = {}
        for i in inscricoes:
            sigla = i.vaga.uf.sigla if (i.vaga and i.vaga.uf) else 'N/A'
            cand_por_uf[sigla] = cand_por_uf.get(sigla, 0) + 1

        st.markdown("### 📋 Painel de Vagas")
        v1, v2, v3 = st.columns(3)
        v1.metric("Total de Vagas Oferecidas", total_vagas)
        v2.metric("Total de Candidatos", total_cand)
        v3.metric("% Vagas com Inscrição", f"{perc_inscritas:.1f}%")

        st.divider()

        st.markdown("### 📍 Painel por UF")
        if vagas_por_uf and cand_por_uf:
            u1, u2 = st.columns(2)
            with u1:
                st.info(f"**Estatísticas de Vagas**\n\n"
                        f"🏆 UF com mais vagas: {max(vagas_por_uf, key=vagas_por_uf.get)} ({max(vagas_por_uf.values())})\n\n"
                        f"📉 UF com menos vagas: {min(vagas_por_uf, key=vagas_por_uf.get)} ({min(vagas_por_uf.values())})")
            with u2:
                st.success(f"**Estatísticas de Candidatos**\n\n"
                           f"🏆 UF com mais candidatos: {max(cand_por_uf, key=cand_por_uf.get)} ({max(cand_por_uf.values())})\n\n"
                           f"📉 UF com menos candidatos: {min(cand_por_uf, key=cand_por_uf.get)} ({min(cand_por_uf.values())})")

def render_vagas_manager():
    st.subheader("⚙️ Controle de Vagas")
    
    with get_db() as db:
        with st.expander("➕ Cadastrar Nova Vaga", expanded=False):
            with st.form("form_nova_vaga", clear_on_submit=True):
                titulo = st.text_input("Título da Vaga*")
                descricao = st.text_area("Descrição/Requisitos*")
                
                # Primeira linha: Salário com R$ fixo
                salario = st.number_input("Salário (R$)", min_value=0.0, format="%.2f", value=0.0, step=100.0, help="Informe o valor em Reais")
                
                # Segunda linha: Cidade e UF juntas
                col_cid, col_uf = st.columns([3, 1])
                cidade = col_cid.text_input("Cidade")
                
                ufs_db = db.query(UF).all()
                opcoes_uf = {u.sigla: u.id for u in ufs_db}
                uf_sel = col_uf.selectbox("UF", options=list(opcoes_uf.keys()))

                if st.form_submit_button("Salvar Vaga", type="primary", width="stretch"):
                    if titulo and descricao:
                        nova_vaga = Vaga(
                            titulo=titulo,
                            descricao=descricao,
                            salario=salario,
                            cidade=cidade,
                            uf_id=opcoes_uf[uf_sel],
                            ativo=True
                        )
                        db.add(nova_vaga)
                        db.commit()
                        st.success("Vaga cadastrada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Por favor, preencha o Título e a Descrição.")

        st.divider()

        vagas = db.query(Vaga).all()
        if not vagas:
            st.info("Nenhuma vaga cadastrada.")
            return

        for v in vagas:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                status = "🟢" if v.ativo else "🔴"
                col1.write(f"{status} **{v.titulo}**")
                col2.write(f"R$ {v.salario:,.2f}" if v.salario else "R$ 0,00")
                
                if col3.button("Pausar/Ativar", key=f"st_{v.id}", width="stretch"):
                    v.ativo = not v.ativo
                    db.commit()
                    st.rerun()
                
                if col4.button("🗑️ Remover", key=f"del_{v.id}", type="secondary", width="stretch"):
                    db.delete(v)
                    db.commit()
                    st.rerun()
