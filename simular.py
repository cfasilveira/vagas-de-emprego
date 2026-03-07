import random
from datetime import datetime, UTC
from src.database.config import get_db
from src.database.models import Vaga, UF, Inscricao, Candidato

def rodar_simulacao_diversificada():
    print("🚀 Iniciando simulação de dados...")
    with get_db() as db:
        ufs = {u.sigla: u.id for u in db.query(UF).all()}
        if not ufs:
            return print("❌ Erro: UFs não encontradas. Rode o seed.py primeiro.")

        vagas_data = [
            ("Dev Python Pleno", "SP", 9500.0, "FastAPI e Clean Architecture."),
            ("Analista de Dados", "PR", 8000.0, "Pandas, SQL e PowerBI."),
            ("Engenheiro Cloud", "SC", 13000.0, "Terraform e AWS."),
            ("Cozinheiro", "MG", 3500.0, "Cozinha industrial e buffet profissional.")
        ]
        
        v_criadas = []
        for t, s, sal, d in vagas_data:
            v = Vaga(titulo=t, cidade="Hub Tech", uf_id=ufs[s], salario=sal, descricao=d, ativo=True)
            db.add(v)
            db.flush()
            v_criadas.append(v)

        cands_data = [
            ("Ana Silva", "ana@test.com", "Feminino", "11988887777", "Expert em Python."),
            ("Bruno Melo", "bruno@test.com", "Masculino", "41977776666", "Especialista em BI."),
            ("Carla Souza", "carla@test.com", "Feminino", "48966665555", "Foco em Cloud."),
            ("Diego Lima", "diego@test.com", "Masculino", "31955554444", "Cozinheiro profissional.")
        ]

        for nome, email, gen, tel, pitch in cands_data:
            c = Candidato(
                nome=nome, email=email, 
                documento=f"CPF-{random.randint(100,999)}", 
                genero=gen, telefone=tel, resumo=pitch
            )
            db.add(c)
            db.flush()
            
            v_alvo = random.choice(v_criadas)
            score = random.randint(45, 98)
            db.add(Inscricao(
                candidato_id=c.id, 
                vaga_id=v_alvo.id, 
                feedback_ia=f"SCORE: {score}% | Candidato com ótimo perfil para a vaga.",
                data=datetime.now(UTC)
            ))
        
        db.commit()
        print(f"✅ Sucesso! Estrutura atualizada e dados inseridos.")

if __name__ == "__main__":
    rodar_simulacao_diversificada()
