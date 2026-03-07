import requests

class AIService:
    def __init__(self, model="mistral-nemo:latest"):
        self.url = "http://host.docker.internal:11434/api/generate"
        self.model = model

    def analisar_candidato(self, nome_vaga, descricao_vaga, resumo_experiencia):
        prompt = f"""
        [INST] Você é um Recrutador Sênior focado em eficiência.
        Avalie o MATCH entre o candidato e a vaga abaixo.
        VAGA: {nome_vaga}
        DESCRIÇÃO: {descricao_vaga}
        PITCH DO CANDIDATO: {resumo_experiencia}

        Responda obrigatoriamente neste formato:
        SCORE: [0-100]%
        PARECER: [Máximo 2 frases sobre o match]
        [/INST]
        """
        try:
            r = requests.post(
                self.url, 
                json={"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": 0.2}}, 
                timeout=80
            )
            return r.json().get('response', "SCORE: 0% | Erro na resposta.")
        except:
            return "SCORE: 0% | IA Offline"
