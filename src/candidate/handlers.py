from src.database.config import SessionLocal
from src.database.models import Candidato, Inscricao, Vaga
from src.ai_service import AIService
from datetime import datetime

def realizar_inscricao(vaga_id, dados):
    db = SessionLocal()
    ai = AIService() # Usa o padrão qwen2.5-coder:7b
    
    try:
        # 1. FAIL FIRST: A vaga precisa existir
        vaga = db.query(Vaga).filter(Vaga.id == vaga_id).first()
        if not vaga:
            print(f"⚠️ Erro: Tentativa de inscrição em vaga inexistente (ID: {vaga_id})")
            return False

        # 2. Gestão do Candidato (Busca por documento ou email)
        candidato = db.query(Candidato).filter(
            (Candidato.documento == dados['documento']) | 
            (Candidato.email == dados['email'])
        ).first()

        # 3. Lógica Linear (Upsert)
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
        
        # Se o candidato já existia, apenas atualizamos os contatos e resumo
        if candidato.id:
            candidato.resumo = dados['resumo']
            candidato.celular = dados['celular']
        
        db.flush() # Garante que o ID do candidato esteja disponível

        # --- MOMENTO IA: Agora enviando Título e Descrição ---
        feedback_ia = ai.analisar_candidato(
            vaga.titulo, 
            vaga.descricao, 
            dados['resumo']
        )

        # 4. Registro da Inscrição com o Feedback rico
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
        db.rollback()
        print(f"❌ Erro Crítico no Processo: {e}") 
        return False
    finally:
        db.close()
