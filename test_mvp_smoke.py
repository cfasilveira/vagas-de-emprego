import requests
from src.database.config import SessionLocal
from src.database.models import UF
from src.security import Security

def test_pilar_1_db():
    try:
        db = SessionLocal()
        count = db.query(UF).count()
        db.close()
        print(f"✅ DB OK ({count} UFs)")
        return True
    except: return False

def test_pilar_2_sec():
    h = Security.gerar_senha_hash("123")
    ok = Security.verificar_senha("123", h)
    if ok: print("✅ Segurança OK")
    return ok

def test_pilar_3_ai():
    print("🔍 Testando IA (Ollama com Mistral-Nemo)...")
    url = "http://host.docker.internal:11434/api/tags"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            modelos = [m['name'] for m in r.json().get('models', [])]
            if "mistral-nemo:latest" in modelos:
                print("✅ Modelo 'mistral-nemo:latest' detectado e pronto!")
                return True
            else:
                print(f"⚠️ Modelos disponíveis: {modelos}. 'mistral-nemo:latest' não encontrado.")
                return False
        return False
    except Exception as e:
        print(f"❌ Falha de conexão: {e}")
        return False

if __name__ == "__main__":
    print("=== SMOKE TEST: VALIDAÇÃO FINAL ===\n")
    if all([test_pilar_1_db(), test_pilar_2_sec(), test_pilar_3_ai()]):
        print("\n🚀 MVP 100% OPERACIONAL E INTEGRADO!")
    else:
        print("\n🚧 VERIFIQUE AS PENDÊNCIAS ACIMA.")
