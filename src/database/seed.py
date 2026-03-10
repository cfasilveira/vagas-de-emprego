from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.database.config import DATABASE_URL, Base
from src.database.models import UF, Administrador
from src.security import Security

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed():
    print("🧹 Limpando lixo e recriando tabelas...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        ufs = [
            ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
            ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"),
            ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"),
            ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"),
            ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
            ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"), ("SC", "Santa Catarina"),
            ("SP", "São Paulo"), ("SE", "Sergipe"), ("TO", "Tocantins")
        ]
        
        print("🌱 Populando UFs...")
        for sigla, nome in ufs:
            db.add(UF(sigla=sigla, nome=nome))

        print("👤 Criando admin oficial...")
        # Usando a sua classe Security para garantir compatibilidade
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
