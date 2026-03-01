# src/database.py
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuração da URL via variável de ambiente (Segurança)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@db:5432/vagas_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Vagas [cite: 38]
class Vaga(Base):
    __tablename__ = "vagas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    descricao = Column(String)
    salario = Column(Float)
    beneficios = Column(String)
    data_termino = Column(Date)

# Modelo de Candidatos [cite: 38]
class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String)
    documento = Column(String, index=True) # RG ou CPF [cite: 38]
    celular = Column(String)
    genero = Column(String)
    vaga_id = Column(Integer, ForeignKey("vagas.id"))
    data_inscricao = Column(Date)

# Função para evitar duplicidade de Vaga [cite: 41]
def existe_vaga_duplicada(db, nome, data_termino):
    return db.query(Vaga).filter(Vaga.nome == nome, Vaga.data_termino == data_termino).first()

# Função para evitar duplicidade de Candidato na mesma vaga [cite: 43]
def candidato_ja_inscrito(db, documento, vaga_id):
    return db.query(Candidato).filter(Candidato.documento == documento, Candidato.vaga_id == vaga_id).first()

def init_db():
    Base.metadata.create_all(bind=engine)
