import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import random

st.set_page_config(page_title="Skill Gap Intelligence",
                   page_icon="🔍", layout="wide")

st.title("🔍 Skill Gap Intelligence")
st.markdown("""
**Identifica lacunas de competências e oportunidades internas**

Sistema que mapeia skills atuais vs necessárias, identifica talentos ocultos, sugere remanejamentos internos e planeja contratações estratégicas.
""")

# --- Dados de Skills e Competências ---
SKILLS_CATALOGO = {
    # Técnicas
    'Python': {'categoria': 'Programação', 'nivel_entrada': 1, 'demanda_mercado': 95, 'salario_impacto': 25},
    'JavaScript': {'categoria': 'Programação', 'nivel_entrada': 1, 'demanda_mercado': 90, 'salario_impacto': 20},
    'SQL': {'categoria': 'Dados', 'nivel_entrada': 1, 'demanda_mercado': 85, 'salario_impacto': 15},
    'Machine Learning': {'categoria': 'IA/ML', 'nivel_entrada': 3, 'demanda_mercado': 98, 'salario_impacto': 40},
    'Power BI': {'categoria': 'Analytics', 'nivel_entrada': 2, 'demanda_mercado': 75, 'salario_impacto': 18},
    'React': {'categoria': 'Frontend', 'nivel_entrada': 2, 'demanda_mercado': 88, 'salario_impacto': 22},
    'AWS': {'categoria': 'Cloud', 'nivel_entrada': 2, 'demanda_mercado': 92, 'salario_impacto': 30},
    'Docker': {'categoria': 'DevOps', 'nivel_entrada': 2, 'demanda_mercado': 80, 'salario_impacto': 25},
    'Kubernetes': {'categoria': 'DevOps', 'nivel_entrada': 3, 'demanda_mercado': 85, 'salario_impacto': 35},
    'Figma': {'categoria': 'Design', 'nivel_entrada': 1, 'demanda_mercado': 70, 'salario_impacto': 12},
    'Scrum': {'categoria': 'Metodologias', 'nivel_entrada': 1, 'demanda_mercado': 65, 'salario_impacto': 10},
    'Análise Estatística': {'categoria': 'Analytics', 'nivel_entrada': 2, 'demanda_mercado': 78, 'salario_impacto': 20},

    # Soft Skills
    'Liderança': {'categoria': 'Soft Skills', 'nivel_entrada': 1, 'demanda_mercado': 95, 'salario_impacto': 30},
    'Comunicação': {'categoria': 'Soft Skills', 'nivel_entrada': 1, 'demanda_mercado': 90, 'salario_impacto': 15},
    'Gestão de Projetos': {'categoria': 'Gestão', 'nivel_entrada': 2, 'demanda_mercado': 80, 'salario_impacto': 25},
    'Negociação': {'categoria': 'Soft Skills', 'nivel_entrada': 2, 'demanda_mercado': 75, 'salario_impacto': 20},
    'Pensamento Crítico': {'categoria': 'Soft Skills', 'nivel_entrada': 1, 'demanda_mercado': 85, 'salario_impacto': 18},
    'Criatividade': {'categoria': 'Soft Skills', 'nivel_entrada': 1, 'demanda_mercado': 70, 'salario_impacto': 15},
}

