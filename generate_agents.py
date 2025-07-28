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

CARGOS = ["Analista de Dados", "Engenheiro de Software", "Gerente de Produto",
          "Designer UX/UI", "Cientista de Dados", "Gerente de Marketing", "Analista de RH"]
DEPARTAMENTOS = ["Tecnologia", "Produto",
                 "Marketing", "Recursos Humanos", "Design"]
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


def encontrar_proximo_id(output_dir):
    """Encontra o próximo ID disponível verificando arquivos existentes"""
    if not os.path.exists(output_dir):
        return 1

    arquivos_existentes = [f for f in os.listdir(
        output_dir) if f.startswith('agente_') and f.endswith('.json')]
    if not arquivos_existentes:
        return 1

    # Extrai os números dos arquivos existentes
    ids_existentes = []
    for arquivo in arquivos_existentes:
        try:
            # Extrai o número do formato "agente_XXX.json"
            numero = int(arquivo.split('_')[1].split('.')[0])
            ids_existentes.append(numero)
        except (ValueError, IndexError):
            continue

    return max(ids_existentes) + 1 if ids_existentes else 1


if __name__ == "__main__":
    # Usar o diretório data/agents ao invés de data/agents
    output_dir = "data/agents"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Encontra o próximo ID disponível
    proximo_id = encontrar_proximo_id(output_dir)
    # quantidade de agentes (funcionários novos) a serem criados
    quantidade_agentes = 4

    print(f"Verificando arquivos existentes em '{output_dir}'...")
    print(f"Próximo ID disponível: {proximo_id}")
    print(f"Criando {quantidade_agentes} novos agentes...")

    # Cria novos agentes sem sobrescrever os existentes
    agentes_criados = []
    for i in range(proximo_id, proximo_id + quantidade_agentes):
        novo_agente = criar_agente(i)
        file_path = os.path.join(output_dir, f"agente_{str(i).zfill(3)}.json")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(novo_agente, f, ensure_ascii=False, indent=2)

        agentes_criados.append(f"agente_{str(i).zfill(3)}.json")
        print(f"✓ Criado: {file_path}")

    print(f"\n🎉 {quantidade_agentes} novos agentes criados com sucesso!")
    print(f"📁 Diretório: {output_dir}")
    print(f"📋 Arquivos criados: {', '.join(agentes_criados)}")
