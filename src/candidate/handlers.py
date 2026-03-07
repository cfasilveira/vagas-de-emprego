from src.database.config import get_db
from src.database.models import Candidato, Inscricao, Vaga
from src.ai_service import AIService
from datetime import datetime
from sqlalchemy import or_

def realizar_inscricao(vaga_id, dados):
    """
    Processa a inscrição: cria/atualiza o candidato e gera o feedback da IA.
    """
    ai = AIService()
    with get_db() as db:
        # 1. Localiza a vaga
        vaga = db.query(Vaga).get(vaga_id)
        if not vaga:
            return False
        
        # 2. Tenta localizar candidato existente por CPF ou E-mail
        c = db.query(Candidato).filter(
            or_(Candidato.documento == dados['documento'], Candidato.email == dados['email'])
        ).first()
        
        pitch = dados.get('resumo', '')
        telefone = dados.get('telefone', '')
        
        if not c:
            # Cria novo candidato com o campo telefone
            c = Candidato(
                nome=dados['nome'], 
                documento=dados['documento'], 
                email=dados['email'], 
                genero=dados.get('genero'),
                telefone=telefone,
                resumo=pitch
            )
            db.add(c)
        else:
            # Atualiza dados do candidato existente
            c.resumo = pitch
            c.telefone = telefone
        
        # Garante que o ID do candidato esteja disponível para a inscrição
        db.flush()
        
        # 3. Chamar a IA Mistral-Nemo para o veredito
        fb = ai.analisar_candidato(vaga.titulo, vaga.descricao, pitch)
        
        # 4. Registrar a inscrição
        nova_insc = Inscricao(
            candidato_id=c.id, 
            vaga_id=vaga.id, 
            feedback_ia=fb, 
            data=datetime.utcnow()
        )
        db.add(nova_insc)
        db.commit()
        return True
