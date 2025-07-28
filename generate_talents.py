#!/usr/bin/env python3
"""
HumaniQ AI - Gerador de Banco de Talentos
Gera candidatos externos para sistema de recrutamento e análise de fit
"""

import json
import random
from faker import Faker
import os
from datetime import datetime, timedelta

# Inicializa o Faker
fake = Faker()

# --- DADOS DE CONFIGURAÇÃO ---
PAISES = {
    "USA": "en_US", "Netherlands": "nl_NL", "India": "en_IN", "China": "zh_CN",
    "Japan": "ja_JP", "Nigeria": "en_US", "Russia": "ru_RU", "South Korea": "ko_KR",
    "Portugal": "pt_PT", "Germany": "de_DE", "Brazil": "pt_BR", "France": "fr_FR",
    "Spain": "es_ES", "Italy": "it_IT", "Mexico": "es_MX", "Argentina": "es_AR"
}
LISTA_PAISES = list(PAISES.keys())

CARGOS = [
    "Analista de Dados", "Engenheiro de Software", "Gerente de Produto",
    "Designer UX/UI", "Cientista de Dados", "Gerente de Marketing",
    "Analista de RH", "DevOps Engineer", "Product Owner", "Data Engineer",
    "Business Analyst", "QA Engineer", "Frontend Developer", "Backend Developer",
    "Full Stack Developer", "Arquiteto de Software", "Gerente de Vendas",
    "Customer Success Manager", "Content Manager", "Social Media Manager"
]

AREAS_INTERESSE = [
    "Tecnologia", "Produto", "Marketing", "Recursos Humanos", "Design",
    "Vendas", "Customer Success", "Finanças", "Operações", "Estratégia"
]

COMPETENCIAS = [
    "Python", "SQL", "Power BI", "Comunicação", "Liderança", "Gestão de Projetos",
    "Java", "React", "Machine Learning", "Análise Estatística", "Figma", "Scrum",
    "JavaScript", "Node.js", "AWS", "Docker", "Kubernetes", "Git", "MongoDB",
    "PostgreSQL", "Tableau", "Excel Avançado", "Apresentação", "Negociação",
    "Agile", "Kanban", "Design Thinking", "UX Research", "Photoshop", "Adobe XD",
    "Google Analytics", "SEO", "SEM", "Facebook Ads", "Instagram Marketing",
    "LinkedIn Sales", "CRM", "Salesforce", "HubSpot", "Slack", "Jira", "Confluence"
]

SITUACAO_ATUAL = [
    "Empregado - Procurando oportunidades",
    "Empregado - Aberto a propostas",
    "Desempregado - Procurando ativamente",
    "Freelancer - Buscando CLT",
    "Estudante - Primeiro emprego",
    "Estudante - Estágio",
    "Empregado - Insatisfeito",
    "Empregado - Crescimento de carreira"
]

MOTIVACOES_MUDANCA = [
    "Crescimento profissional",
    "Melhor remuneração",
    "Desafios técnicos",
    "Cultura empresarial",
    "Work-life balance",
    "Aprendizado e desenvolvimento",
    "Liderança e gestão",
    "Inovação e tecnologia",
    "Propósito e impacto social",
    "Flexibilidade e remoto"
]

NIVEL_EXPERIENCIA = [
    "Júnior (0-2 anos)",
    "Pleno (2-5 anos)",
    "Sênior (5-8 anos)",
    "Especialista (8-12 anos)",
    "Líder (12+ anos)"
]

EMPRESAS_EXEMPLO = [
    "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix", "Spotify",
    "Uber", "Airbnb", "Tesla", "SpaceX", "Slack", "Zoom", "Salesforce",
    "Adobe", "Oracle", "IBM", "Intel", "NVIDIA", "Startup inovadora",
    "Consultoria internacional", "Banco digital", "Fintech", "Healthtech",
    "Edtech", "E-commerce", "Multinacional", "Scale-up"
]

# --- FUNÇÃO DE GERAÇÃO ---


