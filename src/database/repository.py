from sqlalchemy.orm import Session
from sqlalchemy import and_
from .models import Vaga, Candidato

class VagaRepository:
    @staticmethod
    def buscar_duplicada(db: Session, nome: str, localidade: str, data_fim):
        return db.query(Vaga).filter(
            and_(Vaga.nome == nome, 
                 Vaga.localidade == localidade, 
                 Vaga.data_termino == data_fim)
        ).first()

    @staticmethod
    def salvar(db: Session, vaga: Vaga):
        db.add(vaga)
        db.commit()
        db.refresh(vaga)
        return vaga

    @staticmethod
    def listar_vagas(db: Session):
        """Retorna todas as vagas ordenadas pela data de criação (mais recentes primeiro)."""
        return db.query(Vaga).order_by(Vaga.id.desc()).all()

class CandidatoRepository:
    @staticmethod
    def ja_inscrito(db: Session, documento: str, vaga_id: int):
        return db.query(Candidato).filter(
            and_(Candidato.documento == documento, 
                 Candidato.vaga_id == vaga_id)
        ).first()

    @staticmethod
    def salvar(db: Session, candidato: Candidato):
        db.add(candidato)
        db.commit()
        db.refresh(candidato)
        return candidato
