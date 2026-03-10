import requests
import re

def calcular_match_ia(resumo_candidato, descricao_vaga):
    # Tenta resolver pelo nome do container, depois pelo IP do gateway do Docker
    urls = ["http://ollama-service:11434/api/generate", "http://172.17.0.1:11434/api/generate"]
    
    prompt = f"\n[INST] Analise a adequação deste CANDIDATO ÚNICO para esta VAGA específica.\nRetorne apenas uma porcentagem global de match no formato XX%.\nAbaixo da porcentagem, liste em tópicos curtos:\n- Pontos Fortes: (2 tópicos)\n- Pontos de Atenção: (2 tópicos)\n\nVAGA: {descricao_vaga}\nRESUMO: {resumo_candidato} [/INST]\n"
    payload = {"model": "mistral-nemo", "prompt": prompt, "stream": False}
    
    for url in urls:
        try:
            response = requests.post(url, json=payload, timeout=90)
            if response.status_code == 200:
                resultado = response.json().get("response", "0%")
                match = re.search(r"(\d+%.*)", resultado, re.DOTALL)
                return match.group(1) if match else "0%"
        except:
            continue
            
    return "IA-Indisponível"
