import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime
import anthropic
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

st.set_page_config(page_title="Comparação de Perfis",
                   page_icon="👥", layout="wide")

st.title("👥 Comparação Inteligente de Perfis")
st.markdown("""
**Powered by Claude AI** - Compare funcionários usando análise comportamental avançada e insights de compatibilidade.
""")

# --- Configuração Claude AI ---


@st.cache_resource
def init_claude():
    """Inicializa cliente Claude AI"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        st.error("🔑 **ANTHROPIC_API_KEY** não encontrada no arquivo .env!")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)


claude_client = init_claude()

# --- Funções de Carregamento ---
AGENT_DIR = "data/agents"


@st.cache_data
def carregar_agentes():
    """Carrega todos os dados dos agentes de arquivos JSON para um DataFrame."""
    if not os.path.exists(AGENT_DIR):
        st.error(
            f"📁 Diretório '{AGENT_DIR}' não encontrado. Execute 'generate_agents.py' primeiro.")
        return pd.DataFrame()

    agent_files = [f for f in os.listdir(AGENT_DIR) if f.endswith('.json')]
    if not agent_files:
        st.warning(
            "⚠️ Nenhum agente encontrado. Execute 'generate_agents.py' primeiro.")
        return pd.DataFrame()

    all_agents_data = []
    for agent_file in agent_files:
        fp = os.path.join(AGENT_DIR, agent_file)
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                all_agents_data.append(json.load(f))
        except Exception as e:
            st.warning(f"⚠️ Erro ao carregar {agent_file}: {e}")

    if not all_agents_data:
        return pd.DataFrame()

    df = pd.json_normalize(all_agents_data)
    return df.set_index('id_funcionario')

# --- Funções de Análise ---


def calcular_compatibilidade_big_five(pessoa1, pessoa2):
    """Calcula compatibilidade baseada em Big Five usando algoritmo científico"""

    # Extrair perfis Big Five
    big_five_cols = [
        'perfil_big_five.abertura_a_experiencia',
        'perfil_big_five.conscienciosidade',
        'perfil_big_five.extroversao',
        'perfil_big_five.amabilidade',
        'perfil_big_five.neuroticismo'
    ]

    perfil1 = np.array([pessoa1.get(col, 5) for col in big_five_cols])
    perfil2 = np.array([pessoa2.get(col, 5) for col in big_five_cols])

    # Lógica baseada em pesquisa psicológica:
    # - Algumas dimensões se complementam (opostos se atraem)
    # - Outras devem ser similares (harmonia)

    scores = {}

    # Abertura: similaridade é boa (criatividade alinhada)
    scores['abertura'] = 100 - abs(perfil1[0] - perfil2[0]) * 10

    # Conscienciosidade: similaridade é boa (trabalho alinhado)
    scores['conscienciosidade'] = 100 - abs(perfil1[1] - perfil2[1]) * 10

    # Extroversão: pode ser complementar (equilíbrio)
    diff_extroversao = abs(perfil1[2] - perfil2[2])
    # Ótimo em ~3 pts diferença
    scores['extroversao'] = 100 - (abs(diff_extroversao - 3) * 8)

    # Amabilidade: similaridade é boa (cooperação)
    scores['amabilidade'] = 100 - abs(perfil1[3] - perfil2[3]) * 12

    # Neuroticismo: ambos baixos é ideal
    scores['neuroticismo'] = 100 - (perfil1[4] + perfil2[4]) * 5

    # Score geral ponderado
    compatibilidade = (
        scores['abertura'] * 0.20 +
        scores['conscienciosidade'] * 0.25 +
        scores['extroversao'] * 0.15 +
        scores['amabilidade'] * 0.25 +
        scores['neuroticismo'] * 0.15
    )

    return max(0, min(100, compatibilidade)), scores


def analisar_dinamica_time(funcionarios_df):
    """Analisa dinâmica geral do time selecionado"""
    if len(funcionarios_df) < 2:
        return {}

    compatibilidades = []
    analises_detalhadas = []

    # Calcular todas as combinações
    funcionarios_list = funcionarios_df.index.tolist()

    for i in range(len(funcionarios_list)):
        for j in range(i + 1, len(funcionarios_list)):
            id1, id2 = funcionarios_list[i], funcionarios_list[j]
            pessoa1 = funcionarios_df.loc[id1]
            pessoa2 = funcionarios_df.loc[id2]

            compat, scores = calcular_compatibilidade_big_five(
                pessoa1, pessoa2)

            compatibilidades.append(compat)
            analises_detalhadas.append({
                'pessoa1': pessoa1['nome'],
                'pessoa2': pessoa2['nome'],
                'compatibilidade': compat,
                'scores_detalhados': scores
            })

    # Estatísticas do time
    compat_media = np.mean(compatibilidades) if compatibilidades else 0
    compat_min = np.min(compatibilidades) if compatibilidades else 0
    compat_max = np.max(compatibilidades) if compatibilidades else 0

    # Diversidade cognitiva (desvio padrão dos perfis)
    big_five_cols = [
        'perfil_big_five.abertura_a_experiencia',
        'perfil_big_five.conscienciosidade',
        'perfil_big_five.extroversao',
        'perfil_big_five.amabilidade',
        'perfil_big_five.neuroticismo'
    ]

    diversidade = funcionarios_df[big_five_cols].std().mean()

    return {
        'compatibilidade_media': round(compat_media, 1),
        'compatibilidade_min': round(compat_min, 1),
        'compatibilidade_max': round(compat_max, 1),
        'diversidade_cognitiva': round(diversidade, 2),
        'tamanho_time': len(funcionarios_df),
        'analises_detalhadas': analises_detalhadas
    }


def gerar_insights_claude(funcionarios_df, analise_time):
    """Gera insights usando Claude AI"""
    if funcionarios_df.empty:
        return "Nenhum funcionário selecionado para análise."

    # Preparar contexto para Claude
    contexto = {
        'funcionarios': [],
        'analise_time': analise_time
    }

    for idx, funcionario in funcionarios_df.iterrows():
        contexto['funcionarios'].append({
            'nome': funcionario['nome'],
            'cargo': funcionario['cargo'],
            'departamento': funcionario.get('departamento', 'N/A'),
            'big_five': {
                'abertura': funcionario.get('perfil_big_five.abertura_a_experiencia', 5),
                'conscienciosidade': funcionario.get('perfil_big_five.conscienciosidade', 5),
                'extroversao': funcionario.get('perfil_big_five.extroversao', 5),
                'amabilidade': funcionario.get('perfil_big_five.amabilidade', 5),
                'neuroticismo': funcionario.get('perfil_big_five.neuroticismo', 5)
            },
            'performance': funcionario.get('performance.metas_atingidas_percentual', 0),
            'engajamento': funcionario.get('engajamento.enps_recente', 5)
        })

    prompt = f"""
