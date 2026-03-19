from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Float, CheckConstraint, CHAR
from sqlalchemy.dialects.postgresql import CITEXT
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
    login = Column(CITEXT, unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)

class TipoTrabalho(Base):
    __tablename__ = "tipos_trabalho"
    id = Column(Integer, primary_key=True)
    nome = Column(String(20), unique=True, nullable=False)

class Vaga(Base):
    __tablename__ = "vagas"
    id = Column(Integer, primary_key=True)
    titulo = Column(CITEXT, nullable=False)
    descricao = Column(Text, nullable=False)
    cidade = Column(String(100))
    salario = Column(Float)
    ativo = Column(Boolean, default=True)
    uf_id = Column(Integer, ForeignKey("ufs.id"))
    uf = relationship("UF")

class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True)
    nome = Column(CITEXT, nullable=False)
    email = Column(CITEXT, unique=True, nullable=False)
    genero = Column(CHAR(1), nullable=False)
    celular = Column(String(11), nullable=False)
    resumo = Column(String(2000), nullable=False)
    vaga_id = Column(Integer, ForeignKey("vagas.id"), nullable=False)
    score_ia = Column(Integer)
    parecer_ia = Column(Text)
    data = Column(DateTime(timezone=True))
    vaga_id = Column(Integer, ForeignKey("vagas.id"), nullable=False)
    score_ia = Column(Integer)
    parecer_ia = Column(Text)
    data = Column(DateTime(timezone=True))
    # Relacionamento para acessar a UF real do candidato


class Inscricao(Base):
    __tablename__ = "inscricoes"
    id = Column(Integer, primary_key=True)
    candidato_id = Column(Integer, ForeignKey("candidatos.id", ondelete="CASCADE"))
    vaga_id = Column(Integer, ForeignKey("vagas.id", ondelete="CASCADE"))
    candidato = relationship("Candidato")
    vaga = relationship("Vaga")
    resumo_submetido = Column(Text, nullable=False)
    feedback_ia = Column(Text)
    data = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC).replace(microsecond=0))
