import json
import os

# --- DADOS DE CONFIGURAÇÃO ---
VAGAS_DEFINICOES = [
    {
        "id_vaga": "VAGA_001",
        "titulo_vaga": "Analista de Dados Sênior",
        "departamento": "Tecnologia",
        "nivel": "Sênior",
        "descricao": "Profissional experiente para análise de dados complexos e geração de insights estratégicos para o negócio.",
        "perfil_ideal_big_five": {
            "abertura_a_experiencia": 8.5,
            "conscienciosidade": 9.0,
            "extroversao": 6.0,
            "amabilidade": 7.0,
            "neuroticismo": 2.5
        },
        "competencias_obrigatorias": ["Python", "SQL", "Análise Estatística", "Power BI"],
        "competencias_desejaveis": ["Machine Learning", "Comunicação", "Gestão de Projetos"],
        "competencias_diferenciais": ["AWS", "Docker", "Scrum"],
        "salario_min": 8000,
        "salario_max": 15000,
        "requisitos_especiais": ["Experiência com big data", "Inglês intermediário", "3+ anos experiência"]
    },
    {
        "id_vaga": "VAGA_002", 
        "titulo_vaga": "Engenheiro de Software Pleno",
        "departamento": "Tecnologia",
        "nivel": "Pleno",
        "descricao": "Desenvolvedor para criação e manutenção de aplicações web modernas em stack completo.",
        "perfil_ideal_big_five": {
            "abertura_a_experiencia": 8.0,
            "conscienciosidade": 8.5,
            "extroversao": 5.5,
            "amabilidade": 6.5,
            "neuroticismo": 3.0
        },
        "competencias_obrigatorias": ["JavaScript", "React", "Python", "SQL"],
        "competencias_desejaveis": ["AWS", "Docker", "Scrum", "Comunicação"],
        "competencias_diferenciais": ["Machine Learning", "Figma", "Liderança"],
        "salario_min": 7000,
        "salario_max": 12000,
        "requisitos_especiais": ["Portfolio no GitHub", "2+ anos experiência", "Conhecimento em APIs REST"]
    },
    {
        "id_vaga": "VAGA_003",
        "titulo_vaga": "Cientista de Dados",
        "departamento": "Tecnologia", 
        "nivel": "Sênior",
        "descricao": "Especialista em ciência de dados para desenvolver modelos preditivos e soluções de machine learning.",
        "perfil_ideal_big_five": {
            "abertura_a_experiencia": 9.0,
            "conscienciosidade": 8.5,
            "extroversao": 5.0,
            "amabilidade": 6.0,
            "neuroticismo": 2.0
        },
        "competencias_obrigatorias": ["Python", "Machine Learning", "Análise Estatística", "SQL"],
        "competencias_desejaveis": ["AWS", "Docker", "Power BI", "Comunicação"],
        "competencias_diferenciais": ["Scrum", "Liderança", "Gestão de Projetos"],
        "salario_min": 12000,
        "salario_max": 20000,
        "requisitos_especiais": ["Mestrado ou PhD preferível", "Experiência com ML em produção", "Inglês avançado"]
    },
    {
        "id_vaga": "VAGA_004",
        "titulo_vaga": "Designer UX/UI Sênior",
        "departamento": "Design",
        "nivel": "Sênior", 
        "descricao": "Designer experiente para criar experiências digitais excepcionais e interfaces intuitivas.",
        "perfil_ideal_big_five": {
            "abertura_a_experiencia": 9.5,
            "conscienciosidade": 7.5,
            "extroversao": 7.0,
            "amabilidade": 8.0,
            "neuroticismo": 3.5
        },
        "competencias_obrigatorias": ["Figma", "Criatividade", "Comunicação"],
        "competencias_desejaveis": ["JavaScript", "Pensamento Crítico", "Gestão de Projetos"],
        "competencias_diferenciais": ["React", "Python", "Liderança"],
        "salario_min": 6000,
        "salario_max": 12000,
        "requisitos_especiais": ["Portfolio robusto", "3+ anos experiência UX", "Conhecimento em design systems"]
    },
    {
        "id_vaga": "VAGA_005",
        "titulo_vaga": "Gerente de Produto",
        "departamento": "Produto",
        "nivel": "Sênior",
        "descricao": "Líder de produto para definir estratégia, roadmap e trabalhar com times multidisciplinares.",
        "perfil_ideal_big_five": {
            "abertura_a_experiencia": 8.0,
            "conscienciosidade": 8.5,
            "extroversao": 8.5,
            "amabilidade": 7.5,
            "neuroticismo": 3.0
        },
        "competencias_obrigatorias": ["Liderança", "Comunicação", "Gestão de Projetos", "Scrum"],
        "competencias_desejaveis": ["Pensamento Crítico", "Negociação", "SQL", "Power BI"],
        "competencias_diferenciais": ["Python", "Machine Learning", "Análise Estatística"],
        "salario_min": 10000,
        "salario_max": 18000,
        "requisitos_especiais": ["5+ anos experiência produto", "MBA desejável", "Inglês fluente"]
    },
    {
        "id_vaga": "VAGA_006",
        "titulo_vaga": "Gerente de Marketing Digital",
        "departamento": "Marketing",
        "nivel": "Sênior",
        "descricao": "Especialista em marketing digital para liderar estratégias de crescimento e campanhas online.",
        "perfil_ideal_big_five": {
            "abertura_a_experiencia": 8.5,
            "conscienciosidade": 7.5,
            "extroversao": 8.5,
            "amabilidade": 7.0,
            "neuroticismo": 3.5
        },
        "competencias_obrigatorias": ["Comunicação", "Liderança", "Criatividade"],
        "competencias_desejaveis": ["Power BI", "SQL", "Negociação", "Gestão de Projetos"],
        "competencias_diferenciais": ["Python", "Machine Learning", "Análise Estatística"],
        "salario_min": 8000,
        "salario_max": 15000,
        "requisitos_especiais": ["4+ anos marketing digital", "Experiência com performance", "Google Analytics/Ads"]
    },
    {
        "id_vaga": "VAGA_007",
        "titulo_vaga": "Analista de RH Pleno",
        "departamento": "Recursos Humanos",
        "nivel": "Pleno",
        "descricao": "Profissional de RH para atuar em recrutamento, desenvolvimento e analytics de pessoas.",
        "perfil_ideal_big_five": {
            "abertura_a_experiencia": 7.0,
            "conscienciosidade": 8.5,
            "extroversao": 7.5,
            "amabilidade": 8.5,
            "neuroticismo": 3.0
        },
        "competencias_obrigatorias": ["Comunicação", "Liderança", "Negociação"],
        "competencias_desejaveis": ["Power BI", "SQL", "Pensamento Crítico", "Gestão de Projetos"],
        "competencias_diferenciais": ["Python", "Machine Learning", "Análise Estatística"],
        "salario_min": 5000,
        "salario_max": 9000,
        "requisitos_especiais": ["Psicologia ou área afim", "2+ anos experiência RH", "Conhecimento em People Analytics"]
    },
    {
        "id_vaga": "VAGA_008",
        "titulo_vaga": "Desenvolvedor Frontend Júnior",
        "departamento": "Tecnologia",
        "nivel": "Júnior",
        "descricao": "Desenvolvedor iniciante para criar interfaces web modernas e responsivas.",
        "perfil_ideal_big_five": {
            "abertura_a_experiencia": 8.0,
            "conscienciosidade": 7.5,
            "extroversao": 5.0,
            "amabilidade": 6.5,
            "neuroticismo": 4.0
        },
        "competencias_obrigatorias": ["JavaScript", "React"],
        "competencias_desejaveis": ["Figma", "Comunicação", "Scrum"],
        "competencias_diferenciais": ["Python", "SQL", "AWS"],
        "salario_min": 3500,
        "salario_max": 6000,
        "requisitos_especiais": ["Portfolio GitHub", "Conhecimento básico HTML/CSS", "Vontade de aprender"]
    }
]

def criar_vaga_arquivo(vaga_data, output_dir):
    """Cria arquivo JSON para uma vaga"""
    filename = f"{vaga_data['id_vaga'].lower()}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(vaga_data, f, ensure_ascii=False, indent=2)
    
    return filename

def main():
    """Função principal para gerar todas as vagas"""
    output_dir = "data/vagas"
    
    # Criar diretório se não existir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Diretório '{output_dir}' criado.")
    
    # Gerar arquivos de vagas
    vagas_criadas = []
    
    for vaga in VAGAS_DEFINICOES:
        filename = criar_vaga_arquivo(vaga, output_dir)
        vagas_criadas.append(filename)
        print(f"✅ Vaga criada: {filename} - {vaga['titulo_vaga']}")
    
    print(f"\n🎯 {len(vagas_criadas)} vagas foram criadas com sucesso em '{output_dir}'!")
    print("\n📋 Vagas disponíveis:")
    for vaga in VAGAS_DEFINICOES:
        print(f"   • {vaga['titulo_vaga']} ({vaga['nivel']}) - {vaga['departamento']}")
    
    print(f"\n💡 Para usar as vagas, execute '3_Análise_de_Fit.py' no Streamlit!")

if __name__ == "__main__":
    main()