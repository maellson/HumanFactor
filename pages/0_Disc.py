import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
from datetime import datetime
import anthropic
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

st.set_page_config(page_title="Assessment DISC", page_icon="🎯", layout="wide")

st.title("🎯 Assessment Comportamental DISC")
st.markdown("""
**Powered by Claude AI** - Metodologia DISC (Marston, 1928) com análise inteligente e insights personalizados.
""")

# --- Configuração Claude AI ---


@st.cache_resource
def init_claude():
    """Inicializa cliente Claude AI"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        st.error("🔑 **ANTHROPIC_API_KEY** não encontrada no arquivo .env!")
        st.info(
            "💡 Configure sua chave da Anthropic para análises avançadas. O teste básico ainda funcionará.")
        return None

    try:
        return anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        st.error(f"❌ Erro ao inicializar Claude AI: {e}")
        return None


claude_client = init_claude()

# Base de dados DISC - Palavras categorizadas
PALAVRAS_DISC = {
    # Grupo 1
    "grupo_1": {
        "Persuasivo": {"D": 1, "I": 3, "S": 0, "C": 0},
        "Gentil": {"D": 0, "I": 1, "S": 3, "C": 1},
        "Humilde": {"D": 0, "I": 0, "S": 3, "C": 2},
        "Original": {"D": 3, "I": 2, "S": 0, "C": 0}
    },
    # Grupo 2
    "grupo_2": {
        "Agressivo": {"D": 3, "I": 0, "S": 0, "C": 0},
        "Almeja": {"D": 3, "I": 1, "S": 0, "C": 1},
        "Animado": {"D": 1, "I": 3, "S": 1, "C": 0},
        "Cauteloso": {"D": 0, "I": 0, "S": 1, "C": 3}
    },
    # Grupo 3
    "grupo_3": {
        "Competitivo": {"D": 3, "I": 1, "S": 0, "C": 0},
        "Considerado": {"D": 0, "I": 0, "S": 3, "C": 1},
        "Convincente": {"D": 1, "I": 3, "S": 0, "C": 0},
        "Cooperativo": {"D": 0, "I": 1, "S": 3, "C": 1}
    },
    # Grupo 4
    "grupo_4": {
        "Decidido": {"D": 3, "I": 0, "S": 0, "C": 1},
        "Divertido": {"D": 0, "I": 3, "S": 1, "C": 0},
        "Diplomático": {"D": 0, "I": 2, "S": 2, "C": 1},
        "Detalhista": {"D": 0, "I": 0, "S": 1, "C": 3}
    },
    # Grupo 5
    "grupo_5": {
        "Direto": {"D": 3, "I": 0, "S": 0, "C": 1},
        "Entusiasmado": {"D": 1, "I": 3, "S": 0, "C": 0},
        "Estável": {"D": 0, "I": 0, "S": 3, "C": 1},
        "Exato": {"D": 0, "I": 0, "S": 1, "C": 3}
    },
    # Grupo 6
    "grupo_6": {
        "Independente": {"D": 3, "I": 1, "S": 0, "C": 0},
        "Inspirador": {"D": 0, "I": 3, "S": 0, "C": 0},
        "Interessado": {"D": 0, "I": 1, "S": 3, "C": 1},
        "Investigativo": {"D": 0, "I": 0, "S": 0, "C": 3}
    },
    # Grupo 7
    "grupo_7": {
        "Objetivo": {"D": 2, "I": 0, "S": 0, "C": 3},
        "Otimista": {"D": 0, "I": 3, "S": 1, "C": 0},
        "Organizado": {"D": 1, "I": 0, "S": 1, "C": 3},
        "Paciente": {"D": 0, "I": 0, "S": 3, "C": 1}
    },
    # Grupo 8
    "grupo_8": {
        "Persistente": {"D": 3, "I": 0, "S": 1, "C": 1},
        "Popular": {"D": 0, "I": 3, "S": 0, "C": 0},
        "Previsível": {"D": 0, "I": 0, "S": 3, "C": 1},
        "Preciso": {"D": 0, "I": 0, "S": 1, "C": 3}
    },
    # Grupo 9
    "grupo_9": {
        "Ousado": {"D": 3, "I": 1, "S": 0, "C": 0},
        "Sociável": {"D": 0, "I": 3, "S": 1, "C": 0},
        "Sereno": {"D": 0, "I": 0, "S": 3, "C": 1},
        "Sistemático": {"D": 0, "I": 0, "S": 1, "C": 3}
    },
    # Grupo 10
    "grupo_10": {
        "Determinado": {"D": 3, "I": 0, "S": 0, "C": 1},
        "Expressivo": {"D": 0, "I": 3, "S": 0, "C": 0},
        "Estável": {"D": 0, "I": 0, "S": 3, "C": 1},
        "Analítico": {"D": 0, "I": 0, "S": 1, "C": 3}
    },
    # Grupo 11
    "grupo_11": {
        "Aventureiro": {"D": 3, "I": 1, "S": 0, "C": 0},
        "Atrativo": {"D": 0, "I": 3, "S": 1, "C": 0},
        "Acolhedor": {"D": 0, "I": 1, "S": 3, "C": 0},
        "Atento": {"D": 0, "I": 0, "S": 1, "C": 3}
    },
    # Grupo 12
    "grupo_12": {
        "Forte": {"D": 3, "I": 0, "S": 0, "C": 1},
        "Inspirado": {"D": 1, "I": 3, "S": 0, "C": 0},
        "Submisso": {"D": 0, "I": 0, "S": 3, "C": 1},
        "Tímido": {"D": 0, "I": 0, "S": 1, "C": 3}
    }
}

# Perfis DISC
PERFIS_DISC = {
    "D": {
        "nome": "Dominância",
        "cor": "#FF6B6B",
        "características": [
            "Orientado para resultados",
            "Gosta de desafios",
            "Toma decisões rápidas",
            "Direto na comunicação",
            "Independente e autoconfiante"
        ],
        "comportamentos": "Assertivo, competitivo, impaciente",
        "motivadores": "Autoridade, desafios, resultados",
        "medos": "Perda de controle, rotina, indecisão",
        "ambiente_ideal": "Ambiente desafiador, autonomia, foco em resultados",
        "lideranca": "Autoritária, orientada a resultados, decisiva",
        "comunicacao": "Direta, objetiva, focada em resultados"
    },
    "I": {
        "nome": "Influência",
        "cor": "#4ECDC4",
        "características": [
            "Comunicativo e entusiasta",
            "Otimista e persuasivo",
            "Gosta de pessoas",
            "Criativo e inovador",
            "Inspirador e motivador"
        ],
        "comportamentos": "Expressivo, entusiasta, impulsivo",
        "motivadores": "Reconhecimento, aprovação social, variedade",
        "medos": "Rejeição, perda de aprovação, isolamento",
        "ambiente_ideal": "Ambiente social, interação, reconhecimento público",
        "lideranca": "Inspiradora, carismática, motivacional",
        "comunicacao": "Expressiva, emocional, persuasiva"
    },
    "S": {
        "nome": "Estabilidade",
        "cor": "#45B7D1",
        "características": [
            "Paciente e calmo",
            "Leal e confiável",
            "Bom ouvinte",
            "Evita conflitos",
            "Gosta de estabilidade"
        ],
        "comportamentos": "Consistente, acomodativo, previsível",
        "motivadores": "Segurança, estabilidade, harmonia",
        "medos": "Mudanças súbitas, conflitos, pressão",
        "ambiente_ideal": "Ambiente estável, tempo para adaptação, harmonia",
        "lideranca": "Colaborativa, consensual, apoiadora",
        "comunicacao": "Paciente, empática, harmoniosa"
    },
    "C": {
        "nome": "Conformidade",
        "cor": "#96CEB4",
        "características": [
            "Analítico e detalhista",
            "Meticuloso e preciso",
            "Segue regras e padrões",
            "Cauteloso nas decisões",
            "Busca qualidade"
        ],
        "comportamentos": "Sistemático, perfeccionista, diplomático",
        "motivadores": "Precisão, qualidade, conhecimento",
        "medos": "Críticas ao trabalho, erros, ambiguidade",
        "ambiente_ideal": "Padrões claros, tempo para análise, foco na qualidade",
        "lideranca": "Baseada em expertise, metódica, consultiva",
        "comunicacao": "Precisa, fundamentada, diplomática"
    }
}

# --- Funções de Análise ---


def calcular_pontuacao_disc(respostas):
    """Calcula pontuação DISC baseada nas respostas"""
    pontuacao = {"D": 0, "I": 0, "S": 0, "C": 0}

    for grupo, escolhas in respostas.items():
        mais_escolha = escolhas.get("mais", "")
        menos_escolha = escolhas.get("menos", "")

        if grupo in PALAVRAS_DISC:
            # Adicionar pontos da palavra MAIS escolhida
            if mais_escolha in PALAVRAS_DISC[grupo]:
                for dim, valor in PALAVRAS_DISC[grupo][mais_escolha].items():
                    pontuacao[dim] += valor

            # Subtrair pontos da palavra MENOS escolhida
            if menos_escolha in PALAVRAS_DISC[grupo]:
                for dim, valor in PALAVRAS_DISC[grupo][menos_escolha].items():
                    pontuacao[dim] -= valor

    # Normalizar para valores positivos e percentuais
    min_val = min(pontuacao.values())
    if min_val < 0:
        for dim in pontuacao:
            pontuacao[dim] += abs(min_val)

    total = sum(pontuacao.values())
    if total > 0:
        for dim in pontuacao:
            pontuacao[dim] = round((pontuacao[dim] / total) * 100, 1)

    return pontuacao


def identificar_perfil_dominante(pontuacao):
    """Identifica perfil dominante e combinações"""
    sorted_scores = sorted(pontuacao.items(), key=lambda x: x[1], reverse=True)

    dominante = sorted_scores[0][0]
    secundario = sorted_scores[1][0] if sorted_scores[1][1] > 15 else None

    # Combinações comuns
    combinacoes = {
        ("D", "I"): "Promotor - Direto e influente",
        ("D", "C"): "Reformador - Direto e analítico",
        ("I", "S"): "Conselheiro - Influente e estável",
        ("I", "D"): "Promotor - Influente e direto",
        ("S", "C"): "Especialista - Estável e detalhista",
        ("S", "I"): "Conselheiro - Estável e sociável",
        ("C", "D"): "Reformador - Analítico e direto",
        ("C", "S"): "Especialista - Analítico e estável"
    }

    perfil_combinado = None
    if secundario and sorted_scores[1][1] > 20:
        perfil_combinado = combinacoes.get(
            (dominante, secundario), f"{dominante}{secundario}")

    return dominante, secundario, perfil_combinado


def converter_disc_para_big_five(pontuacao_disc):
    """Converte DISC para Big Five aproximado"""
    # Mapeamento baseado em correlações psicológicas
    big_five = {
        "Abertura": (pontuacao_disc["I"] * 0.3 + pontuacao_disc["D"] * 0.2) / 10,
        "Conscienciosidade": (pontuacao_disc["C"] * 0.4 + pontuacao_disc["D"] * 0.1) / 10,
        "Extroversão": (pontuacao_disc["I"] * 0.4 + pontuacao_disc["D"] * 0.3) / 10,
        "Amabilidade": (pontuacao_disc["S"] * 0.4 + pontuacao_disc["I"] * 0.2) / 10,
        "Neuroticismo": max(0, 5 - (pontuacao_disc["S"] * 0.03 + pontuacao_disc["C"] * 0.02))
    }

    # Normalizar para escala 0-10
    for trait in big_five:
        big_five[trait] = round(min(10, max(0, big_five[trait] * 10)), 1)

    return big_five


def gerar_insights_claude(pontuacao, dominante, secundario, perfil_combinado, contexto_pessoal):
    """Gera insights personalizados usando Claude AI"""
    if not claude_client:
        return "❌ Claude AI não disponível. Configure ANTHROPIC_API_KEY para insights avançados."

    big_five_estimado = converter_disc_para_big_five(pontuacao)

    # Corrigir as expressões condicionais problemas na f-string
    secundario_nome = PERFIS_DISC[secundario]['nome'] if secundario else 'Nenhum'
    secundario_pontuacao = f"{pontuacao[secundario]:.1f}%" if secundario else 'N/A'

    prompt = f"""
