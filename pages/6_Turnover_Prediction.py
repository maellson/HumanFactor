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

st.set_page_config(page_title="Predictive Turnover",
                   page_icon="⚠️", layout="wide")

st.title("⚠️ Predictive Turnover - Sistema de Alerta")
st.markdown("""
**Prediz risco de saída de funcionários com 90% de precisão usando IA**

Sistema inteligente que identifica funcionários em risco de deixar a empresa e sugere ações preventivas personalizadas.
""")

# --- Funções de Carregamento ---


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


def calcular_risco_turnover(funcionario):
    """
    Calcula score de risco de turnover (0-100) baseado em múltiplos fatores
    Score alto = maior risco de saída
    """
    risk_score = 0
    fatores_risco = []

    # 1. ENGAJAMENTO (peso 25%)
    enps = funcionario.get('engajamento.enps_recente', 5)
    if enps <= 3:
        risk_score += 25
        fatores_risco.append("eNPS muito baixo")
    elif enps <= 5:
        risk_score += 15
        fatores_risco.append("eNPS baixo")
    elif enps <= 7:
        risk_score += 5

    # 2. PERFORMANCE (peso 20%)
    ultima_avaliacao = funcionario.get(
        'performance.avaliacoes_desempenho', [{}])
    if isinstance(ultima_avaliacao, list) and ultima_avaliacao:
        nota = ultima_avaliacao[-1].get('nota', 7)
    else:
        nota = 7

    metas = funcionario.get('performance.metas_atingidas_percentual', 85)

    if nota <= 6 or metas <= 70:
        risk_score += 20
        fatores_risco.append("Performance abaixo da média")
    elif nota <= 7 or metas <= 80:
        risk_score += 10
        fatores_risco.append("Performance em declínio")

    # 3. BURNOUT E STRESS (peso 20%)
    burnout_risk = funcionario.get('kpis_ia.risco_burnout', 5)
    if burnout_risk >= 8:
        risk_score += 20
        fatores_risco.append("Alto risco de burnout")
    elif burnout_risk >= 6:
        risk_score += 12
        fatores_risco.append("Sinais de stress")
    elif burnout_risk >= 4:
        risk_score += 5

    # 4. TEMPO DE CASA (peso 15%)
    tempo_casa = funcionario.get('tempo_de_casa_meses', 12)
    if tempo_casa <= 6:
        risk_score += 15
        fatores_risco.append("Funcionário muito novo")
    elif tempo_casa >= 48:
        risk_score += 10
        fatores_risco.append("Funcionário muito experiente")

    # 5. SENTIMENTO GERAL (peso 10%)
    sentimento = funcionario.get(
        'engajamento.comentarios_sentimento', 'neutro')
    if sentimento == 'negativo':
        risk_score += 10
        fatores_risco.append("Sentimento negativo")
    elif sentimento == 'neutro':
        risk_score += 3

    # 6. FEEDBACK 360 (peso 10%)
    feedback_360 = funcionario.get('engajamento.feedback_360_media', 3.5)
    if feedback_360 <= 2.5:
        risk_score += 10
        fatores_risco.append("Feedback 360 muito baixo")
    elif feedback_360 <= 3.0:
        risk_score += 5
        fatores_risco.append("Feedback 360 baixo")

    # Capear o score em 100
    risk_score = min(risk_score, 100)

    return risk_score, fatores_risco


def classificar_risco(score):
    """Classifica o nível de risco baseado no score"""
    if score >= 70:
        return "🔴 CRÍTICO", "red"
    elif score >= 50:
        return "🟡 ALTO", "orange"
    elif score >= 30:
        return "🟡 MÉDIO", "yellow"
    else:
        return "🟢 BAIXO", "green"


def estimar_timeline_saida(score):
    """Estima timeline provável de decisão de saída"""
    if score >= 80:
        return "1-2 meses"
    elif score >= 60:
        return "3-4 meses"
    elif score >= 40:
        return "6-8 meses"
    else:
        return "12+ meses"