CARGOS_SKILLS_NECESSARIAS = {
    'Analista de Dados': {
        'obrigatorias': ['Python', 'SQL', 'Análise Estatística', 'Power BI'],
        'desejaveis': ['Machine Learning', 'AWS', 'Comunicação'],
        'futuras': ['Kubernetes', 'Docker']
    },
    'Engenheiro de Software': {
        'obrigatorias': ['Python', 'JavaScript', 'SQL'],
        'desejaveis': ['React', 'AWS', 'Docker', 'Scrum'],
        'futuras': ['Kubernetes', 'Machine Learning']
    },
    'Cientista de Dados': {
        'obrigatorias': ['Python', 'Machine Learning', 'Análise Estatística', 'SQL'],
        'desejaveis': ['AWS', 'Docker', 'Comunicação'],
        'futuras': ['Kubernetes', 'Power BI']
    },
    'Designer UX/UI': {
        'obrigatorias': ['Figma', 'Criatividade', 'Comunicação'],
        'desejaveis': ['JavaScript', 'Pensamento Crítico'],
        'futuras': ['React', 'Python']
    },
    'Gerente de Produto': {
        'obrigatorias': ['Comunicação', 'Liderança', 'Gestão de Projetos', 'Scrum'],
        'desejaveis': ['Pensamento Crítico', 'Negociação', 'SQL'],
        'futuras': ['Machine Learning', 'Python']
    },
    'Gerente de Marketing': {
        'obrigatorias': ['Comunicação', 'Liderança', 'Criatividade'],
        'desejaveis': ['Power BI', 'SQL', 'Negociação'],
        'futuras': ['Machine Learning', 'Python']
    },
    'Analista de RH': {
        'obrigatorias': ['Comunicação', 'Liderança', 'Negociação'],
        'desejaveis': ['Power BI', 'SQL', 'Pensamento Crítico'],
        'futuras': ['Machine Learning', 'Python']
    }
}

# --- Funções Auxiliares ---


@st.cache_data
def carregar_agentes():
    AGENT_DIR = "data/agents"
    if not os.path.exists(AGENT_DIR):
        return pd.DataFrame()

    agent_files = [f for f in os.listdir(AGENT_DIR) if f.endswith('.json')]
    if not agent_files:
        return pd.DataFrame()

    all_agents_data = []
    for f in agent_files:
        with open(os.path.join(AGENT_DIR, f), 'r', encoding='utf-8') as file:
            all_agents_data.append(json.load(file))

    df = pd.json_normalize(all_agents_data)
    return df.set_index('id_funcionario')


def mapear_skills_atuais_vs_necessarias(df_funcionarios):
    """Mapeia skills atuais vs necessárias por cargo"""
    analise_skills = []

    for idx, funcionario in df_funcionarios.iterrows():
        cargo = funcionario.get('cargo', '')
        skills_atuais = set(funcionario.get('competencias', []))

        if cargo in CARGOS_SKILLS_NECESSARIAS:
            skills_necessarias = CARGOS_SKILLS_NECESSARIAS[cargo]

            # Skills obrigatórias
            obrigatorias = set(skills_necessarias['obrigatorias'])
            gap_obrigatorias = obrigatorias - skills_atuais
            match_obrigatorias = len(obrigatorias.intersection(
                skills_atuais)) / len(obrigatorias) * 100

            # Skills desejáveis
            desejaveis = set(skills_necessarias['desejaveis'])
            gap_desejaveis = desejaveis - skills_atuais
            match_desejaveis = len(desejaveis.intersection(
                skills_atuais)) / len(desejaveis) * 100 if desejaveis else 100

            # Skills futuras
            futuras = set(skills_necessarias['futuras'])
            gap_futuras = futuras - skills_atuais
            match_futuras = len(futuras.intersection(
                skills_atuais)) / len(futuras) * 100 if futuras else 100

            # Skills extras
            todas_necessarias = obrigatorias.union(desejaveis).union(futuras)
            skills_extras = skills_atuais - todas_necessarias

            # Score geral
            score_geral = (match_obrigatorias * 0.6 +
                           match_desejaveis * 0.3 + match_futuras * 0.1)

            analise_skills.append({
                'id': idx,
                'nome': funcionario['nome'],
                'cargo': cargo,
                'departamento': funcionario.get('departamento', ''),
                'skills_atuais': skills_atuais,
                'gap_obrigatorias': gap_obrigatorias,
                'gap_desejaveis': gap_desejaveis,
                'gap_futuras': gap_futuras,
                'skills_extras': skills_extras,
                'match_obrigatorias': match_obrigatorias,
                'match_desejaveis': match_desejaveis,
                'match_futuras': match_futuras,
                'score_geral': score_geral
            })

    return analise_skills


