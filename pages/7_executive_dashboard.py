import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Executive Dashboard",
                   page_icon="🎛️", layout="wide")

st.title("🎛️ Executive Dashboard - HumaniQ AI")
st.markdown("""
**Dashboard executivo com métricas e insights em tempo real para tomada de decisões estratégicas**

Visão consolidada do capital humano com foco em ROI, riscos e oportunidades de otimização.
""")

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


def calcular_metricas_principais(df):
    """Calcula as métricas principais do dashboard"""
    total_funcionarios = len(df)

    # ROI simulado baseado em performance e engajamento
    performance_media = df.apply(lambda x:
                                 x.get('performance.avaliacoes_desempenho', [
                                       {}])[-1].get('nota', 7)
                                 if isinstance(x.get('performance.avaliacoes_desempenho'), list) else 7, axis=1
                                 ).mean()

    engajamento_medio = df['engajamento.enps_recente'].mean()
    roi_estimado = (performance_media / 10 * 0.6 +
                    engajamento_medio / 10 * 0.4) * 847  # Base: 847% ROI

    # Redução de turnover simulada
    funcionarios_risco = len(
        df[df.apply(calcular_risco_turnover_exec, axis=1) >= 50])
    reducao_turnover = max(
        0, 70 - (funcionarios_risco / total_funcionarios * 100))

    # Fit cultural médio
    big_five_cols = [
        'perfil_big_five.abertura_a_experiencia',
        'perfil_big_five.conscienciosidade',
        'perfil_big_five.extroversao',
        'perfil_big_five.amabilidade',
        'perfil_big_five.neuroticismo'
    ]
    fit_cultural = (df[big_five_cols].mean().mean() / 10 * 100)

    # Payback simulado
    payback_meses = max(2, 6 - (roi_estimado / 847 * 4))

    # Aumento de produtividade
    metas_media = df['performance.metas_atingidas_percentual'].mean()
    produtividade = min(35, metas_media / 100 * 40)

    return {
        'total_funcionarios': total_funcionarios,
        'roi_estimado': roi_estimado,
        'reducao_turnover': reducao_turnover,
        'fit_cultural': fit_cultural,
        'payback_meses': payback_meses,
        'aumento_produtividade': produtividade,
        'funcionarios_risco': funcionarios_risco
    }


def calcular_risco_turnover_exec(funcionario):
    """Versão simplificada do cálculo de risco para o executive dashboard"""
    risk_score = 0

    # Engajamento
    enps = funcionario.get('engajamento.enps_recente', 5)
    if enps <= 3:
        risk_score += 25
    elif enps <= 5:
        risk_score += 15

    # Performance
    metas = funcionario.get('performance.metas_atingidas_percentual', 85)
    if metas <= 70:
        risk_score += 20
    elif metas <= 80:
        risk_score += 10

    # Burnout
    burnout_risk = funcionario.get('kpis_ia.risco_burnout', 5)
    if burnout_risk >= 8:
        risk_score += 20
    elif burnout_risk >= 6:
        risk_score += 12

    # Sentimento
    sentimento = funcionario.get(
        'engajamento.comentarios_sentimento', 'neutro')
    if sentimento == 'negativo':
        risk_score += 10

    return min(risk_score, 100)


def calcular_fit_vaga_simples(funcionario, vaga_perfil):
    """Calcula fit simplificado entre funcionário e perfil ideal"""
    perfil_func = np.array([
        funcionario.get('perfil_big_five.abertura_a_experiencia', 5),
        funcionario.get('perfil_big_five.conscienciosidade', 5),
        funcionario.get('perfil_big_five.extroversao', 5),
        funcionario.get('perfil_big_five.amabilidade', 5),
        funcionario.get('perfil_big_five.neuroticismo', 5)
    ])

    distancia = np.linalg.norm(perfil_func - vaga_perfil)
    fit = max(0, 1 - distancia /
              np.linalg.norm(np.array([10, 10, 10, 10, 10]))) * 100
    return fit


