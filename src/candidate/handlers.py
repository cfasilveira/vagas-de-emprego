from src.database.config import get_db
from src.database.models import Candidato, Inscricao, Vaga
from src.ai_service import AIService
from datetime import datetime

def realizar_inscricao(vaga_id, dados):
    ai = AIService()
    
    try:
        with get_db() as db:
            # 1. Verifica se a vaga existe
            vaga = db.query(Vaga).filter(Vaga.id == vaga_id).first()
            if not vaga: 
                return False

            # 2. Busca ou Cria/Atualiza o Candidato por CPF
            candidato = db.query(Candidato).filter(Candidato.documento == dados['documento']).first()

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
                # Atualiza dados para manter sincronia
                candidato.nome = dados['nome']
                candidato.email = dados['email']
                candidato.celular = dados['celular']
                candidato.resumo = dados['resumo']
            
            db.flush() 

            # 3. IA ANALISA O MATCH (Simulação ou Chamada Real)
            feedback_ia = ai.analisar_candidato(vaga.titulo, vaga.descricao, dados['resumo'])

            # 4. Verifica se já existe inscrição ATIVA para esta vaga
            inscricao_existente = db.query(Inscricao).filter(
                Inscricao.candidato_id == candidato.id,
                Inscricao.vaga_id == vaga.id,
                Inscricao.ativo == True
            ).first()

            if not inscricao_existente:
                nova_inscricao = Inscricao(
                    candidato_id=candidato.id,
                    vaga_id=vaga.id,
                    data=datetime.utcnow(),
                    feedback_ia=feedback_ia
                )
                db.add(nova_inscricao)
            
            db.commit()
            return True

    except Exception as e:
        print(f"❌ Erro no Handlers de Inscrição: {e}") 
        return False
