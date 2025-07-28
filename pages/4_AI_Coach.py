import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import anthropic

# Carregar variáveis de ambiente
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

st.set_page_config(page_title="AI Coach (Claude)",
                   page_icon="🧠", layout="wide")
st.title("🧠 HumaniQ AI Coach - Powered by Claude")
st.markdown(
    "Coach de carreira inteligente usando Claude AI da Anthropic para análise de fatores humanos.")

# --- Base de Conhecimento Expandida ---
knowledge_base = """
=== PRINCÍPIOS HUMANIQ AI ===

1. BEM-ESTAR COMO FUNDAMENTO
- Saúde mental é prioridade absoluta
- Técnica Pomodoro: 25min foco + 5min pausa
- Burnout: sinais incluem fadiga, cinismo, baixa eficácia
- Pausas regulares aumentam produtividade 23%

2. COMUNICAÇÃO CONSCIENTE
- Feedback construtivo acelera desenvolvimento
- Escuta ativa resolve 80% dos conflitos
- Transparência reduz ansiedade organizacional
- Alinhamento de expectativas previne frustrações

3. DESENVOLVIMENTO CIENTÍFICO
- Big Five: cada traço influencia performance diferente
- Conscienciosidade correlaciona com sucesso 65%
- Abertura à experiência prediz inovação
- Cada desafio = oportunidade de crescimento neural

4. EQUILÍBRIO SUSTENTÁVEL
- Work-life balance não é luxo, é necessidade
- Desconexão digital após expediente é essencial
- Produtividade real vem do descanso adequado
- Pessoas descansadas tomam decisões 40% melhores

5. CULTURA E FIT
- Fit cultural > competência técnica para retenção
- Diversidade cognitiva aumenta inovação 70%
- Valores alinhados geram engajamento duradouro
- Mudança cultural leva 18-24 meses para sedimentar

=== METODOLOGIAS APLICADAS ===

BIG FIVE:
- Abertura: criatividade, curiosidade, inovação
- Conscienciosidade: organização, disciplina, confiabilidade
- Extroversão: energia social, assertividade, otimismo
- Amabilidade: cooperação, confiança, empatia
- Neuroticismo: estabilidade emocional, gestão de stress

HOFSTEDE CULTURAL:
- Distância do poder, individualismo, masculinidade
- Aversão à incerteza, orientação temporal
- Indulgência vs restrição

EVIDENCE-BASED INTERVENTIONS:
- Terapia cognitivo-comportamental para burnout
- Mindfulness para regulação emocional
- Goal-setting theory para motivação
- Strengths-based development
"""

# --- Funções ---


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


def get_claude_response(prompt, funcionario_context):
    """Gera resposta usando Claude AI com contexto do funcionário"""
    if not ANTHROPIC_API_KEY:
        return "❌ Erro: ANTHROPIC_API_KEY não configurada. Configure no arquivo .env"

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        # Construir contexto rico do funcionário
        perfil_texto = f"""
        PERFIL DO FUNCIONÁRIO:
        Nome: {funcionario_context.get('nome', 'N/A')}
        Cargo: {funcionario_context.get('cargo', 'N/A')}
        Departamento: {funcionario_context.get('departamento', 'N/A')}
        Tempo na empresa: {funcionario_context.get('tempo_de_casa_meses', 0)} meses
        
        PERSONALIDADE (Big Five - escala 1-10):
        - Abertura: {funcionario_context.get('perfil_big_five', {}).get('abertura_a_experiencia', 'N/A')}
        - Conscienciosidade: {funcionario_context.get('perfil_big_five', {}).get('conscienciosidade', 'N/A')}
        - Extroversão: {funcionario_context.get('perfil_big_five', {}).get('extroversao', 'N/A')}
        - Amabilidade: {funcionario_context.get('perfil_big_five', {}).get('amabilidade', 'N/A')}
        - Neuroticismo: {funcionario_context.get('perfil_big_five', {}).get('neuroticismo', 'N/A')}
        
        COMPETÊNCIAS: {', '.join(funcionario_context.get('competencias', []))}
        
        PERFORMANCE:
        - Última avaliação: {funcionario_context.get('performance', {}).get('avaliacoes_desempenho', [{}])[-1].get('nota', 'N/A')}
        - Metas atingidas: {funcionario_context.get('performance', {}).get('metas_atingidas_percentual', 'N/A')}%
        
        ENGAJAMENTO:
        - eNPS: {funcionario_context.get('engajamento', {}).get('enps_recente', 'N/A')}
        - Feedback 360: {funcionario_context.get('engajamento', {}).get('feedback_360_media', 'N/A')}
        - Sentimento: {funcionario_context.get('engajamento', {}).get('comentarios_sentimento', 'N/A')}
        
        RISCOS IA:
        - Risco burnout: {funcionario_context.get('kpis_ia', {}).get('risco_burnout', 'N/A')}/10
        - Engajamento inferido: {funcionario_context.get('kpis_ia', {}).get('engajamento_inferido', 'N/A')}/10
        
        OBJETIVOS: {funcionario_context.get('objetivos_carreira', 'Não definido')}
        """

        system_prompt = f"""
        Você é um Coach de Carreira especializado em Fatores Humanos, parte da HumaniQ AI. 
        
        MISSÃO: Fornecer orientação personalizada baseada em ciência comportamental, psicologia organizacional e evidence-based practices.
        
        ESTILO DE COMUNICAÇÃO:
        - Empático mas direto
        - Use insights científicos relevantes
        - Faça perguntas reflexivas
        - Sugira ações concretas
        - Considere o perfil Big Five para personalizar a abordagem
        
        BASE DE CONHECIMENTO:
        {knowledge_base}
        
        CONTEXTO DO FUNCIONÁRIO:
        {perfil_texto}
        
        Responda sempre considerando:
        1. O perfil de personalidade único da pessoa
        2. Seu momento de carreira atual
        3. Riscos identificados pela IA
        4. Princípios científicos aplicáveis
        5. Ações práticas e mensuráveis
        """

        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return message.content[0].text

    except Exception as e:
        return f"❌ Erro ao conectar com Claude: {str(e)}"


