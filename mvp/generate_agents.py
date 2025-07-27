import json
import random
from faker import Faker
import os

# Inicializa o Faker
fake = Faker()

# --- DADOS DE CONFIGURAÇÃO ---
PAISES = {
    "USA": "en_US", "Netherlands": "nl_NL", "India": "en_IN", "China": "zh_CN",
    "Japan": "ja_JP", "Nigeria": "en_US", "Russia": "ru_RU", "South Korea": "ko_KR",
    "Portugal": "pt_PT", "Germany": "de_DE", "Brazil": "pt_BR"
}
LISTA_PAISES = list(PAISES.keys())

CARGOS = ["Analista de Dados", "Engenheiro de Software", "Gerente de Produto", "Designer UX/UI", "Cientista de Dados", "Gerente de Marketing", "Analista de RH"]
DEPARTAMENTOS = ["Tecnologia", "Produto", "Marketing", "Recursos Humanos", "Design"]
COMPETENCIAS = [
    "Python", "SQL", "Power BI", "Comunicação", "Liderança", "Gestão de Projetos",
    "Java", "React", "Machine Learning", "Análise Estatística", "Figma", "Scrum"
]

# --- FUNÇÃO DE GERAÇÃO ---
def criar_agente(id_agente):
    pais = random.choice(LISTA_PAISES)
    locale = PAISES[pais]
    fake_local = Faker(locale)
    
    genero = random.choice(["Masculino", "Feminino", "Não-binário"])
    nome = fake_local.name_male() if genero == "Masculino" else fake_local.name_female()

    agente = {
        "id_funcionario": f"HF{str(id_agente).zfill(3)}",
        "nome": nome,
        "cargo": random.choice(CARGOS),
        "departamento": random.choice(DEPARTAMENTOS),
        "equipe_atual": f"Equipe {random.choice(['Alpha', 'Beta', 'Gama', 'Delta'])}",
        "tempo_de_casa_meses": random.randint(3, 60),
        "demografia": {
            "pais_origem": pais,
            "genero": genero
        },
        "perfil_big_five": {
            "abertura_a_experiencia": round(random.uniform(1, 10), 1),
            "conscienciosidade": round(random.uniform(1, 10), 1),
            "extroversao": round(random.uniform(1, 10), 1),
            "amabilidade": round(random.uniform(1, 10), 1),
            "neuroticismo": round(random.uniform(1, 10), 1)
        },
        "competencias": random.sample(COMPETENCIAS, k=random.randint(3, 6)),
        "performance": {
            "avaliacoes_desempenho": [
                {"ciclo": "2023-H2", "nota": round(random.uniform(5, 10), 1)},
                {"ciclo": "2024-H1", "nota": round(random.uniform(5, 10), 1)}
            ],
            "metas_atingidas_percentual": round(random.uniform(70, 100), 1)
        },
        "engajamento": {
            "enps_recente": random.randint(1, 10),
            "feedback_360_media": round(random.uniform(3, 5), 1),
            "comentarios_sentimento": random.choice(["positivo", "neutro", "negativo"])
        },
        "historico": {
            "promocoes": random.randint(0, 3),
            "projetos_chave_participados": random.randint(1, 10)
        },
        "objetivos_carreira": fake.sentence(nb_words=10),
        "kpis_ia": {
            "risco_burnout": round(random.uniform(0, 10), 1),
            "engajamento_inferido": round(random.uniform(0, 10), 1),
            "sentimento_medio": round(random.uniform(-1, 1), 2)
        }
    }
    return agente

# --- EXECUÇÃO ---
if __name__ == "__main__":
    output_dir = "mvp/data/agents"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Começamos do 2 para não sobrescrever o agente 001 que já temos
    for i in range(2, 22):
        novo_agente = criar_agente(i)
        file_path = os.path.join(output_dir, f"agente_{str(i).zfill(3)}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(novo_agente, f, ensure_ascii=False, indent=2)
    
    print(f"20 novos agentes foram criados com sucesso em '{output_dir}'")