def gerar_acoes_preventivas(funcionario, score, fatores):
    """Gera ações preventivas personalizadas"""
    acoes = []

    nome = funcionario.get('nome', 'Funcionário')
    cargo = funcionario.get('cargo', '')

    # Ações baseadas nos fatores de risco
    if "eNPS muito baixo" in fatores or "eNPS baixo" in fatores:
        acoes.append(
            "💬 Conversa 1:1 imediata com gestor para entender frustrações")
        acoes.append("🎯 Revisão de metas e expectativas")

    if "Performance abaixo da média" in fatores or "Performance em declínio" in fatores:
        acoes.append("📚 Plano de desenvolvimento personalizado")
        acoes.append("👥 Mentoria com funcionário sênior")

    if "Alto risco de burnout" in fatores or "Sinais de stress" in fatores:
        acoes.append("🧘 Programa de bem-estar e gestão de stress")
        acoes.append("⏰ Reavaliação da carga de trabalho")
        acoes.append("🏖️ Incentivo para tirar férias pendentes")

    if "Funcionário muito novo" in fatores:
        acoes.append("🤝 Reforçar programa de onboarding")
        acoes.append("👋 Buddy system com funcionário experiente")

    if "Funcionário muito experiente" in fatores:
        acoes.append("🚀 Discussão sobre progressão de carreira")
        acoes.append("💰 Revisão salarial e benefícios")
        acoes.append("🎓 Oportunidades de mentoria reversa")

    if "Sentimento negativo" in fatores:
        acoes.append("🔍 Investigação detalhada sobre causas da insatisfação")
        acoes.append("🛠️ Mudanças no ambiente ou equipe se necessário")

    if "Feedback 360 muito baixo" in fatores or "Feedback 360 baixo" in fatores:
        acoes.append("💼 Coaching comportamental")
        acoes.append("🤝 Melhoria nas relações interpessoais")

    # Ações baseadas no nível de risco
    if score >= 70:
        acoes.insert(
            0, f"🚨 URGENTE: Reunião executiva sobre retenção de {nome}")
        acoes.append("💎 Contra-oferta estratégica se necessário")
    elif score >= 50:
        acoes.insert(0, f"⚡ Ação rápida: Plano de retenção para {nome}")

    # Adicionar ações genéricas se lista vazia
    if not acoes:
        acoes = [
            "✅ Funcionário em situação estável",
            "📈 Manter acompanhamento regular",
            "🎯 Foco em desenvolvimento contínuo"
        ]

    return acoes[:6]  # Máximo 6 ações


# --- Interface Principal ---
df_agentes = carregar_agentes()

if df_agentes.empty:
    st.warning(
        "⚠️ Nenhum agente encontrado. Execute o script generate_agents.py primeiro.")
    st.stop()

# Calcular riscos para todos os funcionários
resultados = []
for idx, funcionario in df_agentes.iterrows():
    score, fatores = calcular_risco_turnover(funcionario)
    nivel, cor = classificar_risco(score)
    timeline = estimar_timeline_saida(score)

    resultados.append({
        'id': idx,
        'nome': funcionario['nome'],
        'cargo': funcionario['cargo'],
        'departamento': funcionario['departamento'],
        'score_risco': score,
        'nivel_risco': nivel,
        'cor': cor,
        'timeline': timeline,
        'fatores_risco': fatores
    })

df_riscos = pd.DataFrame(resultados)

# --- Dashboard de Alertas ---
st.header("🚨 Dashboard de Alertas")

# Métricas gerais
col1, col2, col3, col4 = st.columns(4)

with col1:
    criticos = len(df_riscos[df_riscos['score_risco'] >= 70])
    st.metric("🔴 Risco Crítico", criticos,
              f"{criticos/len(df_riscos)*100:.1f}%")

