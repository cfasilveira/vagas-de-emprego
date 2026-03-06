import requests

class AIService:
    def __init__(self, model="mistral-nemo:latest"):
        self.url = "http://host.docker.internal:11434/api/generate"
        self.model = model

    def analisar_candidato(self, nome_vaga, descricao_vaga, resumo_experiencia):
        prompt = f"""
        [INST] Recrutador Sênior: Avalie o match.
        VAGA: {nome_vaga} | RESUMO: {resumo_experiencia}
        Responda EXATAMENTE assim:
        SCORE: [0-100]%
        FORTE: [Motivo]
        GAP: [Falta] [/INST]
        """
        try:
            r = requests.post(self.url, json={"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": 0.2}}, timeout=80)
            return r.json().get('response', "SCORE: 0% | Erro na resposta.")
        except:
            return "SCORE: 0% | IA Offline"
