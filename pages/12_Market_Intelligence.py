import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Market Intelligence",
                   page_icon="🌍", layout="wide")

st.title("🌍 Market Intelligence Connector")
st.markdown("""
**Conecta com inteligência de mercado para benchmarking automático**

Sistema que monitora tendências salariais, demanda de competências, análise competitiva de talentos e insights de employer branding em tempo real.
""")

# --- Dados de Mercado (Simulados) ---
DADOS_MERCADO = {
    'salarios_por_cargo': {
        'Analista de Dados': {
            'junior': {'min': 4500, 'max': 7000, 'medio': 5750, 'crescimento_anual': 12},
            'pleno': {'min': 7000, 'max': 12000, 'medio': 9500, 'crescimento_anual': 15},
            'senior': {'min': 12000, 'max': 20000, 'medio': 16000, 'crescimento_anual': 18}
        },
        'Engenheiro de Software': {
            'junior': {'min': 5000, 'max': 8000, 'medio': 6500, 'crescimento_anual': 14},
            'pleno': {'min': 8000, 'max': 15000, 'medio': 11500, 'crescimento_anual': 16},
            'senior': {'min': 15000, 'max': 25000, 'medio': 20000, 'crescimento_anual': 20}
        },
        'Cientista de Dados': {
            'junior': {'min': 6000, 'max': 10000, 'medio': 8000, 'crescimento_anual': 25},
            'pleno': {'min': 10000, 'max': 18000, 'medio': 14000, 'crescimento_anual': 28},
            'senior': {'min': 18000, 'max': 35000, 'medio': 26500, 'crescimento_anual': 30}
        },
        'Designer UX/UI': {
            'junior': {'min': 3500, 'max': 6000, 'medio': 4750, 'crescimento_anual': 10},
            'pleno': {'min': 6000, 'max': 11000, 'medio': 8500, 'crescimento_anual': 12},
            'senior': {'min': 11000, 'max': 18000, 'medio': 14500, 'crescimento_anual': 15}
        },
        'Gerente de Produto': {
            'junior': {'min': 8000, 'max': 12000, 'medio': 10000, 'crescimento_anual': 8},
            'pleno': {'min': 12000, 'max': 20000, 'medio': 16000, 'crescimento_anual': 10},
            'senior': {'min': 20000, 'max': 35000, 'medio': 27500, 'crescimento_anual': 12}
        },
        'Gerente de Marketing': {
            'junior': {'min': 6000, 'max': 10000, 'medio': 8000, 'crescimento_anual': 6},
            'pleno': {'min': 10000, 'max': 16000, 'medio': 13000, 'crescimento_anual': 8},
            'senior': {'min': 16000, 'max': 28000, 'medio': 22000, 'crescimento_anual': 10}
        },
        'Analista de RH': {
            'junior': {'min': 3000, 'max': 5000, 'medio': 4000, 'crescimento_anual': 5},
            'pleno': {'min': 5000, 'max': 8500, 'medio': 6750, 'crescimento_anual': 7},
            'senior': {'min': 8500, 'max': 15000, 'medio': 11750, 'crescimento_anual': 9}
        }
    },

    'demanda_skills': {
        'Python': {'demanda_atual': 95, 'crescimento_6m': 8, 'escassez': 'Alta', 'salario_premium': 25},
        'JavaScript': {'demanda_atual': 90, 'crescimento_6m': 5, 'escassez': 'Média', 'salario_premium': 15},
        'Machine Learning': {'demanda_atual': 98, 'crescimento_6m': 15, 'escassez': 'Crítica', 'salario_premium': 40},
        'SQL': {'demanda_atual': 85, 'crescimento_6m': 3, 'escassez': 'Baixa', 'salario_premium': 8},
        'React': {'demanda_atual': 88, 'crescimento_6m': 10, 'escassez': 'Média', 'salario_premium': 18},
        'AWS': {'demanda_atual': 92, 'crescimento_6m': 12, 'escassez': 'Alta', 'salario_premium': 30},
        'Liderança': {'demanda_atual': 95, 'crescimento_6m': 4, 'escassez': 'Alta', 'salario_premium': 35},
        'Comunicação': {'demanda_atual': 90, 'crescimento_6m': 2, 'escassez': 'Média', 'salario_premium': 10}
    },

    'employer_branding': {
        'nossa_empresa': {
            'glassdoor_rating': 4.2,
            'linkedin_followers': 15680,
            'mentions_positivas': 78,
            'employee_satisfaction': 82,
            'cultura_score': 4.1,
            'beneficios_score': 3.9,
            'crescimento_score': 4.3
        },
        'concorrentes': {
            'Empresa A': {
                'glassdoor_rating': 4.5,
                'linkedin_followers': 25000,
                'mentions_positivas': 85,
                'employee_satisfaction': 88,
                'cultura_score': 4.4,
                'beneficios_score': 4.2,
                'crescimento_score': 4.1
            },
            'Empresa B': {
                'glassdoor_rating': 3.8,
                'linkedin_followers': 12000,
                'mentions_positivas': 65,
                'employee_satisfaction': 75,
                'cultura_score': 3.9,
                'beneficios_score': 3.7,
                'crescimento_score': 3.8
            },
            'Empresa C': {
                'glassdoor_rating': 4.1,
                'linkedin_followers': 18500,
                'mentions_positivas': 72,
                'employee_satisfaction': 80,
                'cultura_score': 4.0,
                'beneficios_score': 3.8,
                'crescimento_score': 4.2
            }
        }
    }
}