# --- Interface Principal ---
df_agentes = carregar_agentes()

if df_agentes.empty:
    st.warning(
        "⚠️ Nenhum agente encontrado. Execute o script generate_agents.py primeiro.")
    st.stop()

# Calcular métricas principais
metricas = calcular_metricas_principais(df_agentes)

# --- SEÇÃO 1: KPIs PRINCIPAIS ---
st.header("📊 KPIs Principais")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "🎯 ROI em 3 Anos",
        f"{metricas['roi_estimado']:.0f}%",
        f"+{metricas['roi_estimado'] - 847:.0f}% vs baseline"
    )

with col2:
    st.metric(
        "📉 Redução Turnover",
        f"{metricas['reducao_turnover']:.0f}%",
        "+5% vs mês anterior"
    )

with col3:
    st.metric(
        "🎭 Fit Cultural Médio",
        f"{metricas['fit_cultural']:.0f}%",
        "+3% vs trimestre"
    )

with col4:
    st.metric(
        "💰 Payback",
        f"{metricas['payback_meses']:.0f} meses",
        "-1 mês vs projeção"
    )

with col5:
    st.metric(
        "📈 Aumento Produtividade",
        f"{metricas['aumento_produtividade']:.0f}%",
        "+2% vs baseline"
    )

with col6:
    st.metric(
        "⚠️ Funcionários em Risco",
        metricas['funcionarios_risco'],
        f"-2 vs mês anterior"
    )

# --- SEÇÃO 2: ALERTS E PRIORIDADES ---
st.header("🚨 Alertas e Prioridades")

# Simular alertas baseados nos dados
alertas = []

if metricas['funcionarios_risco'] >= 3:
    alertas.append({
        'tipo': 'CRÍTICO',
        'cor': 'error',
        'titulo': f"{metricas['funcionarios_risco']} funcionários em risco alto de saída",
        'acao': "Revisar estratégias de retenção imediatamente"
    })

if metricas['fit_cultural'] < 85:
    alertas.append({
        'tipo': 'ATENÇÃO',
        'cor': 'warning',
        'titulo': "Fit cultural abaixo do objetivo (85%)",
        'acao': "Implementar programa de alinhamento cultural"
    })

if metricas['roi_estimado'] < 800:
    alertas.append({
        'tipo': 'OPORTUNIDADE',
        'cor': 'info',
        'titulo': "ROI abaixo da meta (847%)",
        'acao': "Otimizar processos de seleção e desenvolvimento"
    })

if not alertas:
    alertas.append({
        'tipo': 'SUCESSO',
        'cor': 'success',
        'titulo': "Todas as métricas dentro dos objetivos",
        'acao': "Manter estratégia atual e monitorar tendências"
    })

for alerta in alertas:
    st.toast(f"{alerta['tipo']}: {alerta['titulo']}",
             icon="🚨" if alerta['tipo'] == 'CRÍTICO' else "ℹ️")

# Exibir alertas em cards
col1, col2 = st.columns(2)
for i, alerta in enumerate(alertas):
    with col1 if i % 2 == 0 else col2:
        if alerta['cor'] == 'error':
            st.error(f"🚨 **{alerta['titulo']}**\n\n➡️ {alerta['acao']}")
        elif alerta['cor'] == 'warning':
            st.warning(f"⚠️ **{alerta['titulo']}**\n\n➡️ {alerta['acao']}")
        elif alerta['cor'] == 'info':
            st.info(f"💡 **{alerta['titulo']}**\n\n➡️ {alerta['acao']}")
        else:
            st.success(f"✅ **{alerta['titulo']}**\n\n➡️ {alerta['acao']}")

# --- SEÇÃO 3: ANÁLISE POR DEPARTAMENTO ---
st.header("🏢 Performance por Departamento")

