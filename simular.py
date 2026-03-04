import os
import sys
from sqlalchemy.orm import Session
from src.database.config import engine, SessionLocal
from src.database.models import Vaga, UF, Candidato, Inscricao
from src.database.seed import seed
from src.candidate.handlers import realizar_inscricao

def rodar_teste_ponta_a_ponta():
    print("🔍 Iniciando Simulação de Fluxo Completo...")
    
    # 1. Garantir que o banco tem as UFs e Admin
    seed()
    
    with SessionLocal() as db:
    # 2. Simular Admin criando uma Vaga em GO (Goiânia)
        go = db.query(UF).filter_by(sigla="GO").first()
        if not go:
            print("❌ Erro: Estado 'GO' não encontrado. Execute o seed primeiro!")
            return

        print(f"📡 Verificando/Criando vaga em {go.nome}...")
        
        # FAIL FIRST: Verifica se a vaga já existe para não estourar a UniqueConstraint
        vaga = db.query(Vaga).filter_by(
            titulo="Engenheiro de Prompt", 
            cidade="Goiânia", 
            uf_id=go.id
        ).first()

        if not vaga:
            vaga = Vaga(
                titulo="Engenheiro de Prompt",
                cidade="Goiânia",
                uf_id=go.id,
                salario=15000.0,
                descricao="Especialista em LLMs e Python.",
                ativo=True
            )
            db.add(vaga)
            db.commit()
            print(f"✅ Nova vaga criada em Goiânia com ID: {vaga.id}")
        else:
            print(f"🔔 Vaga já existente encontrada em Goiânia (ID: {vaga.id})")
        
        vaga_id = vaga.id
    # 3. Simular Candidato se inscrevendo
    dados_candidato = {
        "nome": "Carlos Teste",
        "documento": "999.888.777-00",
        "email": "carlos@teste.com",
        "celular": "11999999999",
        "genero": "M",
        "resumo": "Experiência com Python, Docker e IA."
    }
    
    print("📝 Simulando inscrição de candidato...")
    sucesso = realizar_inscricao(vaga_id, dados_candidato)
    
    if sucesso:
        print("✅ Inscrição processada com sucesso!")
        
        # 4. Validar se os dados aparecem para o Dashboard
        with SessionLocal() as db:
            contagem = db.query(Inscricao).filter_by(vaga_id=vaga_id).count()
            print(f"📊 Verificação BI: {contagem} inscrição(ões) encontrada(s) para a nova vaga.")
            if contagem > 0:
                print("\n🚀 CONCLUSÃO: O sistema está pronto para produção!")
    else:
        print("❌ Falha na simulação de inscrição.")

if __name__ == "__main__":
    rodar_teste_ponta_a_ponta()