TENDENCIAS_MERCADO = [
    {
        'tendencia': 'IA Generativa',
        'impacto': 'Alto',
        'timeline': '6-12 meses',
        'skills_relacionadas': ['Machine Learning', 'Python', 'NLP'],
        'oportunidades': 'Criação de novos cargos especializados',
        'riscos': 'Obsolescência de algumas funções tradicionais'
    },
    {
        'tendencia': 'Trabalho Remoto Híbrido',
        'impacto': 'Médio',
        'timeline': 'Já em curso',
        'skills_relacionadas': ['Comunicação', 'Liderança', 'Colaboração Digital'],
        'oportunidades': 'Acesso a talentos globais',
        'riscos': 'Competição aumentada por talentos'
    },
    {
        'tendencia': 'Sustentabilidade ESG',
        'impacto': 'Médio',
        'timeline': '12-24 meses',
        'skills_relacionadas': ['Análise de Dados', 'Compliance', 'Gestão de Projetos'],
        'oportunidades': 'Novos cargos em ESG e sustentabilidade',
        'riscos': 'Pressão regulatória e de stakeholders'
    },
    {
        'tendencia': 'Automação RPA',
        'impacto': 'Alto',
        'timeline': '3-18 meses',
        'skills_relacionadas': ['Python', 'Análise de Processos', 'UiPath'],
        'oportunidades': 'Eficiência operacional',
        'riscos': 'Redução de cargos operacionais'
    }
]

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


def simular_salarios_internos(df_funcionarios):
    """Simula salários internos baseados em cargo e senioridade"""
    salarios_internos = []

    for idx, funcionario in df_funcionarios.iterrows():
        cargo = funcionario.get('cargo', '')
        tempo_casa = funcionario.get('tempo_de_casa_meses', 12)

        # Determinar senioridade baseada no tempo
        if tempo_casa <= 12:
            senioridade = 'junior'
        elif tempo_casa <= 36:
            senioridade = 'pleno'
        else:
            senioridade = 'senior'

        # Buscar dados de mercado
        if cargo in DADOS_MERCADO['salarios_por_cargo']:
            dados_cargo = DADOS_MERCADO['salarios_por_cargo'][cargo][senioridade]

            # Simular salário interno (variação de ±15% do mercado)
            salario_mercado = dados_cargo['medio']
            variacao = random.uniform(-0.15, 0.15)
            salario_interno = salario_mercado * (1 + variacao)

            salarios_internos.append({
                'id': idx,
                'nome': funcionario['nome'],
                'cargo': cargo,
                'senioridade': senioridade,
                'salario_interno': round(salario_interno, 0),
                'salario_mercado': salario_mercado,
                'gap_salarial': round((salario_interno - salario_mercado) / salario_mercado * 100, 1),
                'min_mercado': dados_cargo['min'],
                'max_mercado': dados_cargo['max'],
                'crescimento_anual': dados_cargo['crescimento_anual']
            })

    return salarios_internos


