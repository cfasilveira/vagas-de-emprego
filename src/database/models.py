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
    tipo_trabalho_id = Column(Integer, ForeignKey("tipos_trabalho.id"), nullable=False)
    quantidade_vagas = Column(Integer, default=1)

class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True)
    nome = Column(CITEXT, nullable=False)
    email = Column(CITEXT, unique=True, nullable=False)
    cpf = Column(CHAR(11), nullable=False)
    genero = Column(CHAR(1), nullable=False)
    telefone = Column(String(11), nullable=False)
    resumo = Column(String(2000), nullable=False)
    logradouro = Column(String(150), nullable=False)
    numero = Column(String(20), nullable=False)
    complemento = Column(String(100))
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    cep = Column(CHAR(8), nullable=False)
    uf_residencia_id = Column(Integer, ForeignKey("ufs.id"), nullable=False)
    # Relacionamento para acessar a UF real do candidato
    uf_residencia = relationship("UF")

    __table_args__ = (
        CheckConstraint("genero IN ('M', 'F')", name="check_genero_mf"),
        CheckConstraint("cpf ~ '^[0-9]{11}$'", name="check_cpf_numerico"),
    )

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
