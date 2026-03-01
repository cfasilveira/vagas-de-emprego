from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from .config import Base
from datetime import date

class Vaga(Base):
    __tablename__ = "vagas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(1000))
    salario = Column(Float, default=0.0)
    beneficios = Column(String(500))
    localidade = Column(String(100)) # Adicionado conforme seu prompt inicial
    data_termino = Column(Date, nullable=False)

class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(100), nullable=False)
    documento = Column(String(20), index=True, nullable=False)
    celular = Column(String(20))
    genero = Column(String(1))
    vaga_id = Column(Integer, ForeignKey("vagas.id"), nullable=False)
    data_inscricao = Column(Date, default=date.today)