def analisar_competitividade_salarial(salarios_internos):
    """Analisa competitividade salarial da empresa"""
    if not salarios_internos:
        return {}

    gaps_positivos = [s for s in salarios_internos if s['gap_salarial'] > 0]
    gaps_negativos = [s for s in salarios_internos if s['gap_salarial'] < 0]

    gap_medio = np.mean([s['gap_salarial'] for s in salarios_internos])

    # Risco de turnover baseado em gap salarial
    alto_risco = [s for s in salarios_internos if s['gap_salarial'] < -15]

    # Análise por cargo
    gaps_por_cargo = {}
    for salario in salarios_internos:
        cargo = salario['cargo']
        if cargo not in gaps_por_cargo:
            gaps_por_cargo[cargo] = []
        gaps_por_cargo[cargo].append(salario['gap_salarial'])

    gaps_cargo_medio = {cargo: np.mean(gaps)
                        for cargo, gaps in gaps_por_cargo.items()}

    return {
        'gap_medio_geral': gap_medio,
        'funcionarios_acima_mercado': len(gaps_positivos),
        'funcionarios_abaixo_mercado': len(gaps_negativos),
        'alto_risco_turnover': len(alto_risco),
        'gaps_por_cargo': gaps_cargo_medio,
        'pessoas_alto_risco': [s['nome'] for s in alto_risco]
    }


def identificar_talentos_escassos(df_funcionarios):
    """Identifica funcionários com skills escassas no mercado"""
    talentos_escassos = []

    for idx, funcionario in df_funcionarios.iterrows():
        skills = funcionario.get('competencias', [])
        score_escassez = 0
        skills_escassas = []

        for skill in skills:
            if skill in DADOS_MERCADO['demanda_skills']:
                dados_skill = DADOS_MERCADO['demanda_skills'][skill]
                if dados_skill['escassez'] in ['Alta', 'Crítica']:
                    score_escassez += dados_skill['demanda_atual']
                    skills_escassas.append({
                        'skill': skill,
                        'escassez': dados_skill['escassez'],
                        'demanda': dados_skill['demanda_atual'],
                        'premium': dados_skill['salario_premium']
                    })

        if skills_escassas:
            talentos_escassos.append({
                'id': idx,
                'nome': funcionario['nome'],
                'cargo': funcionario['cargo'],
                'score_escassez': score_escassez,
                'skills_escassas': skills_escassas,
                'risco_recrutamento': 'Alto' if score_escassez > 180 else 'Médio' if score_escassez > 90 else 'Baixo'
            })

    return sorted(talentos_escassos, key=lambda x: x['score_escassez'], reverse=True)


def gerar_relatorio_employer_branding():
    """Gera relatório de posicionamento no mercado"""
    nossa_empresa = DADOS_MERCADO['employer_branding']['nossa_empresa']
    concorrentes = DADOS_MERCADO['employer_branding']['concorrentes']

    # Comparações
    comparacoes = {}
    for metrica in ['glassdoor_rating', 'employee_satisfaction', 'cultura_score', 'beneficios_score', 'crescimento_score']:
        nosso_valor = nossa_empresa[metrica]
        valores_concorrentes = [dados[metrica]
                                for dados in concorrentes.values()]
        media_mercado = np.mean(valores_concorrentes)
        posicao = sum(1 for v in valores_concorrentes if nosso_valor > v) + 1

        comparacoes[metrica] = {
            'nosso_valor': nosso_valor,
            'media_mercado': media_mercado,
            'gap': nosso_valor - media_mercado,
            'posicao': f"{posicao}º de {len(concorrentes) + 1}",
            'percentil': (len(concorrentes) + 1 - posicao) / (len(concorrentes) + 1) * 100
        }

    return comparacoes


