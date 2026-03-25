import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.config import get_db
from src.database.models import Vaga, Inscricao, Candidato, UF
from src.admin.forms import render_vaga_form

def render_dashboard(inscricoes):
    st.subheader("📊 Estatísticas Estratégicas")
    
    with get_db() as db:
        # KPIs GLOBAIS
        total_vagas_global = db.query(Vaga).count()
        total_cand_global = db.query(Candidato).count()
        vagas_com_ins_global = db.query(Inscricao.vaga_id).distinct().count()
        perc_inscritas = (vagas_com_ins_global / total_vagas_global * 100) if total_vagas_global > 0 else 0

        v1, v2, v3 = st.columns(3)
        v1.metric("Vagas Oferecidas", total_vagas_global)
        v2.metric("Total Candidatos", total_cand_global)
        v3.metric("% Vagas c/ Inscrição", f"{perc_inscritas:.1f}%")

        # --- GRÁFICO 1: EVOLUÇÃO TEMPORAL ---
        res_tempo = db.query(Inscricao.data).all()
        if res_tempo:
            df_vagas_tempo = pd.DataFrame(res_tempo, columns=["Data"])
            df_vagas_tempo["Data"] = pd.to_datetime(df_vagas_tempo["Data"]).dt.date
            df_vagas_tempo = df_vagas_tempo.groupby("Data").size().cumsum().reset_index(name="Total")
            fig_time = px.line(df_vagas_tempo, x="Data", y="Total", title="Crescimento de Inscrições")
        else:
            fig_time = px.line(title="Aguardando Inscrições (Sem dados)")
        st.plotly_chart(fig_time, width="stretch")

        # --- GRÁFICO 2: FAIXAS SALARIAIS ---
        res_sal = db.query(Vaga.salario).filter(Vaga.ativo == True).all()
        if res_sal:
            df_sal = pd.DataFrame(res_sal, columns=["Salario"])
            df_sal["Faixa"] = pd.cut(df_sal["Salario"], bins=[0, 3000, 6000, 10000, 100000], 
                                     labels=["Até 3k", "3k-6k", "6k-10k", "Acima 10k"])
            df_sal_count = df_sal["Faixa"].value_counts().reset_index()
            df_sal_count.columns = ["Faixa", "Total"]
            fig_sal = px.pie(df_sal_count, values="Total", names="Faixa", title="Distribuição Salarial")
        else:
            fig_sal = px.pie(title="Nenhuma vaga ativa cadastrada")
        st.plotly_chart(fig_sal, width="stretch")

def render_vagas_manager():
    """Gerencia a aba de Controle de Vagas"""
    st.subheader("➕ Gestão de Oportunidades")
    
    # 1. Formulário de Cadastro (Importado de forms.py)
    render_vaga_form()
    
    st.divider()
    st.subheader("📋 Vagas Cadastradas")
    
    with get_db() as db:
        # Busca UFs para o filtro
        ufs = db.query(UF).order_by(UF.sigla).all()
        opcoes_filtro = {f"{u.sigla} - {u.nome}": u.id for u in ufs}
        
        col_f1, col_f2 = st.columns([1, 2])
        uf_filtro_sel = col_f1.selectbox("Filtrar por UF:", ["Todas"] + list(opcoes_filtro.keys()))

        # Query base
        query = db.query(Vaga)
        
        # Aplicar filtro se selecionado
        if uf_filtro_sel != "Todas":
            id_uf = opcoes_filtro[uf_filtro_sel]
            query = query.filter(Vaga.uf_id == id_uf)
            
        vagas = query.order_by(Vaga.id.desc()).all()
        
        if not vagas:
            st.info("Nenhuma vaga encontrada com os filtros atuais.")
            return

        for v in vagas:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                
                # Info Principal
                uf_sigla = v.uf.sigla if v.uf else "N/A"
                c1.write(f"**{v.titulo}**")
                c1.caption(f"📍 {v.cidade} - {uf_sigla} | 💰 R$ {v.salario:,.2f}")
                
                # Status
                status = "🟢 Ativa" if v.ativo else "🔴 Inativa"
                c2.write(f"Status: {status}")
                
                # Alternar Status
                label_btn = "Desativar" if v.ativo else "Ativar"
                if c3.button(label_btn, key=f"toggle_{v.id}"):
                    v.ativo = not v.ativo
                    db.commit()
                    st.rerun()

                # Excluir
                if c4.button("🗑️ Excluir", key=f"del_{v.id}"):
                    db.delete(v)
                    db.commit()
                    st.success(f"Vaga {v.id} removida!")
                    st.rerun()