# --- Interface Principal ---
st.sidebar.header("🔧 Configurações")

# Carregar dados dos agentes
df_agentes = carregar_agentes()

if df_agentes.empty:
    st.warning(
        "⚠️ Nenhum agente encontrado. Execute o script generate_agents.py primeiro.")
    st.stop()

# Seleção do funcionário
id_selecionado = st.sidebar.selectbox(
    "👤 Funcionário logado:",
    options=df_agentes.index.tolist(),
    format_func=lambda x: f"{df_agentes.loc[x, 'nome']} ({df_agentes.loc[x, 'cargo']})"
)

agente_atual = df_agentes.loc[id_selecionado].to_dict()

# --- Interface de Conversa ---
st.subheader(f"👋 Olá, {agente_atual['nome']}!")

# Insights automáticos baseados no perfil
with st.expander("🔍 Insights do seu Perfil", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        st.metric("🎯 Risco Burnout",
                  f"{agente_atual.get('kpis_ia', {}).get('risco_burnout', 0)}/10")
        st.metric("💡 Engajamento IA",
                  f"{agente_atual.get('kpis_ia', {}).get('engajamento_inferido', 0)}/10")

    with col2:
        perfil = agente_atual.get('perfil_big_five', {})
        maior_traco = max(
            perfil.items(), key=lambda x: x[1]) if perfil else ("N/A", 0)
        st.metric("🌟 Traço Dominante",
                  f"{maior_traco[0].replace('_', ' ').title()}")
        st.metric("📊 Intensidade", f"{maior_traco[1]}/10")

# Sugestões de conversas
st.markdown("### 💭 Sugestões de conversas:")
sugestoes = [
    "Como posso melhorar meu equilíbrio vida-trabalho?",
    "Quais são os próximos passos na minha carreira?",
    "Como desenvolver melhor minhas competências?",
    "Estou me sentindo desmotivado, o que fazer?",
    "Como melhorar minha comunicação com a equipe?",
    "Quero mudar de área, por onde começar?"
]

for i, sugestao in enumerate(sugestoes):
    if st.button(f"💡 {sugestao}", key=f"sugestao_{i}"):
        st.session_state.conversa_input = sugestao

# Input de conversa
conversa = st.text_area(
    "✍️ Sua mensagem:",
    height=150,
    value=st.session_state.get('conversa_input', ''),
    placeholder="Exemplo: Estou me sentindo sobrecarregado com minhas tarefas..."
)

# Botão de envio
if st.button("🚀 Conversar com Claude", type="primary"):
    if not conversa.strip():
        st.warning("⚠️ Por favor, escreva uma mensagem.")
    else:
        with st.spinner("🧠 Claude está analisando seu perfil e preparando uma resposta personalizada..."):
            resposta = get_claude_response(conversa, agente_atual)

            st.divider()
            st.subheader("🎯 Resposta do HumaniQ AI Coach:")
            st.success(resposta)

            # Feedback sobre a resposta
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("👍 Útil"):
                    st.success("Obrigado pelo feedback!")
            with col2:
                if st.button("👎 Não útil"):
                    st.info("Obrigado! Vamos melhorar.")
            with col3:
                if st.button("🔄 Nova resposta"):
                    st.experimental_rerun()

# --- Histórico de Conversas (Simulado) ---
st.divider()
st.subheader("📚 Sessões Recentes")
st.info("""
🎯 **Última sessão**: Discussão sobre desenvolvimento de liderança  
📅 **Data**: 15/01/2025  
⭐ **Progresso**: Implementou 3 das 5 sugestões  
""")

# --- Métricas de Progresso ---
with st.expander("📈 Seu Progresso no Coach"):
    progress_col1, progress_col2 = st.columns(2)

    with progress_col1:
        st.metric("Sessões este mês", "8", "+3")
        st.metric("Ações completadas", "12", "+5")

    with progress_col2:
        st.metric("Satisfação média", "4.7/5", "+0.3")
        st.metric("Metas atingidas", "85%", "+15%")

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
🧠 <strong>HumaniQ AI Coach</strong> - Powered by Claude AI da Anthropic<br>
Baseado em ciência comportamental e evidence-based practices
</div>
""", unsafe_allow_html=True)
