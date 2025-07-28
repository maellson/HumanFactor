import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

st.set_page_config(page_title="Agent REPLAY", page_icon="🎯", layout="wide")

st.title("🎯 Agent REPLAY - Funcionário Modelo")
st.markdown("""
**Identifica funcionários modelo por cargo e extrai padrões de excelência para replicação**

O Agent REPLAY usa IA para mapear top performers e descobrir o "DNA do sucesso" que pode ser replicado em outros funcionários.
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


def calcular_score_performance(row):
    """Calcula score de performance baseado em múltiplos fatores"""
    # Última avaliação (peso 30%)
    ultima_avaliacao = row.get('performance.avaliacoes_desempenho', [{}])
    if ultima_avaliacao:
        nota_avaliacao = ultima_avaliacao[-1].get(
            'nota', 5) if isinstance(ultima_avaliacao, list) else 5
    else:
        nota_avaliacao = 5

    # Metas atingidas (peso 25%)
    metas = row.get('performance.metas_atingidas_percentual', 75) / 100

    # Engajamento (peso 20%)
    enps = row.get('engajamento.enps_recente', 5) / 10
    feedback_360 = row.get('engajamento.feedback_360_media', 3) / 5

    # Baixo risco burnout (peso 15%)
    risco_burnout = 1 - (row.get('kpis_ia.risco_burnout', 5) / 10)

    # Tempo de casa (peso 10% - estabilidade)
    tempo_casa = min(row.get('tempo_de_casa_meses', 12) /
                     36, 1)  # Normalizado para 3 anos

    score = (
        (nota_avaliacao / 10) * 0.30 +
        metas * 0.25 +
        enps * 0.15 +
        (feedback_360 / 5) * 0.05 +
        risco_burnout * 0.15 +
        tempo_casa * 0.10
    ) * 100

    return round(score, 2)


def identificar_funcionarios_modelo(df, cargo_filtro=None, top_n=3):
    """Identifica top performers por cargo"""
    if cargo_filtro:
        df_filtrado = df[df['cargo'] == cargo_filtro].copy()
    else:
        df_filtrado = df.copy()

    if df_filtrado.empty:
        return df_filtrado

    # Calcular score de performance
    df_filtrado['score_performance'] = df_filtrado.apply(
        calcular_score_performance, axis=1)

    # Ordenar por performance
    df_top = df_filtrado.nlargest(top_n, 'score_performance')

    return df_top


def extrair_dna_sucesso(df_top_performers):
    """Extrai padrões comportamentais dos top performers"""
    if df_top_performers.empty:
        return {}

    # Perfil Big Five médio
    big_five_cols = [
        'perfil_big_five.abertura_a_experiencia',
        'perfil_big_five.conscienciosidade',
        'perfil_big_five.extroversao',
        'perfil_big_five.amabilidade',
        'perfil_big_five.neuroticismo'
    ]

    perfil_medio = df_top_performers[big_five_cols].mean()

    # Competências mais comuns
    todas_competencias = []
    for competencias in df_top_performers['competencias']:
        if isinstance(competencias, list):
            todas_competencias.extend(competencias)

    from collections import Counter
    competencias_comuns = Counter(todas_competencias).most_common(5)

    # Características de performance
    performance_stats = {
        'avaliacao_media': df_top_performers.apply(
            lambda x: x.get('performance.avaliacoes_desempenho', [
                            {}])[-1].get('nota', 5)
            if isinstance(x.get('performance.avaliacoes_desempenho'), list) else 5, axis=1
        ).mean(),
        'metas_media': df_top_performers['performance.metas_atingidas_percentual'].mean(),
        'enps_medio': df_top_performers['engajamento.enps_recente'].mean(),
        'feedback_360_medio': df_top_performers['engajamento.feedback_360_media'].mean(),
        'risco_burnout_medio': df_top_performers['kpis_ia.risco_burnout'].mean()
    }

    return {
        'perfil_big_five': perfil_medio.to_dict(),
        'competencias_chave': competencias_comuns,
        'performance_stats': performance_stats,
        'tamanho_amostra': len(df_top_performers)
    }


def comparar_com_dna(funcionario, dna_sucesso):
    """Compara um funcionário com o DNA de sucesso"""
    if not dna_sucesso:
        return {}

    # Comparação Big Five
    gaps_big_five = {}
    for trait, valor_ideal in dna_sucesso['perfil_big_five'].items():
        valor_atual = funcionario.get(trait, 5)
        gap = valor_ideal - valor_atual
        gaps_big_five[trait] = {
            'atual': valor_atual,
            'ideal': round(valor_ideal, 1),
            'gap': round(gap, 1),
            'status': 'Acima' if gap < -0.5 else 'Abaixo' if gap > 0.5 else 'Adequado'
        }

    # Comparação competências
    competencias_funcionario = set(funcionario.get('competencias', []))
    competencias_ideais = set([comp[0]
                              for comp in dna_sucesso['competencias_chave']])

    competencias_gap = {
        'tem': list(competencias_funcionario.intersection(competencias_ideais)),
        'falta': list(competencias_ideais - competencias_funcionario),
        'extras': list(competencias_funcionario - competencias_ideais)
    }

    return {
        'gaps_big_five': gaps_big_five,
        'competencias_gap': competencias_gap
    }


# --- Interface Principal ---
df_agentes = carregar_agentes()

if df_agentes.empty:
    st.warning(
        "⚠️ Nenhum agente encontrado. Execute o script generate_agents.py primeiro.")
    st.stop()

# Sidebar - Configurações
st.sidebar.header("🔧 Configurações REPLAY")

# Filtro por cargo
cargos_disponiveis = ['Todos'] + sorted(df_agentes['cargo'].unique().tolist())
cargo_selecionado = st.sidebar.selectbox(
    "🎯 Filtrar por cargo:",
    options=cargos_disponiveis
)

cargo_filtro = None if cargo_selecionado == 'Todos' else cargo_selecionado

# Número de top performers
top_n = st.sidebar.slider("📊 Número de top performers:", 1, 10, 3)

# --- Análise Principal ---
st.header("🏆 Identificação de Top Performers")

# Identificar funcionários modelo
df_top = identificar_funcionarios_modelo(df_agentes, cargo_filtro, top_n)

if df_top.empty:
    st.warning(
        f"Nenhum funcionário encontrado para o cargo: {cargo_selecionado}")
    st.stop()

# Exibir ranking
st.subheader(f"🥇 Top {len(df_top)} Performers - {cargo_selecionado}")

# Criar DataFrame para exibição
df_display = df_top[['nome', 'cargo',
                     'departamento', 'score_performance']].copy()
df_display['score_performance'] = df_display['score_performance'].round(1)

st.dataframe(
    df_display.style.format({'score_performance': '{:.1f}%'})
    .background_gradient(subset=['score_performance'], cmap='RdYlGn'),
    use_container_width=True
)

# --- DNA do Sucesso ---
st.header("🧬 DNA do Sucesso")

dna = extrair_dna_sucesso(df_top)

if dna:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎭 Perfil Comportamental Ideal")

        # Gráfico radar do perfil ideal
        fig_radar = go.Figure()

        categorias = list(dna['perfil_big_five'].keys())
        valores = list(dna['perfil_big_five'].values())
        categorias_display = [cat.replace('perfil_big_five.', '').replace(
            '_', ' ').title() for cat in categorias]

        fig_radar.add_trace(go.Scatterpolar(
            r=valores,
            theta=categorias_display,
            fill='toself',
            name='Perfil Ideal',
            fillcolor='rgba(0, 100, 200, 0.3)',
            line=dict(color='rgb(0, 100, 200)')
        ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10])
            ),
            title="Perfil Big Five dos Top Performers"
        )

        st.plotly_chart(fig_radar, use_container_width=True)

    with col2:
        st.subheader("🛠️ Competências Chave")

        # Top competências
        for i, (comp, freq) in enumerate(dna['competencias_chave']):
            st.metric(
                label=f"#{i+1} {comp}",
                value=f"{freq}/{dna['tamanho_amostra']} pessoas",
                delta=f"{round(freq/dna['tamanho_amostra']*100)}% dos top performers"
            )

        st.subheader("📈 Estatísticas de Performance")
        stats = dna['performance_stats']

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Avaliação Média", f"{stats['avaliacao_media']:.1f}/10")
            st.metric("Metas Atingidas", f"{stats['metas_media']:.1f}%")
        with col_b:
            st.metric("eNPS Médio", f"{stats['enps_medio']:.1f}/10")
            st.metric("Risco Burnout",
                      f"{stats['risco_burnout_medio']:.1f}/10")

# --- Análise de Gap Individual ---
st.header("🎯 Análise de Gap Individual")

funcionario_selecionado = st.selectbox(
    "👤 Selecione um funcionário para análise:",
    options=df_agentes.index.tolist(),
    format_func=lambda x: f"{df_agentes.loc[x, 'nome']} ({df_agentes.loc[x, 'cargo']})"
)

funcionario_data = df_agentes.loc[funcionario_selecionado].to_dict()
gaps = comparar_com_dna(funcionario_data, dna)

if gaps:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎭 Gaps de Personalidade")

        gaps_df = pd.DataFrame.from_dict(gaps['gaps_big_five'], orient='index')

        # Gráfico de comparação
        fig_gap = go.Figure()

        categorias = [cat.replace('perfil_big_five.', '').replace('_', ' ').title()
                      for cat in gaps_df.index]

        fig_gap.add_trace(go.Scatterpolar(
            r=gaps_df['atual'].values,
            theta=categorias,
            fill='toself',
            name=funcionario_data['nome'],
            opacity=0.7
        ))

        fig_gap.add_trace(go.Scatterpolar(
            r=gaps_df['ideal'].values,
            theta=categorias,
            fill='toself',
            name='Perfil Ideal',
            opacity=0.5
        ))

        fig_gap.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            title="Comparação com Perfil Ideal"
        )

        st.plotly_chart(fig_gap, use_container_width=True)

        # Tabela de gaps
        st.dataframe(
            gaps_df.style.format(
                {'atual': '{:.1f}', 'ideal': '{:.1f}', 'gap': '{:.1f}'})
            .applymap(lambda x: 'background-color: #ffcccc' if x == 'Abaixo'
                      else 'background-color: #ccffcc' if x == 'Adequado'
                      else 'background-color: #ffffcc', subset=['status'])
        )

    with col2:
        st.subheader("🛠️ Gaps de Competências")

        comp_gaps = gaps['competencias_gap']

        if comp_gaps['tem']:
            st.success("✅ **Competências Alinhadas:**")
            for comp in comp_gaps['tem']:
                st.write(f"• {comp}")

        if comp_gaps['falta']:
            st.warning("⚠️ **Competências a Desenvolver:**")
            for comp in comp_gaps['falta']:
                st.write(f"• {comp}")

        if comp_gaps['extras']:
            st.info("ℹ️ **Competências Extras:**")
            for comp in comp_gaps['extras']:
                st.write(f"• {comp}")

        # Score atual do funcionário
        score_atual = calcular_score_performance(funcionario_data)
        st.metric("📊 Score Performance Atual", f"{score_atual:.1f}%")

        # Recomendações
        st.subheader("💡 Recomendações")

        recomendacoes = []

        # Baseado nos gaps de personalidade
        for trait, gap_info in gaps['gaps_big_five'].items():
            if gap_info['status'] == 'Abaixo':
                trait_name = trait.replace(
                    'perfil_big_five.', '').replace('_', ' ')
                recomendacoes.append(
                    f"Desenvolver {trait_name} através de coaching específico")

        # Baseado nas competências
        if comp_gaps['falta']:
            recomendacoes.append(
                f"Priorizar treinamento em: {', '.join(comp_gaps['falta'][:2])}")

        if not recomendacoes:
            recomendacoes.append(
                "Perfil já está bem alinhado com top performers!")

        for i, rec in enumerate(recomendacoes, 1):
            st.write(f"{i}. {rec}")

# --- Insights Organizacionais ---
st.header("🏢 Insights Organizacionais")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Top Performers Identificados",
        len(df_top),
        f"de {len(df_agentes)} funcionários"
    )

with col2:
    score_medio_geral = df_agentes.apply(
        calcular_score_performance, axis=1).mean()
    score_medio_top = df_top['score_performance'].mean()
    st.metric(
        "Score Médio Top vs Geral",
        f"{score_medio_top:.1f}%",
        f"+{score_medio_top - score_medio_geral:.1f}% vs média"
    )

with col3:
    # Calcular potencial de melhoria
    funcionarios_com_potencial = len(df_agentes[
        df_agentes.apply(calcular_score_performance,
                         axis=1) < score_medio_top - 10
    ])
    st.metric(
        "Funcionários com Potencial",
        funcionarios_com_potencial,
        "para desenvolvimento direcionado"
    )

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
🎯 <strong>Agent REPLAY</strong> - HumaniQ AI<br>
Identifica padrões de excelência e acelera o desenvolvimento organizacional
</div>
""", unsafe_allow_html=True)
