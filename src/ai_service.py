import requests
import json

class AIService:
    def __init__(self):
        # Endereço para o app dentro do Docker falar com o Ollama no Host Linux
        self.url = "http://host.docker.internal:11434/api/generate"
        self.model = "mistral-nemo:latest"

    def analisar_candidato(self, titulo_vaga, descricao_vaga, resumo_candidato):
        prompt = f"""
        [INST]
        Atue como um Recrutador Especialista Tech. 
        Analise o match entre a vaga e o candidato.
        
        VAGA: {titulo_vaga}
        DESCRIÇÃO: {descricao_vaga}
        RESUMO CANDIDATO: {resumo_candidato}
        
        Responda obrigatoriamente neste formato:
        SCORE: [0-100]%
        PARECER: [Máximo 2 frases sobre o match]
        [/INST]
        """
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2}
        }

        try:
            r = requests.post(self.url, json=payload, timeout=80)
            if r.status_code == 200:
                return r.json().get('response', "SCORE: 0% | Erro no processamento.")
            else:
                return f"SCORE: 0% | Erro Ollama: {r.status_code}"
        except Exception as e:
            return f"SCORE: 0% | IA Offline: {str(e)}"
