from .config import Base, engine, get_db
from .models import Vaga, Candidato, Inscricao, UF

def init_db(reset=False):
    if reset:
        print("⚠️ Resetando banco de dados...")
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
