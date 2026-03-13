from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Float, CHAR
from sqlalchemy.orm import relationship
from src.database.config import Base
from datetime import datetime, UTC

class UF(Base):
    __tablename__ = "ufs"
    id = Column(Integer, primary_key=True)
    sigla = Column(CHAR(2), unique=True, nullable=False)
    nome = Column(String(50), nullable=False)

class Administrador(Base):
    __tablename__ = "administradores"
    id = Column(Integer, primary_key=True)
    login = Column(String(255), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)

class Vaga(Base):
    __tablename__ = "vagas"
    id = Column(Integer, primary_key=True)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=False)
    cidade = Column(String(100))
    salario = Column(Float)
    ativa = Column(Boolean, default=True)
    uf_id = Column(Integer, ForeignKey("ufs.id"), nullable=False)
    uf = relationship("UF")
    data_criacao = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC).replace(microsecond=0))
    data_expiracao = Column(DateTime(timezone=True))
    candidatos = relationship("Candidato", back_populates="vaga")

class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    celular = Column(String(20), nullable=False) # Alinhado com o DB
    genero = Column(String(20))
    resumo = Column(Text, nullable=False)
    vaga_id = Column(Integer, ForeignKey("vagas.id"), nullable=False)
    vaga = relationship("Vaga", back_populates="candidatos")
    score_ia = Column(Integer)
    parecer_ia = Column(Text)
    data = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC).replace(microsecond=0))