def criar_talento(id_talento):
    """Cria um perfil de talento/candidato externo"""

    pais = random.choice(LISTA_PAISES)
    locale = PAISES[pais]
    fake_local = Faker(locale)

    genero = random.choice(["Masculino", "Feminino", "Não-binário"])
    nome = fake_local.name_male() if genero == "Masculino" else fake_local.name_female()

    # Nível de experiência afeta salário e competências
    nivel_exp = random.choice(NIVEL_EXPERIENCIA)
    anos_experiencia = {
        "Júnior (0-2 anos)": random.randint(0, 2),
        "Pleno (2-5 anos)": random.randint(2, 5),
        "Sênior (5-8 anos)": random.randint(5, 8),
        "Especialista (8-12 anos)": random.randint(8, 12),
        "Líder (12+ anos)": random.randint(12, 20)
    }[nivel_exp]

    # Pretensão salarial baseada no nível
    salario_base = {
        "Júnior (0-2 anos)": random.randint(3000, 6000),
        "Pleno (2-5 anos)": random.randint(6000, 12000),
        "Sênior (5-8 anos)": random.randint(12000, 20000),
        "Especialista (8-12 anos)": random.randint(20000, 30000),
        "Líder (12+ anos)": random.randint(30000, 50000)
    }[nivel_exp]

    # Número de competências baseado na experiência
    num_competencias = min(len(COMPETENCIAS), max(
        3, anos_experiencia // 2 + random.randint(2, 4)))

    talento = {
        "id_talento": f"TL{str(id_talento).zfill(3)}",
        "nome": nome,
        "cargo_atual": random.choice(CARGOS),
        "cargo_interesse": random.choice(CARGOS),
        "area_interesse": random.choice(AREAS_INTERESSE),
        "nivel_experiencia": nivel_exp,
        "anos_experiencia": anos_experiencia,

        "demografia": {
            "pais_origem": pais,
            "genero": genero,
            "idade": random.randint(22, 55),
            "cidade": fake_local.city(),
            "disponibilidade_mudanca": random.choice([True, False]),
            # 75% aceita remoto
            "aceita_remoto": random.choice([True, True, True, False])
        },

        "perfil_big_five": {
            "abertura_a_experiencia": round(random.uniform(1, 10), 1),
            "conscienciosidade": round(random.uniform(1, 10), 1),
            "extroversao": round(random.uniform(1, 10), 1),
            "amabilidade": round(random.uniform(1, 10), 1),
            "neuroticismo": round(random.uniform(1, 10), 1)
        },

        "competencias": random.sample(COMPETENCIAS, k=num_competencias),

        "experiencia_profissional": {
            "empresa_atual": random.choice(EMPRESAS_EXEMPLO),
            "tempo_empresa_atual_meses": random.randint(6, 48),
            "empresas_anteriores": random.randint(1, 5),
            "setores_experiencia": random.sample(AREAS_INTERESSE, k=random.randint(1, 3))
        },

        "situacao_profissional": {
            "status": random.choice(SITUACAO_ATUAL),
            "disponibilidade_inicio": random.choice([
                "Imediata", "15 dias", "30 dias", "45 dias", "60 dias", "90 dias"
            ]),
            "motivo_mudanca": random.choice(MOTIVACOES_MUDANCA),
            # 66% flexível
            "flexibilidade_horario": random.choice([True, True, False]),
        },

        "expectativas_financeiras": {
            "pretensao_salarial_bruto": salario_base + random.randint(-1000, 2000),
            "negociavel": random.choice([True, True, False]),  # 66% negociável
            "beneficios_prioritarios": random.sample([
                "Vale refeição", "Plano de saúde", "Plano dental", "Vale transporte",
                "Home office", "Flexibilidade horário", "Seguro de vida",
                "Previdência privada", "Auxílio educação", "Gympass", "Day off"
            ], k=random.randint(3, 6))
        },

        "fit_cultural": {
            "valores_importantes": random.sample([
                "Inovação", "Colaboração", "Transparência", "Diversidade",
                "Sustentabilidade", "Crescimento", "Qualidade", "Agilidade",
                "Autonomia", "Propósito", "Excelência", "Respeito"
            ], k=random.randint(3, 5)),
            "estilo_trabalho_preferido": random.choice([
                "Colaborativo", "Independente", "Híbrido", "Estruturado", "Flexível"
            ]),
            "tamanho_empresa_preferido": random.choice([
                "Startup (< 50)", "Pequena (50-200)", "Média (200-1000)",
                "Grande (1000+)", "Sem preferência"
            ])
        },

        "soft_skills": {
            "comunicacao": round(random.uniform(6, 10), 1),
            "trabalho_em_equipe": round(random.uniform(6, 10), 1),
            "adaptabilidade": round(random.uniform(5, 10), 1),
            "resolucao_problemas": round(random.uniform(6, 10), 1),
            "lideranca": round(random.uniform(4, 10), 1),
            "criatividade": round(random.uniform(5, 10), 1)
        },

        "formacao": {
            "nivel_educacao": random.choice([
                "Ensino Médio", "Tecnólogo", "Graduação", "Pós-graduação",
                "MBA", "Mestrado", "Doutorado"
            ]),
            "area_formacao": random.choice([
                "Ciência da Computação", "Engenharia", "Administração", "Marketing",
                "Design", "Psicologia", "Economia", "Estatística", "Matemática",
                "Comunicação", "Engenharia de Produção"
            ]),
            "certificacoes": random.sample([
                "PMP", "Scrum Master", "AWS Certified", "Google Analytics",
                "Salesforce Admin", "Azure Fundamentals", "Power BI", "Tableau",
                "ITIL", "Six Sigma", "Design Thinking", "Agile Coach"
            ], k=random.randint(0, 3))
        },

        "conhecimento_empresa": {
            "ja_aplicou_antes": random.choice([True, False]),
            # 33% conhece
            "conhece_alguem_empresa": random.choice([True, False, False]),
            "interesse_especifico": random.choice([
                "Cultura inovadora", "Crescimento rápido", "Tecnologia de ponta",
                "Impacto social", "Marca reconhecida", "Oportunidade aprendizado",
                "Liderança de mercado", "Ambiente colaborativo"
            ]),
            "como_conheceu_vaga": random.choice([
                "LinkedIn", "Site da empresa", "Indicação", "Head hunter",
                "Portal de empregos", "Redes sociais", "Evento", "Newsletter"
            ])
        },

        "score_engagement": round(random.uniform(6, 10), 1),
        "score_potencial": round(random.uniform(5, 10), 1),
        "ultima_atualizacao": datetime.now().isoformat()
    }

    return talento


def gerar_talentos(num_talentos=100):
    """Gera e salva talentos em arquivos JSON"""

    # Criar diretório se não existir
    os.makedirs("data/talentos", exist_ok=True)

    print(f"🎯 Gerando {num_talentos} talentos...")

    for i in range(1, num_talentos + 1):
        talento = criar_talento(i)

        # Salvar em arquivo JSON
        filename = f"data/talentos/talento_{str(i).zfill(3)}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(talento, f, ensure_ascii=False, indent=2)

        if i % 10 == 0:
            print(f"✅ {i} talentos gerados...")

    print(f"🎉 {num_talentos} talentos gerados com sucesso!")
    print(f"📁 Arquivos salvos em: data/talentos/")

    # Gerar relatório
    gerar_relatorio_talentos()


def gerar_relatorio_talentos():
    """Gera relatório dos talentos criados"""

    print("\n" + "="*60)
    print("📊 RELATÓRIO DO BANCO DE TALENTOS")
    print("="*60)

    talentos_files = [f for f in os.listdir(
        "data/talentos") if f.endswith('.json')]
    total_talentos = len(talentos_files)

    print(f"📈 Total de talentos: {total_talentos}")

    # Analisar alguns padrões
    if total_talentos > 0:
        # Ler alguns arquivos para estatísticas
        sample_files = talentos_files[:min(10, total_talentos)]
        cargos = []
        paises = []
        experiencias = []

        for filename in sample_files:
            with open(f"data/talentos/{filename}", 'r', encoding='utf-8') as f:
                talento = json.load(f)
                cargos.append(talento['cargo_interesse'])
                paises.append(talento['demografia']['pais_origem'])
                experiencias.append(talento['nivel_experiencia'])

        print(f"🎯 Cargos de interesse (amostra): {set(cargos)}")
        print(f"🌍 Países representados (amostra): {set(paises)}")
        print(f"📊 Níveis de experiência (amostra): {set(experiencias)}")

    print("\n💡 Próximos passos:")
    print("1. Execute o sistema de Análise de Fit")
    print("2. Compare talentos externos vs funcionários internos")
    print("3. Use filtros avançados por competências e cultura")
    print("="*60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Gera banco de talentos para HumaniQ AI')
    parser.add_argument('--num', type=int, default=100,
                        help='Número de talentos a gerar (padrão: 100)')

    args = parser.parse_args()

    print("🧠 HumaniQ AI - Gerador de Banco de Talentos")
    print("=" * 50)

    gerar_talentos(args.num)
