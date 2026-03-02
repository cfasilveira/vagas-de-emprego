# src/admin/__init__.py

from .views import render_admin_portal
from .auth import check_password, render_login
from .forms import render_vaga_form
from .comp_vagas import render_vagas_table       # Adicionado
from .comp_candidatos import render_candidato_card # Adicionado

# Isso define o que é exposto publicamente pelo pacote administrativo
__all__ = [
    'render_admin_portal', 
    'check_password', 
    'render_login', 
    'render_vaga_form',
    'render_vagas_table',
    'render_candidato_card'
]