def calcular_custo_substituicao(funcionario_info, salarios_mercado):
    """Calcula custo de substituição de um funcionário"""
    cargo = funcionario_info.get('cargo', '')

    # Buscar salário de mercado
    salario_mercado = 0
    for sal in salarios_mercado:
        if sal['nome'] == funcionario_info.get('nome', ''):
            salario_mercado = sal['salario_mercado']
            break

    if salario_mercado == 0:
        salario_mercado = 8000  # Default

    # Componentes do custo de substituição
    custos = {
        'recrutamento': salario_mercado * 0.5,  # 0.5x salário mensal
        'onboarding': salario_mercado * 1.0,    # 1x salário mensal
        'treinamento': salario_mercado * 0.8,   # 0.8x salário mensal
        'produtividade_perdida': salario_mercado * 2.0,  # 2x salário mensal
        'knowledge_loss': salario_mercado * 0.7  # 0.7x salário mensal
    }

    custo_total = sum(custos.values())

    return {
        'custo_total': custo_total,
        'breakdown': custos,
        'meses_payback': round(custo_total / salario_mercado, 1)
    }


def simular_dados_temporais():
    """Simula evolução temporal de métricas de mercado"""
    dates = pd.date_range(start='2024-01-01', end='2025-01-01', freq='M')

    # Simular evolução do Glassdoor rating
    nossa_rating = []
    rating_base = 4.2
    for i, date in enumerate(dates):
        # Simulação de melhoria gradual
        rating = rating_base + (i * 0.02) + random.gauss(0, 0.05)
        rating = max(1, min(5, rating))  # Entre 1 e 5
        nossa_rating.append(rating)

    # Simular market share de talentos
    market_share = []
    share_base = 15
    for i, date in enumerate(dates):
        share = share_base + (i * 0.5) + random.gauss(0, 1)
        share = max(5, min(30, share))  # Entre 5% e 30%
        market_share.append(share)

    return pd.DataFrame({
        'data': dates,
        'glassdoor_rating': nossa_rating,
        'market_share_talentos': market_share,
        # % em relação ao mercado
        'competitividade_salarial': [random.gauss(95, 5) for _ in dates]
    })


# --- Interface Principal ---
df_agentes = carregar_agentes()

if df_agentes.empty:
    st.warning(
        "⚠️ Nenhum agente encontrado. Execute o script generate_agents.py primeiro.")
    st.stop()

# Análises iniciais
salarios_internos = simular_salarios_internos(df_agentes)
competitividade = analisar_competitividade_salarial(salarios_internos)
talentos_escassos = identificar_talentos_escassos(df_agentes)
employer_branding = gerar_relatorio_employer_branding()

# --- Dashboard Principal ---
st.header("📊 Market Intelligence Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Gap Salarial Médio",
        f"{competitividade.get('gap_medio_geral', 0):.1f}%",
        "vs mercado"
    )

with col2:
    st.metric(
        "⚠️ Alto Risco Turnover",
        competitividade.get('alto_risco_turnover', 0),
        "por salário"
    )

with col3:
    st.metric(
        "💎 Talentos Escassos",
        len(talentos_escassos),
        "identificados"
    )

with col4:
    glassdoor_rating = employer_branding.get(
        'glassdoor_rating', {}).get('nosso_valor', 0)
    percentil = employer_branding.get(
        'glassdoor_rating', {}).get('percentil', 0)
    st.metric(
        "⭐ Glassdoor Rating",
        f"{glassdoor_rating:.1f}/5",
        f"{percentil:.0f}º percentil"
    )

# --- Benchmarking Salarial ---
st.header("💰 Benchmarking Salarial")

