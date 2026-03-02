import requests
import json

class AIService:
    def __init__(self, model="llama3.1"):
        # Usamos o nome do container 'ollama-service' definido no seu docker ps
        self.url = "http://ollama-service:11434/api/generate"
        self.model = model

    def analisar_candidato(self, nome_vaga, resumo_experiencia):
        """Analisa o currículo e gera feedback técnico."""
        prompt = f"""
        Você é um recrutador especializado. 
        Vaga: {nome_vaga}
        Resumo do Candidato: {resumo_experiencia}
        
        Tarefa: Avalie se o candidato tem aderência técnica. 
        Responda em no máximo 3 frases curtas e objetivas.
        """
        
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=25 # Limite para não travar o Streamlit
            )
            if response.status_code == 200:
                return response.json().get('response', "Análise concluída, mas sem texto.")
            return f"IA Temporariamente indisponível (Erro {response.status_code})"
        except Exception as e:
            return f"Erro de conexão com Ollama: Localhost não atingível via Docker Network."