def identificar_talentos_ocultos(df_funcionarios):
    """Identifica funcionários com skills subutilizadas"""
    talentos_ocultos = []

    for idx, funcionario in df_funcionarios.iterrows():
        cargo_atual = funcionario.get('cargo', '')
        skills_atuais = set(funcionario.get('competencias', []))

        # Verificar se tem skills para outros cargos
        for cargo_alternativo, skills_necessarias in CARGOS_SKILLS_NECESSARIAS.items():
            if cargo_alternativo != cargo_atual:
                obrigatorias = set(skills_necessarias['obrigatorias'])
                desejaveis = set(skills_necessarias['desejaveis'])

                match_obrigatorias = len(obrigatorias.intersection(
                    skills_atuais)) / len(obrigatorias) * 100
                match_desejaveis = len(desejaveis.intersection(
                    skills_atuais)) / len(desejaveis) * 100 if desejaveis else 100

                # Se tem bom match com outro cargo
                if match_obrigatorias >= 60 and (match_obrigatorias + match_desejaveis) / 2 >= 70:
                    # Calcular potencial de crescimento salarial
                    skills_valiosas = obrigatorias.union(
                        desejaveis).intersection(skills_atuais)
                    impacto_salarial = sum([SKILLS_CATALOGO.get(skill, {}).get(
                        'salario_impacto', 0) for skill in skills_valiosas])

                    talentos_ocultos.append({
                        'id': idx,
                        'nome': funcionario['nome'],
                        'cargo_atual': cargo_atual,
                        'cargo_sugerido': cargo_alternativo,
                        'match_obrigatorias': match_obrigatorias,
                        'match_desejaveis': match_desejaveis,
                        'score_total': (match_obrigatorias + match_desejaveis) / 2,
                        'impacto_salarial': impacto_salarial,
                        'skills_relevantes': list(skills_valiosas)
                    })

    # Remover duplicatas e ordenar por score
    talentos_unicos = {}
    for talento in talentos_ocultos:
        key = talento['id']
        if key not in talentos_unicos or talento['score_total'] > talentos_unicos[key]['score_total']:
            talentos_unicos[key] = talento

    return sorted(talentos_unicos.values(), key=lambda x: x['score_total'], reverse=True)


def analisar_gaps_organizacionais(analise_skills):
    """Analisa gaps de skills a nível organizacional"""
    if not analise_skills:
        return {}

    # Contar gaps por skill
    gaps_skills = Counter()
    pessoas_com_gaps = Counter()

    for pessoa in analise_skills:
        todas_gaps = pessoa['gap_obrigatorias'].union(
            pessoa['gap_desejaveis']).union(pessoa['gap_futuras'])
        for skill in todas_gaps:
            gaps_skills[skill] += 1
            pessoas_com_gaps[skill] += 1

    # Skills mais críticas
    total_pessoas = len(analise_skills)
    gaps_criticos = []

    for skill, count in gaps_skills.most_common():
        percentual = count / total_pessoas * 100
        demanda_mercado = SKILLS_CATALOGO.get(
            skill, {}).get('demanda_mercado', 50)
        impacto_salarial = SKILLS_CATALOGO.get(
            skill, {}).get('salario_impacto', 0)

        # Score de criticidade
        criticidade = percentual * 0.4 + demanda_mercado * 0.4 + impacto_salarial * 0.2

        gaps_criticos.append({
            'skill': skill,
            'pessoas_afetadas': count,
            'percentual_organizacao': percentual,
            'demanda_mercado': demanda_mercado,
            'impacto_salarial': impacto_salarial,
            'criticidade': criticidade,
            'categoria': SKILLS_CATALOGO.get(skill, {}).get('categoria', 'Outros')
        })

    return sorted(gaps_criticos, key=lambda x: x['criticidade'], reverse=True)