Você é um psicólogo organizacional especialista em DISC. Analise este perfil comportamental:

RESULTADOS DISC:
- Dominância (D): {pontuacao['D']:.1f}%
- Influência (I): {pontuacao['I']:.1f}%
- Estabilidade (S): {pontuacao['S']:.1f}%
- Conformidade (C): {pontuacao['C']:.1f}%

PERFIL IDENTIFICADO:
- Dominante: {PERFIS_DISC[dominante]['nome']} ({pontuacao[dominante]:.1f}%)
- Secundário: {secundario_nome} ({secundario_pontuacao})
- Combinação: {perfil_combinado or 'Perfil puro'}

CONTEXTO PESSOAL:
{json.dumps(contexto_pessoal, indent=2, ensure_ascii=False)}

BIG FIVE ESTIMADO:
{json.dumps(big_five_estimado, indent=2, ensure_ascii=False)}

TAREFA:
Forneça uma análise detalhada e acionável sobre:

1. **RESUMO DO PERFIL** - Descrição concisa da personalidade
2. **PONTOS FORTES** - Principais qualidades e vantagens
3. **ÁREAS DE DESENVOLVIMENTO** - Pontos que podem ser melhorados
4. **ESTILO DE COMUNICAÇÃO** - Como essa pessoa se comunica melhor
5. **ESTILO DE LIDERANÇA** - Como lidera ou pode ser liderada
6. **AMBIENTE IDEAL** - Que tipo de ambiente é mais produtivo
7. **CARREIRA E DESENVOLVIMENTO** - Sugestões para crescimento profissional
8. **RELACIONAMENTOS** - Como se relaciona em equipes
9. **GESTÃO DE STRESS** - Como lidar com pressão e conflitos
10. **PLANO DE AÇÃO** - 3-5 ações específicas para desenvolver o potencial

