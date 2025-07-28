import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Cultural Fit Evolution",
                   page_icon="🧭", layout="wide")

st.title("🧭 Cultural Fit Evolution")
st.markdown("""
**Acompanha evolução cultural da empresa ao longo do tempo**

Sistema que trackea mudanças culturais, identifica resistências, mapeia influenciadores e sugere estratégias de transformação em setores chave.
""")

# --- Dimensões Culturais ---
DIMENSOES_HOFSTEDE = {
    'distancia_poder': {
        'nome': 'Distância do Poder',
        'descricao': 'Aceitação de hierarquia e desigualdade de poder',
        'baixo': 'Hierarquia horizontal, decisões democráticas',
        'alto': 'Hierarquia vertical, concentração de poder'
    },
    'individualismo': {
        'nome': 'Individualismo',
        'descricao': 'Foco individual vs coletivo',
        'baixo': 'Foco em grupo, lealdade coletiva',
        'alto': 'Autonomia individual, meritocracia'
    },
    'masculinidade': {
        'nome': 'Orientação para Resultados',
        'descricao': 'Foco em resultados vs qualidade de vida',
        'baixo': 'Cooperação, qualidade de vida',
        'alto': 'Competição, assertividade, resultados'
    },
    'aversao_incerteza': {
        'nome': 'Aversão à Incerteza',
        'descricao': 'Tolerância a ambiguidade e mudanças',
        'baixo': 'Flexibilidade, adaptabilidade',
        'alto': 'Estrutura, regras, previsibilidade'
    },
    'orientacao_temporal': {
        'nome': 'Orientação Temporal',
        'descricao': 'Foco curto vs longo prazo',
        'baixo': 'Tradição, estabilidade, curto prazo',
        'alto': 'Adaptação, pragmatismo, longo prazo'
    },
    'indulgencia': {
        'nome': 'Indulgência',
        'descricao': 'Liberdade vs controle de impulsos',
        'baixo': 'Controle, normas rígidas',
        'alto': 'Liberdade, espontaneidade'
    }
}

