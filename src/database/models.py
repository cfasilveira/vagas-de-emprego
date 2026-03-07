from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from src.database.config import Base
from datetime import datetime

class UF(Base):
    __tablename__ = "ufs"
    id = Column(Integer, primary_key=True)
    sigla = Column(String(2), unique=True, nullable=False)
    nome = Column(String(50), nullable=False)

class Vaga(Base):
    __tablename__ = "vagas"
    id = Column(Integer, primary_key=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(Text)
    cidade = Column(String(100))
    salario = Column(Float)
    ativo = Column(Boolean, default=True)
    uf_id = Column(Integer, ForeignKey("ufs.id"))
    uf = relationship("UF")

class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    documento = Column(String(20), unique=True, nullable=False)
    genero = Column(String(20))
    telefone = Column(String(20)) # Novo Campo
    resumo = Column(Text)

class Inscricao(Base):
    __tablename__ = "inscricoes"
    id = Column(Integer, primary_key=True)
    candidato_id = Column(Integer, ForeignKey("candidatos.id"))
    vaga_id = Column(Integer, ForeignKey("vagas.id"))
    data = Column(DateTime, default=datetime.utcnow)
    feedback_ia = Column(Text)
    
    candidato = relationship("Candidato")
    vaga = relationship("Vaga")

class Administrador(Base):
    __tablename__ = "administradores"
    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
