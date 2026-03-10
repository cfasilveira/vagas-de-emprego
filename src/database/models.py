from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Float
from sqlalchemy.orm import relationship
from src.database.config import Base
from datetime import datetime, UTC

class UF(Base):
    __tablename__ = "ufs"
    id = Column(Integer, primary_key=True)
    sigla = Column(String(2), unique=True, nullable=False)
    nome = Column(String(50), nullable=False)

class Administrador(Base):
    __tablename__ = "administradores"
    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)

class Vaga(Base):
    __tablename__ = "vagas"
    id = Column(Integer, primary_key=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=False)
    cidade = Column(String(100))
    salario = Column(Float)
    ativo = Column(Boolean, default=True)
    uf_id = Column(Integer, ForeignKey("ufs.id")) # Sincronizado com simular.py

class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    documento = Column(String(20)) # Sincronizado com simular.py
    genero = Column(String(20))    # Sincronizado com simular.py (String direta)
    telefone = Column(String(20))
    resumo = Column(Text)
    endereco = Column(String(255))

class Inscricao(Base):
    __tablename__ = "inscricoes"
    id = Column(Integer, primary_key=True)
    candidato_id = Column(Integer, ForeignKey("candidatos.id"))
    vaga_id = Column(Integer, ForeignKey("vagas.id"))
    feedback_ia = Column(Text)
    data = Column(DateTime, default=lambda: datetime.now(UTC))
