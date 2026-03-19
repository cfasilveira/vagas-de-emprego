import streamlit as st
import pandas as pd
from src.database.config import get_db
from src.database.models import Vaga, Candidato, Inscricao

def render_dashboard(inscricoes):
    st.subheader("📊 Estatísticas Estratégicas")
    
    with get_db() as db:
        # Cálculos do Painel Vagas
        total_vagas = db.query(Vaga).count()
        total_cand = db.query(Candidato).count()
        vagas_com_ins = db.query(Inscricao.vaga_id).distinct().count()
        perc_inscritas = (vagas_com_ins / total_vagas * 100) if total_vagas > 0 else 0

        # Cálculos do Painel UFs
        vagas_por_uf = {}
        for v in db.query(Vaga).all():
            sigla = v.uf.sigla if v.uf else 'N/A'
            vagas_por_uf[sigla] = vagas_por_uf.get(sigla, 0) + 1

        cand_por_uf = {}
        for i in inscricoes:
            sigla = i.vaga.uf.sigla if (i.vaga and i.vaga.uf) else 'N/A'
            cand_por_uf[sigla] = cand_por_uf.get(sigla, 0) + 1

        # Renderização - PAINEL VAGAS
        st.markdown("### 📋 Painel de Vagas")
        v1, v2, v3 = st.columns(3)
        v1.metric("Total de Vagas", total_vagas)
        v2.metric("Total de Candidatos", total_cand)
        v3.metric("% Vagas com Inscrição", f"{perc_inscritas:.1f}%")

        st.divider()

        # Renderização - PAINEL UFs
        st.markdown("### 📍 Painel por UF")
        if vagas_por_uf and cand_por_uf:
            u1, u2 = st.columns(2)
            with u1:
                st.info(f"**Distribuição de Vagas**\n\n"
                        f"🏆 Mais Vagas: {max(vagas_por_uf, key=vagas_por_uf.get)} ({max(vagas_por_uf.values())})\n\n"
                        f"📉 Menos Vagas: {min(vagas_por_uf, key=vagas_por_uf.get)} ({min(vagas_por_uf.values())})")
            with u2:
                st.success(f"**Demanda de Candidatos**\n\n"
                           f"🏆 Mais Candidatos: {max(cand_por_uf, key=cand_por_uf.get)} ({max(cand_por_uf.values())})\n\n"
                           f"📉 Menos Candidatos: {min(cand_por_uf, key=cand_por_uf.get)} ({min(cand_por_uf.values())})")

def render_vagas_manager():
    st.subheader("⚙️ Painel Operacional de Vagas")
    with get_db() as db:
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
