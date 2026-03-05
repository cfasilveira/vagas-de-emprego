(Upgrade de Inteligência: Migração para Mistral-Nemo (12B)

Este documento descreve a transição do motor de análise técnica do projeto Cadastro de Vagas para o modelo Mistral-Nemo, uma colaboração entre Mistral AI e NVIDIA.
🚀 O que mudou?

Anteriormente, o sistema utilizava modelos de entrada (7B ou inferiores). A migração para o Mistral-Nemo 12B via Ollama elevou o patamar de compreensão contextual das inscrições.
🛠️ Especificações Técnicas

    Modelo: mistral-nemo:latest

    Parâmetros: 12.2 Bilhões

    Context Window: 128k (otimizado para análises extensas)

    Integração: REST API via Ollama (Docker-to-Host)

💎 Vantagens da Alteração

    Raciocínio Técnico Superior: Diferente de modelos menores, o Mistral-Nemo identifica correlações entre tecnologias específicas (ex: relacionar NVIDIA/LLMs a Processamento de Linguagem Natural), gerando feedbacks mais acionáveis.

    Rigor na Avaliação (Score Realista): O modelo passou a apresentar critérios mais estritos, identificando "GAPs" reais de competência, em vez de gerar aprovações genéricas.

    Saída Estruturada: Otimização do prompt para garantir que o feedback sempre siga o formato:

        SCORE: Percentual de match.

        FORTE: Principal diferencial técnico.

        GAP: O que o candidato precisa desenvolver.

    Normalização de Dados: Implementação de lógica de Data Cleaning para garantir que variações de input não poluam os dashboards de BI (Analytics).)
