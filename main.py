import streamlit as st
from src.database.config import engine, SessionLocal
from src.database.models import Base, UF
from src.candidate.views import render_candidate_portal
from src.admin.auth import render_login_page
from src.admin.views import render_admin_portal

# --- INICIALIZAÇÃO AUTOMÁTICA (ESSENCIAL PARA NUVEM) ---
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    if db.query(UF).count() == 0:
        ufs = [
            ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
            ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
            ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
        ]
        for sigla, nome in ufs:
            db.add(UF(sigla=sigla, nome=nome))
        db.commit()
finally:
    db.close()
# -----------------------------------------------------

st.set_page_config(page_title="RH IA", page_icon="🎯", layout="wide")

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

def main():
    with st.sidebar:
        st.title("🚀 Navegação")
        escolha = st.radio("Ir para:", ["Portal do Candidato", "Área Administrativa"])
        st.divider()

    if escolha == "Portal do Candidato":
        render_candidate_portal()
    else:
        if not st.session_state.is_admin:
            render_login_page()
        else:
            render_admin_portal()

if __name__ == "__main__":
    main()