if salarios_internos:
    # Gráfico de comparação salarial por cargo
    df_salarios = pd.DataFrame(salarios_internos)

    fig_salarios = px.scatter(
        df_salarios,
        x='salario_mercado',
        y='salario_interno',
        color='senioridade',
        size=abs(df_salarios['gap_salarial']),
        hover_name='nome',
        hover_data=['cargo', 'gap_salarial'],
        title="Salários Internos vs Mercado por Senioridade",
        labels={
            'salario_mercado': 'Salário Mercado (R$)',
            'salario_interno': 'Salário Interno (R$)'
        }
    )

    # Linha de paridade
    max_salario = max(df_salarios['salario_mercado'].max(
    ), df_salarios['salario_interno'].max())
    fig_salarios.add_trace(go.Scatter(
        x=[0, max_salario],
        y=[0, max_salario],
        mode='lines',
        name='Linha de Paridade',
        line=dict(dash='dash', color='red')
    ))

    st.plotly_chart(fig_salarios, use_container_width=True)

    # Análise por cargo
    st.subheader("📊 Competitividade por Cargo")

    gaps_por_cargo = competitividade.get('gaps_por_cargo', {})
    if gaps_por_cargo:
        df_gaps_cargo = pd.DataFrame([
            {'Cargo': cargo, 'Gap Médio (%)': gap}
            for cargo, gap in gaps_por_cargo.items()
        ])

        fig_gaps_cargo = px.bar(
            df_gaps_cargo,
            x='Cargo',
            y='Gap Médio (%)',
            title="Gap Salarial Médio por Cargo",
            color='Gap Médio (%)',
            color_continuous_scale='RdYlGn'
        )

        fig_gaps_cargo.add_hline(y=0, line_dash="dash", line_color="black",
                                 annotation_text="Paridade com mercado")

        st.plotly_chart(fig_gaps_cargo, use_container_width=True)

    # Funcionários em risco
    if competitividade.get('pessoas_alto_risco'):
        st.subheader("🚨 Funcionários em Alto Risco (Gap > -15%)")

        funcionarios_risco = [
            s for s in salarios_internos if s['gap_salarial'] < -15]

        for funcionario in funcionarios_risco:
            with st.container():
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.write(f"**{funcionario['nome']}**")
                    st.write(f"{funcionario['cargo']}")

                with col2:
                    st.metric("Gap Salarial",
                              f"{funcionario['gap_salarial']:.1f}%")

                with col3:
                    st.metric("Salário Atual",
                              f"R$ {funcionario['salario_interno']:,.0f}")
                    st.metric(
                        "Mercado", f"R$ {funcionario['salario_mercado']:,.0f}")

                with col4:
                    # Calcular custo de substituição
                    custo_substituicao = calcular_custo_substituicao(
                        {'nome': funcionario['nome'],
                            'cargo': funcionario['cargo']},
                        salarios_internos
                    )
                    st.metric("Custo Substituição",
                              f"R$ {custo_substituicao['custo_total']:,.0f}")

                    if st.button(f"💰 Ajustar Salário", key=f"ajuste_{funcionario['id']}"):
                        st.success("✅ Proposta de ajuste salarial criada!")

                st.divider()

# --- Demanda de Skills ---
st.header("🎯 Demanda de Competências no Mercado")

skills_mercado = DADOS_MERCADO['demanda_skills']

# Top skills em demanda
df_skills_demanda = pd.DataFrame([
    {
        'Skill': skill,
        'Demanda Atual': dados['demanda_atual'],
        'Crescimento 6M': dados['crescimento_6m'],
        'Escassez': dados['escassez'],
        'Prêmio Salarial': dados['salario_premium']
    }
    for skill, dados in skills_mercado.items()
]).sort_values('Demanda Atual', ascending=False)

col1, col2 = st.columns(2)

