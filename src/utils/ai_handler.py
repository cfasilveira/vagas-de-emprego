import requests
import re

def calcular_match_ia(resumo_candidato, descricao_vaga):
    # Redundância de URLs conforme scripts de validação
    urls = ["http://ollama-service:11434/api/generate", "http://172.17.0.1:11434/api/generate"]
    
    prompt = f"[INST] Analise o match deste candidato para a vaga. Retorne primeiro a porcentagem (ex: 85%) e depois os pontos fortes e de atenção.\nVAGA: {descricao_vaga}\nRESUMO: {resumo_candidato} [/INST]"
    
    for url in urls:
        try:
            response = requests.post(url, json={"model": "mistral-nemo", "prompt": prompt, "stream": False}, timeout=90)
            if response.status_code == 200:
                return response.json().get("response", "0% - Resposta vazia")
        except:
            continue
    return "IA indisponível no momento"