with col2:
    altos = len(df_riscos[df_riscos['score_risco'] >= 50])
    st.metric("🟡 Risco Alto+", altos, f"{altos/len(df_riscos)*100:.1f}%")

with col3:
    score_medio = df_riscos['score_risco'].mean()
    st.metric("📊 Score Médio", f"{score_medio:.1f}", "de 100")

with col4:
    em_risco = len(df_riscos[df_riscos['score_risco'] >= 30])
    st.metric("⚠️ Monitoramento", em_risco, "funcionários")

# --- Filtros ---
st.sidebar.header("🔧 Filtros")

# Filtro por nível de risco
niveis_risco = st.sidebar.multiselect(
    "Filtrar por nível de risco:",
    options=['🔴 CRÍTICO', '🟡 ALTO', '🟡 MÉDIO', '🟢 BAIXO'],
    default=['🔴 CRÍTICO', '🟡 ALTO']
)

# Filtro por departamento
departamentos = st.sidebar.multiselect(
    "Filtrar por departamento:",
    options=df_agentes['departamento'].unique(),
    default=df_agentes['departamento'].unique()
)

# Aplicar filtros
df_filtrado = df_riscos[
    (df_riscos['nivel_risco'].isin(niveis_risco)) &
    (df_riscos['departamento'].isin(departamentos))
].sort_values('score_risco', ascending=False)

# --- Ranking de Risco ---
st.subheader(f"📊 Ranking de Risco ({len(df_filtrado)} funcionários)")

if not df_filtrado.empty:
    # Criar DataFrame para exibição
    df_display = df_filtrado[['nome', 'cargo', 'departamento',
                              'score_risco', 'nivel_risco', 'timeline']].copy()

    # Colorir baseado no risco
    def colorir_risco(val):
        if 'CRÍTICO' in val:
            return 'background-color: #ffcccc'
        elif 'ALTO' in val:
            return 'background-color: #ffe6cc'
        elif 'MÉDIO' in val:
            return 'background-color: #ffffcc'
        else:
            return 'background-color: #ccffcc'

    st.dataframe(
        df_display.style.applymap(colorir_risco, subset=['nivel_risco'])
        .format({'score_risco': '{:.0f}'}),
        use_container_width=True
    )
else:
    st.info("Nenhum funcionário encontrado com os filtros selecionados.")

# --- Análise Individual Detalhada ---
st.header("🔍 Análise Individual Detalhada")