with col1:
    # Gráfico de demanda vs crescimento
    fig_demanda = px.scatter(
        df_skills_demanda,
        x='Demanda Atual',
        y='Crescimento 6M',
        size='Prêmio Salarial',
        color='Escassez',
        hover_name='Skill',
        title="Demanda Atual vs Crescimento Projetado",
        color_discrete_map={
            'Crítica': 'red',
            'Alta': 'orange',
            'Média': 'yellow',
            'Baixa': 'green'
        }
    )

    st.plotly_chart(fig_demanda, use_container_width=True)

with col2:
    # Top skills por prêmio salarial
    top_premium = df_skills_demanda.nlargest(6, 'Prêmio Salarial')

    fig_premium = px.bar(
        top_premium,
        x='Prêmio Salarial',
        y='Skill',
        orientation='h',
        title="Top Skills por Prêmio Salarial",
        color='Escassez',
        color_discrete_map={
            'Crítica': 'red',
            'Alta': 'orange',
            'Média': 'yellow',
            'Baixa': 'green'
        }
    )

    st.plotly_chart(fig_premium, use_container_width=True)

# Skills gap vs mercado
st.subheader("🔍 Nossos Skills vs Demanda de Mercado")

# Analisar quais skills em alta demanda temos/não temos
all_skills_funcionarios = set()
for _, funcionario in df_agentes.iterrows():
    all_skills_funcionarios.update(funcionario.get('competencias', []))

skills_analysis = []
for skill, dados in skills_mercado.items():
    temos_skill = skill in all_skills_funcionarios
    pessoas_com_skill = 0

    if temos_skill:
        for _, funcionario in df_agentes.iterrows():
            if skill in funcionario.get('competencias', []):
                pessoas_com_skill += 1

    skills_analysis.append({
        'Skill': skill,
        'Demanda Mercado': dados['demanda_atual'],
        'Temos Skill': 'Sim' if temos_skill else 'Não',
        'Pessoas com Skill': pessoas_com_skill,
        'Cobertura (%)': (pessoas_com_skill / len(df_agentes) * 100) if pessoas_com_skill > 0 else 0,
        'Gap': 'Alto' if dados['demanda_atual'] > 85 and not temos_skill else 'Médio' if dados['demanda_atual'] > 85 and pessoas_com_skill < 3 else 'Baixo'
    })

df_skills_analysis = pd.DataFrame(skills_analysis)

# Destacar gaps críticos
gaps_criticos = df_skills_analysis[df_skills_analysis['Gap'] == 'Alto']
if not gaps_criticos.empty:
    st.error("🚨 **Skills Críticos em Falta:**")
    for _, row in gaps_criticos.iterrows():
        st.write(
            f"• **{row['Skill']}** - Demanda: {row['Demanda Mercado']}% | Status: {row['Temos Skill']}")

st.dataframe(
    df_skills_analysis.style.applymap(
        lambda x: 'background-color: #ffcccc' if x == 'Alto'
        else 'background-color: #ffffcc' if x == 'Médio'
        else 'background-color: #ccffcc' if x == 'Baixo'
        else '', subset=['Gap']
    ),
    use_container_width=True
)

# --- Talentos Escassos ---
st.header("💎 Talentos Escassos - Risco de Recrutamento")

if talentos_escassos:
    st.subheader("🎯 Funcionários com Skills Escassas no Mercado")

    for talento in talentos_escassos[:8]:  # Top 8
        risco_cor = 'error' if talento['risco_recrutamento'] == 'Alto' else 'warning' if talento['risco_recrutamento'] == 'Médio' else 'info'

        with st.container():
            col1, col2, col3 = st.columns([0.4, 0.4, 0.2])

            with col1:
                st.write(f"**{talento['nome']}** ({talento['cargo']})")
                st.write(
                    f"Risco de recrutamento: **{talento['risco_recrutamento']}**")

            with col2:
                st.write("**Skills Escassas:**")
                for skill_info in talento['skills_escassas'][:3]:  # Top 3 skills
                    st.write(
                        f"• {skill_info['skill']} (Escassez: {skill_info['escassez']}, +{skill_info['premium']}% salário)")

            with col3:
                st.metric("Score Escassez", f"{talento['score_escassez']:.0f}")

                # Calcular custo de substituição
                custo_substituicao = calcular_custo_substituicao(
                    {'nome': talento['nome'], 'cargo': talento['cargo']},
                    salarios_internos
                )
                st.metric("Custo Substituição",
                          f"R$ {custo_substituicao['custo_total']:,.0f}")

                if st.button(f"🛡️ Criar Plano Retenção", key=f"retencao_{talento['id']}"):
                    st.success("✅ Plano de retenção criado!")

            st.divider()
