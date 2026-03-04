import requests

class AIService:
    def __init__(self, model="qwen2.5-coder:7b"):
        # Gateway do Docker para o host local
        self.url = "http://host.docker.internal:11434/api/generate"
        self.model = model

    def analisar_candidato(self, nome_vaga, descricao_vaga, resumo_experiencia):
        """
        Analisa o currículo. Fail First: Se a IA falhar, o sistema continua operando.
        """
        # 1. Validação Básica de Entrada
        if not resumo_experiencia or len(resumo_experiencia) < 10:
            return "Resumo insuficiente para uma análise técnica detalhada."
        
        desc_vaga = descricao_vaga if descricao_vaga else "Descrição padrão do cargo."

        prompt = f"""
        Aja como um recrutador técnico rigoroso. 
        VAGA: {nome_vaga}
        DESCRIÇÃO: {desc_vaga}
        RESUMO CANDIDATO: {resumo_experiencia}

        Gere um feedback técnico em PT-BR com 3 frases curtas:
        1. Match %: Estimativa de aderência.
        2. Ponto Forte: O maior destaque técnico.
        3. Ponto de Atenção: O que falta ou deve ser validado.
        """
        
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30 # Tempo limite para evitar travar o app Streamlit
            )
            
            if response.status_code == 200:
                return response.json().get('response', "Análise concluída sem texto de retorno.")
            
            return f"⚠️ IA em Manutenção (Status {response.status_code}). Inscrição processada normalmente."
            
        except Exception as e:
            # FAIL FIRST: O sistema de recrutamento é mais importante que a IA.
            # Se a conexão falhar, retornamos uma mensagem amigável sem interromper o banco.
            return "🤖 IA temporariamente offline. A análise técnica será processada em breve."