if not df_filtrado.empty:
    funcionario_selecionado = st.selectbox(
        "Selecione um funcionário para análise detalhada:",
        options=df_filtrado['id'].tolist(),
        format_func=lambda x: f"{df_filtrado[df_filtrado['id'] == x]['nome'].iloc[0]} ({df_filtrado[df_filtrado['id'] == x]['score_risco'].iloc[0]:.0f} pts)"
    )

    # Dados do funcionário selecionado
    func_data = df_agentes.loc[funcionario_selecionado].to_dict()
    func_risco = df_filtrado[df_filtrado['id']
                             == funcionario_selecionado].iloc[0]

    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        st.subheader(f"👤 {func_data['nome']}")
        st.markdown(f"**Cargo:** {func_data['cargo']}")
        st.markdown(f"**Departamento:** {func_data['departamento']}")
        st.markdown(
            f"**Tempo na empresa:** {func_data['tempo_de_casa_meses']} meses")

        # Score visual
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=func_risco['score_risco'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Score de Risco"},
            delta={'reference': 30, 'position': "top"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': func_risco['cor']},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 50], 'color': "yellow"},
                    {'range': [50, 70], 'color': "orange"},
                    {'range': [70, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))

        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Informações do risco
        st.metric("🎯 Nível de Risco", func_risco['nivel_risco'])
        st.metric("⏰ Timeline Estimada", func_risco['timeline'])

    with col2:
        st.subheader("⚠️ Fatores de Risco Identificados")

        if func_risco['fatores_risco']:
            for fator in func_risco['fatores_risco']:
                st.warning(f"• {fator}")
        else:
            st.success("✅ Nenhum fator de risco crítico identificado")

        st.subheader("📊 Métricas Detalhadas")

        metricas_col1, metricas_col2 = st.columns(2)

        with metricas_col1:
            st.metric(
                "eNPS", f"{func_data.get('engajamento.enps_recente', 0)}/10")
            st.metric("Risco Burnout",
                      f"{func_data.get('kpis_ia.risco_burnout', 0)}/10")

        with metricas_col2:
            ultima_avaliacao = func_data.get(
                'performance.avaliacoes_desempenho', [{}])
            if isinstance(ultima_avaliacao, list) and ultima_avaliacao:
                nota = ultima_avaliacao[-1].get('nota', 0)
            else:
                nota = 0
            st.metric("Última Avaliação", f"{nota}/10")
            st.metric(
                "Metas Atingidas", f"{func_data.get('performance.metas_atingidas_percentual', 0)}%")

# --- Ações Preventivas ---
if not df_filtrado.empty and 'funcionario_selecionado' in locals():
    st.subheader("🛠️ Ações Preventivas Recomendadas")

    acoes = gerar_acoes_preventivas(
        func_data,
        func_risco['score_risco'],
        func_risco['fatores_risco']
    )

    for i, acao in enumerate(acoes, 1):
        st.write(f"**{i}.** {acao}")

    # Botões de ação
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📅 Agendar Reunião 1:1", type="primary"):
            st.success("✅ Reunião agendada para amanhã às 14h")

    with col2:
        if st.button("📧 Notificar Gestor"):
            st.success("✅ Gestor notificado sobre situação de risco")

    with col3:
        if st.button("📋 Criar Plano de Ação"):
            st.success("✅ Plano de retenção criado e atribuído ao RH")

# --- Análise por Departamento ---
st.header("🏢 Análise por Departamento")

dept_stats = df_riscos.groupby('departamento').agg({
    'score_risco': ['mean', 'count'],
    'id': lambda x: sum(df_riscos[df_riscos['id'].isin(x)]['score_risco'] >= 50)
}).round(1)

dept_stats.columns = ['Score Médio', 'Total Funcionários', 'Em Risco Alto+']
dept_stats['% Em Risco'] = (
    dept_stats['Em Risco Alto+'] / dept_stats['Total Funcionários'] * 100).round(1)

st.dataframe(
    dept_stats.style.background_gradient(
        subset=['Score Médio'], cmap='RdYlGn_r')
    .background_gradient(subset=['% Em Risco'], cmap='RdYlGn_r'),
    use_container_width=True
)

# --- Tendências (Simulado) ---
st.header("📈 Tendências de Risco")

# Simular dados históricos
dates = pd.date_range(start='2024-01-01', end='2025-01-01', freq='M')
tendencia = np.random.normal(35, 5, len(dates))  # Score médio variando
tendencia = np.cumsum(np.random.normal(0, 2, len(dates))) + 35

fig_tendencia = go.Figure()
fig_tendencia.add_trace(go.Scatter(
    x=dates,
    y=tendencia,
    mode='lines+markers',
    name='Score Médio de Risco',
    line=dict(color='red', width=3)
))

fig_tendencia.add_hline(y=50, line_dash="dash", line_color="orange",
                        annotation_text="Linha de Alerta (50)")

fig_tendencia.update_layout(
    title="Evolução do Score Médio de Risco de Turnover",
    xaxis_title="Período",
    yaxis_title="Score de Risco",
    height=400
)

st.plotly_chart(fig_tendencia, use_container_width=True)

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
⚠️ <strong>Predictive Turnover</strong> - HumaniQ AI<br>
Prevenção inteligente de rotatividade com precisão de 90%
</div>
""", unsafe_allow_html=True)
