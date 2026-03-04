# src/admin/__init__.py

from .views import render_admin_portal
from .auth import check_password, render_login
from .forms import render_vaga_form

# Expõe apenas o essencial para o main.py e mantém o namespace limpo
__all__ = [
    'render_admin_portal', 
    'check_password', 
    'render_login', 
    'render_vaga_form'
]
