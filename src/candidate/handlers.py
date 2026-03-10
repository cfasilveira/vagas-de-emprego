from src.database.config import get_db
from src.database.models import Candidato, Inscricao, Vaga, Genero
from src.ai_service import AIService
from datetime import datetime

def realizar_inscricao(vaga_id, dados):
    """Processa a inscrição usando o schema de 7 tabelas."""
    ai = AIService()
    with get_db() as db:
        vaga = db.query(Vaga).get(vaga_id)
        if not vaga:
            return False
        
        # Busca Gênero ID
        gen = db.query(Genero).filter(Genero.nome == dados['genero']).first()
        
        # Localiza ou cria candidato pelo CPF (Campo único)
        c = db.query(Candidato).filter(Candidato.cpf == dados['documento']).first()
        
        if not c:
            c = Candidato(
                nome=dados['nome'],
                cpf=dados['documento'],
                whatsapp=dados['telefone'],
                resumo=dados['resumo'],
                fk_genero=gen.id if gen else None
            )
            db.add(c)
        else:
            c.resumo = dados['resumo']
            c.whatsapp = dados['telefone']
        
        db.flush()
        
        # Chamada IA
        fb = ai.analisar_candidato(vaga.titulo, vaga.descricao, dados['resumo'])
        
        # Registro da Inscrição (FKs corrigidas)
        nova_insc = Inscricao(
            fk_candidato=c.id, 
            fk_vaga=vaga.id, 
            feedback_ia=fb, 
            data_inscricao=datetime.utcnow()
        )
        db.add(nova_insc)
        db.commit()
        return True
