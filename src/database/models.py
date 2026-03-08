from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from src.database.config import Base
from datetime import datetime

class Genero(Base):
    __tablename__ = "generos"
    id = Column(Integer, primary_key=True)
    nome = Column(String(20), unique=True, nullable=False) # 'Masculino' ou 'Feminino'

class Escolaridade(Base):
    __tablename__ = "escolaridade"
    id = Column(Integer, primary_key=True)
    nivel = Column(String(50), unique=True, nullable=False)

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
    fk_uf = Column(Integer, ForeignKey("ufs.id"))
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_expiracao = Column(DateTime)
    ativo = Column(Boolean, default=True)
    
    uf = relationship("UF")

class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    nascimento = Column(DateTime)
    cpf = Column(String(14), unique=True, nullable=False)
    whatsapp = Column(String(20))
    resumo = Column(Text)
    fk_genero = Column(Integer, ForeignKey("generos.id"))
    fk_escolaridade = Column(Integer, ForeignKey("escolaridade.id"))
    
    genero = relationship("Genero")
    escolaridade = relationship("Escolaridade")

class Inscricao(Base):
    __tablename__ = "inscricoes"
    id = Column(Integer, primary_key=True)
    fk_candidato = Column(Integer, ForeignKey("candidatos.id"))
    fk_vaga = Column(Integer, ForeignKey("vagas.id"))
    feedback_ia = Column(Text)
    data_inscricao = Column(DateTime, default=datetime.utcnow)
    
    candidato = relationship("Candidato")
    vaga = relationship("Vaga")
