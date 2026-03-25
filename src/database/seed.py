import random
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.database.config import DATABASE_URL, Base
from src.database.models import UF, Administrador, Vaga, Candidato, Inscricao
from src.security import Security
from datetime import datetime, UTC

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def seed():
    print("🧹 Reiniciando tabelas para teste limpo...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Popular UFs
        ufs_data = [
            ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
            ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"),
            ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"),
            ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"),
            ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), 
            ("RN", "Rio Grande do Norte"), ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), 
            ("RR", "Roraima"), ("SC", "Santa Catarina"), ("SP", "São Paulo"), 
            ("SE", "Sergipe"), ("TO", "Tocantins")
        ]
        print("🌱 Populando UFs...")
        for sigla, nome in ufs_data:
            db.add(UF(sigla=sigla, nome=nome))
        db.commit()

        # 2. Criar Vagas (Com Descrições Enriquecidas para IA)
        print("💼 Criando 9 vagas com descrições detalhadas...")
        ufs_db = {u.sigla: u.id for u in db.query(UF).all()}
        
        vagas_data = [
            ("Cozinheiro", "Responsável pelo preparo de pratos a la carte e buffet. Requisitos: Experiência com cozinha brasileira, manipulação de alimentos (HACCP) e liderança de equipe. Desejável curso técnico em Gastronomia.", "Goiânia", ufs_db["GO"], 2800.0),
            ("Recepcionista", "Atendimento bilíngue a clientes e fornecedores. Gestão de agenda, reserva de salas e suporte administrativo básico. Requisitos: Inglês intermediário, boa dicção e domínio do Pacote Office.", "Maceió", ufs_db["AL"], 2200.0),
            ("Auxiliar de Limpeza", "Manutenção de higiene em ambiente hospitalar. Controle de estoque de materiais de limpeza e descarte de resíduos químicos. Requisitos: Experiência prévia em hospitais ou clínicas e agilidade.", "São Paulo", ufs_db["SP"], 2100.0),
            ("Garçom", "Atendimento de excelência em restaurante de alta gastronomia. Sugestão de vinhos e harmonizações. Requisitos: Experiência como sommelier será um diferencial. Disponibilidade para horários noturnos.", "Florianópolis", ufs_db["SC"], 2400.0),
            ("Cozinheiro", "Preparação de cardápio variado para eventos de grande porte. Foco em massas e risotos. Requisitos: Agilidade sob pressão, conhecimento em cortes finos e disponibilidade para viagens curtas.", "Campinas", ufs_db["SP"], 3200.0),
            ("Recepcionista", "Atendimento ao público em clínica estética de luxo. Recebimento de valores e fechamento de caixa. Requisitos: Aparência profissional, experiência em vendas consultivas e sistemas de agendamento.", "Niterói", ufs_db["RJ"], 2800.0),
            ("Arrumadeira", "Limpeza e organização de suítes em hotel 5 estrelas. Reposição de frigobar e amenities. Requisitos: Atenção extrema aos detalhes, discrição e experiência em hotelaria de luxo.", "Belo Horizonte", ufs_db["MG"], 2500.0),
            ("Garçom", "Atendimento de mesas em choperia movimentada. Lançamento de pedidos via tablet. Requisitos: Proatividade, facilidade com tecnologia e boa comunicação interpessoal.", "Ribeirão Preto", ufs_db["SP"], 2200.0),
            ("Auxiliar de Cozinha", "Suporte no preparo de ingredientes (mise en place), limpeza de utensílios e organização de câmaras frias. Requisitos: Vontade de aprender, dinamismo e foco em higiene.", "Petrópolis", ufs_db["RJ"], 2100.0)
        ]
        
        for titulo, desc, cidade, uf_id, salario in vagas_data:
            db.add(Vaga(titulo=titulo, descricao=desc, cidade=cidade, uf_id=uf_id, salario=salario, ativo=True))
        db.commit()
        vagas_db = db.query(Vaga).all()

        # 3. Criar 10 Candidatos (Cadastro Completo e Resumo > 3 linhas)
        print("👥 Adicionando 10 candidatos com experiências densas...")
        candidatos_raw = [
            ("Ana Oliveira", "ana@email.com", "F", "Possuo 5 anos de experiência em cozinhas industriais e buffets.\nEspecialista em pratos típicos brasileiros e controle de estoque de perecíveis.\nTenho curso de boas práticas de manipulação e já liderei equipes de até 10 pessoas."),
            ("Bruno Santos", "bruno@email.com", "M", "Chef de cozinha com foco em gastronomia italiana e massas artesanais.\nTrabalhei nos últimos 3 anos em um restaurante premiado no centro da cidade.\nBusco uma oportunidade para aplicar meus conhecimentos em cortes finos e gestão de cardápios."),
            ("Carla Souza", "carla@email.com", "F", "Experiência sólida como recepcionista em hotéis de rede internacional.\nFalo inglês fluente e espanhol básico para atendimento a turistas.\nDomino sistemas de gestão hoteleira (PMS) e rotinas administrativas de back-office."),
            ("Diego Lima", "diego@email.com", "M", "Atuei como auxiliar operacional e logística nos últimos 2 anos.\nTenho facilidade com organização de depósitos, conferência de notas e carga/descarga.\nSou pontual, proativo e possuo ensino médio completo com cursos técnicos na área."),
            ("Elena Martins", "elena@email.com", "F", "Profissional de limpeza com foco em ambientes corporativos e hospitalares.\nConhecimento técnico em diluição de produtos químicos e uso de enceradeiras industriais.\nPrezo pela organização máxima e silêncio durante a execução das tarefas diárias."),
            ("Fabio Silva", "fabio@email.com", "M", "Garçom com 10 anos de experiência em estabelecimentos de alto padrão.\nConhecimento avançado em cartas de vinhos e técnicas de serviço franco-americano.\nPossuo inglês básico para conversação e curso de sommelier concluído recentemente."),
            ("Gisele Rocha", "gisele@email.com", "F", "Auxiliar de cozinha com experiência em corte de carnes e preparação de caldos.\nTrabalhei em regime de escala 6x1 em grandes restaurantes de shopping.\nTenho disponibilidade total de horário e facilidade para trabalhar em equipe sob pressão."),
            ("Hugo Mendes", "hugo@email.com", "M", "Recepcionista com foco em atendimento hospitalar e clínicas médicas.\nExperiência em autorização de convênios, triagem de pacientes e organização de prontuários.\nBusco um ambiente dinâmico onde eu possa aplicar minha empatia e agilidade."),
            ("Iara Costa", "iara@email.com", "F", "Atendimento ao cliente em lojas de varejo e caixas de supermercado.\nExperiência com fechamento de caixa, sangria e resolução de conflitos com consumidores.\nSou comunicativa, organizada e tenho facilidade com cálculos matemáticos rápidos."),
            ("João Pereira", "joao@email.com", "M", "Auxiliar de serviços gerais com experiência em manutenção predial básica.\nRealizo pequenos reparos elétricos, hidráulicos e pintura, além da limpeza pesada.\nTenho referências positivas de empregos anteriores pela minha honestidade e esforço.")
        ]

        for i, (nome, email, genero, resumo) in enumerate(candidatos_raw):
            vaga = random.choice(vagas_db)
            score = random.randint(65, 98)
            cand = Candidato(
                nome=nome, email=email, genero=genero, 
                celular=f"6298888000{i}", resumo=resumo,
                vaga_id=vaga.id, score_ia=score,
                data=datetime.now(UTC)
            )
            db.add(cand)
            db.commit()

            # Inscrição com feedback simulado baseado no score
            db.add(Inscricao(
                candidato_id=cand.id, vaga_id=vaga.id, 
                resumo_submetido=resumo,
                feedback_ia=f"SCORE: {score}%.\nO candidato apresenta excelente aderência técnica.\nPontos Fortes: Experiência comprovada e cursos na área.\nPonto de Atenção: Verificar disponibilidade para início imediato.",
                data=datetime.now(UTC)
            ))
        
        # 4. Criar admin
        print("👤 Criando admin oficial...")
        h_senha = Security.gerar_senha_hash("seguranca2026")
        db.add(Administrador(login="admin", senha_hash=h_senha))
        
        db.commit()
        print("✅ Seed finalizado com sucesso!")
        print("👉 9 Vagas criadas | 10 Candidatos detalhados inseridos.")
        print("👉 Use: admin / seguranca2026")
        
    except Exception as e:
        print(f"❌ Erro no seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
