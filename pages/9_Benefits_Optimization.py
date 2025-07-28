import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Benefits Optimization",
                   page_icon="💎", layout="wide")

st.title("💎 Benefits Optimization")
st.markdown("""
**Personalização inteligente de benefícios por funcionário usando IA**

Sistema que mapeia preferências individuais, prediz necessidades futuras e otimiza custos através de marketplace interno e ajustes automáticos.
""")

# --- Dados de Benefícios ---
CATALOGO_BENEFICIOS = {
    'VR': {'custo_mensal': 600, 'categoria': 'Alimentação', 'flexivel': True},
    'VA': {'custo_mensal': 400, 'categoria': 'Alimentação', 'flexivel': True},
    'Plano_Saude': {'custo_mensal': 450, 'categoria': 'Saúde', 'flexivel': False},
    'Plano_Dental': {'custo_mensal': 50, 'categoria': 'Saúde', 'flexivel': True},
    'Seguro_Vida': {'custo_mensal': 30, 'categoria': 'Proteção', 'flexivel': False},
    'Auxilio_Creche': {'custo_mensal': 800, 'categoria': 'Família', 'flexivel': True},
    'Auxilio_Educacao': {'custo_mensal': 500, 'categoria': 'Desenvolvimento', 'flexivel': True},
    'Gympass': {'custo_mensal': 80, 'categoria': 'Bem-estar', 'flexivel': True},
    'Auxilio_Internet': {'custo_mensal': 100, 'categoria': 'Home Office', 'flexivel': True},
    'Auxilio_Transporte': {'custo_mensal': 250, 'categoria': 'Mobilidade', 'flexivel': True},
    'Day_Off_Extra': {'custo_mensal': 200, 'categoria': 'Tempo', 'flexivel': True},
    'Auxilio_Psicologico': {'custo_mensal': 200, 'categoria': 'Saúde Mental', 'flexivel': True},
    'Previdencia_Privada': {'custo_mensal': 300, 'categoria': 'Futuro', 'flexivel': True},
    'Coworking': {'custo_mensal': 150, 'categoria': 'Home Office', 'flexivel': True},
    'Massagem_Corporativa': {'custo_mensal': 120, 'categoria': 'Bem-estar', 'flexivel': True}
}

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


def gerar_lifestyle_profile(funcionario):
    """Gera perfil de lifestyle baseado nos dados do funcionário"""

    # Fatores que influenciam preferências de benefícios
    idade_simulada = random.randint(22, 55)  # Simular idade
    tem_filhos = random.choice([True, False])
    modalidade_trabalho = random.choice(['Presencial', 'Híbrido', 'Remoto'])
    transporte = random.choice(
        ['Carro', 'Transporte Público', 'Bicicleta', 'Caminhada'])

    # Estilo de vida baseado em personalidade
    extroversao = funcionario.get('perfil_big_five.extroversao', 5)
    conscienciosidade = funcionario.get('perfil_big_five.conscienciosidade', 5)
    abertura = funcionario.get('perfil_big_five.abertura_a_experiencia', 5)
    neuroticismo = funcionario.get('perfil_big_five.neuroticismo', 5)

    # Preferências derivadas da personalidade
    prefere_saude_mental = neuroticismo > 6
    prefere_desenvolvimento = abertura > 7 and conscienciosidade > 6
    prefere_fitness = extroversao > 6
    prefere_flexibilidade = abertura > 7

    return {
        'idade': idade_simulada,
        'tem_filhos': tem_filhos,
        'modalidade_trabalho': modalidade_trabalho,
        'transporte': transporte,
        'prefere_saude_mental': prefere_saude_mental,
        'prefere_desenvolvimento': prefere_desenvolvimento,
        'prefere_fitness': prefere_fitness,
        'prefere_flexibilidade': prefere_flexibilidade,
        'risco_burnout': funcionario.get('kpis_ia.risco_burnout', 5)
    }


