import streamlit as st

st.set_page_config(
    page_title="RH IA - Portal de Vagas",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #003366;
        }
        [data-testid="stSidebar"] *, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] .stMarkdown p {
            color: white !important;
        }
        div[data-testid="stSidebar"] button[key="logout_sidebar"] {
            background-color: #ff4b4b !important;
            border: none !important;
        }
        div[data-testid="stSidebar"] button[key="logout_sidebar"] p {
            color: white !important;
            font-weight: bold !important;
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
