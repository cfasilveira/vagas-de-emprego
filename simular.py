from src.database.config import SessionLocal
from src.database.models import Candidato, Inscricao, Vaga, UF
import random

def enriquecer_e_popular():
    db = SessionLocal()
    
    # 1. Enriquecer as descrições das Vagas para permitir o Match
    # Isso garante que a vaga tenha palavras que o candidato possa dar match
    vagas = db.query(Vaga).all()
    termos_por_vaga = {
        "Python": "Desenvolvimento Python Django Flask FastAPI SQL Docker APIs Rest",
        "Data": "Análise de dados Python Pandas extração SQL ETL Dashboards estatística",
        "RH": "Recrutamento seleção gestão de pessoas treinamento RH indicadores",
        "Sistemas": "Infraestrutura redes segurança Linux servidores suporte técnico",
        "Designer": "UI UX Design prototipagem Figma interfaces usabilidade frontend"
    }

    for v in vagas:
        for chave, texto in termos_por_vaga.items():
            if chave.lower() in v.titulo.lower():
                v.descricao = f"{v.titulo}. Requisitos: {texto}"
    
    db.commit()
    print("Vagas enriquecidas com descrições técnicas.")

    # 2. Novos candidatos com descrições compatíveis
    novos_dados = [
        ("Mariana Costa", "Feminino", "mariana.c@email.com", "Experiente em Python, Django e criação de APIs Rest com Docker."),
        ("Ricardo Oliveira", "Masculino", "ricardo.o@email.com", "Especialista em infraestrutura de redes, Linux e segurança de servidores."),
        ("Carla Souza", "Feminino", "carla.s@email.com", "Gestão de pessoas, recrutamento e seleção de talentos para RH."),
        ("Fernando Dias", "Masculino", "fernando.d@email.com", "Desenvolvedor Backend Python focado em SQL, Docker e FastAPI."),
        ("Beatriz Lima", "Feminino", "beatriz.l@email.com", "Cientista de dados, análise estatística com Pandas, Python e SQL."),
        ("André Santos", "Masculino", "andre.s@email.com", "Engenheiro de software, APIs Rest, Python e bancos de dados SQL."),
        ("Juliana Rocha", "Feminino", "juliana.r@email.com", "Designer de interfaces UI UX, prototipagem no Figma e usabilidade."),
        ("Marcos Vinícius", "Masculino", "marcos.v@email.com", "Estagiário de tecnologia com curso de Python e lógica de SQL."),
        ("Patrícia Gomes", "Feminino", "patricia.g@email.com", "Liderança técnica em TI, gestão de projetos e desenvolvimento Python."),
        ("Tiago Barbosa", "Masculino", "tiago.b@email.com", "Segurança da informação, redes de computadores e scripts em Python.")
    ]

    for nome, genero, email, resumo in novos_dados:
        # Evita duplicidade
        if not db.query(Candidato).filter(Candidato.email == email).first():
            cand = Candidato(
                nome=nome, genero=genero, email=email,
                documento=f"{random.randint(100,999)}.000.000-00",
                telefone=f"(11) 9{random.randint(7000,9999)}-0000",
                resumo=resumo
            )
            db.add(cand)
            db.flush()

            # Vincula à vaga mais adequada pelo título
            vaga_alvo = random.choice(vagas)
            for v in vagas:
                if any(palavra in cand.resumo.lower() for palavra in v.titulo.lower().split()):
                    vaga_alvo = v
                    break
            
            db.add(Inscricao(candidato_id=cand.id, vaga_id=vaga_alvo.id, feedback_ia="Análise técnica positiva."))

    db.commit()
    db.close()
    print("Sucesso! Vagas atualizadas e 10 novos candidatos inseridos com currículos compatíveis.")

if __name__ == "__main__":
    enriquecer_e_popular()
