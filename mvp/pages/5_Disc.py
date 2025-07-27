import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
from datetime import datetime

st.set_page_config(page_title="Assessment DISC - HumaniQ AI", page_icon="🎯", layout="wide")

st.title("🎯 Assessment Comportamental DISC")
st.markdown("""
**Baseado na metodologia DISC (Marston, 1928) - Formato inspirado no Solides**

Escolha a palavra que **MAIS** se parece com você e a que **MENOS** se parece com você em cada grupo.
""")

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
        "Planejador": {"D": 1, "I": 0, "S": 1, "C": 3},
        "Popular": {"D": 0, "I": 3, "S": 0, "C": 0},
        "Persistente": {"D": 2, "I": 0, "S": 2, "C": 1},
        "Preciso": {"D": 0, "I": 0, "S": 0, "C": 3}
    },
    # Grupo 9
    "grupo_9": {
        "Reservado": {"D": 0, "I": 0, "S": 2, "C": 3},
        "Respeitoso": {"D": 0, "I": 0, "S": 3, "C": 2},
        "Responsável": {"D": 1, "I": 0, "S": 2, "C": 3},
        "Relaxado": {"D": 0, "I": 2, "S": 3, "C": 0}
    },
    # Grupo 10
    "grupo_10": {
        "Sociável": {"D": 0, "I": 3, "S": 1, "C": 0},
        "Sistemático": {"D": 0, "I": 0, "S": 1, "C": 3},
        "Solidário": {"D": 0, "I": 1, "S": 3, "C": 0},
        "Seguro": {"D": 2, "I": 1, "S": 1, "C": 1}
    }
}

# Descrições dos perfis DISC
PERFIS_DISC = {
    "D": {
        "nome": "Dominância",
        "cor": "#FF6B6B",
        "características": [
            "Orientado para resultados",
            "Gosta de desafios",
            "Toma decisões rapidamente", 
            "Direto na comunicação",
            "Focado em objetivos"
        ],
        "comportamentos": "Assertivo, competitivo, determinado",
        "motivadores": "Poder, autoridade, desafios, resultados",
        "medos": "Perda de controle, aproveitamento",
        "ambiente_ideal": "Autonomia, variedade, resultados mensuráveis"
    },
    "I": {
        "nome": "Influência", 
        "cor": "#4ECDC4",
        "características": [
            "Sociável e expressivo",
            "Otimista e entusiasmado",
            "Persuasivo e inspirador",
            "Gosta de interação social",
            "Comunicativo"
        ],
        "comportamentos": "Falante, emotivo, impulsivo",
        "motivadores": "Reconhecimento social, popularidade, aprovação",
        "medos": "Rejeição social, perda de aprovação",
        "ambiente_ideal": "Interação social, reconhecimento público, flexibilidade"
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
        "ambiente_ideal": "Ambiente estável, tempo para adaptação, harmonia"
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
        "ambiente_ideal": "Padrões claros, tempo para análise, foco na qualidade"
    }
}

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
        perfil_combinado = combinacoes.get((dominante, secundario), f"{dominante}{secundario}")
    
    return dominante, secundario, perfil_combinado

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

if not st.session_state.teste_completo:
    st.header("📝 Questionário DISC")
    
    progress_bar = st.progress(0)
    total_grupos = len(PALAVRAS_DISC)
    
    for i, (grupo_id, palavras) in enumerate(PALAVRAS_DISC.items()):
        st.subheader(f"Grupo {i+1} de {total_grupos}")
        st.markdown("**Escolha a palavra que MAIS se parece com você e a que MENOS se parece com você:**")
        
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
            opcoes_menos = [palavra for palavra in palavras.keys() if palavra != mais_escolha]
            
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
            st.experimental_rerun()
        else:
            st.error("Por favor, complete todas as questões!")