Você é um especialista em psicologia organizacional e análise de equipes. Analise o seguinte grupo de funcionários:

DADOS DO TIME:
{json.dumps(contexto, indent=2, ensure_ascii=False)}

TAREFA:
Forneça insights detalhados sobre:

1. **DINÂMICA DO TIME** - Como essas personalidades interagem?
2. **PONTOS FORTES** - Quais são as principais vantagens desta composição?
3. **PONTOS DE ATENÇÃO** - Onde podem surgir conflitos ou desafios?
4. **RECOMENDAÇÕES** - Como otimizar a colaboração deste time?
5. **PAPÉIS IDEAIS** - Que papel cada pessoa deveria assumir?

Use linguagem profissional mas acessível. Seja específico e acionável.

FORMATO DE RESPOSTA:
Use markdown com seções bem definidas e bullet points.
"""

    try:
        response = claude_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    except Exception as e:
        return f"❌ Erro ao gerar insights: {str(e)}"

# --- Interface Principal ---


def main():
    df_all = carregar_agentes()

    if df_all.empty:
        st.stop()

    # --- Sidebar: Filtros e Configurações ---
    st.sidebar.header("🔧 Configurações")

    # Filtro por departamento
    departamentos = ['Todos'] + \
        sorted(df_all['departamento'].unique().tolist())
    dept_selecionado = st.sidebar.selectbox(
        "Filtrar por departamento:", departamentos)

    if dept_selecionado != 'Todos':
        df_filtrado = df_all[df_all['departamento'] == dept_selecionado]
    else:
        df_filtrado = df_all

    # Filtro por cargo
    cargos = ['Todos'] + sorted(df_filtrado['cargo'].unique().tolist())
    cargo_selecionado = st.sidebar.selectbox("Filtrar por cargo:", cargos)

    if cargo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['cargo'] == cargo_selecionado]

    st.sidebar.divider()
    st.sidebar.markdown("**🎯 Funcionários disponíveis:**")
    st.sidebar.write(f"📊 Total: {len(df_filtrado)}")

    # --- Seleção de Funcionários ---
    st.header("👥 Seleção de Funcionários para Comparação")

    funcionarios_selecionados = st.multiselect(
        "Escolha 2 ou mais funcionários para comparar:",
        options=df_filtrado.index.tolist(),
        format_func=lambda x: f"{df_filtrado.loc[x, 'nome']} ({df_filtrado.loc[x, 'cargo']})",
        help="Selecione pelo menos 2 funcionários para ver análise comparativa"
    )

    if len(funcionarios_selecionados) < 2:
        st.info("👆 Selecione pelo menos **2 funcionários** para iniciar a comparação.")
        return

    # Dados dos funcionários selecionados
    df_selected = df_filtrado.loc[funcionarios_selecionados]

    # --- Análise de Compatibilidade ---
    st.header("🧮 Análise de Compatibilidade")

    analise = analisar_dinamica_time(df_selected)

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👥 Pessoas no Time", analise['tamanho_time'])

    with col2:
        compat_media = analise['compatibilidade_media']
        cor_delta = "normal" if compat_media >= 70 else "inverse"
        st.metric("🤝 Compatibilidade Média",
                  f"{compat_media:.1f}%", delta_color=cor_delta)

    with col3:
        st.metric("📊 Menor Compatibilidade",
                  f"{analise['compatibilidade_min']:.1f}%")

    with col4:
        diversidade = analise['diversidade_cognitiva']
        st.metric("🧠 Diversidade Cognitiva", f"{diversidade:.1f}",
                  delta="Alta" if diversidade > 2 else "Média" if diversidade > 1 else "Baixa")

    # --- Gráfico de Radar Comparativo ---
    st.subheader("📊 Comparativo de Personalidade (Big Five)")

    fig = go.Figure()

    categorias = [
        'perfil_big_five.abertura_a_experiencia',
        'perfil_big_five.conscienciosidade',
        'perfil_big_five.extroversao',
        'perfil_big_five.amabilidade',
        'perfil_big_five.neuroticismo'
    ]
    categorias_simples = [cat.replace('perfil_big_five.', '').replace(
        '_', ' ').title() for cat in categorias]

    cores = ['#FF6B6B', '#4ECDC4', '#45B7D1',
             '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']

    for i, (index, row) in enumerate(df_selected.iterrows()):
        valores = [row.get(cat, 5) for cat in categorias]

        fig.add_trace(go.Scatterpolar(
            r=valores + [valores[0]],  # Fechar o radar
            theta=categorias_simples +
            [categorias_simples[0]],  # Fechar o radar
            fill='toself',
            name=row['nome'],
            line=dict(color=cores[i % len(cores)], width=2),
            fillcolor=cores[i % len(cores)],
            opacity=0.3
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickmode='linear',
                tick0=0,
                dtick=2
            )
        ),
        showlegend=True,
        title="Comparativo de Personalidade (Big Five)",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Matriz de Compatibilidade ---
    if len(df_selected) >= 2:
        st.subheader("🔥 Matriz de Compatibilidade")

        # Criar matriz
        nomes = df_selected['nome'].tolist()
        n = len(nomes)
        matriz = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    pessoa1 = df_selected.iloc[i]
                    pessoa2 = df_selected.iloc[j]
                    compat, _ = calcular_compatibilidade_big_five(
                        pessoa1, pessoa2)
                    matriz[i, j] = compat
                else:
                    matriz[i, j] = 100  # Auto-compatibilidade

        # Gráfico de heatmap
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=matriz,
            x=nomes,
            y=nomes,
            colorscale='RdYlGn',
            zmid=70,  # Ponto médio em 70%
            text=np.round(matriz, 1),
            texttemplate="%{text}%",
            textfont={"size": 12},
            colorbar=dict(title="Compatibilidade %")
        ))

        fig_heatmap.update_layout(
            title="Matriz de Compatibilidade entre Membros do Time",
            xaxis_title="",
            yaxis_title="",
            height=400
        )

        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Análise das compatibilidades
        st.subheader("🔍 Análise Detalhada de Compatibilidades")

        # Melhores e piores pares
        if analise['analises_detalhadas']:
            analises_ordenadas = sorted(analise['analises_detalhadas'],
                                        key=lambda x: x['compatibilidade'], reverse=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**💚 Melhores Compatibilidades:**")
                for analise_par in analises_ordenadas[:3]:
                    compat = analise_par['compatibilidade']
                    cor = "🟢" if compat >= 80 else "🟡" if compat >= 60 else "🔴"
                    st.write(
                        f"{cor} **{analise_par['pessoa1']}** ↔ **{analise_par['pessoa2']}**: {compat:.1f}%")

            with col2:
                st.markdown("**⚠️ Compatibilidades de Atenção:**")
                for analise_par in analises_ordenadas[-3:]:
                    compat = analise_par['compatibilidade']
                    cor = "🟢" if compat >= 80 else "🟡" if compat >= 60 else "🔴"
                    st.write(
                        f"{cor} **{analise_par['pessoa1']}** ↔ **{analise_par['pessoa2']}**: {compat:.1f}%")

    # --- Insights do Claude AI ---
    st.header("🧠 Insights Avançados (Claude AI)")

    if st.button("🔮 Gerar Análise Inteligente", type="primary"):
        with st.spinner("🤖 Claude AI analisando o time..."):
            insights = gerar_insights_claude(df_selected, analise)

        st.markdown("### 📝 Análise do Time pelo Claude AI")
        st.markdown(insights)

    # --- Tabela Detalhada ---
    st.header("📋 Dados Detalhados dos Funcionários")

    # Preparar dados para exibição
    df_display = df_selected.copy()

    # Adicionar colunas calculadas
    colunas_exibir = [
        'nome', 'cargo', 'departamento',
        'perfil_big_five.abertura_a_experiencia',
        'perfil_big_five.conscienciosidade',
        'perfil_big_five.extroversao',
        'perfil_big_five.amabilidade',
        'perfil_big_five.neuroticismo',
        'performance.metas_atingidas_percentual',
        'engajamento.enps_recente'
    ]

    # Renomear colunas para exibição
    nomes_colunas = {
        'nome': 'Nome',
        'cargo': 'Cargo',
        'departamento': 'Departamento',
        'perfil_big_five.abertura_a_experiencia': 'Abertura',
        'perfil_big_five.conscienciosidade': 'Conscienciosidade',
        'perfil_big_five.extroversao': 'Extroversão',
        'perfil_big_five.amabilidade': 'Amabilidade',
        'perfil_big_five.neuroticismo': 'Neuroticismo',
        'performance.metas_atingidas_percentual': 'Performance (%)',
        'engajamento.enps_recente': 'eNPS'
    }

    df_display_renamed = df_display[colunas_exibir].rename(
        columns=nomes_colunas)

    st.dataframe(
        df_display_renamed.style.format({
            'Abertura': '{:.1f}',
            'Conscienciosidade': '{:.1f}',
            'Extroversão': '{:.1f}',
            'Amabilidade': '{:.1f}',
            'Neuroticismo': '{:.1f}',
            'Performance (%)': '{:.1f}%',
            'eNPS': '{:.0f}'
        }),
        use_container_width=True
    )

    # --- Export/Save ---
    st.header("💾 Exportar Análise")

    if st.button("📊 Gerar Relatório de Comparação"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        relatorio = {
            "timestamp": timestamp,
            "funcionarios_comparados": df_selected['nome'].tolist(),
            "analise_time": analise,
            "compatibilidades_detalhadas": analise['analises_detalhadas'] if 'analises_detalhadas' in analise else []
        }

        # Exibir JSON
        st.json(relatorio)
        st.success("✅ Relatório gerado! Copie o JSON acima para salvar.")


if __name__ == "__main__":
    main()

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
👥 <strong>Comparação de Perfis</strong> - HumaniQ AI<br>
Powered by ManalyticsAI | Análise científica baseada no modelo Big Five
</div>
""", unsafe_allow_html=True)