def calcular_relevancia_beneficio(funcionario, lifestyle, beneficio):
    """Calcula relevância de um benefício para um funcionário específico"""
    relevancia = 50  # Base

    # Ajustes baseados no lifestyle
    if beneficio == 'Auxilio_Creche' and lifestyle['tem_filhos']:
        relevancia += 40
    elif beneficio == 'Auxilio_Creche' and not lifestyle['tem_filhos']:
        relevancia -= 30

    if beneficio in ['Auxilio_Internet', 'Coworking'] and lifestyle['modalidade_trabalho'] == 'Remoto':
        relevancia += 30
    elif beneficio == 'Auxilio_Transporte' and lifestyle['modalidade_trabalho'] == 'Remoto':
        relevancia -= 20

    if beneficio == 'Auxilio_Transporte' and lifestyle['transporte'] == 'Transporte Público':
        relevancia += 25
    elif beneficio == 'Auxilio_Transporte' and lifestyle['transporte'] == 'Carro':
        relevancia -= 10

    if beneficio == 'Gympass' and lifestyle['prefere_fitness']:
        relevancia += 20

    if beneficio in ['Auxilio_Psicologico', 'Massagem_Corporativa'] and lifestyle['prefere_saude_mental']:
        relevancia += 25

    if beneficio == 'Auxilio_Educacao' and lifestyle['prefere_desenvolvimento']:
        relevancia += 20

    if beneficio == 'Day_Off_Extra' and lifestyle['risco_burnout'] > 7:
        relevancia += 30

    # Ajustes por idade
    if lifestyle['idade'] > 40:
        if beneficio in ['Plano_Saude', 'Previdencia_Privada']:
            relevancia += 15
        if beneficio == 'Gympass':
            relevancia -= 5

    if lifestyle['idade'] < 30:
        if beneficio in ['Auxilio_Educacao', 'Gympass']:
            relevancia += 10
        if beneficio == 'Previdencia_Privada':
            relevancia -= 10

    return max(0, min(100, relevancia))


def otimizar_pacote_beneficios(funcionario, lifestyle, budget_limite=2000):
    """Otimiza pacote de benefícios dentro do budget"""
    beneficios_relevancia = []

    for beneficio, dados in CATALOGO_BENEFICIOS.items():
        if dados['flexivel']:  # Só otimizar benefícios flexíveis
            relevancia = calcular_relevancia_beneficio(
                funcionario, lifestyle, beneficio)
            # ROI = relevância por custo
            roi = relevancia / dados['custo_mensal']

            beneficios_relevancia.append({
                'beneficio': beneficio,
                'relevancia': relevancia,
                'custo': dados['custo_mensal'],
                'roi': roi,
                'categoria': dados['categoria']
            })

    # Ordenar por ROI (relevância/custo)
    beneficios_relevancia.sort(key=lambda x: x['roi'], reverse=True)

    # Seleção gulosa respeitando budget
    pacote_otimo = []
    custo_total = 0

    # Sempre incluir obrigatórios
    for beneficio, dados in CATALOGO_BENEFICIOS.items():
        if not dados['flexivel']:
            pacote_otimo.append({
                'beneficio': beneficio,
                'relevancia': 100,  # Obrigatório
                'custo': dados['custo_mensal'],
                'categoria': dados['categoria'],
                'tipo': 'Obrigatório'
            })
            custo_total += dados['custo_mensal']

    # Adicionar flexíveis por ROI
    for item in beneficios_relevancia:
        if custo_total + item['custo'] <= budget_limite:
            item['tipo'] = 'Recomendado'
            pacote_otimo.append(item)
            custo_total += item['custo']

    return pacote_otimo, custo_total


def predizer_life_events(funcionario, lifestyle):
    """Prediz eventos de vida e mudanças futuras nas necessidades"""
    eventos = []

    # Casamento (baseado em idade e perfil)
    if lifestyle['idade'] < 35 and not lifestyle['tem_filhos']:
        prob_casamento = 15 + \
            (10 - funcionario.get('perfil_big_five.neuroticismo', 5)) * 2
        if random.randint(0, 100) < prob_casamento:
            eventos.append({
                'evento': 'Casamento',
                'timeline': '6-12 meses',
                'mudancas_beneficios': ['Plano_Saude (família)', 'Auxilio_Transporte (parceiro)'],
                'probabilidade': f"{prob_casamento:.0f}%"
            })

    # Filhos
    if lifestyle['idade'] < 40 and random.randint(0, 100) < 20:
        eventos.append({
            'evento': 'Nascimento de filho',
            'timeline': '1-2 anos',
            'mudancas_beneficios': ['Auxilio_Creche', 'Auxilio_Educacao', 'Day_Off_Extra'],
            'probabilidade': '20%'
        })

    # Mudança para remoto
    abertura = funcionario.get('perfil_big_five.abertura_a_experiencia', 5)
    if lifestyle['modalidade_trabalho'] != 'Remoto' and abertura > 6:
        eventos.append({
            'evento': 'Migração para trabalho remoto',
            'timeline': '3-6 meses',
            'mudancas_beneficios': ['Auxilio_Internet', 'Coworking', '-Auxilio_Transporte'],
            'probabilidade': f"{abertura * 10:.0f}%"
        })

    # Burnout prevention
    if lifestyle['risco_burnout'] > 6:
        eventos.append({
            'evento': 'Necessidade de bem-estar intensivo',
            'timeline': '1-3 meses',
            'mudancas_beneficios': ['Auxilio_Psicologico', 'Massagem_Corporativa', 'Day_Off_Extra'],
            'probabilidade': f"{lifestyle['risco_burnout'] * 10:.0f}%"
        })

    return eventos