else:
    st.info("✅ Baixo risco: poucos funcionários com skills críticas em escassez.")

# --- Employer Branding ---
st.header("🏢 Análise de Employer Branding")

if employer_branding:
    st.subheader("📊 Nosso Posicionamento vs Concorrentes")

    # Métricas de employer branding
    metricas_eb = ['glassdoor_rating', 'employee_satisfaction',
                   'cultura_score', 'beneficios_score', 'crescimento_score']
    nomes_metricas = ['Glassdoor Rating', 'Satisfação Funcionários',
                      'Cultura', 'Benefícios', 'Crescimento']

    nossos_valores = [employer_branding[metrica]['nosso_valor']
                      for metrica in metricas_eb]
    media_mercado = [employer_branding[metrica]['media_mercado']
                     for metrica in metricas_eb]

    fig_eb = go.Figure()

    fig_eb.add_trace(go.Scatterpolar(
        r=nossos_valores,
        theta=nomes_metricas,
        fill='toself',
        name='Nossa Empresa',
        fillcolor='rgba(0, 100, 200, 0.3)'
    ))

    fig_eb.add_trace(go.Scatterpolar(
        r=media_mercado,
        theta=nomes_metricas,
        fill='toself',
        name='Média Mercado',
        fillcolor='rgba(200, 100, 0, 0.3)'
    ))

    fig_eb.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        title="Employer Branding: Nossa Empresa vs Mercado"
    )

    st.plotly_chart(fig_eb, use_container_width=True)

    # Detalhamento das métricas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Nossos Pontos Fortes")
        pontos_fortes = []
        for metrica in metricas_eb:
            dados = employer_branding[metrica]
            if dados['gap'] > 0:
                pontos_fortes.append((metrica, dados['gap']))

        pontos_fortes.sort(key=lambda x: x[1], reverse=True)

        for metrica, gap in pontos_fortes:
            nome_metrica = dict(zip(metricas_eb, nomes_metricas))[metrica]
            st.success(f"✅ {nome_metrica}: +{gap:.2f} vs mercado")

    with col2:
        st.subheader("⚠️ Oportunidades de Melhoria")
        melhorias = []
        for metrica in metricas_eb:
            dados = employer_branding[metrica]
            if dados['gap'] < 0:
                melhorias.append((metrica, dados['gap']))

        melhorias.sort(key=lambda x: x[1])

        for metrica, gap in melhorias:
            nome_metrica = dict(zip(metricas_eb, nomes_metricas))[metrica]
            st.warning(f"⚠️ {nome_metrica}: {gap:.2f} vs mercado")

# --- Tendências de Mercado ---
st.header("📈 Tendências de Mercado")

st.subheader("🔮 Tendências Emergentes")

for tendencia in TENDENCIAS_MERCADO:
    impacto_cor = 'error' if tendencia['impacto'] == 'Alto' else 'warning' if tendencia['impacto'] == 'Médio' else 'info'

    with st.expander(f"🎯 {tendencia['tendencia']} - Impacto {tendencia['impacto']}"):
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Timeline:** {tendencia['timeline']}")
            st.write(
                f"**Skills Relacionadas:** {', '.join(tendencia['skills_relacionadas'])}")

        with col2:
            st.write("**Oportunidades:**")
            st.write(f"• {tendencia['oportunidades']}")
            st.write("**Riscos:**")
            st.write(f"• {tendencia['riscos']}")

        # Verificar se temos as skills relacionadas
        skills_que_temos = []
        skills_que_faltam = []

        for skill in tendencia['skills_relacionadas']:
            if skill in all_skills_funcionarios:
                skills_que_temos.append(skill)
            else:
                skills_que_faltam.append(skill)

        if skills_que_temos:
            st.success(
                f"✅ **Skills que temos:** {', '.join(skills_que_temos)}")

        if skills_que_faltam:
            st.error(
                f"❌ **Skills que faltam:** {', '.join(skills_que_faltam)}")