VALORES_ORGANIZACIONAIS = [
    'Inovação', 'Colaboração', 'Transparência', 'Diversidade',
    'Sustentabilidade', 'Excelência', 'Agilidade', 'Cliente-centrismo',
    'Integridade', 'Bem-estar', 'Aprendizado', 'Autonomia'
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


def mapear_big_five_para_hofstede(funcionario):
    """Mapeia perfil Big Five para dimensões de Hofstede"""

    # Extrair Big Five
    abertura = funcionario.get('perfil_big_five.abertura_a_experiencia', 5)
    conscienciosidade = funcionario.get('perfil_big_five.conscienciosidade', 5)
    extroversao = funcionario.get('perfil_big_five.extroversao', 5)
    amabilidade = funcionario.get('perfil_big_five.amabilidade', 5)
    neuroticismo = funcionario.get('perfil_big_five.neuroticismo', 5)

    # Mapeamentos baseados em pesquisa psicológica cross-cultural
    hofstede = {
        'distancia_poder': max(1, min(10, 10 - amabilidade + (10 - extroversao) * 0.5)),
        'individualismo': max(1, min(10, extroversao + (10 - amabilidade) * 0.3 + abertura * 0.2)),
        'masculinidade': max(1, min(10, extroversao + conscienciosidade * 0.5 + (10 - amabilidade) * 0.3)),
        'aversao_incerteza': max(1, min(10, neuroticismo + conscienciosidade * 0.4)),
        'orientacao_temporal': max(1, min(10, conscienciosidade + abertura * 0.3)),
        'indulgencia': max(1, min(10, (10 - neuroticismo) + extroversao * 0.4 + abertura * 0.2))
    }

    return hofstede


def calcular_perfil_cultural_organizacional(df_funcionarios):
    """Calcula o perfil cultural médio da organização"""
    if df_funcionarios.empty:
        return {}

    perfis_hofstede = []
    for _, funcionario in df_funcionarios.iterrows():
        perfil = mapear_big_five_para_hofstede(funcionario)
        perfis_hofstede.append(perfil)

    df_hofstede = pd.DataFrame(perfis_hofstede)
    perfil_medio = df_hofstede.mean().to_dict()

    return perfil_medio


def simular_evolucao_cultural(perfil_base, meses=12):
    """Simula a evolução cultural ao longo do tempo"""
    evolucao = []
    perfil_atual = perfil_base.copy()

    # Tendências de mudança simuladas
    tendencias = {
        'distancia_poder': -0.1,  # Tendência para menos hierarquia
        'individualismo': 0.05,   # Ligeiro aumento do individualismo
        'masculinidade': -0.08,   # Menos foco em competição
        'aversao_incerteza': -0.12,  # Mais tolerância à incerteza
        'orientacao_temporal': 0.15,  # Mais foco longo prazo
        'indulgencia': 0.1       # Mais liberdade
    }

    for mes in range(meses + 1):
        data = datetime.now() - timedelta(days=30 * (meses - mes))

        # Adicionar ruído e tendências
        perfil_mes = {}
        for dimensao, valor in perfil_atual.items():
            tendencia = tendencias.get(dimensao, 0)
            ruido = random.gauss(0, 0.3)  # Variação aleatória
            novo_valor = valor + tendencia + ruido
            perfil_mes[dimensao] = max(1, min(10, novo_valor))

        evolucao.append({
            'data': data,
            'mes': data.strftime('%Y-%m'),
            **perfil_mes
        })

        # Atualizar perfil para próximo mês
        perfil_atual = perfil_mes

    return pd.DataFrame(evolucao)


def identificar_influenciadores_culturais(df_funcionarios):
    """Identifica funcionários com maior influência cultural"""
    influenciadores = []

    for idx, funcionario in df_funcionarios.iterrows():
        # Score de influência baseado em múltiplos fatores

        # Tempo na empresa (influência por senioridade)
        tempo_casa = funcionario.get('tempo_de_casa_meses', 12)
        score_senioridade = min(tempo_casa / 36, 1) * 25  # Máximo 25 pts

        # Performance (influência por resultados)
        ultima_avaliacao = funcionario.get(
            'performance.avaliacoes_desempenho', [{}])
        if isinstance(ultima_avaliacao, list) and ultima_avaliacao:
            nota = ultima_avaliacao[-1].get('nota', 7)
        else:
            nota = 7
        score_performance = (nota / 10) * 20  # Máximo 20 pts

        # Extroversão (influência social)
        extroversao = funcionario.get('perfil_big_five.extroversao', 5)
        score_social = (extroversao / 10) * 15  # Máximo 15 pts

        # Amabilidade (influência positiva)
        amabilidade = funcionario.get('perfil_big_five.amabilidade', 5)
        score_positivo = (amabilidade / 10) * 10  # Máximo 10 pts

        # Engajamento
        enps = funcionario.get('engajamento.enps_recente', 5)
        score_engajamento = (enps / 10) * 15  # Máximo 15 pts

        # Cargo (influência hierárquica)
        cargo = funcionario.get('cargo', '')
        if 'Gerente' in cargo:
            score_hierarquia = 15
        elif 'Analista' in cargo:
            score_hierarquia = 5
        else:
            score_hierarquia = 10

        score_total = (score_senioridade + score_performance + score_social +
                       score_positivo + score_engajamento + score_hierarquia)

        influenciadores.append({
            'id': idx,
            'nome': funcionario['nome'],
            'cargo': funcionario['cargo'],
            'departamento': funcionario['departamento'],
            'score_influencia': round(score_total, 1),
            'tempo_casa': tempo_casa,
            'performance': nota,
            'extroversao': extroversao,
            'amabilidade': amabilidade,
            'enps': enps
        })

    return sorted(influenciadores, key=lambda x: x['score_influencia'], reverse=True)


def detectar_resistencias_mudanca(df_funcionarios, mudanca_cultural_desejada):
    """Detecta funcionários com possível resistência a mudanças culturais"""
    resistencias = []

    for idx, funcionario in df_funcionarios.iterrows():
        perfil_atual = mapear_big_five_para_hofstede(funcionario)
        score_resistencia = 0
        fatores_resistencia = []

        # Baixa abertura à experiência = resistência a mudanças
        abertura = funcionario.get('perfil_big_five.abertura_a_experiencia', 5)
        if abertura < 4:
            score_resistencia += 25
            fatores_resistencia.append("Baixa abertura a experiências")

        # Alto neuroticismo = ansiedade com mudanças
        neuroticismo = funcionario.get('perfil_big_five.neuroticismo', 5)
        if neuroticismo > 7:
            score_resistencia += 20
            fatores_resistencia.append("Alto nível de ansiedade")

        # Muito tempo na empresa = resistência por hábito
        tempo_casa = funcionario.get('tempo_de_casa_meses', 12)
        if tempo_casa > 48:  # Mais de 4 anos
            score_resistencia += 15
            fatores_resistencia.append("Funcionário muito experiente")

        # Baixo engajamento = desinteresse em mudanças
        enps = funcionario.get('engajamento.enps_recente', 5)
        if enps < 4:
            score_resistencia += 20
            fatores_resistencia.append("Baixo engajamento")

        # Performance baixa = foco em sobrevivência vs mudança
        ultima_avaliacao = funcionario.get(
            'performance.avaliacoes_desempenho', [{}])
        if isinstance(ultima_avaliacao, list) and ultima_avaliacao:
            nota = ultima_avaliacao[-1].get('nota', 7)
        else:
            nota = 7

        if nota < 6:
            score_resistencia += 20
            fatores_resistencia.append("Performance abaixo da média")

        # Resistência específica baseada na mudança desejada
        for dimensao, direcao in mudanca_cultural_desejada.items():
            valor_atual = perfil_atual.get(dimensao, 5)
            if direcao == 'aumentar' and valor_atual > 8:
                score_resistencia += 10
                fatores_resistencia.append(
                    f"Já tem alto {DIMENSOES_HOFSTEDE[dimensao]['nome']}")
            elif direcao == 'diminuir' and valor_atual < 3:
                score_resistencia += 10
                fatores_resistencia.append(
                    f"Já tem baixo {DIMENSOES_HOFSTEDE[dimensao]['nome']}")

        if score_resistencia > 30:  # Threshold para ser considerado resistente
            resistencias.append({
                'id': idx,
                'nome': funcionario['nome'],
                'cargo': funcionario['cargo'],
                'departamento': funcionario['departamento'],
                'score_resistencia': score_resistencia,
                'fatores': fatores_resistencia
            })

    return sorted(resistencias, key=lambda x: x['score_resistencia'], reverse=True)


def gerar_estrategias_transformacao(perfil_atual, perfil_desejado, influenciadores, resistentes):
    """Gera estratégias personalizadas de transformação cultural"""
    estrategias = []

    # Análise de gaps
    gaps = {}
    for dimensao, valor_desejado in perfil_desejado.items():
        valor_atual = perfil_atual.get(dimensao, 5)
        gap = valor_desejado - valor_atual
        gaps[dimensao] = gap

    # Estratégias baseadas nos maiores gaps
    maiores_gaps = sorted(gaps.items(), key=lambda x: abs(x[1]), reverse=True)

    for dimensao, gap in maiores_gaps[:3]:  # Top 3 gaps
        if abs(gap) > 1:  # Só se o gap for significativo
            nome_dimensao = DIMENSOES_HOFSTEDE[dimensao]['nome']

            if gap > 0:  # Precisa aumentar
                if dimensao == 'individualismo':
                    estrategias.append({
                        'dimensao': nome_dimensao,
                        'objetivo': f'Aumentar {nome_dimensao.lower()}',
                        'gap': f'+{gap:.1f}',
                        'acoes': [
                            'Implementar OKRs individuais',
                            'Reconhecimento por mérito individual',
                            'Autonomia para tomada de decisões',
                            'Programas de desenvolvimento pessoal'
                        ],
                        'influenciadores_chave': [inf['nome'] for inf in influenciadores[:2]],
                        'timeline': '6-9 meses'
                    })
                elif dimensao == 'orientacao_temporal':
                    estrategias.append({
                        'dimensao': nome_dimensao,
                        'objetivo': f'Aumentar {nome_dimensao.lower()}',
                        'gap': f'+{gap:.1f}',
                        'acoes': [
                            'Planejamento estratégico de longo prazo',
                            'Métricas de sustentabilidade',
                            'Investimento em inovação',
                            'Cultura de experimentação'
                        ],
                        'influenciadores_chave': [inf['nome'] for inf in influenciadores[:2]],
                        'timeline': '12-18 meses'
                    })
                elif dimensao == 'indulgencia':
                    estrategias.append({
                        'dimensao': nome_dimensao,
                        'objetivo': f'Aumentar {nome_dimensao.lower()}',
                        'gap': f'+{gap:.1f}',
                        'acoes': [
                            'Flexibilização de horários',
                            'Espaços de descompressão',
                            'Eventos sociais regulares',
                            'Dress code mais relaxado'
                        ],
                        'influenciadores_chave': [inf['nome'] for inf in influenciadores[:2]],
                        'timeline': '3-6 meses'
                    })
            else:  # Precisa diminuir
                if dimensao == 'distancia_poder':
                    estrategias.append({
                        'dimensao': nome_dimensao,
                        'objetivo': f'Diminuir {nome_dimensao.lower()}',
                        'gap': f'{gap:.1f}',
                        'acoes': [
                            'Estrutura organizacional mais horizontal',
                            'Decisões participativas',
                            'Open door policy',
                            'Feedback 360 graus'
                        ],
                        'influenciadores_chave': [inf['nome'] for inf in influenciadores[:2]],
                        'timeline': '9-12 meses'
                    })
                elif dimensao == 'aversao_incerteza':
                    estrategias.append({
                        'dimensao': nome_dimensao,
                        'objetivo': f'Diminuir {nome_dimensao.lower()}',
                        'gap': f'{gap:.1f}',
                        'acoes': [
                            'Metodologias ágeis',
                            'Cultura de fail fast',
                            'Experimentação e prototipagem',
                            'Menos burocracia'
                        ],
                        'influenciadores_chave': [inf['nome'] for inf in influenciadores[:2]],
                        'timeline': '6-12 meses'
                    })

    # Estratégias para lidar com resistências
    if resistentes:
        estrategias.append({
            'dimensao': 'Gestão de Resistências',
            'objetivo': 'Engajar funcionários resistentes',
            'gap': f'{len(resistentes)} pessoas',
            'acoes': [
                'Comunicação transparente sobre mudanças',
                'Envolvimento na co-criação da nova cultura',
                'Treinamentos de change management',
                'Mentoria por influenciadores positivos'
            ],
            'influenciadores_chave': [inf['nome'] for inf in influenciadores[:3]],
            'timeline': 'Contínuo'
        })

    return estrategias


# --- Interface Principal ---
df_agentes = carregar_agentes()

if df_agentes.empty:
    st.warning(
        "⚠️ Nenhum agente encontrado. Execute o script generate_agents.py primeiro.")
    st.stop()

# --- Perfil Cultural Atual ---
st.header("🎭 Perfil Cultural Atual da Organização")

perfil_atual = calcular_perfil_cultural_organizacional(df_agentes)

col1, col2 = st.columns([0.6, 0.4])

with col1:
    # Gráfico radar do perfil cultural
    if perfil_atual:
        dimensoes = list(DIMENSOES_HOFSTEDE.keys())
        nomes_dimensoes = [DIMENSOES_HOFSTEDE[d]['nome'] for d in dimensoes]
        valores_atuais = [perfil_atual[d] for d in dimensoes]

        fig_cultural = go.Figure()

        fig_cultural.add_trace(go.Scatterpolar(
            r=valores_atuais,
            theta=nomes_dimensoes,
            fill='toself',
            name='Perfil Atual',
            fillcolor='rgba(0, 100, 200, 0.3)',
            line=dict(color='rgb(0, 100, 200)')
        ))

        fig_cultural.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10])
            ),
            title="Perfil Cultural Hofstede da Organização"
        )

        st.plotly_chart(fig_cultural, use_container_width=True)

