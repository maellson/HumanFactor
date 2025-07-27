import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Comparação de Perfis", page_icon="👥", layout="wide")

st.title("👥 Comparação Direta de Perfis")
st.markdown("""
Selecione dois ou mais funcionários para comparar seus perfis de personalidade (Big Five)
lado a lado em um gráfico de radar.
""")

AGENT_DIR = "data/agents"

@st.cache_data
def carregar_agentes():
    """Carrega todos os dados dos agentes de arquivos JSON para um DataFrame."""
    agent_files = [f for f in os.listdir(AGENT_DIR) if f.endswith('.json')]
    if not agent_files:
        return pd.DataFrame()
    
    all_agents_data = []
    for agent_file in agent_files:
        fp = os.path.join(AGENT_DIR, agent_file)
        with open(fp, 'r', encoding='utf-8') as f:
            all_agents_data.append(json.load(f))
    
    df = pd.json_normalize(all_agents_data)
    return df.set_index('id_funcionario')

try:
    df_all = carregar_agentes()

    if df_all.empty:
        st.warning("Nenhum agente encontrado no diretório 'mvp/data/agents'.")
    else:
        # --- Seleção de Funcionários ---
        funcionarios_selecionados = st.multiselect(
            "Selecione os funcionários para comparar:",
            options=df_all.index.tolist(),
            format_func=lambda x: f"{df_all.loc[x, 'nome']} ({df_all.loc[x, 'cargo']})"
        )

        if len(funcionarios_selecionados) >= 2:
            df_selected = df_all.loc[funcionarios_selecionados]

            # --- Gráfico de Radar ---
            st.subheader("📊 Comparativo de Personalidade (Gráfico de Radar)")
            
            fig = go.Figure()
            
            categorias = [
                'perfil_big_five.abertura_a_experiencia',
                'perfil_big_five.conscienciosidade',
                'perfil_big_five.extroversao',
                'perfil_big_five.amabilidade',
                'perfil_big_five.neuroticismo'
            ]
            categorias_simples = [cat.replace('perfil_big_five.', '').replace('_', ' ').title() for cat in categorias]

            for index, row in df_selected.iterrows():
                valores = row[categorias].values.tolist()
                fig.add_trace(go.Scatterpolar(
                    r=valores + [valores[0]], # Fechar o radar
                    theta=categorias_simples + [categorias_simples[0]], # Fechar o radar
                    fill='toself',
                    name=row['nome']
                ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=True,
                title="Comparativo de Personalidade (Big Five)"
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("Por favor, selecione pelo menos dois funcionários para iniciar a comparação.")

except Exception as e:
    st.error(f"Ocorreu um erro ao processar a página: {e}")