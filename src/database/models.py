from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, UniqueConstraint, DateTime, Date
from sqlalchemy.orm import relationship
from src.database.config import Base
from datetime import datetime

class UF(Base):
    __tablename__ = "ufs"
    id = Column(Integer, primary_key=True)
    sigla = Column(String(2), unique=True, nullable=False)
    nome = Column(String(50), unique=True, nullable=False)

class Administrador(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)

class Vaga(Base):
    __tablename__ = "vagas"
    id = Column(Integer, primary_key=True)
    titulo = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    salario = Column(Float, nullable=False)
    descricao = Column(Text, nullable=True)
    data_termino = Column(Date, nullable=True)
    uf_id = Column(Integer, ForeignKey("ufs.id"), nullable=False)
    
    uf = relationship("UF")
    inscricoes = relationship("Inscricao", back_populates="vaga", cascade="all, delete")
    
    __table_args__ = (UniqueConstraint('titulo', 'cidade', 'uf_id', name='_vaga_uc'),)

class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    documento = Column(String(20), unique=True, nullable=False)
    celular = Column(String(20), nullable=True)
    
    inscricoes = relationship("Inscricao", back_populates="candidato")

class Inscricao(Base):
    __tablename__ = "inscricoes"
    id = Column(Integer, primary_key=True)
    candidato_id = Column(Integer, ForeignKey("candidatos.id"), nullable=False)
    vaga_id = Column(Integer, ForeignKey("vagas.id"), nullable=False)
    data = Column(DateTime, default=datetime.utcnow) # Pode manter utcnow por enquanto
    feedback_ia = Column(Text, nullable=True)
    
    candidato = relationship("Candidato", back_populates="inscricoes")
    vaga = relationship("Vaga", back_populates="inscricoes")

    # ESTA LINHA É A TRAVA DE SEGURANÇA (Obrigatória para o teste passar):
    __table_args__ = (UniqueConstraint('candidato_id', 'vaga_id', name='_insc_unica_uc'),)    