else:
    # Mostrar resultados
    st.header("📊 Seus Resultados DISC")
    
    # Calcular pontuação
    pontuacao = calcular_pontuacao_disc(st.session_state.respostas_disc)
    dominante, secundario, perfil_combinado = identificar_perfil_dominante(pontuacao)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("D - Dominância", f"{pontuacao['D']:.1f}%")
    with col2:
        st.metric("I - Influência", f"{pontuacao['I']:.1f}%")
    with col3:
        st.metric("S - Estabilidade", f"{pontuacao['S']:.1f}%")
    with col4:
        st.metric("C - Conformidade", f"{pontuacao['C']:.1f}%")
    
    # Gráfico radar
    st.subheader("📈 Seu Perfil DISC")
    
    fig = go.Figure()
    
    dimensoes = list(pontuacao.keys())
    valores = list(pontuacao.values())
    cores = [PERFIS_DISC[dim]["cor"] for dim in dimensoes]
    
    fig.add_trace(go.Scatterpolar(
        r=valores,
        theta=[PERFIS_DISC[dim]["nome"] for dim in dimensoes],
        fill='toself',
        name='Seu Perfil',
        marker=dict(size=8),
        line=dict(width=3)
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
    
    # Análise do perfil dominante
    st.subheader(f"🎯 Seu Perfil Dominante: {PERFIS_DISC[dominante]['nome']}")
    
    col1, col2 = st.columns([0.6, 0.4])
    
    with col1:
        perfil_info = PERFIS_DISC[dominante]
        
        st.markdown("**🌟 Características Principais:**")
        for caracteristica in perfil_info["características"]:
            st.write(f"• {caracteristica}")
        
        st.markdown(f"**💼 Comportamentos Típicos:** {perfil_info['comportamentos']}")
        st.markdown(f"**🚀 Motivadores:** {perfil_info['motivadores']}")
        st.markdown(f"**⚠️ Medos/Aversões:** {perfil_info['medos']}")
        st.markdown(f"**🏢 Ambiente Ideal:** {perfil_info['ambiente_ideal']}")
    
    with col2:
        if perfil_combinado:
            st.info(f"**Perfil Combinado:** {perfil_combinado}")
        
        if secundario:
            st.markdown(f"**Traço Secundário:** {PERFIS_DISC[secundario]['nome']} ({pontuacao[secundario]:.1f}%)")
        
        # Score de intensidade
        intensidade = pontuacao[dominante]
        if intensidade > 40:
            st.success(f"✅ Perfil **muito forte** em {PERFIS_DISC[dominante]['nome']}")
        elif intensidade > 30:
            st.warning(f"⚠️ Perfil **moderado** em {PERFIS_DISC[dominante]['nome']}")
        else:
            st.info(f"ℹ️ Perfil **equilibrado** com tendência para {PERFIS_DISC[dominante]['nome']}")
    
    # Comparação com Big Five (conversão aproximada)
    st.subheader("🔄 Conversão Aproximada para Big Five")
    
    # Mapeamento DISC -> Big Five
    big_five_estimado = {
        "Abertura": pontuacao["I"] * 0.3 + pontuacao["D"] * 0.2,
        "Conscienciosidade": pontuacao["C"] * 0.4 + pontuacao["D"] * 0.1,
        "Extroversão": pontuacao["I"] * 0.4 + pontuacao["D"] * 0.3,
        "Amabilidade": pontuacao["S"] * 0.4 + pontuacao["I"] * 0.2,
        "Neuroticismo": 50 - (pontuacao["S"] * 0.3 + pontuacao["C"] * 0.2)
    }
    
    # Normalizar para escala 0-10
    for trait in big_five_estimado:
        big_five_estimado[trait] = round(big_five_estimado[trait] / 10, 1)
    
    df_big_five = pd.DataFrame([big_five_estimado])
    st.dataframe(df_big_five, use_container_width=True)
    
    st.info("💡 **Nota:** Esta conversão é aproximada. Para análise precisa do Big Five, recomenda-se um teste específico.")
    
    # Salvar resultados
    if nome:
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
                with open(f"results/{filename}", "w", encoding="utf-8") as f:
                    json.dump(resultado_completo, f, ensure_ascii=False, indent=2)
                st.success(f"✅ Resultados salvos em: {filename}")
            except:
                st.error("❌ Erro ao salvar. Verifique se a pasta 'results' existe.")
                
                # Mostrar JSON para copy/paste
                st.subheader("📋 Resultado em JSON (copie e salve manualmente):")
                st.json(resultado_completo)
    
    # Botão para refazer teste
    if st.button("🔄 Fazer Novo Teste"):
        st.session_state.respostas_disc = {}
        st.session_state.teste_completo = False
        st.experimental_rerun()

# Informações sobre DISC
with st.expander("ℹ️ Sobre o Modelo DISC"):
    st.markdown("""
    ### 📚 Metodologia DISC
    
    **Desenvolvido por:** William Moulton Marston (1928)
    **Refinado por:** John Geier (1970s)
    
    **Base Científica:**
    - Teoria das emoções de Marston
    - Comportamento observável em situações específicas
    - Não mede habilidades, inteligência ou valores
    - Foca em "como" a pessoa se comporta
    
    **Aplicações:**
    - Seleção e recrutamento
    - Desenvolvimento de liderança  
    - Formação de equipes
    - Melhoria da comunicação
    - Gestão de conflitos
    
    **Limitações:**
    - Não é teste psicológico clínico
    - Pode variar com contexto/humor
    - Autoavaliação pode ter vieses
    - Complementar a outras avaliações
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
🎯 <strong>Assessment DISC</strong> - HumaniQ AI<br>
Baseado na metodologia científica de William Marston (1928)
</div>
""", unsafe_allow_html=True)