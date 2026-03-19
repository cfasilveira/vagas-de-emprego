import random
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.database.config import DATABASE_URL, Base
from src.database.models import UF, Administrador, Vaga, Candidato, Inscricao
from src.security import Security
from datetime import datetime, UTC

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed():
    print("🧹 Reiniciando tabelas para teste limpo...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Popular UFs
        ufs_data = [
            ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
            ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"),
            ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"),
            ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"),
            ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), 
            ("RN", "Rio Grande do Norte"), ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), 
            ("RR", "Roraima"), ("SC", "Santa Catarina"), ("SP", "São Paulo"), 
            ("SE", "Sergipe"), ("TO", "Tocantins")
        ]
        print("🌱 Populando UFs...")
        for sigla, nome in ufs_data:
            db.add(UF(sigla=sigla, nome=nome))
        db.commit()

        # 2. Criar Vagas
        print("💼 Criando vagas variadas...")
        ufs_db = db.query(UF).all()
        vagas_data = [
            ("Cozinheiro", "Preparação de pratos.", "Goiânia", ufs_db[8].id, 2800.0),
            ("Recepcionista", "Atendimento público.", "Maceió", ufs_db[1].id, 2200.0),
            ("Auxiliar de Limpeza", "Limpeza geral.", "São Paulo", ufs_db[24].id, 2100.0),
            ("Garçom", "Serviço de mesa.", "Florianópolis", ufs_db[23].id, 2400.0)
        ]
        for titulo, desc, cidade, uf_id, salario in vagas_data:
            db.add(Vaga(titulo=titulo, descricao=desc, cidade=cidade, uf_id=uf_id, salario=salario, ativo=True))
        db.commit()
        vagas_db = db.query(Vaga).all()

        # 3. Adicionar 10 Candidatos (Mapeado conforme models.py)
        print("👥 Adicionando 10 candidatos completos...")
        candidatos_raw = [
            ("Ana Oliveira", "ana@email.com", "F", "Experiência em buffet."),
            ("Bruno Santos", "bruno@email.com", "M", "Especialista em massas."),
            ("Carla Souza", "carla@email.com", "F", "Atendimento bilíngue."),
            ("Diego Lima", "diego@email.com", "M", "Auxiliar operacional."),
            ("Elena Martins", "elena@email.com", "F", "Limpeza organizada."),
            ("Fabio Silva", "fabio@email.com", "M", "Garçom sommelier."),
            ("Gisele Rocha", "gisele@email.com", "F", "Cozinha industrial."),
            ("Hugo Mendes", "hugo@email.com", "M", "Recepcionista noturno."),
            ("Iara Costa", "iara@email.com", "F", "Atendimento e caixa."),
            ("João Pereira", "joao@email.com", "M", "Serviços gerais.")
        ]

        for i, (nome, email, genero, resumo) in enumerate(candidatos_raw):
            vaga = random.choice(vagas_db)
            # Candidato conforme src/database/models.py
            cand = Candidato(
                nome=nome, 
                email=email, 
                genero=genero, 
                celular=f"6298888000{i}",
                resumo=resumo,
                vaga_id=vaga.id,
                score_ia=random.randint(60, 95),
                data=datetime.now(UTC)
            )
            db.add(cand)
            db.commit() # Commit aqui para gerar o ID do candidato

            # Criar Inscrição (Tabela vinculada)
            db.add(Inscricao(
                candidato_id=cand.id, 
                vaga_id=vaga.id, 
                resumo_submetido=resumo,
                feedback_ia=f"O candidato apresenta aderência de {cand.score_ia}% baseada em seu histórico.",
                data=datetime.now(UTC)
            ))
        
        # 4. Criar admin
        print("👤 Criando admin oficial...")
        h_senha = Security.gerar_senha_hash("seguranca2026")
        db.add(Administrador(login="admin", senha_hash=h_senha))
        
        db.commit()
        print("✅ Sucesso! Use: admin / seguranca2026")
        
    except Exception as e:
        print(f"❌ Erro no seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