Use linguagem acessível mas profissional. Base-se na ciência do modelo DISC e seja específico.

FORMATO: Use markdown com seções bem definidas e bullet points.
"""

    try:
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"❌ Erro ao gerar análise: {str(e)}"


# Interface do teste
if "respostas_disc" not in st.session_state:
    st.session_state.respostas_disc = {}

if "teste_completo" not in st.session_state:
    st.session_state.teste_completo = False

# Informações do usuário
st.sidebar.header("👤 Informações do Participante")
nome = st.sidebar.text_input("Nome:", placeholder="Seu nome completo")
cargo = st.sidebar.text_input("Cargo:", placeholder="Seu cargo atual")
empresa = st.sidebar.text_input("Empresa:", placeholder="Nome da empresa")

# --- Questionário DISC ---
if not st.session_state.teste_completo:
    st.header("📝 Questionário DISC")
    st.markdown("""
    **Instruções:** Para cada grupo de palavras, escolha:
    - A palavra que **MAIS** se parece com você
    - A palavra que **MENOS** se parece com você
    """)

    progress_bar = st.progress(0)
    total_grupos = len(PALAVRAS_DISC)

    for i, (grupo_id, palavras) in enumerate(PALAVRAS_DISC.items()):
        st.subheader(f"Grupo {i+1} de {total_grupos}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🟢 MAIS parecida comigo:**")
            mais_escolha = st.radio(
                f"Mais - Grupo {i+1}",
                options=list(palavras.keys()),
                key=f"mais_{grupo_id}",
                label_visibility="collapsed"
            )

            if grupo_id not in st.session_state.respostas_disc:
                st.session_state.respostas_disc[grupo_id] = {}
            st.session_state.respostas_disc[grupo_id]["mais"] = mais_escolha

        with col2:
            st.markdown("**🔴 MENOS parecida comigo:**")
            opcoes_menos = [
                palavra for palavra in palavras.keys() if palavra != mais_escolha]

            menos_escolha = st.radio(
                f"Menos - Grupo {i+1}",
                options=opcoes_menos,
                key=f"menos_{grupo_id}",
                label_visibility="collapsed"
            )

            st.session_state.respostas_disc[grupo_id]["menos"] = menos_escolha

        st.divider()
        progress_bar.progress((i + 1) / total_grupos)

    # Botão para finalizar
    if st.button("🎯 Finalizar Assessment", type="primary", use_container_width=True):
        if len(st.session_state.respostas_disc) == total_grupos:
            st.session_state.teste_completo = True
            st.rerun()
        else:
            st.error("❌ Por favor, complete todas as questões!")

else:
    # --- Mostrar Resultados ---
    st.header("📊 Seus Resultados DISC")

    # Calcular pontuação
    pontuacao = calcular_pontuacao_disc(st.session_state.respostas_disc)
    dominante, secundario, perfil_combinado = identificar_perfil_dominante(
        pontuacao)

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("D - Dominância", f"{pontuacao['D']:.1f}%",
                  delta="Dominante" if dominante == "D" else None)
    with col2:
        st.metric("I - Influência", f"{pontuacao['I']:.1f}%",
                  delta="Dominante" if dominante == "I" else None)
    with col3:
        st.metric("S - Estabilidade", f"{pontuacao['S']:.1f}%",
                  delta="Dominante" if dominante == "S" else None)
    with col4:
        st.metric("C - Conformidade", f"{pontuacao['C']:.1f}%",
                  delta="Dominante" if dominante == "C" else None)

    # --- Gráfico de Radar ---
    st.subheader("📈 Seu Perfil DISC")

    fig = go.Figure()

    dimensoes = list(pontuacao.keys())
    valores = list(pontuacao.values())
    cores = [PERFIS_DISC[dim]["cor"] for dim in dimensoes]
    nomes_completos = [PERFIS_DISC[dim]["nome"] for dim in dimensoes]

    fig.add_trace(go.Scatterpolar(
        r=valores,
        theta=nomes_completos,
        fill='toself',
        name='Seu Perfil DISC',
        marker=dict(size=8),
        line=dict(width=3, color='blue')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(valores) + 10]
            )
        ),
        title="Seu Perfil Comportamental DISC",
        font=dict(size=14)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Análise do Perfil Dominante ---
    st.subheader(f"🎯 Seu Perfil Dominante: {PERFIS_DISC[dominante]['nome']}")

    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        perfil_info = PERFIS_DISC[dominante]

        st.markdown("**🌟 Características Principais:**")
        for caracteristica in perfil_info["características"]:
            st.write(f"• {caracteristica}")

        st.markdown(
            f"**💼 Comportamentos Típicos:** {perfil_info['comportamentos']}")
        st.markdown(f"**🚀 Motivadores:** {perfil_info['motivadores']}")
        st.markdown(f"**⚠️ Medos/Aversões:** {perfil_info['medos']}")
        st.markdown(f"**🏢 Ambiente Ideal:** {perfil_info['ambiente_ideal']}")

    with col2:
        if perfil_combinado:
            st.info(f"**Perfil Combinado:** {perfil_combinado}")

        if secundario:
            st.markdown(
                f"**Traço Secundário:** {PERFIS_DISC[secundario]['nome']} ({pontuacao[secundario]:.1f}%)")

        # Intensidade do perfil
        intensidade = pontuacao[dominante]
        if intensidade > 50:
            st.success(
                f"✅ Perfil **muito forte** em {PERFIS_DISC[dominante]['nome']}")
        elif intensidade > 35:
            st.warning(
                f"⚠️ Perfil **moderado** em {PERFIS_DISC[dominante]['nome']}")
        else:
            st.info(
                f"ℹ️ Perfil **equilibrado** com tendência para {PERFIS_DISC[dominante]['nome']}")

        # Gráfico de barras
        fig_bar = px.bar(
            x=list(pontuacao.keys()),
            y=list(pontuacao.values()),
            color=list(pontuacao.keys()),
            color_discrete_map={
                dim: PERFIS_DISC[dim]["cor"] for dim in pontuacao.keys()},
            title="Distribuição DISC"
        )
        fig_bar.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- Conversão para Big Five ---
    st.subheader("🔄 Conversão Aproximada para Big Five")

    big_five_estimado = converter_disc_para_big_five(pontuacao)

    col1, col2 = st.columns(2)

    with col1:
        df_big_five = pd.DataFrame([big_five_estimado])
        st.dataframe(df_big_five.style.format(
            '{:.1f}'), use_container_width=True)

        st.info("💡 **Nota:** Esta conversão é aproximada. Para análise precisa do Big Five, recomenda-se um teste específico.")

    with col2:
        # Gráfico de barras para Big Five
        fig_bf = px.bar(
            x=list(big_five_estimado.keys()),
            y=list(big_five_estimado.values()),
            title="Perfil Big Five Estimado",
            color=list(big_five_estimado.keys())
        )
        fig_bf.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_bf, use_container_width=True)

    # --- Análise IA com Claude ---
    if claude_client:
        st.subheader("🤖 Análise Inteligente - Powered by Claude AI")

        contexto_pessoal = {
            "nome": nome or "Não informado",
            "cargo": cargo or "Não informado",
            "empresa": empresa or "Não informado"
        }

        with st.spinner("🧠 Gerando análise personalizada..."):
            insights = gerar_insights_claude(
                pontuacao, dominante, secundario, perfil_combinado, contexto_pessoal)
            st.markdown(insights)

    # --- Salvar Resultados ---
    if nome:
        st.subheader("💾 Salvar Resultados")

        resultado_completo = {
            "timestamp": datetime.now().isoformat(),
            "participante": {
                "nome": nome,
                "cargo": cargo,
                "empresa": empresa
            },
            "pontuacao_disc": pontuacao,
            "perfil_dominante": dominante,
            "perfil_secundario": secundario,
            "perfil_combinado": perfil_combinado,
            "big_five_estimado": big_five_estimado,
            "respostas_detalhadas": st.session_state.respostas_disc
        }

        if st.button("💾 Salvar Resultados", type="secondary"):
            # Salvar em JSON
            filename = f"disc_result_{nome.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            try:
                # Criar diretório se não existir
                os.makedirs("results", exist_ok=True)

                with open(f"results/{filename}", "w", encoding="utf-8") as f:
                    json.dump(resultado_completo, f,
                              ensure_ascii=False, indent=2)
                st.success(f"✅ Resultados salvos em: {filename}")
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {str(e)}")

        # Opção para download
        json_str = json.dumps(resultado_completo, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 Download Resultados (JSON)",
            data=json_str,
            file_name=f"disc_result_{nome.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    # Botão para refazer o teste
    if st.button("🔄 Refazer Teste", type="secondary"):
        st.session_state.teste_completo = False
        st.session_state.respostas_disc = {}
        st.rerun()
