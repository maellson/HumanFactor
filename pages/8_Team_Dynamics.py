import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from itertools import combinations
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Team Dynamics Optimizer",
                   page_icon="🔥", layout="wide")

st.title("🔥 Team Dynamics Optimizer")
st.markdown("""
**Otimiza formação e dinâmica de equipes para máxima produtividade**

Analisa compatibilidades comportamentais, identifica conflitos potenciais e sugere reorganizações estratégicas para formar equipes de alta performance.
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


def calcular_compatibilidade(pessoa1, pessoa2):
    """Calcula compatibilidade entre duas pessoas baseada em Big Five"""
    # Extrair perfis Big Five
    perfil1 = np.array([
        pessoa1.get('perfil_big_five.abertura_a_experiencia', 5),
        pessoa1.get('perfil_big_five.conscienciosidade', 5),
        pessoa1.get('perfil_big_five.extroversao', 5),
        pessoa1.get('perfil_big_five.amabilidade', 5),
        pessoa1.get('perfil_big_five.neuroticismo', 5)
    ])

    perfil2 = np.array([
        pessoa2.get('perfil_big_five.abertura_a_experiencia', 5),
        pessoa2.get('perfil_big_five.conscienciosidade', 5),
        pessoa2.get('perfil_big_five.extroversao', 5),
        pessoa2.get('perfil_big_five.amabilidade', 5),
        pessoa2.get('perfil_big_five.neuroticismo', 5)
    ])

    # Lógica de compatibilidade baseada em pesquisa psicológica
    # Alguns traços se complementam, outros devem ser similares

    # Abertura: similar é melhor (criatividade alinhada)
    abertura_compat = 1 - abs(perfil1[0] - perfil2[0]) / 10

    # Conscienciosidade: similar é melhor (organização alinhada)
    conscienc_compat = 1 - abs(perfil1[1] - perfil2[1]) / 10

    # Extroversão: complementar pode ser bom (balance)
    extrov_compat = 1 - abs(abs(perfil1[2] - perfil2[2]) - 5) / 5

    # Amabilidade: similar é melhor (cooperação)
    amab_compat = 1 - abs(perfil1[3] - perfil2[3]) / 10

    # Neuroticismo: ambos baixos é ideal
    neuro_compat = 1 - (perfil1[4] + perfil2[4]) / 20

    # Score ponderado
    compatibilidade = (
        abertura_compat * 0.25 +
        conscienc_compat * 0.25 +
        extrov_compat * 0.15 +
        amab_compat * 0.25 +
        neuro_compat * 0.10
    ) * 100

    return round(compatibilidade, 1)


def detectar_conflitos_potenciais(pessoa1, pessoa2):
    """Detecta possíveis áreas de conflito entre duas pessoas"""
    conflitos = []

    p1_neuro = pessoa1.get('perfil_big_five.neuroticismo', 5)
    p2_neuro = pessoa2.get('perfil_big_five.neuroticismo', 5)

    p1_amab = pessoa1.get('perfil_big_five.amabilidade', 5)
    p2_amab = pessoa2.get('perfil_big_five.amabilidade', 5)

    p1_conscienc = pessoa1.get('perfil_big_five.conscienciosidade', 5)
    p2_conscienc = pessoa2.get('perfil_big_five.conscienciosidade', 5)

    # Alto neuroticismo + baixa amabilidade = conflito
    if (p1_neuro > 7 and p2_amab < 4) or (p2_neuro > 7 and p1_amab < 4):
        conflitos.append(
            "Risco de conflitos interpessoais (stress + baixa cooperação)")

    # Diferenças extremas em conscienciosidade
    if abs(p1_conscienc - p2_conscienc) > 6:
        conflitos.append(
            "Estilos de trabalho incompatíveis (organização vs flexibilidade)")

    # Ambos com alto neuroticismo
    if p1_neuro > 7 and p2_neuro > 7:
        conflitos.append(
            "Ambiente potencialmente estressante (ambos com alto neuroticismo)")

    # Ambos com baixa amabilidade
    if p1_amab < 4 and p2_amab < 4:
        conflitos.append(
            "Possível falta de cooperação (baixa amabilidade de ambos)")

    return conflitos


def analisar_dinamica_equipe(df_equipe):
    """Analisa a dinâmica geral de uma equipe"""
    if len(df_equipe) < 2:
        return {}

    # Calcular matriz de compatibilidade
    compatibilidades = []
    conflitos_totais = []

    for i, (idx1, pessoa1) in enumerate(df_equipe.iterrows()):
        for j, (idx2, pessoa2) in enumerate(df_equipe.iterrows()):
            if i < j:  # Evitar duplicatas
                compat = calcular_compatibilidade(pessoa1, pessoa2)
                conflitos = detectar_conflitos_potenciais(pessoa1, pessoa2)

                compatibilidades.append(compat)
                conflitos_totais.extend(conflitos)

    # Métricas da equipe
    compat_media = np.mean(compatibilidades) if compatibilidades else 0
    compat_min = np.min(compatibilidades) if compatibilidades else 0
    num_conflitos = len(conflitos_totais)

    # Diversidade cognitiva (variância dos perfis)
    big_five_cols = [
        'perfil_big_five.abertura_a_experiencia',
        'perfil_big_five.conscienciosidade',
        'perfil_big_five.extroversao',
        'perfil_big_five.amabilidade',
        'perfil_big_five.neuroticismo'
    ]

    diversidade = df_equipe[big_five_cols].var().mean()

    # Score geral da equipe
    score_equipe = (
        compat_media * 0.4 +
        max(0, 100 - num_conflitos * 5) * 0.3 +  # Penalizar conflitos
        min(diversidade * 10, 50) * 0.2 +  # Bonificar diversidade (até 50 pts)
        max(0, 100 - compat_min) * 0.1  # Penalizar links fracos
    )

    return {
        'compatibilidade_media': round(compat_media, 1),
        'compatibilidade_minima': round(compat_min, 1),
        'numero_conflitos': num_conflitos,
        'diversidade_cognitiva': round(diversidade, 2),
        'score_geral': round(score_equipe, 1),
        'conflitos_detalhados': conflitos_totais
    }


def sugerir_reorganizacao(df_funcionarios, tamanho_equipe=4):
    """Sugere formação ótima de equipe usando algoritmo genético simplificado"""
    if len(df_funcionarios) < tamanho_equipe:
        return None

    melhor_score = 0
    melhor_equipe = None

    # Testar múltiplas combinações (limitado para performance)
    max_combinacoes = min(
        1000, len(list(combinations(df_funcionarios.index, tamanho_equipe))))

    for i, combinacao in enumerate(combinations(df_funcionarios.index, tamanho_equipe)):
        if i >= max_combinacoes:
            break

        df_teste = df_funcionarios.loc[list(combinacao)]
        analise = analisar_dinamica_equipe(df_teste)

        if analise.get('score_geral', 0) > melhor_score:
            melhor_score = analise['score_geral']
            melhor_equipe = combinacao

    return melhor_equipe, melhor_score


def calcular_network_metrics(df_funcionarios):
    """Calcula métricas de rede social baseadas em compatibilidade"""
    G = nx.Graph()

    # Adicionar nós
    for idx, funcionario in df_funcionarios.iterrows():
        G.add_node(idx, nome=funcionario['nome'], cargo=funcionario['cargo'])

    # Adicionar arestas baseadas em compatibilidade
    for i, (idx1, pessoa1) in enumerate(df_funcionarios.iterrows()):
        for j, (idx2, pessoa2) in enumerate(df_funcionarios.iterrows()):
            if i < j:
                compat = calcular_compatibilidade(pessoa1, pessoa2)
                if compat > 70:  # Só conectar se alta compatibilidade
                    G.add_edge(idx1, idx2, weight=compat)

    # Calcular métricas
    if len(G.edges()) > 0:
        centralidade = nx.degree_centrality(G)
        clustering = nx.clustering(G)
        densidade = nx.density(G)
    else:
        centralidade = {node: 0 for node in G.nodes()}
        clustering = {node: 0 for node in G.nodes()}
        densidade = 0

    return G, centralidade, clustering, densidade


# --- Interface Principal ---
df_agentes = carregar_agentes()

if df_agentes.empty:
    st.warning(
        "⚠️ Nenhum agente encontrado. Execute o script generate_agents.py primeiro.")
    st.stop()

# --- Sidebar - Configurações ---
st.sidebar.header("🔧 Configurações")

# Filtros
departamentos_selecionados = st.sidebar.multiselect(
    "Departamentos:",
    options=df_agentes['departamento'].unique(),
    default=df_agentes['departamento'].unique()
)

equipes_selecionadas = st.sidebar.multiselect(
    "Equipes:",
    options=df_agentes['equipe_atual'].unique(),
    default=df_agentes['equipe_atual'].unique()
)

df_filtrado = df_agentes[
    (df_agentes['departamento'].isin(departamentos_selecionados)) &
    (df_agentes['equipe_atual'].isin(equipes_selecionadas))
]

# --- Análise de Equipes Existentes ---
st.header("🏆 Análise de Equipes Existentes")

equipes_stats = []
for equipe in df_filtrado['equipe_atual'].unique():
    df_equipe = df_filtrado[df_filtrado['equipe_atual'] == equipe]
    analise = analisar_dinamica_equipe(df_equipe)

    equipes_stats.append({
        'Equipe': equipe,
        'Tamanho': len(df_equipe),
        'Score Geral': analise.get('score_geral', 0),
        'Compatibilidade Média': analise.get('compatibilidade_media', 0),
        'Conflitos': analise.get('numero_conflitos', 0),
        'Diversidade': analise.get('diversidade_cognitiva', 0)
    })

df_equipes = pd.DataFrame(equipes_stats).sort_values(
    'Score Geral', ascending=False)

# Métricas gerais
col1, col2, col3, col4 = st.columns(4)

with col1:
    score_medio = df_equipes['Score Geral'].mean()
    st.metric("📊 Score Médio Equipes", f"{score_medio:.1f}/100")

with col2:
    melhor_equipe = df_equipes.iloc[0] if not df_equipes.empty else None
    if melhor_equipe is not None:
        st.metric("🥇 Melhor Equipe",
                  melhor_equipe['Equipe'], f"{melhor_equipe['Score Geral']:.1f} pts")

with col3:
    conflitos_totais = df_equipes['Conflitos'].sum()
    st.metric("⚠️ Conflitos Totais", conflitos_totais)

with col4:
    equipes_otimas = len(df_equipes[df_equipes['Score Geral'] >= 80])
    st.metric("✅ Equipes Ótimas", f"{equipes_otimas}/{len(df_equipes)}")

# Tabela de ranking
st.subheader("📊 Ranking de Equipes")
st.dataframe(
    df_equipes.style.format({
        'Score Geral': '{:.1f}',
        'Compatibilidade Média': '{:.1f}',
        'Diversidade': '{:.2f}'
    }).background_gradient(subset=['Score Geral'], cmap='RdYlGn'),
    use_container_width=True
)

# --- Análise Detalhada de Equipe ---
st.header("🔍 Análise Detalhada de Equipe")

equipe_selecionada = st.selectbox(
    "Selecione uma equipe para análise detalhada:",
    options=df_filtrado['equipe_atual'].unique()
)

df_equipe_detalhe = df_filtrado[df_filtrado['equipe_atual']
                                == equipe_selecionada]
analise_detalhada = analisar_dinamica_equipe(df_equipe_detalhe)

if not df_equipe_detalhe.empty:
    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        st.subheader(f"👥 {equipe_selecionada}")

        # Matriz de compatibilidade
        if len(df_equipe_detalhe) >= 2:
            matriz_compat = np.zeros(
                (len(df_equipe_detalhe), len(df_equipe_detalhe)))
            nomes = df_equipe_detalhe['nome'].tolist()

            for i, (idx1, pessoa1) in enumerate(df_equipe_detalhe.iterrows()):
                for j, (idx2, pessoa2) in enumerate(df_equipe_detalhe.iterrows()):
                    if i != j:
                        matriz_compat[i, j] = calcular_compatibilidade(
                            pessoa1, pessoa2)

            fig_heatmap = go.Figure(data=go.Heatmap(
                z=matriz_compat,
                x=nomes,
                y=nomes,
                colorscale='RdYlGn',
                text=matriz_compat,
                texttemplate="%{text:.1f}",
                colorbar=dict(title="Compatibilidade %")
            ))

            fig_heatmap.update_layout(
                title="Matriz de Compatibilidade da Equipe",
                xaxis_title="",
                yaxis_title=""
            )

            st.plotly_chart(fig_heatmap, use_container_width=True)

    with col2:
        st.subheader("📈 Métricas da Equipe")

        st.metric("🎯 Score Geral",
                  f"{analise_detalhada.get('score_geral', 0):.1f}/100")
        st.metric("🤝 Compatibilidade Média",
                  f"{analise_detalhada.get('compatibilidade_media', 0):.1f}%")
        st.metric("⚠️ Número de Conflitos",
                  analise_detalhada.get('numero_conflitos', 0))
        st.metric("🧠 Diversidade Cognitiva",
                  f"{analise_detalhada.get('diversidade_cognitiva', 0):.2f}")

        # Conflitos identificados
        conflitos = analise_detalhada.get('conflitos_detalhados', [])
        if conflitos:
            st.subheader("⚠️ Conflitos Identificados")
            for conflito in conflitos[:3]:  # Mostrar só os 3 primeiros
                st.warning(f"• {conflito}")
        else:
            st.success("✅ Nenhum conflito identificado!")

        # Perfil Big Five da equipe
        st.subheader("🎭 Perfil Médio da Equipe")
        big_five_cols = [
            'perfil_big_five.abertura_a_experiencia',
            'perfil_big_five.conscienciosidade',
            'perfil_big_five.extroversao',
            'perfil_big_five.amabilidade',
            'perfil_big_five.neuroticismo'
        ]

        perfil_medio = df_equipe_detalhe[big_five_cols].mean()

        fig_radar = go.Figure()

        categorias = [col.replace('perfil_big_five.', '').replace(
            '_', ' ').title() for col in big_five_cols]
        valores = perfil_medio.values.tolist()

        fig_radar.add_trace(go.Scatterpolar(
            r=valores,
            theta=categorias,
            fill='toself',
            name=equipe_selecionada,
            fillcolor='rgba(0, 100, 200, 0.3)'
        ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            title="Perfil Big Five Médio"
        )

        st.plotly_chart(fig_radar, use_container_width=True)

# --- Otimizador de Equipes ---
st.header("🚀 Otimizador de Equipes")

st.markdown("Crie equipes otimizadas baseadas em compatibilidade comportamental:")

col1, col2 = st.columns(2)

with col1:
    tamanho_equipe = st.slider("Tamanho da equipe:", 2, 8, 4)

with col2:
    incluir_todos = st.checkbox(
        "Incluir todos os funcionários filtrados", value=True)

if st.button("🔮 Gerar Equipe Otimizada", type="primary"):
    with st.spinner("Analisando combinações possíveis..."):
        df_para_otimizar = df_filtrado if incluir_todos else df_filtrado.sample(
            min(15, len(df_filtrado)))

        resultado = sugerir_reorganizacao(df_para_otimizar, tamanho_equipe)

        if resultado:
            melhor_equipe_ids, score = resultado
            df_equipe_otima = df_para_otimizar.loc[list(melhor_equipe_ids)]

            st.success(f"✅ Equipe otimizada gerada com score: {score:.1f}/100")

            # Mostrar membros da equipe
            st.subheader("👥 Membros da Equipe Otimizada")

            for _, membro in df_equipe_otima.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
                    with col1:
                        st.write(f"**{membro['nome']}**")
                    with col2:
                        st.write(f"{membro['cargo']}")
                    with col3:
                        st.write(f"{membro['departamento']}")

            # Análise da equipe otimizada
            analise_otima = analisar_dinamica_equipe(df_equipe_otima)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 Score Final",
                          f"{analise_otima.get('score_geral', 0):.1f}/100")
            with col2:
                st.metric("🤝 Compatibilidade",
                          f"{analise_otima.get('compatibilidade_media', 0):.1f}%")
            with col3:
                st.metric("⚠️ Conflitos", analise_otima.get(
                    'numero_conflitos', 0))
        else:
            st.error(
                "Não foi possível gerar equipe otimizada com os funcionários selecionados.")

# --- Network Analysis ---
st.header("🕸️ Análise de Rede Social")

# Calcular métricas de rede
G, centralidade, clustering, densidade = calcular_network_metrics(df_filtrado)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🌐 Densidade da Rede", f"{densidade:.2f}")

with col2:
    if centralidade:
        pessoa_central = max(centralidade.items(), key=lambda x: x[1])
        nome_central = df_filtrado.loc[pessoa_central[0], 'nome']
        st.metric("🌟 Mais Central", nome_central)

with col3:
    clustering_medio = np.mean(list(clustering.values())) if clustering else 0
    st.metric("🔗 Clustering Médio", f"{clustering_medio:.2f}")

# Visualização da rede
if len(G.edges()) > 0:
    pos = nx.spring_layout(G, k=1, iterations=50)

    # Preparar dados para plotly
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x = []
    node_y = []
    node_text = []
    node_color = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(df_filtrado.loc[node, 'nome'])
        node_color.append(centralidade.get(node, 0))

    fig_network = go.Figure()

    # Adicionar arestas
    fig_network.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    ))

    # Adicionar nós
    fig_network.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="middle center",
        marker=dict(
            size=20,
            color=node_color,
            colorscale='viridis',
            colorbar=dict(title="Centralidade"),
            line=dict(width=2, color='white')
        )
    ))

    fig_network.update_layout(
        title="Rede de Compatibilidade (>70%)",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        annotations=[
            dict(
                text="Nós maiores = mais centrais | Conexões = alta compatibilidade",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='gray', size=12)
            )
        ],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    st.plotly_chart(fig_network, use_container_width=True)
else:
    st.info("Não há conexões suficientes para exibir a rede (compatibilidade >70%)")

# --- Recomendações Estratégicas ---
st.header("💡 Recomendações Estratégicas")

recomendacoes = []

# Análise das equipes e geração de recomendações
if not df_equipes.empty:
    # Equipes com baixo score
    equipes_problema = df_equipes[df_equipes['Score Geral'] < 60]
    if not equipes_problema.empty:
        for _, equipe in equipes_problema.iterrows():
            recomendacoes.append({
                'tipo': 'REORGANIZAÇÃO',
                'prioridade': 'ALTA',
                'titulo': f"Reorganizar {equipe['Equipe']}",
                'descricao': f"Score atual: {equipe['Score Geral']:.1f}/100. Identificados {equipe['Conflitos']} conflitos potenciais.",
                'acao': "Usar o otimizador para formar nova configuração"
            })

    # Muitos conflitos
    if df_equipes['Conflitos'].sum() > len(df_equipes) * 2:
        recomendacoes.append({
            'tipo': 'TREINAMENTO',
            'prioridade': 'MÉDIA',
            'titulo': 'Programa de comunicação interpessoal',
            'descricao': f"Identificados {df_equipes['Conflitos'].sum()} conflitos potenciais na organização.",
            'acao': "Implementar workshops de comunicação e resolução de conflitos"
        })

    # Baixa diversidade
    diversidade_media = df_equipes['Diversidade'].mean()
    if diversidade_media < 2:
        recomendacoes.append({
            'tipo': 'CONTRATAÇÃO',
            'prioridade': 'BAIXA',
            'titulo': 'Aumentar diversidade cognitiva',
            'descricao': f"Diversidade média: {diversidade_media:.2f}. Equipes homogêneas podem ter menor inovação.",
            'acao': "Priorizar perfis diversos nas próximas contratações"
        })

# Se não há recomendações críticas
if not recomendacoes:
    recomendacoes.append({
        'tipo': 'MANUTENÇÃO',
        'prioridade': 'BAIXA',
        'titulo': 'Equipes funcionando bem',
        'descricao': 'Dinâmicas de equipe estão saudáveis.',
        'acao': 'Manter monitoramento regular e ajustes finos'
    })

for i, rec in enumerate(recomendacoes):
    cor = 'error' if rec['prioridade'] == 'ALTA' else 'warning' if rec['prioridade'] == 'MÉDIA' else 'info'

    if cor == 'error':
        st.error(
            f"🚨 **{rec['titulo']}** - {rec['prioridade']}\n\n{rec['descricao']}\n\n➡️ **Ação:** {rec['acao']}")
    elif cor == 'warning':
        st.warning(
            f"⚠️ **{rec['titulo']}** - {rec['prioridade']}\n\n{rec['descricao']}\n\n➡️ **Ação:** {rec['acao']}")
    else:
        st.info(
            f"ℹ️ **{rec['titulo']}** - {rec['prioridade']}\n\n{rec['descricao']}\n\n➡️ **Ação:** {rec['acao']}")

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
🔥 <strong>Team Dynamics Optimizer</strong> - HumaniQ AI<br>
Otimização de equipes baseada em ciência comportamental e compatibilidade psicológica
</div>

""", unsafe_allow_html=True)
