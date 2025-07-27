import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Análise de Fit", page_icon="🎯", layout="wide")

st.title("🎯 Análise de Fit de Vaga")
st.markdown("Selecione uma vaga para ver o ranking de funcionários mais compatíveis.")

# --- Funções de Carregamento ---
@st.cache_data
def carregar_dados(diretorio):
    arquivos = [f for f in os.listdir(diretorio) if f.endswith('.json')]
    dados = {}
    for arquivo in arquivos:
        caminho = os.path.join(diretorio, arquivo)
        with open(caminho, 'r', encoding='utf-8') as f:
            dados[arquivo.replace('.json', '')] = json.load(f)
    return dados

# --- Carregar Dados ---
VAGAS_DIR = "data/vagas"
AGENTS_DIR = "data/agents"

vagas = carregar_dados(VAGAS_DIR)
agentes = carregar_dados(AGENTS_DIR)

if not vagas:
    st.warning("Nenhuma vaga encontrada no diretório 'data/vagas'.")
    st.stop()

# --- Interface ---
col1, col2 = st.columns(2)
with col1:
    vaga_selecionada_id = st.selectbox("1. Selecione a Vaga", options=vagas.keys(), format_func=lambda x: vagas[x]['titulo_vaga'])
vaga_selecionada = vagas[vaga_selecionada_id]

df_agentes = pd.DataFrame.from_dict(agentes, orient='index')

with col2:
    funcionarios_selecionados = st.multiselect(
        "2. Selecione os Funcionários (ou deixe em branco para analisar todos)",
        options=df_agentes.index.tolist(),
        format_func=lambda x: f"{df_agentes.loc[x, 'nome']} ({df_agentes.loc[x, 'cargo']})"
    )

# --- Lógica de Cálculo de Fit ---
def calcular_fit(agente, vaga):
    # ... (código de cálculo de fit permanece o mesmo)
    perfil_agente = np.array(list(agente['perfil_big_five'].values()))
    perfil_vaga = np.array(list(vaga['perfil_ideal_big_five'].values()))
    distancia = np.linalg.norm(perfil_agente - perfil_vaga)
    fit_personalidade = max(0, 1 - distancia / np.linalg.norm(np.array([10,10,10,10,10]))) * 100
    competencias_agente = set(agente['competencias'])
    obg = set(vaga['competencias_obrigatorias'])
    des = set(vaga['competencias_desejaveis'])
    fit_obg = len(competencias_agente.intersection(obg)) / len(obg) * 100 if obg else 100
    fit_des = len(competencias_agente.intersection(des)) / len(des) * 100 if des else 100
    fit_competencias = (fit_obg * 2 + fit_des * 1) / 3
    score_final = (fit_personalidade * 0.4) + (fit_competencias * 0.6)
    return round(score_final, 2), round(fit_personalidade, 2), round(fit_competencias, 2)

# Filtrar agentes se selecionados, senão usar todos
df_para_analise = df_agentes.loc[funcionarios_selecionados] if funcionarios_selecionados else df_agentes

scores = df_para_analise.apply(lambda row: calcular_fit(row, vaga_selecionada), axis=1)
df_scores = pd.DataFrame(scores.tolist(), index=df_para_analise.index, columns=['Score Final', 'Fit Personalidade', 'Fit Competências'])
df_resultado = df_para_analise.join(df_scores)
df_resultado = df_resultado.sort_values(by='Score Final', ascending=False)

# --- Exibição dos Resultados ---
st.subheader(f"Ranking de Compatibilidade para: {vaga_selecionada['titulo_vaga']}")
st.dataframe(df_resultado[['nome', 'cargo', 'Score Final', 'Fit Personalidade', 'Fit Competências']])

# --- Gráfico de Radar Comparativo ---
st.subheader("Comparativo de Perfil vs. Vaga Ideal")

if not df_resultado.empty and funcionarios_selecionados:
    fig = go.Figure()
    categorias = list(vaga_selecionada['perfil_ideal_big_five'].keys())
    categorias_simples = [cat.replace('_', ' ').title() for cat in categorias]

    # Perfil Ideal da Vaga (sempre o primeiro)
    fig.add_trace(go.Scatterpolar(
        r=list(vaga_selecionada['perfil_ideal_big_five'].values()),
        theta=categorias_simples,
        fill='toself',
        name='Perfil Ideal da Vaga',
        opacity=0.5
    ))
    
    # Perfis dos Candidatos Selecionados
    for index, row in df_resultado.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=list(row['perfil_big_five'].values()),
            theta=categorias_simples,
            name=row['nome']
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        title="Comparativo de Personalidade (Big Five)"
    )
    st.plotly_chart(fig, use_container_width=True)
elif not funcionarios_selecionados:
    st.info("Selecione um ou mais funcionários para visualizar o gráfico de radar comparativo.")