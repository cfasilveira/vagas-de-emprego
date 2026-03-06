from src.database.config import get_db
from src.database.models import Candidato, Inscricao, Vaga
from src.ai_service import AIService
from datetime import datetime
from sqlalchemy import or_

def normalizar_genero(txt):
    c = str(txt).strip().upper() if txt else ""
    if c in ['M', 'MASCULINO']: return 'Masculino'
    if c in ['F', 'FEMININO']: return 'Feminino'
    return 'Outro'

def realizar_inscricao(vaga_id, dados):
    ai = AIService()
    gen = normalizar_genero(dados.get('genero'))
    with get_db() as db:
        vaga = db.query(Vaga).get(vaga_id)
        if not vaga: return False
        c = db.query(Candidato).filter(or_(Candidato.documento == dados['documento'], Candidato.email == dados['email'])).first()
        if not c:
            c = Candidato(nome=dados['nome'], documento=dados['documento'], email=dados['email'], genero=gen, resumo=dados['resumo'])
            db.add(c); db.flush()
        else:
            c.genero = gen; c.resumo = dados['resumo']
        
        fb = ai.analisar_candidato(vaga.titulo, vaga.descricao, dados['resumo'])
        db.add(Inscricao(candidato_id=c.id, vaga_id=vaga.id, feedback_ia=fb, data=datetime.utcnow()))
        db.commit()
        return True
