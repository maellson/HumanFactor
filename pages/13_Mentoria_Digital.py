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

st.set_page_config(page_title="Mentoria Digital",
                   page_icon="👨‍🏫", layout="wide")
st.title("👨‍🏫 Mentoria Digital - Company Culture Developer")
st.markdown(
    "Desenvolva sua cultura empresarial com mentores especializados em diferentes áreas.")

# --- Base de Conhecimento dos Mentores ---
MENTORES_DATA = {
    "Elon Musk": {
        "perfil": "Inovação e Criatividade",
        "descricao": "Especialista em inovação disruptiva, empreendedorismo e visão futurista.",
        "areas": ["Inovação", "Tecnologia", "Empreendedorismo", "Visão de Futuro"],
        "estilo": "Direto, desafiador e focado em resultados extraordinários."
    },
    "Silvio Santos": {
        "perfil": "Liderança e Negócios",
        "descricao": "Especialista em comunicação, entretenimento e construção de impérios empresariais.",
        "areas": ["Liderança", "Comunicação", "Negócios", "Empreendedorismo"],
        "estilo": "Prático, comunicativo e focado em conexão com pessoas."
    },
    "Bill Gates": {
        "perfil": "Tecnologia e Estratégia",
        "descricao": "Especialista em tecnologia, filantropia e estratégia de longo prazo.",
        "areas": ["Tecnologia", "Estratégia", "Filantropia", "Inovação Social"],
        "estilo": "Analítico, estratégico e focado em impacto global."
    },
    "Steve Jobs": {
        "perfil": "Design e Excelência",
        "descricao": "Especialista em design, experiência do usuário e excelência executiva.",
        "areas": ["Design", "Experiência do Usuário", "Excelência", "Inovação"],
        "estilo": "Perfeccionista, visionário e focado em detalhes."
    }
}

# --- Perfis de Especialistas ---
ESPECIALISTAS = {
    "Psicólogo": {
        "descricao": "Especialista em desenvolvimento pessoal e bem-estar psicológico.",
        "areas": ["Desenvolvimento Pessoal", "Saúde Mental", "Autoconhecimento", "Equilíbrio Emocional"]
    },
    "Gestor de Pessoas": {
        "descricao": "Especialista em gestão de pessoas, desenvolvimento de talentos e cultura organizacional.",
        "areas": ["Gestão de Pessoas", "Desenvolvimento de Talentos", "Cultura Organizacional", "Liderança"]
    },
    "Liderança": {
        "descricao": "Especialista em liderança, motivação de equipes e tomada de decisão.",
        "areas": ["Liderança", "Motivação", "Tomada de Decisão", "Gestão de Equipes"]
    },
    "Psicanalista": {
        "descricao": "Especialista em compreensão do comportamento humano e dinâmicas inconscientes.",
        "areas": ["Comportamento Humano", "Dinâmicas Inconscientes", "Autoconhecimento Profundo", "Relacionamentos"]
    },
    "Médico": {
        "descricao": "Especialista em saúde integral, bem-estar físico e prevenção de burnout.",
        "areas": ["Saúde Integral", "Bem-estar Físico", "Prevenção de Burnout", "Qualidade de Vida"]
    },
    "Nutricionista": {
        "descricao": "Especialista em nutrição, hábitos saudáveis e performance através da alimentação.",
        "areas": ["Nutrição", "Hábitos Saudáveis", "Performance", "Energia"]
    },
    "Tecnologia": {
        "descricao": "Especialista em transformação digital, automação e inovação tecnológica.",
        "areas": ["Transformação Digital", "Automação", "Inovação Tecnológica", "Eficiência"]
    },
    "Financeiro": {
        "descricao": "Especialista em gestão financeira, planejamento estratégico e otimização de recursos.",
        "areas": ["Gestão Financeira", "Planejamento Estratégico", "Otimização de Recursos", "Investimentos"]
    },
    "Inovação e Criatividade": {
        "descricao": "Especialista em fomentar a criatividade, resolver problemas inovadores e pensar fora da caixa.",
        "areas": ["Criatividade", "Inovação", "Resolução de Problemas", "Pensamento Criativo"]
    }
}

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


