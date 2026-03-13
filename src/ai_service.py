import os
import requests

class AIService:
    def __init__(self):
        self.use_ollama = True 
        # No Linux, 172.17.0.1 acessa o host que redireciona para o container do Ollama
        self.ollama_url = "http://172.17.0.1:11434/api/generate" 
        print("IA: Conectando ao ollama-service via 172.17.0.1")

    def analisar_candidato(self, titulo_vaga, descricao_vaga, resumo_candidato):
        prompt = f"""
        Compare o RESUMO DO CANDIDATO com a VAGA:
        VAGA: {titulo_vaga} | DESCRIÇÃO: {descricao_vaga}
        RESUMO: {resumo_candidato}
        
        REGRAS:
        1. Se o termo está no resumo, considere experiência confirmada.
        2. SCORE < 90%: Liste o que NÃO foi encontrado no resumo.
        3. SCORE >= 90%: Destaque pontos fortes.
        FORMATO:
        SCORE: [X]%
        PARECER: [Sua análise em até 3 frases]
        """
        try:
            payload = {
                "model": "mistral-nemo",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            }
            # Timeout de 60s para o mistral-nemo processar
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get('response', '')
        except Exception as e:
            return f"SCORE: 0% \nPARECER: Erro na conexão: {str(e)}"