# Calcular métricas por departamento
dept_metrics = []
for dept in df_agentes['departamento'].unique():
    dept_df = df_agentes[df_agentes['departamento'] == dept]

    # Performance média
    perf_media = dept_df.apply(lambda x:
                               x.get('performance.avaliacoes_desempenho',
                                     [{}])[-1].get('nota', 7)
                               if isinstance(x.get('performance.avaliacoes_desempenho'), list) else 7, axis=1
                               ).mean()

    # Engajamento médio
    eng_medio = dept_df['engajamento.enps_recente'].mean()

    # Funcionários em risco
    em_risco = len(dept_df[dept_df.apply(
        calcular_risco_turnover_exec, axis=1) >= 50])

    # Fit cultural
    big_five_cols = [
        'perfil_big_five.abertura_a_experiencia',
        'perfil_big_five.conscienciosidade',
        'perfil_big_five.extroversao',
        'perfil_big_five.amabilidade',
        'perfil_big_five.neuroticismo'
    ]
    fit_cultural_dept = (dept_df[big_five_cols].mean().mean() / 10 * 100)

    dept_metrics.append({
        'Departamento': dept,
        'Total': len(dept_df),
        'Performance': perf_media,
        'Engajamento': eng_medio,
        'Em Risco': em_risco,
        '% Risco': em_risco / len(dept_df) * 100,
        'Fit Cultural': fit_cultural_dept
    })

df_dept = pd.DataFrame(dept_metrics)

# Gráfico de performance por departamento
fig_dept = px.scatter(
    df_dept,
    x='Performance',
    y='Engajamento',
    size='Total',
    color='% Risco',
    hover_name='Departamento',
    title="Performance vs Engajamento por Departamento",
    color_continuous_scale='RdYlGn_r',
    labels={
        'Performance': 'Performance Média (0-10)',
        'Engajamento': 'Engajamento Médio (0-10)',
        '% Risco': '% Funcionários em Risco'
    }
)

fig_dept.update_layout(height=500)
st.plotly_chart(fig_dept, use_container_width=True)

# Tabela detalhada
st.subheader("📋 Métricas Detalhadas por Departamento")
st.dataframe(
    df_dept.style.format({
        'Performance': '{:.1f}',
        'Engajamento': '{:.1f}',
        '% Risco': '{:.1f}%',
        'Fit Cultural': '{:.1f}%'
    }).background_gradient(subset=['% Risco'], cmap='RdYlGn_r')
    .background_gradient(subset=['Performance'], cmap='RdYlGn')
    .background_gradient(subset=['Engajamento'], cmap='RdYlGn'),
    use_container_width=True
)

# --- SEÇÃO 4: PIPELINE DE TALENTOS ---
st.header("🎯 Pipeline de Talentos e Fit Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top Performers por Cargo")

    # Identificar top performers
    top_performers = []
    for cargo in df_agentes['cargo'].unique():
        cargo_df = df_agentes[df_agentes['cargo'] == cargo]
        if len(cargo_df) > 0:
            # Score baseado em performance e engajamento
            cargo_df_scored = cargo_df.copy()
            cargo_df_scored['score'] = (
                cargo_df.apply(lambda x:
                               x.get('performance.avaliacoes_desempenho',
                                     [{}])[-1].get('nota', 7)
                               if isinstance(x.get('performance.avaliacoes_desempenho'), list) else 7, axis=1
                               ) * 0.6 +
                cargo_df['engajamento.enps_recente'] * 0.4
            )
            top_performer = cargo_df_scored.nlargest(1, 'score')
            if not top_performer.empty:
                top_performers.append({
                    'cargo': cargo,
                    'nome': top_performer.iloc[0]['nome'],
                    'score': top_performer.iloc[0]['score']
                })

    top_df = pd.DataFrame(top_performers).sort_values('score', ascending=False)

    for _, row in top_df.head(5).iterrows():
        st.metric(
            f"🥇 {row['cargo']}",
            row['nome'],
            f"{row['score']:.1f} pts"
        )

