# 🎯 Portal de Vagas Segura (AI-Enhanced Architecture)

Este sistema de gestão de vagas e candidatos foi construído sob a metodologia **Fail Fast** e **Clean Architecture**, utilizando IA para elevar os padrões de segurança cibernética e robustez modular.

## 🤖 Inteligência e IA no Ciclo de Vida
Diferente do desenvolvimento tradicional, este projeto utiliza **IA Especialista** para:
* **Refatoração Preditiva:** Identificação proativa de "code smells" (como o fatiamento do antigo "linguição" de banco de dados).
* **Testes de Injeção Hacker:** Validação via IA de expressões regulares para bloquear ataques XSS e SQL Injection antes que cheguem ao banco.
* **Arquitetura de Confiança Zero:** Implementação de um "Audit Trail" (Rastro de Auditoria) sugerido pela análise de riscos da IA para garantir a integridade de cada transação.

## 🛡️ Pilares do Sistema

### 1. Robustez (Fail Fast)
O sistema é projetado para falhar rápido e informar o erro. Através de **Health Checks** automáticos, a aplicação valida a saúde do banco PostgreSQL e das variáveis de ambiente no instante do boot, impedindo estados inconsistentes.

### 2. Segurança Cibernética
* **Sanitização Ativa:** Módulo `validators.py` que limpa e valida documentos e nomes.
* **Audit Log:** Cada tentativa de duplicidade ou acesso restrito é logada, criando um rastro forense.
* **Aperto de Mão (Handshake):** Comunicação entre módulos protegida por lógica de repositório isolada.

### 3. Inteligência de Dados
O sistema impede nativamente:
* Vagas duplicadas (mesmo nome/localidade/data).
* Inscrições duplas de um mesmo candidato na mesma vaga.

## 🚀 Estrutura Modular
\`\`\`text
├── src/
│   ├── database/    # Persistência inteligente (Models/Repository/Config)
│   ├── logger.py    # Sistema de Auditoria (Audit Trail)
│   ├── security.py  # Core de segurança e autenticação
│   └── validators.py # Validação proativa contra injeções
├── tests/           # Testes de integração e segurança
└── docker-compose.yml # Orquestração de ambiente isolado
\`\`\`

## 🛠️ Como Rodar (Ambiente Isolado)
Certifique-se de ter o Docker e o \`uv\` instalados.

1.  **Inicializar Ambiente:**
    \`\`\`bash
    docker compose up -d
    \`\`\`

2.  **Rodar Testes de Elite (IA-Validated):**
    \`\`\`bash
    docker compose run --rm -e PYTHONPATH=. app uv run python tests/test_database.py
    \`\`\`

---
**Status:** Fase 2 Concluída | **Qualidade:** 100% Cobertura de Lógica | **Segurança:** Ativa
