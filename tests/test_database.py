# tests/test_database.py
from src.database import init_db, get_db, Vaga, Candidato
from src.database.repository import VagaRepository, CandidatoRepository
from datetime import date, timedelta

def testar_fluxo_banco():
    print("--- 🚀 Iniciando Teste de Integração (Database Modular) ---")
    
    # 1. Inicializa as tabelas
    init_db()
    print("✅ Passo 1: Tabelas verificadas/criadas.")

    with next(get_db()) as db:
        # 2. Teste de Criação de Vaga
        nome_vaga = "Dev Python Senior"
        local = "Remoto"
        data_fim = date.today() + timedelta(days=30)

        # Limpeza para o teste ser repetível
        vaga_existente = VagaRepository.buscar_duplicada(db, nome_vaga, local, data_fim)
        if not vaga_existente:
            nova_vaga = Vaga(nome=nome_vaga, descricao="Teste", salario=10000, localidade=local, data_termino=data_fim)
            VagaRepository.salvar(db, nova_vaga)
            print(f"✅ Passo 2: Vaga '{nome_vaga}' criada.")
        else:
            print(f"ℹ️ Passo 2: Vaga '{nome_vaga}' já existia (OK).")

        # 3. Teste de Duplicidade (O ponto crítico!)
        duplicada = VagaRepository.buscar_duplicada(db, nome_vaga, local, data_fim)
        if duplicada:
            print("✅ Passo 3: Detector de duplicidade de vagas funcionando!")

        # 4. Teste de Inscrição de Candidato
        doc_teste = "12345678901"
        vaga_id = duplicada.id
        
        if not CandidatoRepository.ja_inscrito(db, doc_teste, vaga_id):
            candi = Candidato(nome_completo="Carlos Teste", documento=doc_teste, vaga_id=vaga_id)
            CandidatoRepository.salvar(db, candi)
            print("✅ Passo 4: Candidato inscrito com sucesso.")
        
        # 5. Verificação de Duplicidade de Candidato
        if CandidatoRepository.ja_inscrito(db, doc_teste, vaga_id):
            print("✅ Passo 5: Detector de duplicidade de candidatos funcionando!")

    print("\n--- ✨ Teste de Integração Concluído com Sucesso! ---")

if __name__ == "__main__":
    testar_fluxo_banco()