def simular_marketplace_trocas(df_funcionarios):
    """Simula trocas no marketplace interno de benefícios"""
    trocas_sugeridas = []

    for i, (id1, func1) in enumerate(df_funcionarios.sample(min(5, len(df_funcionarios))).iterrows()):
        for j, (id2, func2) in enumerate(df_funcionarios.sample(min(5, len(df_funcionarios))).iterrows()):
            if i >= j:
                continue

            lifestyle1 = gerar_lifestyle_profile(func1)
            lifestyle2 = gerar_lifestyle_profile(func2)

            # Simular que func1 tem VR alto mas prefere VA
            # e func2 tem Gympass mas não usa

            if random.random() < 0.3:  # 30% chance de match
                beneficio1 = random.choice(
                    ['VR', 'Gympass', 'Auxilio_Transporte'])
                beneficio2 = random.choice(
                    ['VA', 'Auxilio_Internet', 'Day_Off_Extra'])

                economia_mutual = random.randint(50, 200)

                trocas_sugeridas.append({
                    'pessoa1': func1['nome'],
                    'pessoa2': func2['nome'],
                    'oferece1': beneficio1,
                    'oferece2': beneficio2,
                    'economia_mensal': economia_mutual,
                    'match_score': random.randint(70, 95)
                })

    return sorted(trocas_sugeridas, key=lambda x: x['match_score'], reverse=True)[:3]


# --- Interface Principal ---
df_agentes = carregar_agentes()

if df_agentes.empty:
    st.warning(
        "⚠️ Nenhum agente encontrado. Execute o script generate_agents.py primeiro.")
    st.stop()

# --- Análise de Custos Atuais ---
st.header("💰 Análise de Custos Atuais")

# Simular custos atuais (pacote padrão para todos)
custo_padrao_mensal = sum([dados['custo_mensal']
                          for dados in CATALOGO_BENEFICIOS.values()])
custo_total_atual = custo_padrao_mensal * len(df_agentes)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💸 Custo Atual Mensal", f"R$ {custo_total_atual:,.0f}")

with col2:
    economia_estimada = custo_total_atual * 0.25  # 25% de economia estimada
    st.metric("💡 Economia Potencial",
              f"R$ {economia_estimada:,.0f}", "+25% otimização")

with col3:
    satisfacao_atual = 65  # Satisfação média atual (simulada)
    st.metric("😊 Satisfação Atual", f"{satisfacao_atual}%")

with col4:
    utilizacao_media = 78  # Utilização média (simulada)
    st.metric("📊 Utilização Média", f"{utilizacao_media}%")

# --- Lifestyle Profiler ---
st.header("👤 Lifestyle Profiler")

funcionario_selecionado = st.selectbox(
    "Selecione um funcionário para análise de lifestyle:",
    options=df_agentes.index.tolist(),
    format_func=lambda x: f"{df_agentes.loc[x, 'nome']} ({df_agentes.loc[x, 'cargo']})"
)

funcionario_data = df_agentes.loc[funcionario_selecionado].to_dict()
lifestyle = gerar_lifestyle_profile(funcionario_data)

col1, col2 = st.columns([0.6, 0.4])

with col1:
    st.subheader(f"🎭 Perfil de {funcionario_data['nome']}")

    # Informações do lifestyle
    col_a, col_b = st.columns(2)

    with col_a:
        st.write(f"**Idade:** {lifestyle['idade']} anos")
        st.write(
            f"**Tem filhos:** {'Sim' if lifestyle['tem_filhos'] else 'Não'}")
        st.write(f"**Modalidade:** {lifestyle['modalidade_trabalho']}")
        st.write(f"**Transporte:** {lifestyle['transporte']}")

    with col_b:
        st.write(
            f"**Prefere saúde mental:** {'Sim' if lifestyle['prefere_saude_mental'] else 'Não'}")
        st.write(
            f"**Prefere desenvolvimento:** {'Sim' if lifestyle['prefere_desenvolvimento'] else 'Não'}")
        st.write(
            f"**Prefere fitness:** {'Sim' if lifestyle['prefere_fitness'] else 'Não'}")
        st.write(f"**Risco burnout:** {lifestyle['risco_burnout']:.1f}/10")

