from src.candidate.handlers import realizar_inscricao
from src.database.config import SessionLocal
from src.database.models import Vaga, UF

def rodar_simulacao():
    db = SessionLocal()
    try:
        # 1. Criar uma vaga de teste se não houver
        vaga = db.query(Vaga).first()
        if not vaga:
            uf_sp = db.query(UF).filter(UF.sigla == "SP").first()
            if not uf_sp:
                print("❌ Erro: Rode o seed primeiro para ter os estados!")
                return
            
            vaga = Vaga(
                titulo="Dev Python Enterprise", 
                cidade="São Paulo", 
                salario=12000, 
                uf_id=uf_sp.id, 
                ativo=True,
                descricao="Vaga para testes do sistema minimalista."
            )
            db.add(vaga)
            db.commit()
            print(f"✅ Vaga '{vaga.titulo}' criada para o teste.")
        
        # 2. Dados de 4 candidatos
        candidatos = [
            {"nome": "Ricardo Silva", "documento": "111", "email": "ric@test.com", "celular": "11", "genero": "M", "resumo": "Expert em Python e Docker"},
            {"nome": "Julia Costa", "documento": "222", "email": "ju@test.com", "celular": "21", "genero": "F", "resumo": "Desenvolvedora Backend focada em IA"},
            {"nome": "Marcos Pires", "documento": "333", "email": "mark@test.com", "celular": "31", "genero": "M", "resumo": "Analista de sistemas e dados"},
            {"nome": "Alex Souza", "documento": "444", "email": "alex@test.com", "celular": "41", "genero": "Outro", "resumo": "Dev Fullstack Minimalista"}
        ]

        print("\n🚀 Iniciando simulação de inscrições...")
        for c in candidatos:
            sucesso = realizar_inscricao(vaga.id, c)
            status = "✅" if sucesso else "❌"
            print(f"{status} Inscrição de {c['nome']}")

        print("\n🛡️ Testando Duplicidade (Mesmo CPF na mesma vaga)...")
        realizar_inscricao(vaga.id, candidatos[0])
        print("✅ Processo de duplicidade concluído.")

    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    rodar_simulacao()