def sugerir_remanejamentos(talentos_ocultos, analise_skills):
    """Sugere remanejamentos internos baseados em skills match"""
    remanejamentos = []

    # Criar mapa de necessidades por cargo
    necessidades_por_cargo = {}
    for pessoa in analise_skills:
        cargo = pessoa['cargo']
        if cargo not in necessidades_por_cargo:
            necessidades_por_cargo[cargo] = []

        if pessoa['score_geral'] < 80:  # Pessoa com gaps significativos
            necessidades_por_cargo[cargo].append({
                'pessoa': pessoa['nome'],
                'score': pessoa['score_geral'],
                'gaps': pessoa['gap_obrigatorias'].union(pessoa['gap_desejaveis'])
            })

    # Identificar oportunidades de remanejamento
    for talento in talentos_ocultos[:10]:  # Top 10 talentos
        cargo_sugerido = talento['cargo_sugerido']

        # Verificar se existe necessidade no cargo sugerido
        if cargo_sugerido in necessidades_por_cargo and len(necessidades_por_cargo[cargo_sugerido]) > 0:
            beneficio_estimado = talento['score_total'] - 50  # Baseline score
            impacto_time = len(necessidades_por_cargo[cargo_sugerido])

            remanejamentos.append({
                'funcionario': talento['nome'],
                'cargo_atual': talento['cargo_atual'],
                'cargo_sugerido': cargo_sugerido,
                'score_match': talento['score_total'],
                'beneficio_estimado': beneficio_estimado,
                'impacto_time': impacto_time,
                'skills_relevantes': talento['skills_relevantes'],
                'prioridade': 'Alta' if beneficio_estimado > 25 else 'Média' if beneficio_estimado > 15 else 'Baixa'
            })

    return sorted(remanejamentos, key=lambda x: x['beneficio_estimado'], reverse=True)


def planejar_contratacoes_estrategicas(gaps_organizacionais, df_funcionarios):
    """Planeja contratações baseadas em gaps críticos"""
    contratacoes = []

    # Analisar departamentos com mais gaps
    gaps_por_dept = {}
    for idx, funcionario in df_funcionarios.iterrows():
        dept = funcionario.get('departamento', '')
        if dept not in gaps_por_dept:
            gaps_por_dept[dept] = []

    # Priorizar skills mais críticas
    for gap in gaps_organizacionais[:8]:  # Top 8 gaps
        skill = gap['skill']
        categoria = gap['categoria']
        pessoas_afetadas = gap['pessoas_afetadas']

        # Determinar urgência
        if gap['percentual_organizacao'] > 60:
            urgencia = 'Imediata'
        elif gap['percentual_organizacao'] > 30:
            urgencia = 'Alta'
        else:
            urgencia = 'Média'

        # Estimar impacto da contratação
        impacto_produtividade = min(gap['percentual_organizacao'] * 0.8, 40)
        economia_treinamento = pessoas_afetadas * \
            5000  # R$ 5k por pessoa em treinamento

        # Perfil sugerido
        perfil_sugerido = f"Especialista em {skill}"
        if categoria == 'Programação':
            perfil_sugerido = f"Desenvolvedor {skill}"
        elif categoria == 'IA/ML':
            perfil_sugerido = f"Cientista de Dados especialista em {skill}"
        elif categoria == 'Soft Skills':
            perfil_sugerido = f"Senior com forte {skill}"

        contratacoes.append({
            'skill_critica': skill,
            'categoria': categoria,
            'perfil_sugerido': perfil_sugerido,
            'pessoas_impactadas': pessoas_afetadas,
            'urgencia': urgencia,
            'impacto_produtividade': impacto_produtividade,
            'economia_treinamento': economia_treinamento,
            'roi_estimado': economia_treinamento + (impacto_produtividade * 1000)
        })

    return contratacoes