with col2:
    # Gráfico de preferências
    categorias = ['Saúde Mental', 'Desenvolvimento',
                  'Fitness', 'Flexibilidade']
    valores = [
        lifestyle['prefere_saude_mental'] * 10,
        lifestyle['prefere_desenvolvimento'] * 10,
        lifestyle['prefere_fitness'] * 10,
        lifestyle['prefere_flexibilidade'] * 10
    ]

    fig_prefs = go.Figure(data=go.Scatterpolar(
        r=valores,
        theta=categorias,
        fill='toself',
        name='Preferências'
    ))

    fig_prefs.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        title="Perfil de Preferências"
    )

    st.plotly_chart(fig_prefs, use_container_width=True)

# --- Otimização de Benefícios ---
st.header("🎯 Otimização de Benefícios")

budget_slider = st.slider(
    "Budget mensal por funcionário (R$):", 1000, 3000, 2000, 100)

if st.button("🔮 Otimizar Pacote de Benefícios", type="primary"):
    pacote_otimo, custo_total = otimizar_pacote_beneficios(
        funcionario_data, lifestyle, budget_slider)

    st.success(
        f"✅ Pacote otimizado gerado! Custo total: R$ {custo_total:,.0f}")

    # Separar por tipo
    obrigatorios = [b for b in pacote_otimo if b.get('tipo') == 'Obrigatório']
    recomendados = [b for b in pacote_otimo if b.get('tipo') == 'Recomendado']

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Benefícios Obrigatórios")
        custo_obr = 0
        for beneficio in obrigatorios:
            st.write(
                f"• **{beneficio['beneficio'].replace('_', ' ')}** - R$ {beneficio['custo']}")
            custo_obr += beneficio['custo']
        st.write(f"**Subtotal:** R$ {custo_obr}")

    with col2:
        st.subheader("🎯 Benefícios Recomendados")
        custo_rec = 0
        for beneficio in recomendados:
            st.write(
                f"• **{beneficio['beneficio'].replace('_', ' ')}** - R$ {beneficio['custo']} (Relevância: {beneficio['relevancia']:.0f}%)")
            custo_rec += beneficio['custo']
        st.write(f"**Subtotal:** R$ {custo_rec}")

    # Comparação com pacote padrão
    economia = custo_padrao_mensal - custo_total
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Pacote Padrão", f"R$ {custo_padrao_mensal}")
    with col2:
        st.metric("🎯 Pacote Otimizado", f"R$ {custo_total}")
    with col3:
        st.metric("💡 Economia", f"R$ {economia}",
                  f"{economia/custo_padrao_mensal*100:.1f}%")

# --- Life Events Predictor ---
st.header("🔮 Life Events Predictor")

eventos_previstos = predizer_life_events(funcionario_data, lifestyle)

