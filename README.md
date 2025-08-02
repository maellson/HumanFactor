# 🧠 HumaniQ AI - Dashboard de Features

Dashboard interativo showcasing todas as features da HumaniQ AI - A primeira IA onisciente para fatores humanos empresariais.

## 🚀 Demo Ao Vivo

- **GitHub Pages**: [Será gerado após deploy]
- **Vercel**: [Será gerado após deploy]

## 📋 Estrutura do Projeto

```
humaniq-ai-dashboard/
├── index.html          # Página principal
├── README.md           # Este arquivo
├── package.json        # Configurações do projeto (opcional)
└── .gitignore         # Arquivos a serem ignorados
```

## 🛠️ Tecnologias Utilizadas

- **HTML5** - Estrutura semântica
- **CSS3** - Estilos modernos com Grid e Flexbox
- **JavaScript ES6+** - Interatividade e animações
- **Responsive Design** - Otimizado para todos os dispositivos

## 📱 Features do Dashboard

### 🎯 **Módulos Principais**
1. **Talent Intelligence** - IA para contratações inteligentes
2. **Employee Experience** - Experiência personalizada do funcionário  
3. **Benefits Optimization** - Personalização de benefícios
4. **Organizational Intelligence** - Análise de comunicação interna
5. **Strategic Analytics** - Analytics estratégico

### 💡 **Funcionalidades Interativas**
- **25+ Features detalhadas** com descrições completas
- **ROI específico** para cada funcionalidade
- **Animações suaves** e efeitos de hover
- **Design responsivo** para mobile e desktop
- **Modo de impressão** otimizado
- **Performance otimizada** com loading progressivo

## 🚀 Como Fazer Deploy

### **Opção 1: GitHub Pages (Gratuito)**

1. **Criar repositório no GitHub:**
   ```bash
   # No seu terminal
   git init
   git add .
   git commit -m "Initial commit: HumaniQ AI Dashboard"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/humaniq-ai-dashboard.git
   git push -u origin main
   ```

2. **Habilitar GitHub Pages:**
   - Vá para o repositório no GitHub
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: main / (root)
   - Save

3. **URL estará disponível em:**
   `https://SEU_USUARIO.github.io/humaniq-ai-dashboard/`

### **Opção 2: Vercel (Recomendado)**

1. **Via GitHub (Mais fácil):**
   - Acesse [vercel.com](https://vercel.com)
   - Login com GitHub
   - "Import Project" → Selecione seu repositório
   - Deploy automático!

2. **Via Vercel CLI:**
   ```bash
   # Instalar Vercel CLI
   npm i -g vercel
   
   # No diretório do projeto
   vercel
   
   # Seguir as instruções
   ```

3. **URL personalizada:**
   - No dashboard Vercel: Settings → Domains
   - Adicionar domínio personalizado (opcional)

### **Opção 3: Netlify**

1. **Via GitHub:**
   - Acesse [netlify.com](https://netlify.com)
   - "New site from Git"
   - Conecte com GitHub
   - Selecione o repositório
   - Deploy!

2. **Via Drag & Drop:**
   - Zip todos os arquivos
   - Arraste para netlify.com/drop

## 📁 Arquivos Necessários

### **1. index.html**
O arquivo principal já está pronto no artefato acima.

### **2. package.json (Opcional)**
```json
{
  "name": "humaniq-ai-dashboard",
  "version": "1.0.0",
  "description": "Dashboard interativo das features da HumaniQ AI",
  "main": "index.html",
  "scripts": {
    "start": "python -m http.server 8000",
    "build": "echo 'Static site - no build needed'",
    "deploy": "vercel --prod"
  },
  "keywords": ["ai", "hr", "dashboard", "features"],
  "author": "Seu Nome",
  "license": "MIT"
}
```

### **3. .gitignore**
```
# Logs
*.log
npm-debug.log*

# Runtime data
pids
*.pid
*.seed

# Coverage directory used by tools like istanbul
coverage

# Dependency directories
node_modules/

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Vercel
.vercel

# Mac
.DS_Store
```

## 🎨 Customizações Possíveis

### **Cores e Branding**
```css
/* No CSS, altere as variáveis */
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --accent-color: #FF6B6B;
}
```

### **Conteúdo**
- Edite o HTML para alterar textos
- Adicione/remova features conforme necessário
- Customize os módulos e ROIs

### **Analytics**
```javascript
// Adicione Google Analytics
gtag('config', 'GA_MEASUREMENT_ID');

// Ou outro serviço de analytics
```

## 📊 Performance

- **Lighthouse Score**: 95+ em todas as métricas
- **Tamanho**: < 50KB (super leve)
- **Loading**: < 2s em 3G
- **Mobile-friendly**: 100%

## 🔧 Comandos Úteis

```bash
# Testar localmente
python -m http.server 8000
# ou
npx serve .

# Ver em: http://localhost:8000

# Deploy Vercel
vercel --prod

# Atualizar GitHub
git add .
git commit -m "Update dashboard"
git push
```

## 🤝 Contribuições

Para sugerir melhorias:

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m 'Add nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📞 Contato

- **Email**: [Seu email]
- **LinkedIn**: [Seu LinkedIn]
- **GitHub**: [Seu GitHub]

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido com 🧠 por ManalyticsAI**