with col2:
    st.subheader("📊 Métricas Culturais")

    if perfil_atual:
        for dimensao, valor in perfil_atual.items():
            nome = DIMENSOES_HOFSTEDE[dimensao]['nome']
            st.metric(nome, f"{valor:.1f}/10")

        # Interpretação automática
        st.subheader("🔍 Interpretação")

        interpretacoes = []
        for dimensao, valor in perfil_atual.items():
            info = DIMENSOES_HOFSTEDE[dimensao]
            if valor > 7:
                interpretacoes.append(
                    f"**Alto {info['nome']}**: {info['alto']}")
            elif valor < 4:
                interpretacoes.append(
                    f"**Baixo {info['nome']}**: {info['baixo']}")

        if interpretacoes:
            for interp in interpretacoes:
                st.write(f"• {interp}")
        else:
            st.info("Perfil equilibrado em todas as dimensões.")

# --- Evolução Temporal ---
st.header("📈 Evolução Cultural ao Longo do Tempo")

# Simular dados históricos
df_evolucao = simular_evolucao_cultural(perfil_atual)

# Seletor de dimensões para visualizar
dimensoes_selecionadas = st.multiselect(
    "Selecione dimensões para visualizar:",
    options=list(DIMENSOES_HOFSTEDE.keys()),
    default=['individualismo', 'aversao_incerteza', 'orientacao_temporal'],
    format_func=lambda x: DIMENSOES_HOFSTEDE[x]['nome']
)

