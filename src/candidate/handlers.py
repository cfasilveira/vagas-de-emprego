from src.database.config import get_db
from src.database.models import Candidato, Inscricao, Vaga
from src.ai_service import AIService
from datetime import datetime
from sqlalchemy import or_

def realizar_inscricao(vaga_id, dados):
    ai = AIService()
    
    try:
        with get_db() as db:
            # 1. FAIL FIRST: Verifica se a vaga existe antes de qualquer processamento
            vaga = db.query(Vaga).filter(Vaga.id == vaga_id).first()
            if not vaga: 
                print(f"❌ Erro: Vaga ID {vaga_id} não encontrada.")
                return False

            # 2. BUSCA INTELIGENTE: Evita UniqueViolation de CPF ou E-mail
            # Procuramos por um candidato que tenha o MESMO documento OU o MESMO e-mail
            candidato = db.query(Candidato).filter(
                or_(
                    Candidato.documento == dados['documento'],
                    Candidato.email == dados['email']
                )
            ).first()

            if not candidato:
                # Se não existe, cria um novo registro
                candidato = Candidato(
                    nome=dados['nome'],
                    documento=dados['documento'],
                    email=dados['email'],
                    celular=dados['celular'],
                    genero=dados['genero'],
                    resumo=dados['resumo'],
                    ativo=True
                )
                db.add(candidato)
                db.flush() # Sincroniza para obter o ID sem fechar a transação
            else:
                # Se já existe (pelo CPF ou E-mail), apenas atualizamos os dados para manter sincronia
                candidato.nome = dados['nome']
                candidato.email = dados['email']
                candidato.celular = dados['celular']
                candidato.resumo = dados['resumo']
                db.flush()

            # 3. IA ANALISA O MATCH (Com tratamento de erro interno no ai_service)
            feedback_ia = ai.analisar_candidato(vaga.titulo, vaga.descricao, dados['resumo'])

            # 4. IDEMPOTÊNCIA DE INSCRIÇÃO: Verifica se já existe inscrição ATIVA para ESTA vaga específica
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
                    feedback_ia=feedback_ia,
                    ativo=True
                )
                db.add(nova_inscricao)
                print(f"✅ Inscrição confirmada para {candidato.nome}")
            else:
                # Atualiza o feedback da IA mesmo se já estiver inscrito (Refresh)
                inscricao_existente.feedback_ia = feedback_ia
                print(f"🔔 Inscrição atualizada para {candidato.nome}")
            
            db.commit()
            return True

    except Exception as e:
        print(f"❌ Falha Crítica no Handler: {e}")
        # O context manager do get_db() cuidará do rollback automaticamente
        return False
