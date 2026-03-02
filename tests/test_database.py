import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from src.database.config import Base, DATABASE_URL
from src.database.models import UF, Vaga, Candidato, Inscricao

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def test_db_resilience():
    """Valida se o banco barra duplicatas de vagas e inscrições."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. SETUP: Criar UF e Vaga
        uf = UF(sigla="GO", nome="Goiás")
        db.add(uf)
        db.commit()

        v1 = Vaga(titulo="Arrumadeira", cidade="Rio Quente", uf_id=uf.id, salario=2500.0)
        db.add(v1)
        db.commit()

        # 2. TESTE: Vaga Duplicada (Deve Falhar)
        v2 = Vaga(titulo="Arrumadeira", cidade="Rio Quente", uf_id=uf.id, salario=2500.0)
        db.add(v2)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        # 3. TESTE: Inscrição Única
        c = Candidato(nome="Carlos", email="c@c.com", documento="123")
        db.add(c)
        db.commit()

        # Primeira inscrição: OK
        i1 = Inscricao(candidato_id=c.id, vaga_id=v1.id)
        db.add(i1)
        db.commit()

        # Segunda inscrição idêntica: DEVE GERAR ERRO NO BANCO
        i2 = Inscricao(candidato_id=c.id, vaga_id=v1.id)
        db.add(i2)
        
        with pytest.raises(IntegrityError):
            db.commit()
            
    finally:
        db.close()
