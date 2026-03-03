import requests

class AIService:
    def __init__(self, model="qwen2.5-coder:7b"):
        # Aponta para o gateway do Docker para alcançar o Ollama no host
        self.url = "http://host.docker.internal:11434/api/generate"
        self.model = model

    def analisar_candidato(self, nome_vaga, descricao_vaga, resumo_experiencia):
        """
        Analisa o currículo comparando com o título e a descrição da vaga.
        """
        # FAIL FIRST: Validação de entradas
        if not resumo_experiencia or len(resumo_experiencia) < 10:
            return "Resumo insuficiente para análise técnica."
        
        # Garante que temos uma descrição para comparar
        desc_vaga = descricao_vaga if descricao_vaga else "Descrição não detalhada."

        prompt = f"""
        Aja como um recrutador técnico rigoroso. 
        Compare o currículo do candidato com os requisitos reais da vaga.

        VAGA: {nome_vaga}
        DETALHES DA VAGA: {desc_vaga}
        
        RESUMO DO CANDIDATO: {resumo_experiencia}

        TAREFA: Gere um feedback técnico em PT-BR com exatamente 3 frases:
        1. Match %: (Seja honesto na nota de aderência aos requisitos).
        2. Ponto Forte: (O que mais se destaca frente à descrição).
        3. Ponto de Atenção: (O que falta ou o que deve ser perguntado na entrevista).
        """
        
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=45 # Contexto maior pode exigir um pouco mais de tempo
            )
            
            # FAIL FIRST: Validação do status da resposta
            if response.status_code != 200:
                return f"IA indisponível (Erro {response.status_code})"
                
            return response.json().get('response', "IA não retornou texto de análise.")
            
        except Exception as e:
            return f"Erro de conexão com o cérebro da IA: {str(e)[:50]}"