def gerar_trilhas_desenvolvimento(pessoa_analise):
    """Gera trilhas personalizadas de desenvolvimento"""
    trilhas = []

    gaps_prioritarios = list(pessoa_analise['gap_obrigatorias'])[
        :3]  # Top 3 gaps obrigatórias
    gaps_desejaveis = list(pessoa_analise['gap_desejaveis'])[
        :2]  # Top 2 desejáveis

    for skill in gaps_prioritarios:
        dados_skill = SKILLS_CATALOGO.get(skill, {})
        nivel_entrada = dados_skill.get('nivel_entrada', 1)
        categoria = dados_skill.get('categoria', 'Geral')

        # Estimar tempo de aprendizado
        if nivel_entrada == 1:
            tempo_estimado = "2-3 meses"
            dificuldade = "Iniciante"
        elif nivel_entrada == 2:
            tempo_estimado = "4-6 meses"
            dificuldade = "Intermediário"
        else:
            tempo_estimado = "6-12 meses"
            dificuldade = "Avançado"

        # Sugerir recursos
        recursos = []
        if categoria == 'Programação':
            recursos = ['Codecademy', 'Udemy', 'LeetCode', 'Projetos práticos']
        elif categoria == 'IA/ML':
            recursos = ['Coursera ML Course', 'Kaggle',
                        'Fast.ai', 'Papers científicos']
        elif categoria == 'Soft Skills':
            recursos = ['LinkedIn Learning',
                        'Coaching interno', 'Workshops', 'Mentoria']
        else:
            recursos = ['Cursos online', 'Certificações',
                        'Projetos práticos', 'Mentoria']

        trilhas.append({
            'skill': skill,
            'prioridade': 'Alta',
            'dificuldade': dificuldade,
            'tempo_estimado': tempo_estimado,
            'categoria': categoria,
            'recursos_sugeridos': recursos,
            'impacto_carreira': dados_skill.get('salario_impacto', 10)
        })

    for skill in gaps_desejaveis:
        dados_skill = SKILLS_CATALOGO.get(skill, {})
        trilhas.append({
            'skill': skill,
            'prioridade': 'Média',
            'dificuldade': 'Variável',
            'tempo_estimado': '3-6 meses',
            'categoria': dados_skill.get('categoria', 'Geral'),
            'recursos_sugeridos': ['Cursos online', 'Projetos side', 'Certificações'],
            'impacto_carreira': dados_skill.get('salario_impacto', 5)
        })

    return trilhas


# --- Interface Principal ---
df_agentes = carregar_agentes()

if df_agentes.empty:
    st.warning(
        "⚠️ Nenhum agente encontrado. Execute o script generate_agents.py primeiro.")
    st.stop()

# Análise inicial
analise_skills = mapear_skills_atuais_vs_necessarias(df_agentes)
gaps_organizacionais = analisar_gaps_organizacionais(analise_skills)
talentos_ocultos = identificar_talentos_ocultos(df_agentes)

# --- Dashboard Principal ---
st.header("📊 Visão Geral dos Skills")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if analise_skills:
        score_medio = np.mean([p['score_geral'] for p in analise_skills])
        st.metric("🎯 Score Médio Skills", f"{score_medio:.1f}%")

with col2:
    st.metric("🔍 Gaps Críticos", len(
        [g for g in gaps_organizacionais if g['criticidade'] > 60]))

with col3:
    st.metric("💎 Talentos Ocultos", len(talentos_ocultos))

with col4:
    pessoas_gaps = len([p for p in analise_skills if p['score_geral'] < 70])
    st.metric("⚠️ Necessitam Desenvolvimento", pessoas_gaps)

# --- Mapeamento de Skills ---
st.header("🗺️ Mapeamento de Skills Atuais vs Necessárias")

# Seletor de departamento
departamentos = ['Todos'] + \
    sorted(df_agentes['departamento'].unique().tolist())
dept_selecionado = st.selectbox("Filtrar por departamento:", departamentos)

# Filtrar dados
if dept_selecionado != 'Todos':
    analise_filtrada = [
        p for p in analise_skills if p['departamento'] == dept_selecionado]
else:
    analise_filtrada = analise_skills

