from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, UniqueConstraint, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from src.database.config import Base
from datetime import datetime

class UF(Base):
    __tablename__ = "ufs"
    id = Column(Integer, primary_key=True)
    sigla = Column(String(2), unique=True, nullable=False)
    nome = Column(String(50), unique=True, nullable=False)
    vagas = relationship("Vaga", back_populates="uf")

    def __repr__(self):
        return f"{self.sigla}"

class Administrador(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)

    def __repr__(self):
        return f"Admin({self.login})"

class Vaga(Base):
    __tablename__ = "vagas"
    id = Column(Integer, primary_key=True)
    titulo = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    salario = Column(Float, nullable=False, default=0.0)
    descricao = Column(Text, nullable=True)
    data_termino = Column(Date, nullable=True)
    uf_id = Column(Integer, ForeignKey("ufs.id"), nullable=False)
    ativo = Column(Boolean, default=True)
    
    uf = relationship("UF", back_populates="vagas", lazy='joined')
    inscricoes = relationship("Inscricao", back_populates="vaga")
    
    __table_args__ = (UniqueConstraint('titulo', 'cidade', 'uf_id', name='_vaga_uc'),)

    def __repr__(self):
        return f"{self.titulo} ({self.cidade}/{self.uf.sigla if self.uf else '??'})"

class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    documento = Column(String(20), unique=True, nullable=False)
    celular = Column(String(20), nullable=True)
    genero = Column(String(20), nullable=True)
    resumo = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True)
    
    inscricoes = relationship("Inscricao", back_populates="candidato")
    __table_args__ = (UniqueConstraint('documento', name='_candidato_cpf_uc'),)

    def __repr__(self):
        return f"{self.nome} ({self.documento})"

class Inscricao(Base):
    __tablename__ = "inscricoes"
    id = Column(Integer, primary_key=True)
    candidato_id = Column(Integer, ForeignKey("candidatos.id"), nullable=False)
    vaga_id = Column(Integer, ForeignKey("vagas.id"), nullable=False)
    data = Column(DateTime, default=datetime.utcnow)
    feedback_ia = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True)
    
    candidato = relationship("Candidato", back_populates="inscricoes", lazy='joined')
    vaga = relationship("Vaga", back_populates="inscricoes", lazy='joined')

    __table_args__ = (UniqueConstraint('candidato_id', 'vaga_id', name='_insc_unica_uc'),)

    def __repr__(self):
        return f"Inscrição {self.id}: {self.candidato.nome} -> {self.vaga.titulo}"