def get_mentor_response(prompt, mentor_name, funcionario_context):
    """Gera resposta usando Claude AI com perfil do mentor selecionado"""
    if not ANTHROPIC_API_KEY:
        return "❌ Erro: ANTHROPIC_API_KEY não configurada. Configure no arquivo .env"

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Obter dados do mentor
        mentor_data = MENTORES_DATA.get(mentor_name, {})
        especialista_data = ESPECIALISTAS.get(mentor_name, {})
        
        # Construir contexto do mentor
        if mentor_data:
            perfil_mentor = f"""
            PERFIL DO MENTOR: {mentor_name}
            Áreas de especialidade: {', '.join(mentor_data.get('areas', []))}
            Estilo de mentoria: {mentor_data.get('estilo', 'Não definido')}
            Descrição: {mentor_data.get('descricao', 'Não definido')}
            """
        elif especialista_data:
            perfil_mentor = f"""
            PERFIL DO ESPECIALISTA: {mentor_name}
            Áreas de especialidade: {', '.join(especialista_data.get('areas', []))}
            Descrição: {especialista_data.get('descricao', 'Não definido')}
            """
        else:
            perfil_mentor = f"MENTOR: {mentor_name}"

        # Construir contexto do funcionário
        perfil_funcionario = f"""
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
        
        OBJETIVOS: {funcionario_context.get('objetivos_carreira', 'Não definido')}
        """

        system_prompt = f"""
        Você é {mentor_name}, um mentor especializado em {perfil_mentor.split('Áreas de especialidade:')[0].split(':')[-1].strip()}.
        
        PERFIL DO MENTOR:
        {perfil_mentor}
        
        MISSÃO: Fornecer orientação personalizada baseada em sua expertise e experiência única.
        
        ESTILO DE COMUNICAÇÃO:
        - Use insights relevantes da área de especialidade do mentor
        - Seja empático mas direto
        - Faça perguntas reflexivas
        - Sugira ações concretas
        - Use linguagem simples e acessível
        - Fale em tom de amizade, sempre dando boas-vindas para a pessoa
        - Use emojis para deixar a conversa mais leve e amigável
        
        CONTEXTO DO FUNCIONÁRIO:
        {perfil_funcionario}
        
        Responda sempre considerando:
        1. O perfil e estilo do mentor selecionado
        2. O momento de carreira do funcionário
        3. As áreas de especialidade relevantes
        4. Ações práticas e mensuráveis
        """

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
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
    "👤 Funcionário:",
    options=df_agentes.index.tolist(),
    format_func=lambda x: f"{df_agentes.loc[x, 'nome']} ({df_agentes.loc[x, 'cargo']})"
)

agente_atual = df_agentes.loc[id_selecionado].to_dict()

# --- Interface de Seleção de Mentores ---
st.subheader("🎯 Escolha seu Mentor")

# Tabs para diferentes categorias de mentores
tab1, tab2 = st.tabs(["🌟 Mentores Celebridades", "🧠 Especialistas"])

with tab1:
    st.markdown("### 🌟 Mentores Baseados em Celebridades")
    st.info("Selecione um mentor inspirador baseado em figuras públicas conhecidas por sua expertise.")
    
    # Grid de mentores
    cols = st.columns(2)
    mentores_celebridades = ["Elon Musk", "Silvio Santos", "Bill Gates", "Steve Jobs"]
    
    for i, mentor in enumerate(mentores_celebridades):
        with cols[i % 2]:
            mentor_data = MENTORES_DATA[mentor]
            st.markdown(f"#### {mentor}")
            st.markdown(f"**Perfil:** {mentor_data['perfil']}")
            st.markdown(f"*{mentor_data['descricao']}*")
            
            if st.button(f"Selecionar {mentor}", key=f"mentor_{mentor}"):
                st.session_state.mentor_selecionado = mentor
                st.session_state.tipo_mentor = "celebridade"
            
            st.markdown("---")

