import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# --- Imports da Nova Stack de IA ---
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI Coach (Advanced)", page_icon="🧠", layout="wide")
st.title("🧠 Advanced AI Career Coach")
st.markdown("Conversas inteligentes com base de conhecimento, usando LangChain e OpenAI.")

# --- Base de Conhecimento (Exemplo para o MVP) ---
knowledge_base_text = """
Princípio 1: Bem-Estar é Prioridade.
É fundamental que os funcionários se sintam seguros e apoiados. Pausas regulares são essenciais para a produtividade e para evitar o burnout. A técnica Pomodoro, com 25 minutos de foco e 5 de descanso, é altamente recomendada.

Princípio 2: Comunicação Aberta.
Incentivamos a comunicação transparente e honesta com os gestores. Se um funcionário se sente sobrecarregado, a primeira etapa é alinhar as expectativas com seu líder. O feedback construtivo é uma ferramenta de crescimento.

Princípio 3: Desenvolvimento Contínuo.
Cada desafio é uma oportunidade de aprendizado. Quando um funcionário enfrenta uma dificuldade técnica, ele deve buscar ajuda dos colegas mais seniores ou procurar recursos de treinamento internos. A empresa oferece uma plataforma de cursos online.

Princípio 4: Equilíbrio Vida-Trabalho.
Respeitamos o horário de trabalho. É importante se desconectar após o expediente para recarregar as energias. Problemas de produtividade muitas vezes estão ligados à falta de descanso adequado.
"""

# --- Funções ---
@st.cache_data
def carregar_agentes():
    AGENT_DIR = "data/agents"
    agent_files = [f for f in os.listdir(AGENT_DIR) if f.endswith('.json')]
    if not agent_files: return pd.DataFrame()
    all_agents_data = [json.load(open(os.path.join(AGENT_DIR, f), 'r', encoding='utf-8')) for f in agent_files]
    df = pd.json_normalize(all_agents_data)
    return df.set_index('id_funcionario')

# --- Interface ---
st.sidebar.header("Configurações")
df_agentes = carregar_agentes()

if df_agentes.empty:
    st.warning("Nenhum agente encontrado.")
    st.stop()

id_selecionado = st.sidebar.selectbox(
    "Selecione o funcionário 'logado':",
    options=df_agentes.index.tolist(),
    format_func=lambda x: f"{df_agentes.loc[x, 'nome']}"
)
agente_atual = df_agentes.loc[id_selecionado].to_dict()

st.subheader(f"Olá, {agente_atual['nome']}! Sobre o que gostaria de conversar?")
conversa = st.text_area("Sua mensagem:", height=150)

if st.button("Enviar para o AI Coach"):
    if not OPENAI_API_KEY:
        st.error("Chave da API da OpenAI não encontrada. Verifique seu arquivo .env e reinicie a aplicação.")
    elif not conversa:
        st.warning("Por favor, escreva uma mensagem.")
    else:
        try:
            with st.spinner("O AI Coach está pensando..."):
                text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                texts = text_splitter.split_text(knowledge_base_text)
                
                embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
                vectorstore = FAISS.from_texts(texts, embeddings)
                
                llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.7)
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=vectorstore.as_retriever()
                )
                
                resposta_dict = qa_chain.invoke(conversa)
                resposta_ia = resposta_dict.get('result', 'Não foi possível obter uma resposta.')

                st.divider()
                st.subheader("Resposta do AI Coach:")
                st.success(resposta_ia)
                st.info("Esta resposta foi gerada usando a base de conhecimento interna e a API da OpenAI.")

        except Exception as e:
            st.error(f"Ocorreu um erro ao se comunicar com a OpenAI: {e}")