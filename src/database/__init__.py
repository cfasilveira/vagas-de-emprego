from .config import Base, engine, get_db
from .models import Vaga, Candidato

def init_db():
    Base.metadata.create_all(bind=engine)
