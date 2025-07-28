import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import anthropic
import matplotlib
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

st.set_page_config(page_title="Análise de Fit", page_icon="🎯", layout="wide")

st.title("🎯 Análise Inteligente de Fit Vaga-Candidato")
st.markdown("""
**Powered by Claude AI** - Encontre o candidato perfeito usando análise de fit cultural e técnico.
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
VAGAS_DIR = "data/vagas"
AGENTS_DIR = "data/agents"


@st.cache_data
def carregar_dados(diretorio):
    """Carrega dados de arquivos JSON"""
    if not os.path.exists(diretorio):
        return {}

    arquivos = [f for f in os.listdir(diretorio) if f.endswith('.json')]
    dados = {}

    for arquivo in arquivos:
        caminho = os.path.join(diretorio, arquivo)
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                dados[arquivo.replace('.json', '')] = json.load(f)
        except Exception as e:
            st.warning(f"⚠️ Erro ao carregar {arquivo}: {e}")

    return dados


def criar_vaga_exemplo():
    """Cria exemplo de vaga se diretório não existir"""
    vaga_exemplo = {
        "id_vaga": "VAGA_001",
        "titulo_vaga": "Analista de Dados Sênior",
        "departamento": "Tecnologia",
        "nivel": "Sênior",
        "descricao": "Profissional para análise de dados e insights estratégicos",
        "perfil_ideal_big_five": {
            "abertura_a_experiencia": 8.0,
            "conscienciosidade": 9.0,
            "extroversao": 6.0,
            "amabilidade": 7.0,
            "neuroticismo": 3.0
        },
        "competencias_obrigatorias": ["Python", "SQL", "Análise Estatística"],
        "competencias_desejaveis": ["Machine Learning", "Power BI", "Comunicação"],
        "competencias_diferenciais": ["AWS", "Docker"],
        "salario_min": 8000,
        "salario_max": 15000,
        "requisitos_especiais": ["Experiência com big data", "Inglês intermediário"]
    }

    return {"vaga_exemplo": vaga_exemplo}

# --- Funções de Análise ---


def calcular_fit_cultural(candidato, vaga):
    """Calcula fit cultural baseado em Big Five"""

    # Perfis Big Five
    big_five_cols = [
        'perfil_big_five.abertura_a_experiencia',
        'perfil_big_five.conscienciosidade',
        'perfil_big_five.extroversao',
        'perfil_big_five.amabilidade',
        'perfil_big_five.neuroticismo'
    ]

    perfil_candidato = np.array([candidato.get(col, 5)
                                for col in big_five_cols])
    perfil_ideal = np.array(list(vaga['perfil_ideal_big_five'].values()))

    # Cálculo de distância euclidiana normalizada
    distancia = np.linalg.norm(perfil_candidato - perfil_ideal)
    distancia_max = np.linalg.norm(np.array([10, 10, 10, 10, 10]))

    # Converter para score de 0-100
    fit_score = max(0, (1 - distancia / distancia_max) * 100)

    # Análise detalhada por dimensão
    dimensoes = ['abertura_a_experiencia', 'conscienciosidade',
                 'extroversao', 'amabilidade', 'neuroticismo']
    fit_detalhado = {}

    for i, dimensao in enumerate(dimensoes):
        diff = abs(perfil_candidato[i] - perfil_ideal[i])
        fit_dim = max(0, (1 - diff / 10) * 100)
        fit_detalhado[dimensao] = {
            'candidato': perfil_candidato[i],
            'ideal': perfil_ideal[i],
            'diferenca': diff,
            'fit_score': fit_dim,
            'status': 'Excelente' if fit_dim >= 80 else 'Bom' if fit_dim >= 60 else 'Atenção' if fit_dim >= 40 else 'Crítico'
        }

    return round(fit_score, 1), fit_detalhado


def calcular_fit_tecnico(candidato, vaga):
    """Calcula fit técnico baseado em competências"""

    competencias_candidato = set(candidato.get('competencias', []))

    # Competências obrigatórias
    obrigatorias = set(vaga.get('competencias_obrigatorias', []))
    match_obrigatorias = len(competencias_candidato.intersection(obrigatorias))
    total_obrigatorias = len(obrigatorias)
    score_obrigatorias = (
        match_obrigatorias / total_obrigatorias * 100) if total_obrigatorias > 0 else 100

    # Competências desejáveis
    desejaveis = set(vaga.get('competencias_desejaveis', []))
    match_desejaveis = len(competencias_candidato.intersection(desejaveis))
    total_desejaveis = len(desejaveis)
    score_desejaveis = (match_desejaveis / total_desejaveis *
                        100) if total_desejaveis > 0 else 100

    # Competências diferenciais
    diferenciais = set(vaga.get('competencias_diferenciais', []))
    match_diferenciais = len(competencias_candidato.intersection(diferenciais))
    total_diferenciais = len(diferenciais)
    score_diferenciais = (
        match_diferenciais / total_diferenciais * 100) if total_diferenciais > 0 else 100

    # Score técnico ponderado
    score_tecnico = (
        score_obrigatorias * 0.6 +  # 60% obrigatórias
        score_desejaveis * 0.3 +    # 30% desejáveis
        score_diferenciais * 0.1    # 10% diferenciais
    )

    analise_detalhada = {
        'obrigatorias': {
            'tem': list(competencias_candidato.intersection(obrigatorias)),
            'falta': list(obrigatorias - competencias_candidato),
            'score': round(score_obrigatorias, 1)
        },
        'desejaveis': {
            'tem': list(competencias_candidato.intersection(desejaveis)),
            'falta': list(desejaveis - competencias_candidato),
            'score': round(score_desejaveis, 1)
        },
        'diferenciais': {
            'tem': list(competencias_candidato.intersection(diferenciais)),
            'falta': list(diferenciais - competencias_candidato),
            'score': round(score_diferenciais, 1)
        }
    }

    return round(score_tecnico, 1), analise_detalhada


def calcular_score_final(candidato, vaga, peso_cultural=0.4, peso_tecnico=0.6):
    """Calcula score final combinando fit cultural e técnico"""

    fit_cultural, detalhes_cultural = calcular_fit_cultural(candidato, vaga)
    fit_tecnico, detalhes_tecnico = calcular_fit_tecnico(candidato, vaga)

    # Score final ponderado
    score_final = (fit_cultural * peso_cultural) + (fit_tecnico * peso_tecnico)

    # Análise de performance histórica (bonus)
    performance = candidato.get('performance.metas_atingidas_percentual', 75)
    engajamento = candidato.get('engajamento.enps_recente', 5)

    bonus_performance = 0
    if performance > 90:
        bonus_performance += 5
    elif performance > 80:
        bonus_performance += 2

    if engajamento > 8:
        bonus_performance += 3
    elif engajamento > 6:
        bonus_performance += 1

    score_final_ajustado = min(100, score_final + bonus_performance)

    return {
        'score_final': round(score_final_ajustado, 1),
        'fit_cultural': fit_cultural,
        'fit_tecnico': fit_tecnico,
        'bonus_performance': bonus_performance,
        'detalhes_cultural': detalhes_cultural,
        'detalhes_tecnico': detalhes_tecnico,
        'classificacao': (
            'Candidato Ideal' if score_final_ajustado >= 85 else
            'Forte Candidato' if score_final_ajustado >= 70 else
            'Candidato Viável' if score_final_ajustado >= 55 else
            'Requer Atenção'
        )
    }


def gerar_insights_claude(candidato, vaga, analise_fit):
    """Gera insights detalhados usando Claude AI"""

    contexto = {
        'candidato': {
            'nome': candidato.get('nome', 'N/A'),
            'cargo_atual': candidato.get('cargo', 'N/A'),
            'experiencia_meses': candidato.get('tempo_de_casa_meses', 0),
            'big_five': {
                'abertura': candidato.get('perfil_big_five.abertura_a_experiencia', 5),
                'conscienciosidade': candidato.get('perfil_big_five.conscienciosidade', 5),
                'extroversao': candidato.get('perfil_big_five.extroversao', 5),
                'amabilidade': candidato.get('perfil_big_five.amabilidade', 5),
                'neuroticismo': candidato.get('perfil_big_five.neuroticismo', 5)
            },
            'competencias': candidato.get('competencias', []),
            'performance': candidato.get('performance.metas_atingidas_percentual', 0),
            'engajamento': candidato.get('engajamento.enps_recente', 5)
        },
        'vaga': vaga,
        'analise_fit': analise_fit
    }

    prompt = f"""
Você é um especialista em recrutamento e seleção com PhD em Psicologia Organizacional. 

Analise este candidato para a vaga:

CANDIDATO:
{json.dumps(contexto['candidato'], indent=2, ensure_ascii=False)}

VAGA:
{json.dumps(contexto['vaga'], indent=2, ensure_ascii=False)}

ANÁLISE DE FIT:
{json.dumps(contexto['analise_fit'], indent=2, ensure_ascii=False)}

TAREFA:
Forneça uma análise detalhada e acionável sobre:

1. **RESUMO EXECUTIVO** - Recomendação final (contratar/não contratar) e justificativa
2. **PONTOS FORTES** - O que mais impressiona neste candidato para esta vaga
3. **PONTOS DE ATENÇÃO** - Riscos ou gaps que precisam ser endereçados
4. **FIT CULTURAL** - Como a personalidade se alinha com o perfil ideal
5. **FIT TÉCNICO** - Análise das competências vs requisitos
6. **PLANO DE INTEGRAÇÃO** - Se contratado, como maximizar o sucesso
7. **PERGUNTAS SUGERIDAS** - 3-4 perguntas específicas para entrevista

Use linguagem profissional, seja específico e acionável. Base suas conclusões nos dados fornecidos.

FORMATO: Use markdown com seções bem definidas.
"""

    try:
        response = claude_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    except Exception as e:
        return f"❌ Erro ao gerar insights: {str(e)}"

# --- Interface Principal ---


def main():
    # Carregar dados
    vagas = carregar_dados(VAGAS_DIR)
    agentes = carregar_dados(AGENTS_DIR)

    # Se não há vagas, criar exemplo
    if not vagas:
        st.warning("⚠️ Nenhuma vaga encontrada. Usando vaga de exemplo.")
        vagas = criar_vaga_exemplo()

    if not agentes:
        st.error(
            "❌ Nenhum candidato encontrado. Execute 'generate_agents.py' primeiro.")
        st.stop()

    # --- Sidebar: Configurações ---
    st.sidebar.header("🔧 Configurações de Análise")

    # Pesos para cálculo de fit
    peso_cultural = st.sidebar.slider(
        "🎭 Peso Fit Cultural:", 0.0, 1.0, 0.4, 0.1)
    peso_tecnico = 1.0 - peso_cultural
    st.sidebar.write(f"⚙️ Peso Fit Técnico: {peso_tecnico:.1f}")

    st.sidebar.divider()

    # Filtros
    df_agentes = pd.DataFrame.from_dict(agentes, orient='index')

    departamentos = ['Todos'] + \
        sorted(df_agentes['departamento'].unique().tolist())
    dept_filtro = st.sidebar.selectbox(
        "Filtrar candidatos por departamento:", departamentos)

    if dept_filtro != 'Todos':
        df_agentes = df_agentes[df_agentes['departamento'] == dept_filtro]

    st.sidebar.write(f"📊 Candidatos disponíveis: {len(df_agentes)}")

    # --- Seleção de Vaga ---
    st.header("🎯 Seleção de Vaga")

    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        vaga_selecionada_id = st.selectbox(
            "Escolha a vaga para análise:",
            options=list(vagas.keys()),
            format_func=lambda x: f"{vagas[x]['titulo_vaga']} ({vagas[x]['departamento']})"
        )
        vaga_selecionada = vagas[vaga_selecionada_id]

    with col2:
        st.markdown("**📋 Detalhes da Vaga:**")
        st.write(f"**Título:** {vaga_selecionada['titulo_vaga']}")
        st.write(f"**Departamento:** {vaga_selecionada['departamento']}")
        st.write(f"**Nível:** {vaga_selecionada.get('nivel', 'N/A')}")

        if 'salario_min' in vaga_selecionada and 'salario_max' in vaga_selecionada:
            st.write(
                f"**Salário:** R$ {vaga_selecionada['salario_min']:,.0f} - R$ {vaga_selecionada['salario_max']:,.0f}")

    # Expandir detalhes da vaga
    with st.expander("🔍 Ver Detalhes Completos da Vaga"):
        st.json(vaga_selecionada)

    # --- Análise de Candidatos ---
    st.header("👥 Análise de Candidatos")

    # Calcular fit para todos os candidatos
    resultados_fit = []

    with st.spinner("🧮 Calculando fit para todos os candidatos..."):
        for idx, candidato in df_agentes.iterrows():
            analise = calcular_score_final(
                candidato, vaga_selecionada, peso_cultural, peso_tecnico
            )

            resultados_fit.append({
                'id': idx,
                'nome': candidato['nome'],
                'cargo_atual': candidato['cargo'],
                'departamento': candidato['departamento'],
                'score_final': analise['score_final'],
                'fit_cultural': analise['fit_cultural'],
                'fit_tecnico': analise['fit_tecnico'],
                'classificacao': analise['classificacao'],
                'analise_completa': analise
            })

    # Ordenar por score
    resultados_fit.sort(key=lambda x: x['score_final'], reverse=True)

    # --- Ranking de Candidatos ---
    st.subheader(
        f"🏆 Ranking de Candidatos para: {vaga_selecionada['titulo_vaga']}")

    # Métricas do processo
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👥 Total Candidatos", len(resultados_fit))

    with col2:
        candidatos_ideais = len(
            [r for r in resultados_fit if r['score_final'] >= 85])
        st.metric("⭐ Candidatos Ideais", candidatos_ideais)

    with col3:
        score_medio = np.mean([r['score_final'] for r in resultados_fit])
        st.metric("📊 Score Médio", f"{score_medio:.1f}")

    with col4:
        melhor_score = resultados_fit[0]['score_final'] if resultados_fit else 0
        st.metric("🥇 Melhor Score", f"{melhor_score:.1f}")

    # Tabela de ranking
    df_ranking = pd.DataFrame(resultados_fit)

    def colorir_classificacao(val):
        cores = {
            'Candidato Ideal': 'background-color: #d4edda; color: #155724',
            'Forte Candidato': 'background-color: #d1ecf1; color: #0c5460',
            'Candidato Viável': 'background-color: #fff3cd; color: #856404',
            'Requer Atenção': 'background-color: #f8d7da; color: #721c24'
        }
        return cores.get(val, '')

    st.dataframe(
        df_ranking[['nome', 'cargo_atual', 'score_final',
                    'fit_cultural', 'fit_tecnico', 'classificacao']]
        .style.format({
            'score_final': '{:.1f}',
            'fit_cultural': '{:.1f}',
            'fit_tecnico': '{:.1f}'
        })
        .applymap(colorir_classificacao, subset=['classificacao'])
        .background_gradient(subset=['score_final'], cmap='RdYlGn'),
        use_container_width=True
    )

    # --- Análise Individual Detalhada ---
    st.header("🔍 Análise Individual Detalhada")

    candidato_selecionado_id = st.selectbox(
        "Selecione um candidato para análise detalhada:",
        options=[r['id'] for r in resultados_fit],
        format_func=lambda x: f"{next(r['nome'] for r in resultados_fit if r['id'] == x)} (Score: {next(r['score_final'] for r in resultados_fit if r['id'] == x):.1f})"
    )

    # Dados do candidato selecionado
    candidato_dados = df_agentes.loc[candidato_selecionado_id]
    resultado_candidato = next(
        r for r in resultados_fit if r['id'] == candidato_selecionado_id)
    analise_completa = resultado_candidato['analise_completa']

    # Layout em colunas
    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        st.subheader(f"👤 {candidato_dados['nome']}")

        # Scores principais
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("🎯 Score Final",
                      f"{analise_completa['score_final']:.1f}%")
        with col_b:
            st.metric("🎭 Fit Cultural",
                      f"{analise_completa['fit_cultural']:.1f}%")
        with col_c:
            st.metric("⚙️ Fit Técnico",
                      f"{analise_completa['fit_tecnico']:.1f}%")

        # Classificação
        classificacao = analise_completa['classificacao']
        if classificacao == 'Candidato Ideal':
            st.success(f"✅ **{classificacao}**")
        elif classificacao == 'Forte Candidato':
            st.info(f"💙 **{classificacao}**")
        elif classificacao == 'Candidato Viável':
            st.warning(f"⚠️ **{classificacao}**")
        else:
            st.error(f"❌ **{classificacao}**")

        # Análise de fit cultural detalhada
        st.markdown("#### 🎭 Análise de Fit Cultural (Big Five)")

        detalhes_cultural = analise_completa['detalhes_cultural']

        for dimensao, dados in detalhes_cultural.items():
            nome_dim = dimensao.replace('_', ' ').title()

            col_dim1, col_dim2, col_dim3 = st.columns([0.3, 0.4, 0.3])
            with col_dim1:
                st.write(f"**{nome_dim}:**")
            with col_dim2:
                st.write(
                    f"Candidato: {dados['candidato']:.1f} | Ideal: {dados['ideal']:.1f}")
            with col_dim3:
                status = dados['status']
                if status == 'Excelente':
                    st.success(status)
                elif status == 'Bom':
                    st.info(status)
                elif status == 'Atenção':
                    st.warning(status)
                else:
                    st.error(status)

        # Análise técnica detalhada
        st.markdown("#### ⚙️ Análise de Fit Técnico")

        detalhes_tecnico = analise_completa['detalhes_tecnico']

        for categoria, dados in detalhes_tecnico.items():
            nome_cat = categoria.title()

            with st.expander(f"📋 {nome_cat} (Score: {dados['score']:.1f}%)"):
                if dados['tem']:
                    st.success(f"✅ **Tem:** {', '.join(dados['tem'])}")

                if dados['falta']:
                    st.error(f"❌ **Falta:** {', '.join(dados['falta'])}")

                if not dados['tem'] and not dados['falta']:
                    st.info("ℹ️ Nenhuma competência nesta categoria")

    with col2:
        # Gráfico radar comparativo
        st.markdown("#### 📊 Comparativo Big Five")

        categorias = list(vaga_selecionada['perfil_ideal_big_five'].keys())
        categorias_display = [cat.replace(
            '_', ' ').title() for cat in categorias]

        valores_candidato = [candidato_dados.get(
            f'perfil_big_five.{cat}', 5) for cat in categorias]
        valores_ideal = list(
            vaga_selecionada['perfil_ideal_big_five'].values())

        fig_radar = go.Figure()

        fig_radar.add_trace(go.Scatterpolar(
            r=valores_ideal,
            theta=categorias_display,
            fill='toself',
            name='Perfil Ideal',
            opacity=0.5,
            fillcolor='rgba(255, 0, 0, 0.3)',
            line=dict(color='red')
        ))

        fig_radar.add_trace(go.Scatterpolar(
            r=valores_candidato,
            theta=categorias_display,
            fill='toself',
            name=candidato_dados['nome'],
            opacity=0.7,
            fillcolor='rgba(0, 0, 255, 0.3)',
            line=dict(color='blue')
        ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            title="Candidato vs Perfil Ideal",
            height=400
        )

        st.plotly_chart(fig_radar, use_container_width=True)

        # Informações adicionais
        st.markdown("#### 📋 Informações Gerais")
        st.write(f"**Cargo Atual:** {candidato_dados['cargo']}")
        st.write(f"**Departamento:** {candidato_dados['departamento']}")
        st.write(
            f"**Experiência:** {candidato_dados.get('tempo_de_casa_meses', 0)} meses")

        performance = candidato_dados.get(
            'performance.metas_atingidas_percentual', 0)
        engajamento = candidato_dados.get('engajamento.enps_recente', 5)

        st.write(f"**Performance:** {performance:.1f}%")
        st.write(f"**eNPS:** {engajamento}/10")

        if analise_completa['bonus_performance'] > 0:
            st.success(
                f"🎁 Bônus Performance: +{analise_completa['bonus_performance']} pontos")

    # --- Insights do Claude AI ---
    st.header("🧠 Análise Avançada (Claude AI)")

    if st.button("🚀 Gerar Análise Detalhada", type="primary"):
        with st.spinner("🤖 Claude AI analisando candidato..."):
            insights = gerar_insights_claude(
                candidato_dados, vaga_selecionada, analise_completa)

        st.markdown("### 📝 Relatório de Análise")
        st.markdown(insights)

    # --- Comparação com Top Candidatos ---
    st.header("📊 Comparação com Top Candidatos")

    top_candidatos = resultados_fit[:5]  # Top 5

    if len(top_candidatos) > 1:
        # Gráfico de comparação
        nomes = [r['nome'] for r in top_candidatos]
        scores_finais = [r['score_final'] for r in top_candidatos]
        scores_culturais = [r['fit_cultural'] for r in top_candidatos]
        scores_tecnicos = [r['fit_tecnico'] for r in top_candidatos]

        fig_comp = go.Figure()

        fig_comp.add_trace(go.Bar(
            name='Score Final',
            x=nomes,
            y=scores_finais,
            marker_color='lightblue'
        ))

        fig_comp.add_trace(go.Bar(
            name='Fit Cultural',
            x=nomes,
            y=scores_culturais,
            marker_color='lightgreen'
        ))

        fig_comp.add_trace(go.Bar(
            name='Fit Técnico',
            x=nomes,
            y=scores_tecnicos,
            marker_color='lightcoral'
        ))

        fig_comp.update_layout(
            title="Comparação Top 5 Candidatos",
            xaxis_title="Candidatos",
            yaxis_title="Score (%)",
            barmode='group',
            height=400
        )

        st.plotly_chart(fig_comp, use_container_width=True)

    # --- Export/Save ---
    st.header("💾 Exportar Resultados")

    if st.button("📊 Gerar Relatório de Fit Analysis"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        relatorio = {
            "timestamp": timestamp,
            "vaga": vaga_selecionada,
            "configuracao_pesos": {
                "cultural": peso_cultural,
                "tecnico": peso_tecnico
            },
            "total_candidatos": len(resultados_fit),
            "top_candidatos": resultados_fit[:10],  # Top 10
            "candidato_analisado": {
                "id": candidato_selecionado_id,
                "dados": candidato_dados.to_dict(),
                "analise_completa": analise_completa
            }
        }

        st.json(relatorio)
        st.success("✅ Relatório gerado! Copie o JSON acima para salvar.")


if __name__ == "__main__":
    main()

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
🎯 <strong>Análise de Fit</strong> - HumaniQ AI<br>
Powered by Claude AI da Anthropic | Fit cultural + técnico com precisão científica
</div>
""", unsafe_allow_html=True)
