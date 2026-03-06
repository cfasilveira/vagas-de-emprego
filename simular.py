from src.database.config import SessionLocal
from src.database.models import Vaga, UF, Candidato, Inscricao
from src.database.seed import seed
from src.candidate.handlers import realizar_inscricao

def simular_producao():
    print("🧹 Limpando e Populando Massa de Dados BI...")
    db = SessionLocal()
    try:
        db.query(Inscricao).delete()
        db.query(Candidato).delete()
        db.query(Vaga).delete()
        db.commit()
        
        seed()

        uf_sp = db.query(UF).filter_by(sigla="SP").first()
        uf_rj = db.query(UF).filter_by(sigla="RJ").first()
        uf_go = db.query(UF).filter_by(sigla="GO").first()

        # Criando Vagas Variadas
        v1 = Vaga(titulo="Arquiteto Cloud", cidade="São Paulo", uf_id=uf_sp.id, ativo=True, salario=18000.0)
        v2 = Vaga(titulo="Analista de Dados", cidade="Rio de Janeiro", uf_id=uf_rj.id, ativo=True, salario=9500.0)
        v3 = Vaga(titulo="Dev Python", cidade="Goiânia", uf_id=uf_go.id, ativo=True, salario=11000.0)
        db.add_all([v1, v2, v3])
        db.commit()

        # Massa de Candidatos (Diversidade de Gêneros e Estados)
        candidatos = [
            ("Ana Silva", "Expert AWS", v1.id, "101", "Feminino"),
            ("Beatriz Tech", "Azure Specialist", v1.id, "102", "Feminino"),
            ("Carlos Data", "SQL/Python", v2.id, "103", "Masculino"),
            ("Daniela Python", "FastAPI", v3.id, "104", "Feminino"),
            ("Eduardo Cloud", "DevOps", v1.id, "105", "Masculino"),
            ("Alex Non-Binary", "Fullstack", v3.id, "106", "Outro")
        ]

        print("🤖 IA processando inscrições...")
        for n, r, v, d, g in candidatos:
            realizar_inscricao(v, {
                "nome": n, "documento": d, "email": f"{d}@teste.com", 
                "genero": g, "resumo": r, "celular": "1198888"
            })
            
        print("✨ Simulação BI finalizada com sucesso!")
    finally:
        db.close()

if __name__ == "__main__":
    simular_producao()
