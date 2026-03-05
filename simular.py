import os
import sys
import random
from src.database.config import SessionLocal
from src.database.models import Vaga, UF
from src.database.seed import seed
from src.candidate.handlers import realizar_inscricao

def rodar_teste_estresse_bi():
    print("🧪 Iniciando Simulação de Estresse de Dados (Gráfico de Pizza)...")
    seed()
    
    with SessionLocal() as db:
        vaga = db.query(Vaga).first()
        if not vaga:
            print("❌ Crie uma vaga primeiro!")
            return
        vaga_id = vaga.id

    # Lista de dados "sujos" para testar a normalização
    testes = [
        {"nome": "João Silva", "gen": "m", "doc": "111"},
        {"nome": "Pedro Souza", "gen": "Masculino", "doc": "222"},
        {"nome": "Maria Luz", "gen": " f ", "doc": "333"},
        {"nome": "Ana Costa", "gen": "FEMININO", "doc": "444"},
        {"nome": "Alex Doe", "gen": "Outros", "doc": "555"},
        {"nome": "Bia Melo", "gen": "n/a", "doc": "666"},
    ]
    
    print(f"🤖 Acionando Mistral-Nemo para {len(testes)} inscrições...")
    
    for t in testes:
        dados = {
            "nome": t['nome'],
            "documento": t['doc'],
            "email": f"teste_{t['doc']}@ai.com",
            "celular": "629999999",
            "genero": t['gen'],
            "resumo": "Experiência sólida em Python e engenharia de dados para modelos de IA."
        }
        realizar_inscricao(vaga_id, dados)

    print("\n🚀 TESTE CONCLUÍDO!")
    print("📊 Abra o Dashboard. O gráfico de Gênero deve exibir apenas 3 fatias limpas.")

if __name__ == "__main__":
    rodar_teste_estresse_bi()
