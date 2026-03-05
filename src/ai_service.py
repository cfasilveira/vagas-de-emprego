import requests

class AIService:
    def __init__(self, model="mistral-nemo:latest"):
        # Gateway do Docker para o host (Ollama)
        self.url = "http://host.docker.internal:11434/api/generate"
        self.model = model

    def analisar_candidato(self, nome_vaga, descricao_vaga, resumo_experiencia):
        """
        Analisa o currículo usando Mistral-Nemo. 
        Fail First: Se a IA falhar ou demorar, a inscrição prossegue.
        """
        if not resumo_experiencia or len(resumo_experiencia) < 20:
            return "Resumo insuficiente para análise técnica."
        
        desc_vaga = descricao_vaga if descricao_vaga else "Descrição padrão."

        # Prompt estruturado para o estilo de resposta do Mistral
        prompt = f"""
        [INST] Você é um Recrutador Técnico Sênior. Avalie este candidato:
        
        VAGA: {nome_vaga}
        REQUISITOS: {desc_vaga}
        RESUMO DO CANDIDATO: {resumo_experiencia}

        Retorne EXATAMENTE 3 frases em PT-BR:
        1. SCORE: (0-100% de match).
        2. FORTE: O maior diferencial técnico.
        3. GAP: O que falta para a vaga. [/INST]
        """
        
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3, # Menos criatividade, mais consistência
                        "num_ctx": 4096
                    }
                },
                timeout=60 # Aumentado para o Mistral-Nemo (12B)
            )
            
            if response.status_code == 200:
                return response.json().get('response', "Análise indisponível.")
            
            return f"⚠️ IA Temporariamente Offline (Status {response.status_code})."
            
        except Exception as e:
            # Fallback para não travar o banco de dados
            return f"🤖 IA em processamento. (Erro: {str(e)[:15]})"
