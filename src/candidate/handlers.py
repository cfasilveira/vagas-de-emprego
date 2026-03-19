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
                email=dados['email'],
                celular=dados['telefone'],
                resumo=dados['resumo'],
                genero=dados['genero'][0],
                vaga_id=vaga.id
            )
            db.add(c)
        else:
            c.resumo = dados['resumo']
            c.celular = dados['telefone']
        
        db.flush()
        
        # Chamada IA
        fb = ai.analisar_candidato(vaga.titulo, vaga.descricao, dados['resumo'])
        
        # Registro da Inscrição (FKs corrigidas)
        nova_insc = Inscricao(
            candidato_id=c.id, 
            vaga_id=vaga.id, 
            resumo_submetido=dados['resumo'],
            feedback_ia=fb
        )
        )
        db.add(nova_insc)
        db.commit()
        return True
