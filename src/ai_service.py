import os
import requests
from google import genai

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.ollama_url = "http://172.17.0.1:11434/api/generate"
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            print("IA: Usando Google GenAI SDK (Nuvem)")
        else:
            print("IA: Usando Ollama (Local)")

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
        
        if self.api_key:
            try:
                response = self.client.models.generate_content(
                    model="gemini-1.5-flash", contents=prompt
                )
                return response.text
            except Exception as e:
                return f"SCORE: 0% \nPARECER: Erro Gemini: {str(e)}"
        else:
            try:
                payload = {
                    "model": "mistral-nemo",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1}
                }
                response = requests.post(self.ollama_url, json=payload, timeout=60)
                response.raise_for_status()
                return response.json().get('response', '')
            except Exception as e:
                return f"SCORE: 0% \nPARECER: Erro Ollama: {str(e)}"
