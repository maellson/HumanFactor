#!/usr/bin/env python3
"""
HumaniQ AI - Script de Instalação Automatizada
Configura todo o ambiente HumaniQ AI de forma automática
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json


def print_banner():
    """Exibe banner da HumaniQ AI"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                         🧠 HumaniQ AI                        ║
    ║              Setup Automatizado - Versão 1.0.0               ║
    ║                                                               ║
    ║        A Primeira IA Onisciente para Fatores Humanos         ║
    ║                        Empresariais                          ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_step(step, total, description):
    """Imprime passo atual do setup"""
    print(f"\n[{step}/{total}] {description}")
    print("─" * 60)


def check_python_version():
    """Verifica versão do Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário.")
        print(f"   Versão atual: {sys.version}")
        return False

    print(f"✅ Python {sys.version.split()[0]} detectado")
    return True


def install_dependencies():
    """Instala dependências Python"""
    print("📦 Instalando dependências...")

    requirements = [
        "streamlit>=1.28.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "anthropic>=0.3.0",
        "plotly>=5.15.0",
        "python-dotenv>=1.0.0",
        "scikit-learn>=1.3.0",
        "Faker>=19.0.0",
        "networkx>=3.1.0",
        "python-dotenv",
        "matplotlib",
        "openai",

    ]

    for package in requirements:
        try:
            print(f"  Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package, "--quiet"
            ])
            print(f"  ✅ {package}")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Erro ao instalar {package}: {e}")
            return False

    return True


def create_directory_structure():
    """Cria estrutura de diretórios"""
    print("📁 Criando estrutura de diretórios...")

    directories = [
        "data",
        "data/agents",
        "data/vagas",
        "results",
        "logs",
        "exports"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}/")

    return True


def create_env_file():
    """Cria arquivo .env se não existir"""
    print("⚙️ Configurando arquivo de ambiente...")

    env_content = """# =============================================================================
# HumaniQ AI - Configuração de Ambiente
# =============================================================================

# -----------------------------------------------------------------------------
# ANTHROPIC (Claude AI) - OBRIGATÓRIO
# -----------------------------------------------------------------------------
# Obtenha sua chave em: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# -----------------------------------------------------------------------------
# CONFIGURAÇÕES GERAIS
# -----------------------------------------------------------------------------
DEBUG=False
LOG_LEVEL=INFO

# -----------------------------------------------------------------------------
# CONFIGURAÇÕES DE STREAMLIT
# -----------------------------------------------------------------------------
STREAMLIT_THEME=light
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost

# -----------------------------------------------------------------------------
# INSTRUÇÕES:
# 1. Substitua 'your_anthropic_api_key_here' pela sua chave real
# 2. Obtenha a chave em: https://console.anthropic.com/
# 3. Nunca compartilhe este arquivo (.env está no .gitignore)
# =============================================================================
"""

    if not os.path.exists(".env"):
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("  ✅ .env criado")
        print("  ⚠️  Configure sua ANTHROPIC_API_KEY no arquivo .env")
    else:
        print("  ℹ️  .env já existe")

    return True


def create_gitignore():
    """Cria arquivo .gitignore"""
    print("🚫 Configurando .gitignore...")

    gitignore_content = """# HumaniQ AI - .gitignore

# Environment variables
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Results and exports
results/
exports/
*.json
*.csv
*.xlsx

# Streamlit
.streamlit/

