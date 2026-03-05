from src.database.config import get_db
from src.database.models import Candidato, Inscricao, Vaga
from src.ai_service import AIService
from datetime import datetime
from sqlalchemy import or_

def normalizar_genero(txt):
    """Padroniza a string de gênero para evitar sujeira no banco."""
    if not txt: return "Outro"
    clean = str(txt).strip().upper()
    if clean in ['M', 'MASCULINO']: return 'Masculino'
    if clean in ['F', 'FEMININO']: return 'Feminino'
    return 'Outro'

def realizar_inscricao(vaga_id, dados):
    ai = AIService()
    genero_limpo = normalizar_genero(dados.get('genero'))
    
    try:
        with get_db() as db:
            vaga = db.query(Vaga).filter(Vaga.id == vaga_id).first()
            if not vaga: 
                print(f"❌ Erro: Vaga {vaga_id} inexistente.")
                return False

            # Busca por CPF ou Email para evitar duplicados
            candidato = db.query(Candidato).filter(
                or_(Candidato.documento == dados['documento'], Candidato.email == dados['email'])
            ).first()

            if not candidato:
                candidato = Candidato(
                    nome=dados['nome'],
                    documento=dados['documento'],
                    email=dados['email'],
                    celular=dados['celular'],
                    genero=genero_limpo,
                    resumo=dados['resumo'],
                    ativo=True
                )
                db.add(candidato)
                db.flush()
            else:
                # Atualização inteligente
                candidato.nome = dados['nome']
                candidato.genero = genero_limpo
                candidato.resumo = dados['resumo']
                db.flush()

            # IA analisa o resumo
            feedback_ia = ai.analisar_candidato(vaga.titulo, vaga.descricao, dados['resumo'])

            # Verifica inscrição existente
            insc_existente = db.query(Inscricao).filter(
                Inscricao.candidato_id == candidato.id,
                Inscricao.vaga_id == vaga.id,
                Inscricao.ativo == True
            ).first()

            if not insc_existente:
                nova_insc = Inscricao(
                    candidato_id=candidato.id,
                    vaga_id=vaga.id,
                    data=datetime.utcnow(),
                    feedback_ia=feedback_ia,
                    ativo=True
                )
                db.add(nova_insc)
                print(f"✅ Nova inscrição: {candidato.nome}")
            else:
                insc_existente.feedback_ia = feedback_ia
                print(f"🔔 Inscrição atualizada: {candidato.nome}")
            
            db.commit()
            return True

    except Exception as e:
        print(f"❌ Falha no Handler: {e}")
        return False