with col2:
    st.subheader("📊 Distribuição de Fit Cultural")

    # Calcular fit cultural para todos
    big_five_cols = [
        'perfil_big_five.abertura_a_experiencia',
        'perfil_big_five.conscienciosidade',
        'perfil_big_five.extroversao',
        'perfil_big_five.amabilidade',
        'perfil_big_five.neuroticismo'
    ]

    fits_culturais = (df_agentes[big_five_cols].mean(axis=1) / 10 * 100)

    fig_hist = px.histogram(
        x=fits_culturais,
        nbins=20,
        title="Distribuição de Fit Cultural",
        labels={'x': 'Fit Cultural (%)', 'y': 'Número de Funcionários'},
        color_discrete_sequence=['#1f77b4']
    )

    fig_hist.add_vline(x=fits_culturais.mean(), line_dash="dash", line_color="red",
                       annotation_text=f"Média: {fits_culturais.mean():.1f}%")

    st.plotly_chart(fig_hist, use_container_width=True)

# --- SEÇÃO 5: RECOMENDAÇÕES ESTRATÉGICAS ---
st.header("💡 Recomendações Estratégicas")

recomendacoes = []

# Análise automática e geração de recomendações
# Mais de 15% em risco
if metricas['funcionarios_risco'] > len(df_agentes) * 0.15:
    recomendacoes.append({
        'prioridade': 'ALTA',
        'categoria': 'Retenção',
        'titulo': 'Implementar programa emergencial de retenção',
        'descricao': f"Com {metricas['funcionarios_risco']} funcionários em risco alto, é crítico implementar ações imediatas.",
        'roi_estimado': '+12% ROI',
        'prazo': '30 dias'
    })

if metricas['fit_cultural'] < 90:
    recomendacoes.append({
        'prioridade': 'MÉDIA',
        'categoria': 'Cultura',
        'titulo': 'Otimizar processo de contratação cultural',
        'descricao': 'Fit cultural médio pode ser melhorado com ajustes no processo seletivo.',
        'roi_estimado': '+8% ROI',
        'prazo': '60 dias'
    })

if df_dept['% Risco'].max() > 20:
    dept_problema = df_dept.loc[df_dept['% Risco'].idxmax(), 'Departamento']
    recomendacoes.append({
        'prioridade': 'ALTA',
        'categoria': 'Departamental',
        'titulo': f'Intervenção focada em {dept_problema}',
        'descricao': f'Departamento {dept_problema} apresenta alto risco de turnover.',
        'roi_estimado': '+15% ROI',
        'prazo': '45 dias'
    })

if not recomendacoes:
    recomendacoes.append({
        'prioridade': 'BAIXA',
        'categoria': 'Manutenção',
        'titulo': 'Manter estratégia atual com ajustes finos',
        'descricao': 'Métricas estão estáveis. Foco em otimizações incrementais.',
        'roi_estimado': '+3% ROI',
        'prazo': '90 dias'
    })

for i, rec in enumerate(recomendacoes):
    with st.expander(f"🎯 {rec['titulo']} - Prioridade {rec['prioridade']}", expanded=i == 0):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(f"**Categoria:** {rec['categoria']}")
            st.write(f"**Prazo:** {rec['prazo']}")

        with col2:
            st.write(f"**ROI Estimado:** {rec['roi_estimado']}")
            cor_prioridade = 'red' if rec['prioridade'] == 'ALTA' else 'orange' if rec['prioridade'] == 'MÉDIA' else 'green'
            st.markdown(
                f"**Prioridade:** <span style='color: {cor_prioridade}'>{rec['prioridade']}</span>", unsafe_allow_html=True)

        with col3:
            if st.button(f"✅ Implementar", key=f"impl_{i}"):
                st.success("✅ Recomendação adicionada ao plano de ação!")

        st.write(f"**Descrição:** {rec['descricao']}")