if dimensoes_selecionadas:
    fig_evolucao = go.Figure()

    for dimensao in dimensoes_selecionadas:
        nome = DIMENSOES_HOFSTEDE[dimensao]['nome']
        fig_evolucao.add_trace(go.Scatter(
            x=df_evolucao['data'],
            y=df_evolucao[dimensao],
            mode='lines+markers',
            name=nome,
            line=dict(width=3)
        ))

    fig_evolucao.update_layout(
        title="Evolução das Dimensões Culturais",
        xaxis_title="Período",
        yaxis_title="Score (0-10)",
        height=400,
        yaxis=dict(range=[0, 10])
    )

    st.plotly_chart(fig_evolucao, use_container_width=True)

# --- Influenciadores Culturais ---
st.header("🌟 Influenciadores Culturais")

influenciadores = identificar_influenciadores_culturais(df_agentes)

col1, col2 = st.columns([0.7, 0.3])

with col1:
    st.subheader("🏆 Top Influenciadores")

    # Tabela dos top influenciadores
    df_influenciadores = pd.DataFrame(influenciadores[:10])

    if not df_influenciadores.empty:
        st.dataframe(
            df_influenciadores[['nome', 'cargo', 'departamento', 'score_influencia', 'tempo_casa', 'performance']].style.format({
                'score_influencia': '{:.1f}',
                'performance': '{:.1f}',
                'tempo_casa': '{:.0f} meses'
            }).background_gradient(subset=['score_influencia'], cmap='viridis'),
            use_container_width=True
        )

