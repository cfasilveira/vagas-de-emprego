import requests
import re

def calcular_match_ia(resumo_candidato, descricao_vaga):
    # Tenta resolver pelo nome do container, depois pelo IP do gateway do Docker
    urls = ["http://ollama-service:11434/api/generate", "http://172.17.0.1:11434/api/generate"]
    
    prompt = f"[INST] Analise o match (0-100%) entre a VAGA e o RESUMO. Responda apenas o número e %. \nVAGA: {descricao_vaga}\nRESUMO: {resumo_candidato}[/INST]"
    payload = {"model": "mistral-nemo", "prompt": prompt, "stream": False}
    
    for url in urls:
        try:
            response = requests.post(url, json=payload, timeout=45)
            if response.status_code == 200:
                resultado = response.json().get("response", "0%")
                match = re.search(r"(\d+%)", resultado)
                return match.group(1) if match else "0%"
        except:
            continue
            
    return "IA-Indisponível"
