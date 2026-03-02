from src.database.config import get_db
from src.database.models import Candidato, Vaga
from src.ai_service import AIService

def realizar_inscricao(vaga_id, dados):
    ai = AIService(model="llama3.1") # Ou "mistral"
    
    try:
        with next(get_db()) as db:
            vaga = db.query(Vaga).filter(Vaga.id == vaga_id).first()
            
            # 1. Gerar Análise de IA antes de salvar
            feedback = ai.analisar_candidato(vaga.nome, dados['resumo'])
            
            # 2. Criar objeto do candidato com as novas colunas
            novo_candidato = Candidato(
                nome_completo=dados['nome'],
                documento=dados['documento'],
                email=dados['email'],
                celular=dados['celular'],
                genero=dados['genero'],
                resumo_experiencia=dados['resumo'],
                feedback_ia=feedback,
                vaga_id=vaga_id
            )
            
            db.add(novo_candidato)
            db.commit()
            return True
    except Exception as e:
        print(f"Erro no Handler: {e}")
        return False