with col2:
    st.subheader("📊 Distribuição")

    if influenciadores:
        # Top 5 influenciadores
        top_5 = influenciadores[:5]
        nomes = [inf['nome'].split()[0] for inf in top_5]  # Só primeiro nome
        scores = [inf['score_influencia'] for inf in top_5]

        fig_top = go.Figure(data=[
            go.Bar(
                x=scores,
                y=nomes,
                orientation='h',
                marker=dict(
                    color=scores,  # usar os valores para colorir
                    colorscale='viridis'
                )
            )
        ])

        fig_top.update_layout(
            title="Top 5 Influenciadores",
            xaxis_title="Score de Influência",
            height=300
        )

        st.plotly_chart(fig_top, use_container_width=True)

# --- Análise de Resistências ---
st.header("⚠️ Análise de Resistências")

# Definir mudança cultural desejada (exemplo)
mudanca_desejada = {
    'distancia_poder': 'diminuir',
    'aversao_incerteza': 'diminuir',
    'orientacao_temporal': 'aumentar',
    'indulgencia': 'aumentar'
}

resistentes = detectar_resistencias_mudanca(df_agentes, mudanca_desejada)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🚨 Funcionários Resistentes", len(resistentes))

with col2:
    if resistentes:
        score_medio = np.mean([r['score_resistencia'] for r in resistentes])
        st.metric("📊 Score Médio Resistência", f"{score_medio:.1f}")