if eventos_previstos:
    st.subheader(f"📅 Eventos Previstos para {funcionario_data['nome']}")

    for evento in eventos_previstos:
        with st.expander(f"🎯 {evento['evento']} ({evento['probabilidade']} prob.)", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Timeline:** {evento['timeline']}")
                st.write(f"**Probabilidade:** {evento['probabilidade']}")

            with col2:
                st.write("**Mudanças nos benefícios:**")
                for mudanca in evento['mudancas_beneficios']:
                    if mudanca.startswith('-'):
                        st.write(f"❌ {mudanca[1:]}")
                    else:
                        st.write(f"✅ {mudanca}")
else:
    st.info("Nenhum evento significativo previsto nos próximos 12 meses.")

# --- Benefits Marketplace ---
st.header("🏪 Benefits Marketplace")

st.markdown("Sistema de troca inteligente de benefícios entre funcionários:")

trocas_sugeridas = simular_marketplace_trocas(df_agentes)

if trocas_sugeridas:
    st.subheader("🔄 Trocas Recomendadas")

    for i, troca in enumerate(trocas_sugeridas):
        with st.container():
            col1, col2, col3 = st.columns([0.4, 0.3, 0.3])

            with col1:
                st.write(f"**{troca['pessoa1']}** ↔️ **{troca['pessoa2']}**")
                st.write(f"Match Score: {troca['match_score']}%")

            with col2:
                st.write(f"Oferece: {troca['oferece1']}")
                st.write(f"Recebe: {troca['oferece2']}")

            with col3:
                st.metric("💰 Economia Mútua",
                          f"R$ {troca['economia_mensal']}/mês")
                if st.button(f"✅ Aprovar", key=f"troca_{i}"):
                    st.success("Troca aprovada! Notificações enviadas.")

            st.divider()
else:
    st.info("Nenhuma troca vantajosa identificada no momento.")

# --- Cost Optimization Dashboard ---
st.header("📊 Cost Optimization Dashboard")

# Simular dados de otimização organizacional
np.random.seed(42)
departamentos = df_agentes['departamento'].unique()

dados_otimizacao = []
for dept in departamentos:
    dept_df = df_agentes[df_agentes['departamento'] == dept]

    # Simular custos e economias
    custo_atual = len(dept_df) * custo_padrao_mensal
    economia_potencial = custo_atual * random.uniform(0.15, 0.35)
    satisfacao_atual = random.uniform(60, 80)
    satisfacao_pos = satisfacao_atual + random.uniform(5, 15)
    utilizacao = random.uniform(65, 85)

    dados_otimizacao.append({
        'Departamento': dept,
        'Funcionários': len(dept_df),
        'Custo Atual': custo_atual,
        'Economia Potencial': economia_potencial,
        '% Economia': economia_potencial / custo_atual * 100,
        'Satisfação Atual': satisfacao_atual,
        'Satisfação Projetada': satisfacao_pos,
        'Utilização %': utilizacao
    })

df_otimizacao = pd.DataFrame(dados_otimizacao)

# Métricas consolidadas
col1, col2, col3 = st.columns(3)

with col1:
    economia_total = df_otimizacao['Economia Potencial'].sum()
    st.metric("💡 Economia Total Anual", f"R$ {economia_total * 12:,.0f}")

with col2:
    melhoria_satisfacao = (
        df_otimizacao['Satisfação Projetada'] - df_otimizacao['Satisfação Atual']).mean()
    st.metric("😊 Melhoria Satisfação", f"+{melhoria_satisfacao:.1f}%")

with col3:
    roi_implementacao = economia_total * 12 / \
        (custo_total_atual * 0.1)  # Assume 10% custo implementação
    st.metric("📈 ROI Implementação", f"{roi_implementacao:.1f}x")

# Gráfico de economia por departamento
fig_dept = px.bar(
    df_otimizacao,
    x='Departamento',
    y='% Economia',
    color='Satisfação Projetada',
    title="Potencial de Economia por Departamento",
    color_continuous_scale='viridis'
)

st.plotly_chart(fig_dept, use_container_width=True)

# Tabela detalhada
st.subheader("📋 Análise Detalhada por Departamento")
st.dataframe(
    df_otimizacao.style.format({
        'Custo Atual': 'R$ {:,.0f}',
        'Economia Potencial': 'R$ {:,.0f}',
        '% Economia': '{:.1f}%',
        'Satisfação Atual': '{:.1f}%',
        'Satisfação Projetada': '{:.1f}%',
        'Utilização %': '{:.1f}%'
    }).background_gradient(subset=['% Economia'], cmap='RdYlGn'),
    use_container_width=True
)

# --- Recomendações Estratégicas ---
st.header("💡 Recomendações Estratégicas")

recomendacoes = [
    {
        'prioridade': 'ALTA',
        'titulo': 'Implementar sistema de personalização',
        'descricao': f'Economia potencial de R$ {economia_total * 12:,.0f}/ano com +{melhoria_satisfacao:.1f}% satisfação.',
        'prazo': '90 dias',
        'investimento': 'R$ 150.000 setup + R$ 20.000/mês'
    },
    {
        'prioridade': 'MÉDIA',
        'titulo': 'Marketplace interno de benefícios',
        'descricao': 'Permite trocas entre funcionários, otimizando utilização.',
        'prazo': '60 dias',
        'investimento': 'R$ 80.000 desenvolvimento'
    },
    {
        'prioridade': 'BAIXA',
        'titulo': 'Life events predictor automático',
        'descricao': 'Antecipa mudanças e ajusta benefícios proativamente.',
        'prazo': '120 dias',
        'investimento': 'R$ 100.000 + integração HRIS'
    }
]

for rec in recomendacoes:
    cor = 'error' if rec['prioridade'] == 'ALTA' else 'warning' if rec['prioridade'] == 'MÉDIA' else 'info'

    with st.expander(f"🎯 {rec['titulo']} - {rec['prioridade']}", expanded=rec['prioridade'] == 'ALTA'):
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Descrição:** {rec['descricao']}")
            st.write(f"**Prazo:** {rec['prazo']}")

        with col2:
            st.write(f"**Investimento:** {rec['investimento']}")
            if st.button(f"📋 Criar Plano", key=f"plano_{rec['titulo']}"):
                st.success("✅ Plano de implementação criado!")

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
💎 <strong>Benefits Optimization</strong> - HumaniQ AI<br>
Personalização inteligente de benefícios com até 35% de economia e +40% satisfação
</div>
""", unsafe_allow_html=True)
