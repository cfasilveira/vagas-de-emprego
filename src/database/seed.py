from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.database.config import DATABASE_URL
from src.database.models import UF, Administrador
from passlib.context import CryptContext

# Configuração de segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed():
    db = SessionLocal()
    try:
        # 1. Lista de UFs do Brasil
        ufs = [
            ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
            ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"),
            ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"),
            ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"),
            ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
            ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"), ("SC", "Santa Catarina"),
            ("SP", "São Paulo"), ("SE", "Sergipe"), ("TO", "Tocantins")
        ]
        
        print("🌱 Populando estados (UFs)...")
        for sigla, nome in ufs:
            if not db.query(UF).filter_by(sigla=sigla).first():
                db.add(UF(sigla=sigla, nome=nome))

        # 2. Admin Padrão (Login: admin / Senha: pass)
        if not db.query(Administrador).filter_by(login="admin").first():
            print("👤 Criando administrador padrão...")
            h_senha = pwd_context.hash("pass")
            db.add(Administrador(login="admin", senha_hash=h_senha))
        
        db.commit()
        print("✅ Banco de dados populado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao popular o banco: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()  # Certifique-se de que esta linha está recuada com 4 espaços