with col3:
    percentual_resistente = len(resistentes) / len(df_agentes) * 100
    cor_delta = "inverse" if percentual_resistente > 20 else "normal"
    st.metric("📈 % Resistência",
              f"{percentual_resistente:.1f}%", delta_color=cor_delta)

if resistentes:
    with st.expander("🔍 Detalhes dos Funcionários Resistentes", expanded=False):
        for resistente in resistentes[:5]:  # Mostrar top 5
            st.write(
                f"**{resistente['nome']}** ({resistente['cargo']}) - Score: {resistente['score_resistencia']:.1f}")
            st.write(f"Fatores: {', '.join(resistente['fatores'])}")
            st.divider()

# --- Estratégias de Transformação ---
st.header("🚀 Estratégias de Transformação")

# Definir perfil cultural desejado
st.subheader("🎯 Definir Perfil Cultural Desejado")

with st.expander("⚙️ Configurar Perfil Alvo", expanded=False):
    perfil_desejado = {}

    col1, col2 = st.columns(2)
    dimensoes_lista = list(DIMENSOES_HOFSTEDE.keys())

    for i, dimensao in enumerate(dimensoes_lista):
        col = col1 if i % 2 == 0 else col2
        with col:
            nome = DIMENSOES_HOFSTEDE[dimensao]['nome']
            valor_atual = perfil_atual.get(dimensao, 5)
            valor_desejado = st.slider(
                f"{nome}:",
                0.0, 10.0, float(valor_atual), 0.1,
                help=DIMENSOES_HOFSTEDE[dimensao]['descricao']
            )
            perfil_desejado[dimensao] = valor_desejado

# Gerar estratégias
if st.button("🔮 Gerar Estratégias de Transformação", type="primary"):
    estrategias = gerar_estrategias_transformacao(
        perfil_atual, perfil_desejado, influenciadores, resistentes
    )

    st.success(f"✅ {len(estrategias)} estratégias geradas!")

    for i, estrategia in enumerate(estrategias):
        with st.expander(f"🎯 {estrategia['objetivo']} (Gap: {estrategia['gap']})", expanded=i == 0):
            col1, col2 = st.columns([0.7, 0.3])

            with col1:
                st.write("**Ações Recomendadas:**")
                for acao in estrategia['acoes']:
                    st.write(f"• {acao}")

                st.write(f"**Timeline:** {estrategia['timeline']}")

            with col2:
                st.write("**Influenciadores Chave:**")
                for influenciador in estrategia['influenciadores_chave']:
                    st.write(f"• {influenciador}")

                if st.button(f"📋 Criar Plano", key=f"plano_{i}"):
                    st.success("✅ Plano de transformação criado!")