with tab2:
    st.markdown("### 🧠 Especialistas em Áreas do Conhecimento")
    st.info("Selecione um especialista em áreas específicas para orientação técnica.")
    
    # Grid de especialistas
    especialistas_lista = list(ESPECIALISTAS.keys())
    cols = st.columns(2)
    
    for i, especialista in enumerate(especialistas_lista):
        with cols[i % 2]:
            especialista_data = ESPECIALISTAS[especialista]
            st.markdown(f"#### {especialista}")
            st.markdown(f"*{especialista_data['descricao']}*")
            st.markdown(f"**Áreas:** {', '.join(especialista_data['areas'][:3])}")
            
            if st.button(f"Selecionar {especialista}", key=f"especialista_{especialista}"):
                st.session_state.mentor_selecionado = especialista
                st.session_state.tipo_mentor = "especialista"
            
            st.markdown("---")

# Mostrar mentor selecionado
if 'mentor_selecionado' in st.session_state:
    mentor_atual = st.session_state.mentor_selecionado
    tipo_mentor = st.session_state.tipo_mentor
    
    st.divider()
    st.subheader(f"👨‍🏫 Seu Mentor: {mentor_atual}")
    
    if tipo_mentor == "celebridade":
        mentor_info = MENTORES_DATA[mentor_atual]
        st.info(f"**Perfil:** {mentor_info['perfil']}")
        st.info(f"**Especialidade:** {', '.join(mentor_info['areas'])}")
    else:
        especialista_info = ESPECIALISTAS[mentor_atual]
        st.info(f"**Especialidade:** {especialista_info['descricao']}")
    
    # Sugestões de perguntas
    st.markdown("### 💭 Sugestões de perguntas:")
    sugestoes = [
        f"Como posso desenvolver minhas habilidades como {mentor_atual}?",
        f"Quais são os princípios fundamentais que guiam seu trabalho?",
        f"Como lidar com fracassos e aprender com eles?",
        f"Qual conselho você daria para alguém começando na área de {mentor_info.get('perfil', 'seu setor') if tipo_mentor == 'celebridade' else mentor_atual}?",
        f"Como equilibrar vida pessoal e profissional?"
    ]
    
    for i, sugestao in enumerate(sugestoes):
        if st.button(f"💡 {sugestao}", key=f"sugestao_{i}"):
            st.session_state.conversa_input = sugestao
    
    # Input de conversa
    conversa = st.text_area(
        "✍️ Sua mensagem:",
        height=150,
        value=st.session_state.get('conversa_input', ''),
        placeholder=f"Exemplo: Olá {mentor_atual}, gostaria de orientação sobre..."
    )
    
    # Botão de envio
    if st.button("🚀 Conversar com seu Mentor", type="primary"):
        if not conversa.strip():
            st.warning("⚠️ Por favor, escreva uma mensagem.")
        else:
            with st.spinner(f"🧠 {mentor_atual} está preparando uma resposta personalizada..."):
                resposta = get_mentor_response(conversa, mentor_atual, agente_atual)
                
                st.divider()
                st.subheader(f"🎯 Resposta de {mentor_atual}:")
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

# --- Informações Adicionais ---
st.divider()
st.subheader("📚 Sobre a Mentoria Digital")

with st.expander("ℹ️ Como funciona a Mentoria Digital", expanded=False):
    st.markdown("""
    ### 🎯 Objetivo
    A Mentoria Digital tem como objetivo desenvolver a cultura empresarial através de agentes que observam os valores, cultura e crenças dos líderes e replicam modelos de comportamento organizacional.
    
    ### 👥 Tipos de Mentores
    
    **Mentores Celebridades:**
    - Inspiradores baseados em figuras públicas reconhecidas
    - Estilos de liderança e visões únicas
    - Experiências reais de sucesso e inovação
    
    **Especialistas:**
    - Profissionais com expertise em áreas específicas
    - Conhecimento técnico e científico atualizado
    - Orientação direcionada para necessidades específicas
    
    ### 🚀 Benefícios
    
    **Para o Funcionário:**
    - Desenvolvimento pessoal e profissional
    - Orientação personalizada baseada em ciência
    - Acesso a conhecimentos de especialistas
    - Crescimento de carreira acelerado
    
    **Para a Empresa:**
    - Desenvolvimento de cultura empresarial forte
    - Retenção de talentos
    - Aumento de engajamento
    - Melhoria de performance coletiva
    """)

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
👨‍🏫 <strong>Mentoria Digital</strong> - HumaniQ AI<br>
Desenvolvimento de cultura empresarial através de mentoria inteligente
</div>
""", unsafe_allow_html=True)