if analise_filtrada:
    # Criar DataFrame para visualização
    df_skills_display = pd.DataFrame([
        {
            'Nome': p['nome'],
            'Cargo': p['cargo'],
            'Departamento': p['departamento'],
            'Score Geral': p['score_geral'],
            'Match Obrigatórias': p['match_obrigatorias'],
            'Match Desejáveis': p['match_desejaveis'],
            'Gaps Críticos': len(p['gap_obrigatorias'])
        }
        for p in analise_filtrada
    ])

    # Gráfico de distribuição de scores
    fig_dist = px.histogram(
        df_skills_display,
        x='Score Geral',
        nbins=20,
        title="Distribuição de Scores de Skills",
        labels={'Score Geral': 'Score (%)', 'count': 'Número de Funcionários'}
    )

    fig_dist.add_vline(x=70, line_dash="dash", line_color="red",
                       annotation_text="Linha de corte (70%)")

    st.plotly_chart(fig_dist, use_container_width=True)

    # Tabela detalhada
    st.subheader("📋 Análise Detalhada por Pessoa")
    st.dataframe(
        df_skills_display.style.format({
            'Score Geral': '{:.1f}%',
            'Match Obrigatórias': '{:.1f}%',
            'Match Desejáveis': '{:.1f}%'
        }).background_gradient(subset=['Score Geral'], cmap='RdYlGn'),
        use_container_width=True
    )

# --- Gaps Organizacionais ---
st.header("🎯 Gaps Organizacionais Críticos")

