import os
import requests

class AIService:
    def __init__(self):
        self.use_ollama = True 
        # Alterado para host.docker.internal para funcionar dentro do container
        self.ollama_url = "http://host.docker.internal:11434/api/generate" 
        print("IA: Configurada para usar Ollama via API REST (Docker Host)")

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
                "model": "mistral",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            }
            response = requests.post(self.ollama_url, json=payload, timeout=45)
            response.raise_for_status()
            return response.json().get('response', '')
        except Exception as e:
            return f"SCORE: 0% \nPARECER: Erro na conexão com Ollama: {str(e)}"