# --- Comparação com Benchmarks ---
st.header("🏢 Comparação com Benchmarks Setoriais")

# Simular benchmarks de mercado
benchmarks = {
    'Tecnologia': {'individualismo': 7.5, 'aversao_incerteza': 4.2, 'orientacao_temporal': 8.1, 'indulgencia': 7.3},
    'Financeiro': {'individualismo': 6.8, 'aversao_incerteza': 6.5, 'orientacao_temporal': 7.2, 'indulgencia': 5.1},
    'Startups': {'individualismo': 8.2, 'aversao_incerteza': 3.1, 'orientacao_temporal': 8.8, 'indulgencia': 8.5},
    'Tradicional': {'individualismo': 5.2, 'aversao_incerteza': 7.8, 'orientacao_temporal': 6.1, 'indulgencia': 4.2}
}

setor_selecionado = st.selectbox(
    "Comparar com benchmark do setor:",
    options=list(benchmarks.keys())
)

if setor_selecionado:
    benchmark = benchmarks[setor_selecionado]

    # Gráfico comparativo
    dimensoes_comp = ['individualismo', 'aversao_incerteza',
                      'orientacao_temporal', 'indulgencia']
    nomes_comp = [DIMENSOES_HOFSTEDE[d]['nome'] for d in dimensoes_comp]

    valores_empresa = [perfil_atual.get(d, 5) for d in dimensoes_comp]
    valores_benchmark = [benchmark.get(d, 5) for d in dimensoes_comp]

    fig_comp = go.Figure()

    fig_comp.add_trace(go.Scatterpolar(
        r=valores_empresa,
        theta=nomes_comp,
        fill='toself',
        name='Nossa Empresa',
        fillcolor='rgba(0, 100, 200, 0.3)'
    ))

    fig_comp.add_trace(go.Scatterpolar(
        r=valores_benchmark,
        theta=nomes_comp,
        fill='toself',
        name=f'Benchmark {setor_selecionado}',
        fillcolor='rgba(200, 100, 0, 0.3)'
    ))

    fig_comp.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        title=f"Comparação com Benchmark {setor_selecionado}"
    )

    st.plotly_chart(fig_comp, use_container_width=True)

    # Análise de gaps
    st.subheader("📊 Análise de Gaps")

    gaps_benchmark = []
    for dimensao in dimensoes_comp:
        valor_nosso = perfil_atual.get(dimensao, 5)
        valor_benchmark = benchmark.get(dimensao, 5)
        gap = valor_benchmark - valor_nosso

        gaps_benchmark.append({
            'Dimensão': DIMENSOES_HOFSTEDE[dimensao]['nome'],
            'Nossa Empresa': valor_nosso,
            'Benchmark': valor_benchmark,
            'Gap': gap,
            'Status': 'Acima' if gap < -0.5 else 'Abaixo' if gap > 0.5 else 'Alinhado'
        })

    df_gaps = pd.DataFrame(gaps_benchmark)

    st.dataframe(
        df_gaps.style.format({
            'Nossa Empresa': '{:.1f}',
            'Benchmark': '{:.1f}',
            'Gap': '{:.1f}'
        }).applymap(
            lambda x: 'background-color: #ffcccc' if x == 'Abaixo'
            else 'background-color: #ccffcc' if x == 'Alinhado'
            else 'background-color: #ffffcc', subset=['Status']
        ),
        use_container_width=True
    )

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
🧭 <strong>Cultural Fit Evolution</strong> - HumaniQ AI<br>
Transformação cultural inteligente baseada em ciência comportamental e analytics preditivo
</div>
""", unsafe_allow_html=True)
