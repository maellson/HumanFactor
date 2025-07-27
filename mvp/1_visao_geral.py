import streamlit as st
import pandas as pd
import json

# Configuração da página
st.set_page_config(
    page_title="HumaniQ AI - MVP",
    page_icon="🧠",
    layout="wide"
)

# Título do Dashboard
st.title("🧠 HumaniQ AI - MVP Dashboard")
st.subheader("Análise de Perfil de Funcionário")

# --- SELEÇÃO DE AGENTE ---
import os

AGENT_DIR = "data/agents"
try:
    agent_files = [f for f in os.listdir(AGENT_DIR) if f.endswith('.json')]
    agent_ids = sorted([f.split('.')[0] for f in agent_files])

    selected_agent_id = st.sidebar.selectbox("Selecione um Agente", options=agent_ids)

    # Carregar dados do agente selecionado
    file_path = os.path.join(AGENT_DIR, f"{selected_agent_id}.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        dados_agente = json.load(f)

    # --- EXIBIÇÃO DOS DADOS ---
    # Extrair informações
    nome = dados_agente.get("nome", "N/A")
    cargo = dados_agente.get("cargo", "N/A")
    equipe = dados_agente.get("equipe_atual", "N/A")
    demografia = dados_agente.get("demografia", {})
    
    st.header(f"Perfil: {nome}")
    st.markdown(f"**Cargo:** {cargo} | **Equipe:** {equipe}")
    st.markdown(f"**País de Origem:** {demografia.get('pais_origem', 'N/A')} | **Gênero:** {demografia.get('genero', 'N/A')}")

    # Criar colunas para melhor layout
    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        st.subheader("📊 Perfil Comportamental (Big Five)")
        perfil_df = pd.DataFrame(
            dados_agente.get("perfil_big_five", {}).items(),
            columns=['Traço', 'Pontuação']
        ).set_index('Traço')
        st.bar_chart(perfil_df)

        st.subheader("🛠️ Competências")
        competencias = dados_agente.get("competencias", [])
        st.multiselect("Habilidades Principais", options=competencias, default=competencias, disabled=True)


    with col2:
        st.subheader("🚀 Performance e Engajamento")
        
        performance = dados_agente.get("performance", {})
        engajamento = dados_agente.get("engajamento", {})

        st.metric(
            label="Última Avaliação de Desempenho",
            value=performance.get("avaliacoes_desempenho", [{}])[-1].get("nota", 0)
        )
        st.metric(
            label="Metas Atingidas",
            value=f"{performance.get('metas_atingidas_percentual', 0)}%"
        )
        st.metric(
            label="eNPS Recente",
            value=engajamento.get("enps_recente", 0)
        )

        st.subheader("🎯 Objetivos de Carreira")
        st.info(dados_agente.get("objetivos_carreira", "Não definido."))

    st.subheader("📄 Dados Completos do Agente (JSON)")
    st.json(dados_agente)

    # --- ANÁLISE DE PCA ---
    st.markdown("---")
    st.header("🔬 Análise de Agrupamento com PCA")
    st.markdown("""
    A Análise de Componentes Principais (PCA) reduz a complexidade dos dados, permitindo visualizar
    perfis de funcionários em um gráfico 2D. Pontos próximos representam funcionários com características semelhantes.
    """)

    # Carregar todos os agentes para a análise
    all_agents_data = []
    for agent_file in agent_files:
        fp = os.path.join(AGENT_DIR, agent_file)
        with open(fp, 'r', encoding='utf-8') as f:
            all_agents_data.append(json.load(f))

    # Criar DataFrame com todos os agentes
    df_all = pd.json_normalize(all_agents_data)

    # Selecionar features numéricas para a PCA
    features = [
        'tempo_de_casa_meses',
        'perfil_big_five.abertura_a_experiencia',
        'perfil_big_five.conscienciosidade',
        'perfil_big_five.extroversao',
        'perfil_big_five.amabilidade',
        'perfil_big_five.neuroticismo',
        'performance.metas_atingidas_percentual',
        'engajamento.enps_recente',
        'engajamento.feedback_360_media'
    ]
    df_features = df_all[features]

    # Normalizar os dados
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df_features)

    # Aplicar PCA
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(scaled_features)

    # Criar DataFrame com os resultados da PCA
    df_pca = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
    df_pca['nome'] = df_all['nome']
    df_pca['cargo'] = df_all['cargo']
    df_pca['pais_origem'] = df_all['demografia.pais_origem']

    # Criar gráfico com Plotly
    import plotly.express as px

    fig = px.scatter(
        df_pca,
        x='PC1',
        y='PC2',
        color='cargo',
        hover_name='nome',
        hover_data={'pais_origem': True, 'cargo': True},
        title='Visualização de Perfis de Funcionários via PCA'
    )
    fig.update_layout(
        xaxis_title="Componente Principal 1 (PC1)",
        yaxis_title="Componente Principal 2 (PC2)",
        legend_title="Cargo"
    )
    st.plotly_chart(fig, use_container_width=True)


except FileNotFoundError:
    st.error(f"Diretório de agentes não encontrado. Verifique o caminho: '{AGENT_DIR}'")
except Exception as e:
    st.error(f"Ocorreu um erro ao processar os dados: {e}")