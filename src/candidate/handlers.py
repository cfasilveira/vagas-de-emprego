from src.database.config import SessionLocal
from src.database.models import Candidato, Inscricao, Vaga
from datetime import datetime

def realizar_inscricao(vaga_id, dados):
    db = SessionLocal()
    try:
        # 1. Validação da Vaga
        vaga = db.query(Vaga).filter(Vaga.id == vaga_id).first()
        if not vaga:
            return False

        # 2. Gestão do Candidato
        candidato = db.query(Candidato).filter(
            (Candidato.documento == dados['documento']) | 
            (Candidato.email == dados['email'])
        ).first()

        if not candidato:
            candidato = Candidato(
                nome=dados['nome'],
                documento=dados['documento'],
                email=dados['email'],
                celular=dados['celular'],
                genero=dados['genero'],
                resumo=dados['resumo']
            )
            db.add(candidato)
        else:
            # Atualiza o resumo para refletir a nova candidatura
            candidato.resumo = dados['resumo']
            candidato.celular = dados['celular']
        
        db.flush() 

        # 3. Registro da Inscrição (Evita duplicados pela UniqueConstraint do models)
        nova_inscricao = Inscricao(
            candidato_id=candidato.id,
            vaga_id=vaga.id,
            data=datetime.utcnow(),
            feedback_ia="Aguardando processamento pela IA..."
        )
        
        db.add(nova_inscricao)
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        print(f"❌ Erro Crítico no Handler: {e}") 
        return False
    finally:
        db.close()