# --- Evolução Temporal ---
st.header("📊 Evolução Temporal")

df_temporal = simular_dados_temporais()

col1, col2 = st.columns(2)

with col1:
    # Evolução do Glassdoor Rating
    fig_rating = px.line(
        df_temporal,
        x='data',
        y='glassdoor_rating',
        title="Evolução do Glassdoor Rating",
        labels={'glassdoor_rating': 'Rating', 'data': 'Período'}
    )

    fig_rating.add_hline(y=4.5, line_dash="dash", line_color="green",
                         annotation_text="Meta: 4.5")

    st.plotly_chart(fig_rating, use_container_width=True)

with col2:
    # Market share de talentos
    fig_share = px.line(
        df_temporal,
        x='data',
        y='market_share_talentos',
        title="Market Share de Talentos (%)",
        labels={'market_share_talentos': 'Market Share (%)', 'data': 'Período'}
    )

    st.plotly_chart(fig_share, use_container_width=True)

# --- Recomendações Estratégicas ---
st.header("💡 Recomendações Estratégicas")

recomendacoes = []

# Baseado em gaps salariais
if competitividade.get('alto_risco_turnover', 0) > 2:
    recomendacoes.append({
        'categoria': 'Retenção Salarial',
        'prioridade': 'Alta',
        'acao': 'Ajustar salários dos funcionários em risco',
        'investimento': f"R$ {len(salarios_internos) * 2000:,.0f}",
        'roi': 'Evitar custos de substituição 5x maiores'
    })

# Baseado em skills escassas
if len(talentos_escassos) > 3:
    recomendacoes.append({
        'categoria': 'Retenção de Talentos',
        'prioridade': 'Alta',
        'acao': 'Programa especial de retenção para talentos escassos',
        'investimento': 'R$ 150.000',
        'roi': 'Reduzir risco de perda de knowledge crítico'
    })

# Baseado em employer branding
glassdoor_gap = employer_branding.get('glassdoor_rating', {}).get('gap', 0)
if glassdoor_gap < -0.2:
    recomendacoes.append({
        'categoria': 'Employer Branding',
        'prioridade': 'Média',
        'acao': 'Campanha de melhoria da marca empregadora',
        'investimento': 'R$ 80.000',
        'roi': 'Melhorar atração de talentos em 25%'
    })

# Baseado em skills gaps
skills_gaps_altos = len(
    df_skills_analysis[df_skills_analysis['Gap'] == 'Alto'])
if skills_gaps_altos > 2:
    recomendacoes.append({
        'categoria': 'Desenvolvimento',
        'prioridade': 'Média',
        'acao': 'Programa intensivo de upskilling',
        'investimento': 'R$ 200.000',
        'roi': 'Reduzir dependência de contratações externas'
    })

for rec in recomendacoes:
    cor = 'error' if rec['prioridade'] == 'Alta' else 'warning' if rec['prioridade'] == 'Média' else 'info'

    with st.expander(f"🎯 {rec['acao']} - {rec['prioridade']}"):
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Categoria:** {rec['categoria']}")
            st.write(f"**Investimento:** {rec['investimento']}")

        with col2:
            st.write(f"**ROI Esperado:** {rec['roi']}")
            if st.button(f"📋 Implementar", key=f"impl_{rec['categoria']}"):
                st.success("✅ Plano de implementação criado!")

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
🌍 <strong>Market Intelligence Connector</strong> - HumaniQ AI<br>
Inteligência de mercado em tempo real para decisões estratégicas de talentos
</div>
""", unsafe_allow_html=True)