# Data (opcional - descomente se não quiser versionar dados)
# data/agents/
# data/vagas/
"""

    if not os.path.exists(".gitignore"):
        with open(".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore_content)
        print("  ✅ .gitignore criado")
    else:
        print("  ℹ️  .gitignore já existe")

    return True


def generate_sample_data():
    """Gera dados de exemplo"""
    print("🎲 Gerando dados de exemplo...")

    # Verificar se generate_agents.py existe
    if not os.path.exists("generate_agents.py"):
        print("  ❌ generate_agents.py não encontrado")
        return False

    try:
        # Executar generate_agents.py
        print("  Gerando funcionários...")
        exec(open("generate_agents.py").read())
        print("  ✅ Funcionários gerados")

        # Executar generate_vagas.py se existir
        if os.path.exists("generate_vagas.py"):
            print("  Gerando vagas...")
            exec(open("generate_vagas.py").read())
            print("  ✅ Vagas geradas")

        return True

    except Exception as e:
        print(f"  ❌ Erro ao gerar dados: {e}")
        return False


def verify_installation():
    """Verifica se instalação foi bem-sucedida"""
    print("🔍 Verificando instalação...")

    checks = []

    # Verificar estrutura de diretórios
    required_dirs = ["data", "data/agents", "data/vagas"]
    for directory in required_dirs:
        if os.path.exists(directory):
            checks.append(f"✅ {directory}/")
        else:
            checks.append(f"❌ {directory}/")

    # Verificar arquivos principais
    required_files = ["main.py", "requirements.txt", ".env"]
    for file in required_files:
        if os.path.exists(file):
            checks.append(f"✅ {file}")
        else:
            checks.append(f"❌ {file}")

    # Verificar dados
    if os.path.exists("data/agents"):
        agent_count = len([f for f in os.listdir(
            "data/agents") if f.endswith('.json')])
        checks.append(f"✅ {agent_count} funcionários gerados")

    if os.path.exists("data/vagas"):
        vaga_count = len([f for f in os.listdir(
            "data/vagas") if f.endswith('.json')])
        checks.append(f"✅ {vaga_count} vagas geradas")

    # Verificar módulos principais
    core_modules = ["1_Visão_Geral.py", "2_Comparar_Cargos.py",
                    "3_Análise_de_Fit.py", "main.py"]
    available_modules = sum(
        1 for module in core_modules if os.path.exists(module))
    checks.append(
        f"✅ {available_modules}/{len(core_modules)} módulos core disponíveis")

    # Exibir resultados
    for check in checks:
        print(f"  {check}")

    # Determinar sucesso
    success_count = sum(1 for check in checks if check.startswith("✅"))
    total_checks = len(checks)
    success_rate = (success_count / total_checks) * 100

    print(
        f"\n📊 Taxa de sucesso: {success_rate:.1f}% ({success_count}/{total_checks})")

    return success_rate >= 80


def show_next_steps():
    """Mostra próximos passos"""
    print("\n" + "="*60)
    print("🎉 INSTALAÇÃO CONCLUÍDA!")
    print("="*60)

    print("\n📋 PRÓXIMOS PASSOS:")

    print("\n1. 🔑 CONFIGURAR API KEY (OBRIGATÓRIO):")
    print("   • Acesse: https://console.anthropic.com/")
    print("   • Crie uma conta e obtenha sua API key")
    print("   • Edite o arquivo .env:")
    print("     ANTHROPIC_API_KEY=sk-ant-api03-xxxxx")

    print("\n2. 🚀 EXECUTAR APLICAÇÃO:")
    print("   streamlit run main.py")
    print("   (ou)")
    print("   python -m streamlit run main.py")

    print("\n3. 🧪 TESTAR MÓDULOS:")
    print("   • 👤 Visão Geral: streamlit run 1_Visão_Geral.py")
    print("   • 👥 Comparar Perfis: streamlit run 2_Comparar_Cargos.py")
    print("   • 🎯 Análise de Fit: streamlit run 3_Análise_de_Fit.py")

    print("\n4. 📚 DOCUMENTAÇÃO:")
    print("   • README.md - Documentação completa")
    print("   • main.py - Dashboard principal com guias")

    print("\n💡 DICAS:")
    print("   • Execute 'python test_modules.py' para verificar tudo")
    print("   • Use o main.py para navegação centralizada")
    print("   • Configure .env antes de usar módulos com Claude AI")

    print("\n🆘 SUPORTE:")
    print("   • GitHub Issues para problemas")
    print("   • README.md para troubleshooting")
    print("   • test_modules.py para diagnósticos")


def main():
    """Função principal do setup"""
    print_banner()

    total_steps = 7
    current_step = 0

    try:
        # Passo 1: Verificar Python
        current_step += 1
        print_step(current_step, total_steps, "Verificando Python")
        if not check_python_version():
            return False

        # Passo 2: Instalar dependências
        current_step += 1
        print_step(current_step, total_steps, "Instalando dependências")
        if not install_dependencies():
            print("❌ Falha na instalação de dependências")
            return False

        # Passo 3: Criar estrutura
        current_step += 1
        print_step(current_step, total_steps,
                   "Criando estrutura de diretórios")
        if not create_directory_structure():
            return False

        # Passo 4: Configurar ambiente
        current_step += 1
        print_step(current_step, total_steps, "Configurando ambiente")
        if not create_env_file():
            return False

        # Passo 5: Criar .gitignore
        current_step += 1
        print_step(current_step, total_steps,
                   "Configurando controle de versão")
        if not create_gitignore():
            return False

        # Passo 6: Gerar dados
        current_step += 1
        print_step(current_step, total_steps, "Gerando dados de exemplo")
        if not generate_sample_data():
            print("⚠️  Dados não gerados - execute manualmente depois")

        # Passo 7: Verificar instalação
        current_step += 1
        print_step(current_step, total_steps, "Verificando instalação")
        success = verify_installation()

        # Exibir resultados
        if success:
            show_next_steps()
            return True
        else:
            print("\n❌ Instalação incompleta. Verifique os erros acima.")
            return False

    except KeyboardInterrupt:
        print("\n\n❌ Setup interrompido pelo usuário.")
        return False
    except Exception as e:
        print(f"\n\n❌ Erro inesperado durante o setup: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