# --- SEÇÃO 6: TENDÊNCIAS E PROJEÇÕES ---
st.header("📈 Tendências e Projeções")

# Simular dados históricos dos últimos 12 meses
dates = pd.date_range(start='2024-02-01', end='2025-01-01', freq='M')
np.random.seed(42)  # Para resultados consistentes

# ROI histórico
roi_historico = np.random.normal(850, 30, len(dates))
roi_historico = np.cumsum(np.random.normal(0, 10, len(dates))) + 820

# Turnover histórico
turnover_historico = np.random.normal(15, 3, len(dates))
turnover_historico = np.abs(np.cumsum(np.random.normal(0, 1, len(dates))) + 18)

# Engajamento histórico
engajamento_historico = np.random.normal(7, 0.5, len(dates))
engajamento_historico = np.cumsum(np.random.normal(0, 0.2, len(dates))) + 6.8

fig_trends = go.Figure()

# ROI
fig_trends.add_trace(go.Scatter(
    x=dates, y=roi_historico,
    mode='lines+markers',
    name='ROI (%)',
    line=dict(color='green', width=3),
    yaxis='y'
))

# Turnover (eixo secundário)
fig_trends.add_trace(go.Scatter(
    x=dates, y=turnover_historico,
    mode='lines+markers',
    name='Taxa Turnover (%)',
    line=dict(color='red', width=2),
    yaxis='y2'
))

# Configurar eixos
fig_trends.update_layout(
    title="Evolução de Métricas Chave (12 meses)",
    xaxis_title="Período",
    yaxis=dict(
        title="ROI (%)",
        side="left",
        color="green"
    ),
    yaxis2=dict(
        title="Taxa de Turnover (%)",
        side="right",
        overlaying="y",
        color="red"
    ),
    legend=dict(x=0.02, y=0.98),
    height=400
)

st.plotly_chart(fig_trends, use_container_width=True)

# --- SEÇÃO 7: ACTIONS ITEMS ---
st.header("📋 Action Items Prioritários")

action_items = [
    {
        'id': 1,
        'titulo': 'Reunião com gestores de alto risco',
        'responsavel': 'Head de RH',
        'prazo': '2 dias',
        'status': 'Pendente',
        'prioridade': 'Alta'
    },
    {
        'id': 2,
        'titulo': 'Implementar survey cultural detalhado',
        'responsavel': 'Equipe de People Analytics',
        'prazo': '1 semana',
        'status': 'Em progresso',
        'prioridade': 'Média'
    },
    {
        'id': 3,
        'titulo': 'Revisar política de benefícios',
        'responsavel': 'CFO + Head RH',
        'prazo': '2 semanas',
        'status': 'Não iniciado',
        'prioridade': 'Baixa'
    }
]

for item in action_items:
    with st.expander(f"📌 {item['titulo']} - {item['prioridade']} prioridade"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.write(f"**Responsável:** {item['responsavel']}")
        with col2:
            st.write(f"**Prazo:** {item['prazo']}")
        with col3:
            cor_status = 'orange' if item['status'] == 'Em progresso' else 'red' if item['status'] == 'Pendente' else 'gray'
            st.markdown(
                f"**Status:** <span style='color: {cor_status}'>{item['status']}</span>", unsafe_allow_html=True)
        with col4:
            if st.button(f"✅ Concluir", key=f"action_{item['id']}"):
                st.success("✅ Item marcado como concluído!")

# --- Footer ---
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📊 Última atualização:** Hoje, 09:15")

with col2:
    st.markdown("**🔄 Próxima sync:** Em 4 horas")

with col3:
    st.markdown("**📞 Suporte:** humaniq-support@empresa.com")

st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em; margin-top: 20px;'>
🎛️ <strong>Executive Dashboard</strong> - HumaniQ AI<br>
Inteligência estratégica para tomada de decisões baseada em dados de fatores humanos
</div>
""", unsafe_allow_html=True)
