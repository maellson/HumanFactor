# Documentação dos Modelos - HumaniQ AI

## 1. Assessment DISC (`0_Disc.py`)

### Função
Realiza o assessment comportamental DISC para os funcionários, calculando pontuações e identificando perfis dominantes. Utiliza a API Claude AI para gerar insights personalizados.

### Metodologia
- Utiliza a metodologia DISC (Marston, 1928) com 60 palavras categorizadas em 12 grupos.
- Calcula pontuação baseada nas escolhas "mais" e "menos" do usuário.
- Identifica perfil dominante e combinações.
- Converte resultados para o modelo Big Five.
- Gera insights personalizados usando Claude AI com base no perfil e contexto pessoal.

## 2. Visão Geral (`1_visao_geral.py`)

### Função
Dashboard inicial que exibe o perfil de um funcionário selecionado, incluindo dados comportamentais, competências e análise de agrupamento com PCA.

### Metodologia
- Carrega dados de agentes de arquivos JSON.
- Exibe perfil comportamental (Big Five) em gráfico de barras.
- Mostra métricas de performance e engajamento.
- Utiliza Análise de Componentes Principais (PCA) para visualizar perfis de funcionários em um gráfico 2D.

## 3. Comparação de Perfis (`2_Comparar_Cargos.py`)

### Função
Compara funcionários usando análise comportamental avançada e insights de compatibilidade, com suporte da API Claude AI.

### Metodologia
- Calcula compatibilidade baseada no modelo Big Five.
- Analisa dinâmica geral do time selecionado.
- Gera insights usando Claude AI com base em dados do time e análise de compatibilidade.
- Utiliza algoritmos científicos para calcular distâncias e similaridades entre perfis.

## 4. Análise de Fit (`3_Analise_Fit.py`)

### Função
Encontra o candidato perfeito para uma vaga utilizando análise de fit cultural e técnico, com suporte da API Claude AI.

### Metodologia
- Calcula fit cultural baseado em Big Five usando distância euclidiana normalizada.
- Calcula fit técnico baseado em competências obrigatórias, desejáveis e diferenciais.
- Combina scores culturais e técnicos com pesos configuráveis.
- Gera insights detalhados usando Claude AI com base no candidato, vaga e análise de fit.

## 5. AI Coach (`4_AI_Coach.py`)

### Função
Coach de carreira inteligente que fornece orientação personalizada baseada em ciência comportamental e evidence-based practices.

### Metodologia
- Utiliza uma base de conhecimento com princípios de bem-estar, comunicação consciente, desenvolvimento científico, equilíbrio sustentável e cultura.
- Gera respostas personalizadas usando Claude AI com contexto rico do funcionário.
- Considera perfil de personalidade (Big Five), momento de carreira, riscos identificados pela IA e princípios científicos.

## 6. Replay (`5_Replay.py`)

### Função
Identifica funcionários modelo por cargo e extrai padrões de excelência para replicação.

### Metodologia
- Calcula score de performance baseado em múltiplos fatores (avaliações, metas, engajamento, burnout, tempo de casa).
- Extrai "DNA do sucesso" dos top performers (perfil comportamental, competências chave, estatísticas de performance).
- Compara qualquer funcionário com o DNA de sucesso para identificar gaps.

## 7. Previsão de Turnover (`6_Turnover_Prediction.py`)

### Função
Prediz risco de saída de funcionários com 90% de precisão usando IA e sugere ações preventivas personalizadas.

### Metodologia
- Calcula score de risco de turnover (0-100) baseado em múltiplos fatores (engajamento, performance, burnout, tempo de casa, sentimento, feedback 360).
- Classifica o nível de risco (baixo, médio, alto, crítico).
- Estima timeline provável de decisão de saída.
- Gera ações preventivas personalizadas com base no perfil e score do funcionário.

## 8. Dashboard Executivo (`7_executive_dashboard.py`)

### Função
Dashboard executivo com métricas e insights em tempo real para tomada de decisões estratégicas.

### Metodologia
- Calcula métricas principais (ROI, redução de turnover, fit cultural médio, payback, aumento de produtividade).
- Identifica alertas e prioridades com base nas métricas.
- Analisa performance por departamento.
- Gera recomendações estratégicas com base em dados agregados e tendências.

## 9. Dinâmica de Equipes (`8_Team_Dynamics.py`)

### Função
Otimiza formação e dinâmica de equipes para máxima produtividade, analisando compatibilidades comportamentais e identificando conflitos potenciais.

### Metodologia
- Calcula compatibilidade entre pessoas baseada em Big Five.
- Detecta possíveis áreas de conflito entre duas pessoas.
- Analisa a dinâmica geral de uma equipe (compatibilidade média, conflitos, diversidade cognitiva).
- Sugere formação ótima de equipe usando algoritmo genético simplificado.
- Calcula métricas de rede social baseadas em compatibilidade.

## 10. Otimização de Benefícios (`9_Benefits_Optimization.py`)

### Função
Personaliza benefícios por funcionário usando IA, mapeando preferências individuais, predizendo necessidades futuras e otimizando custos.

### Metodologia
- Gera perfil de lifestyle baseado nos dados do funcionário.
- Calcula relevância de benefícios para cada funcionário.
- Otimiza pacote de benefícios dentro de um budget definido.
- Prediz eventos de vida e mudanças futuras nas necessidades.
- Simula trocas no marketplace interno de benefícios.

## 11. Evolução do Fit Cultural (`10_Cultural_Fit_Evolution.py`)

### Função
Acompanha evolução cultural da empresa ao longo do tempo, identificando resistências e sugerindo estratégias de transformação.

### Metodologia
- Mapeia perfil Big Five para dimensões de Hofstede.
- Calcula o perfil cultural médio da organização.
- Simula evolução cultural ao longo do tempo.
- Identifica funcionários com maior influência cultural.
- Detecta funcionários com possível resistência a mudanças culturais.
- Gera estratégias personalizadas de transformação cultural.

## 12. Inteligência de Gaps de Skills (`11_Skill_Gap_Intelligence.py`)

### Função
Identifica lacunas de competências e oportunidades internas, sugerindo remanejamentos e contratações estratégicas.

### Metodologia
- Mapeia skills atuais vs necessárias por cargo.
- Identifica funcionários com skills subutilizadas.
- Analisa gaps de skills a nível organizacional.
- Sugere remanejamentos internos baseados em skills match.
- Planeja contratações baseadas em gaps críticos.
- Gera trilhas personalizadas de desenvolvimento.

## 13. Mentoria Digital (`13_Mentoria_Digital.py`)

### Função
Desenvolve cultura empresarial com mentores especializados em diferentes áreas, incluindo celebridades e especialistas.

### Metodologia
- Utiliza base de conhecimento de mentores celebridades e especialistas.
- Gera respostas usando Claude AI com perfil do mentor selecionado e contexto do funcionário.
- Fornece orientação personalizada baseada na expertise e experiência única do mentor.
- Considera perfil e estilo do mentor, momento de carreira do funcionário e ações práticas.

## 14. Inteligência de Mercado (`12_Market_Intelligence.py`)

### Função
Conecta com inteligência de mercado para benchmarking automático, monitorando tendências salariais, demanda de competências e análise competitiva.

### Metodologia
- Simula salários internos baseados em cargo e senioridade.
- Analisa competitividade salarial da empresa.
- Identifica funcionários com skills escassas no mercado.
- Gera relatório de posicionamento no mercado (employer branding).
- Calcula custo de substituição de um funcionário.
- Monitora tendências de mercado e evolução temporal de métricas.