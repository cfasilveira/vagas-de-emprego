# tests/test_validators.py
from src.validators import CandidatoSchema, VagaSchema
from pydantic import ValidationError

def testar_validacoes():
    print("--- Iniciando Testes de Segurança (Validators) ---")

    # Teste 1: Dados Válidos (Sucesso esperado)
    try:
        dados_ok = {
            "nome_completo": "Carlos Silva",
            "documento": "123.456.789-00",
            "celular": "(11) 98888-7777",
            "genero": "M"
        }
        candidato = CandidatoSchema(**dados_ok)
        print("✅ Teste 1 (Dados Válidos): Passou! Documento limpo:", candidato.documento)
    except ValidationError as e:
        print("❌ Teste 1 Falhou inesperadamente:", e.json())

    # Teste 2: Tentativa de Injeção de Script (Hacker do bem bloqueando)
    try:
        dados_maliciosos = {
            "nome_completo": "Carlos <script>alert(1)</script>",
            "documento": "1234567",
            "celular": "11999998888",
            "genero": "M"
        }
        CandidatoSchema(**dados_maliciosos)
        print("❌ Teste 2 (Injeção): Falhou! O sistema aceitou caracteres perigosos.")
    except ValidationError:
        print("✅ Teste 2 (Injeção): Passou! Bloqueou caracteres especiais com sucesso.")

    # Teste 3: Salário Negativo (Regra de negócio)
    try:
        vaga_ruim = {
            "nome": "Dev Python",
            "descricao": "Vaga remota",
            "salario": -1000.0,
            "beneficios": "Nenhum",
            "data_termino": "2026-12-31"
        }
        VagaSchema(**vaga_ruim)
        print("❌ Teste 3 (Salário): Falhou! O sistema aceitou salário negativo.")
    except ValidationError:
        print("✅ Teste 3 (Salário): Passou! Bloqueou valor negativo corretamente.")

if __name__ == "__main__":
    testar_validacoes()