if gaps_organizacionais:
    # Top 10 gaps mais críticos
    top_gaps = gaps_organizacionais[:10]

    df_gaps = pd.DataFrame(top_gaps)

    # Gráfico de barras dos gaps mais críticos
    fig_gaps = px.bar(
        df_gaps,
        x='skill',
        y='criticidade',
        color='categoria',
        title="Skills com Maiores Gaps (Score de Criticidade)",
        labels={'criticidade': 'Score de Criticidade', 'skill': 'Skill'}
    )

    st.plotly_chart(fig_gaps, use_container_width=True)

    # Detalhamento dos gaps
    st.subheader("🔍 Análise Detalhada dos Gaps")

    for gap in top_gaps:
        with st.expander(f"📌 {gap['skill']} - {gap['pessoas_afetadas']} pessoas afetadas"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("🎯 Criticidade", f"{gap['criticidade']:.1f}")
                st.metric("👥 Pessoas Afetadas", gap['pessoas_afetadas'])

            with col2:
                st.metric("📊 % da Organização",
                          f"{gap['percentual_organizacao']:.1f}%")
                st.metric("🌍 Demanda Mercado", f"{gap['demanda_mercado']}%")

            with col3:
                st.metric("💰 Impacto Salarial", f"+{gap['impacto_salarial']}%")
                st.metric("🏷️ Categoria", gap['categoria'])

            # Ações recomendadas
            st.write("**🎯 Ações Recomendadas:**")
            if gap['pessoas_afetadas'] > 5:
                st.write("• Treinamento corporativo em grupo")
                st.write("• Contratação de especialista interno")
            else:
                st.write("• Treinamentos individualizados")
                st.write("• Mentoria com especialistas externos")

            st.write("• Parcerias com plataformas de ensino")
            st.write("• Projetos práticos para aplicação")

# --- Talentos Ocultos ---
st.header("💎 Talentos Ocultos")

if talentos_ocultos:
    st.subheader("🌟 Funcionários com Potencial Subutilizado")

    # Top 10 talentos ocultos
    top_talentos = talentos_ocultos[:10]

    for talento in top_talentos:
        with st.container():
            col1, col2, col3 = st.columns([0.4, 0.3, 0.3])

            with col1:
                st.write(f"**{talento['nome']}**")
                st.write(f"Atual: {talento['cargo_atual']}")
                st.write(f"Sugerido: **{talento['cargo_sugerido']}**")

            with col2:
                st.metric("🎯 Score Total", f"{talento['score_total']:.1f}%")
                st.metric("✅ Match Obrigatórias",
                          f"{talento['match_obrigatorias']:.1f}%")

            with col3:
                st.metric("💰 Impacto Salarial",
                          f"+{talento['impacto_salarial']}%")
                if st.button(f"📋 Avaliar Transição", key=f"transicao_{talento['id']}"):
                    st.success("✅ Avaliação de transição iniciada!")

            # Skills relevantes
            st.write(
                f"**Skills relevantes:** {', '.join(talento['skills_relevantes'])}")
            st.divider()

# --- Sugestões de Remanejamento ---
st.header("🔄 Sugestões de Remanejamento")

remanejamentos = sugerir_remanejamentos(talentos_ocultos, analise_skills)

if remanejamentos:
    st.subheader("🎯 Remanejamentos Estratégicos Recomendados")

    for remanejamento in remanejamentos[:5]:  # Top 5
        cor_prioridade = 'error' if remanejamento[
            'prioridade'] == 'Alta' else 'warning' if remanejamento['prioridade'] == 'Média' else 'info'

        with st.container():
            col1, col2, col3 = st.columns([0.4, 0.3, 0.3])

            with col1:
                st.write(f"**{remanejamento['funcionario']}**")
                st.write(
                    f"{remanejamento['cargo_atual']} → **{remanejamento['cargo_sugerido']}**")

            with col2:
                st.metric("🎯 Score Match",
                          f"{remanejamento['score_match']:.1f}%")
                st.metric("📈 Benefício",
                          f"+{remanejamento['beneficio_estimado']:.1f}%")

            with col3:
                st.metric("🎨 Prioridade", remanejamento['prioridade'])
                if st.button(f"✅ Implementar", key=f"remanej_{remanejamento['funcionario']}"):
                    st.success("🎯 Plano de remanejamento criado!")

            st.write(
                f"**Skills relevantes:** {', '.join(remanejamento['skills_relevantes'])}")
            st.divider()
else:
    st.info("✅ Não foram identificadas oportunidades de remanejamento no momento.")

# --- Planejamento de Contratações ---
st.header("🎯 Planejamento de Contratações Estratégicas")

contratacoes = planejar_contratacoes_estrategicas(
    gaps_organizacionais, df_agentes)

if contratacoes:
    st.subheader("👥 Contratações Prioritárias")

    # Métricas de impacto
    col1, col2, col3 = st.columns(3)

    with col1:
        economia_total = sum([c['economia_treinamento'] for c in contratacoes])
        st.metric("💰 Economia Treinamento", f"R$ {economia_total:,.0f}")

    with col2:
        pessoas_impactadas = sum([c['pessoas_impactadas']
                                 for c in contratacoes])
        st.metric("👥 Pessoas Impactadas", pessoas_impactadas)

    with col3:
        roi_total = sum([c['roi_estimado'] for c in contratacoes])
        st.metric("📈 ROI Estimado", f"R$ {roi_total:,.0f}")

    # Lista de contratações
    for contratacao in contratacoes[:6]:  # Top 6
        urgencia_cor = 'error' if contratacao['urgencia'] == 'Imediata' else 'warning' if contratacao['urgencia'] == 'Alta' else 'info'

        with st.expander(f"🎯 {contratacao['perfil_sugerido']} - {contratacao['urgencia']}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Skill Crítica:** {contratacao['skill_critica']}")
                st.write(f"**Categoria:** {contratacao['categoria']}")
                st.write(
                    f"**Pessoas Impactadas:** {contratacao['pessoas_impactadas']}")

            with col2:
                st.metric("⚡ Urgência", contratacao['urgencia'])
                st.metric("📈 Impacto Produtividade",
                          f"+{contratacao['impacto_produtividade']:.1f}%")
                st.metric("💰 ROI Estimado",
                          f"R$ {contratacao['roi_estimado']:,.0f}")

            if st.button(f"📋 Criar Job Description", key=f"job_{contratacao['skill_critica']}"):
                st.success(
                    "✅ Job description criada e enviada para recrutamento!")

# --- Análise Individual ---
st.header("👤 Análise Individual de Skills")

funcionario_selecionado = st.selectbox(
    "Selecione um funcionário para análise detalhada:",
    options=[p['id'] for p in analise_skills],
    format_func=lambda x: f"{next(p['nome'] for p in analise_skills if p['id'] == x)} ({next(p['cargo'] for p in analise_skills if p['id'] == x)})"
)

pessoa_analise = next(
    (p for p in analise_skills if p['id'] == funcionario_selecionado), None)

if pessoa_analise:
    st.subheader(f"🎯 Análise de {pessoa_analise['nome']}")

    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        # Gaps detalhados
        st.write("**🔴 Skills Obrigatórias em Falta:**")
        for skill in pessoa_analise['gap_obrigatorias']:
            categoria = SKILLS_CATALOGO.get(skill, {}).get('categoria', 'N/A')
            st.write(f"• {skill} ({categoria})")

        if pessoa_analise['gap_desejaveis']:
            st.write("**🟡 Skills Desejáveis em Falta:**")
            for skill in pessoa_analise['gap_desejaveis']:
                categoria = SKILLS_CATALOGO.get(
                    skill, {}).get('categoria', 'N/A')
                st.write(f"• {skill} ({categoria})")

        if pessoa_analise['skills_extras']:
            st.write("**✅ Skills Extras (Vantagem Competitiva):**")
            for skill in pessoa_analise['skills_extras']:
                categoria = SKILLS_CATALOGO.get(
                    skill, {}).get('categoria', 'N/A')
                st.write(f"• {skill} ({categoria})")

    with col2:
        # Métricas
        st.metric("🎯 Score Geral", f"{pessoa_analise['score_geral']:.1f}%")
        st.metric("✅ Match Obrigatórias",
                  f"{pessoa_analise['match_obrigatorias']:.1f}%")
        st.metric("🌟 Match Desejáveis",
                  f"{pessoa_analise['match_desejaveis']:.1f}%")
        st.metric("🚀 Match Futuras", f"{pessoa_analise['match_futuras']:.1f}%")

    # Trilhas de desenvolvimento
    st.subheader("🛤️ Trilhas de Desenvolvimento Personalizadas")

    trilhas = gerar_trilhas_desenvolvimento(pessoa_analise)

    if trilhas:
        for trilha in trilhas:
            cor = 'error' if trilha['prioridade'] == 'Alta' else 'warning' if trilha['prioridade'] == 'Média' else 'info'

            with st.expander(f"📚 {trilha['skill']} - {trilha['prioridade']} Prioridade"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Dificuldade:** {trilha['dificuldade']}")
                    st.write(f"**Tempo Estimado:** {trilha['tempo_estimado']}")
                    st.write(f"**Categoria:** {trilha['categoria']}")

                with col2:
                    st.metric("💰 Impacto Carreira",
                              f"+{trilha['impacto_carreira']}%")
                    if st.button(f"🚀 Iniciar Trilha", key=f"trilha_{trilha['skill']}"):
                        st.success("✅ Trilha de desenvolvimento iniciada!")

                st.write("**📖 Recursos Sugeridos:**")
                for recurso in trilha['recursos_sugeridos']:
                    st.write(f"• {recurso}")

# --- Análise por Categoria ---
st.header("📊 Análise por Categoria de Skills")

if gaps_organizacionais:
    # Agrupar gaps por categoria
    gaps_por_categoria = {}
    for gap in gaps_organizacionais:
        categoria = gap['categoria']
        if categoria not in gaps_por_categoria:
            gaps_por_categoria[categoria] = []
        gaps_por_categoria[categoria].append(gap)

    # Gráfico por categoria
    categorias = list(gaps_por_categoria.keys())
    critico_por_categoria = [
        sum([g['criticidade'] for g in gaps_por_categoria[cat]]) for cat in categorias]

    fig_cat = px.bar(
        x=categorias,
        y=critico_por_categoria,
        title="Criticidade Total de Gaps por Categoria",
        labels={'x': 'Categoria', 'y': 'Score Total de Criticidade'}
    )

    st.plotly_chart(fig_cat, use_container_width=True)

    # Detalhamento por categoria
    for categoria, gaps_cat in gaps_por_categoria.items():
        with st.expander(f"📂 {categoria} ({len(gaps_cat)} skills)"):
            for gap in gaps_cat[:3]:  # Top 3 da categoria
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**{gap['skill']}**")
                with col2:
                    st.write(f"Criticidade: {gap['criticidade']:.1f}")
                with col3:
                    st.write(f"Pessoas: {gap['pessoas_afetadas']}")

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
🔍 <strong>Skill Gap Intelligence</strong> - HumaniQ AI<br>
Mapeamento inteligente de competências para desenvolvimento estratégico de talentos
</div>
""", unsafe_allow_html=True)
