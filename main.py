import streamlit as st

st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #003366;
        }
        [data-testid="stSidebar"] *, [data-testid="stSidebar"] p {
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

from src.admin.auth import render_login_page
from src.admin.views import render_admin_portal
from src.candidate.views import render_candidate_portal

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

with st.sidebar:
    st.title("RH IA")
    if not st.session_state.is_admin:
        menu = st.radio("Navegação", ["Portal do Candidato", "Área do Recrutador"])

if st.session_state.is_admin:
    render_admin_portal()
else:
    if menu == "Portal do Candidato":
        render_candidate_portal()
    else:
        render_login_page()
