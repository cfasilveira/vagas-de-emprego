🚀 Sistema de Cadastro de Vagas (v2.0 - Relacional & Resiliente)

Este projeto evoluiu de um modelo simplificado para uma arquitetura de banco de dados relacional robusta, utilizando PostgreSQL, SQLAlchemy e o gerenciador de pacotes uv. A aplicação está totalmente conteinerizada para garantir um ambiente de desenvolvimento isolado e um host imaculado.
🏗️ Mudança de Paradigma: Arquitetura 2.0

A estrutura foi normalizada em 5 tabelas, garantindo integridade referencial e eliminando redundâncias:

    ufs: Tabela mestre para os 27 estados brasileiros, garantindo padronização regional.

    vagas: Armazena as oportunidades, vinculadas obrigatoriamente a uma UF.

    candidatos: Registro único de usuários com travas em email e documento.

    inscricoes: Tabela de Junção (M:N). Ela conecta o conjunto de candidatos ao conjunto de vagas. Permite que vários candidatos se inscrevam em várias vagas, registrando logs de data e o feedback da análise de IA.

    admins: Gestão de acesso administrativo com senhas criptografadas.

🛡️ Resiliência e Integridade

A segurança agora é aplicada no nível do banco de dados através de UniqueConstraints:

    Vagas: Uma vaga não pode ser duplicada para o mesmo título, cidade e estado (_vaga_uc).

    Inscrições: Um candidato não pode se inscrever duas vezes na mesma vaga (_insc_unica_uc), garantindo que a relação entre um candidato e uma oportunidade seja única.

🛠️ Stack Tecnológica

    Linguagem: Python 3.12 (Gerenciado por uv via pyproject.toml)

    Frontend: Streamlit

    Banco de Dados: PostgreSQL 15 (Alpine)

    ORM: SQLAlchemy 2.0

    Infraestrutura: Docker & Docker Compose

🚀 Como Executar (Host Limpo)

O projeto utiliza volumes mapeados, mas o ambiente virtual e as dependências são geridos internamente pelo container via uv.
1. Subir a Infraestrutura
Bash

docker compose up -d --build

2. Popular o Banco (Seed)

Necessário para injetar os estados (UFs) e o usuário administrativo inicial:
Bash

docker compose exec app uv run python -m src.database.seed

3. Rodar Testes de Estresse

Valida as travas de duplicidade e integridade no PostgreSQL:
Bash

docker compose exec app uv run pytest tests/test_database.py

📊 Estrutura de Tabelas (Banco: vagas_db)

    Database: vagas_db

    Usuário: user | Senha: pass

    Constraints Ativas:

        _vaga_uc btree (titulo, cidade, uf_id)

        _insc_unica_uc btree (candidato_id, vaga_id)
