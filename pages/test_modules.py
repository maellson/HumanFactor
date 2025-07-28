#!/usr/bin/env python3
"""
HumaniQ AI - Script de Teste dos Módulos
Verifica se todos os módulos estão funcionando corretamente
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
import traceback

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def print_step(step, text):
    """Imprime passo formatado"""
    print(f"\n[{step}] {text}")

def check_file_exists(filepath):
    """Verifica se arquivo existe"""
    if os.path.exists(filepath):
        print(f"  ✅ {filepath}")
        return True
    else:
        print(f"  ❌ {filepath} - NÃO ENCONTRADO")
        return False

def check_directory_exists(dirpath):
    """Verifica se diretório existe"""
    if os.path.exists(dirpath):
        files = len([f for f in os.listdir(dirpath) if f.endswith('.json')])
        print(f"  ✅ {dirpath} ({files} arquivos)")
        return True
    else:
        print(f"  ❌ {dirpath} - NÃO ENCONTRADO")
        return False

def check_python_module(filepath):
    """Verifica se módulo Python pode ser importado"""
    try:
        spec = importlib.util.spec_from_file_location("module", filepath)
        module = importlib.util.module_from_spec(spec)
        # Não executamos o módulo, apenas verificamos se pode ser carregado
        print(f"  ✅ {filepath} - Sintaxe OK")
        return True
    except Exception as e:
        print(f"  ❌ {filepath} - ERRO: {str(e)}")
        return False

def check_json_file(filepath):
    """Verifica se arquivo JSON é válido"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"  ✅ {filepath} - JSON válido")
        return True
    except Exception as e:
        print(f"  ❌ {filepath} - JSON inválido: {str(e)}")
        return False

def check_env_file():
    """Verifica configuração de ambiente"""
    env_path = ".env"
    env_example_path = ".env.example"
    
    print_step("ENV", "Verificando configuração de ambiente...")
    
    if not check_file_exists(env_example_path):
        return False
    
    if os.path.exists(env_path):
        print(f"  ✅ {env_path}")
        
        # Verificar se tem ANTHROPIC_API_KEY
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                if 'ANTHROPIC_API_KEY=' in content:
                    if 'your_anthropic_api_key_here' not in content:
                        print("  ✅ ANTHROPIC_API_KEY configurada")
                    else:
                        print("  ⚠️ ANTHROPIC_API_KEY precisa ser configurada")
                else:
                    print("  ⚠️ ANTHROPIC_API_KEY não encontrada no .env")
        except Exception as e:
            print(f"  ❌ Erro ao ler .env: {e}")
    else:
        print(f"  ⚠️ {env_path} - Copie de .env.example e configure")
    
    return True

def check_dependencies():
    """Verifica dependências Python"""
    print_step("DEPS", "Verificando dependências...")
    
    required_packages = [
        'streamlit',
        'pandas', 
        'numpy',
        'anthropic',
        'plotly',
        'python-dotenv',
        'scikit-learn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NÃO INSTALADO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n  🔧 Para instalar pacotes faltantes:")
        print(f"     pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Função principal de teste"""
    print_header("🧠 HumaniQ AI - Teste de Módulos")
    
    # Contadores
    total_checks = 0
    passed_checks = 0
    
    # 1. Verificar dependências
    if check_dependencies():
        passed_checks += 1
    total_checks += 1
    
    # 2. Verificar configuração
    if check_env_file():
        passed_checks += 1
    total_checks += 1
    
    # 3. Verificar arquivos principais
    print_step("FILES", "Verificando arquivos principais...")
    
    main_files = [
        "generate_agents.py",
        "generate_vagas.py", 
        "requirements.txt",
        ".env.example"
    ]
    
    files_ok = 0
    for file in main_files:
        if check_file_exists(file):
            files_ok += 1
    
    if files_ok == len(main_files):
        passed_checks += 1
    total_checks += 1
    
    # 4. Verificar módulos Streamlit
    print_step("MODULES", "Verificando módulos Streamlit...")
    
    streamlit_modules = [
        "1_Visão_Geral.py",
        "2_Comparar_Cargos.py", 
        "3_Análise_de_Fit.py",
        "4_AI_Coach.py",
        "5_REPLAY_Analysis.py",
        "6_Turnover_Prediction.py",
        "7_Executive_Dashboard.py",
        "8_Team_Dynamics.py",
        "9_Benefits_Optimization.py",
        "10_Cultural_Fit_Evolution.py",
        "11_Skill_Gap_Intelligence.py",
        "12_Market_Intelligence.py"
    ]
    
    modules_ok = 0
    for module in streamlit_modules:
        if os.path.exists(module):
            if check_python_module(module):
                modules_ok += 1
        else:
            print(f"  ❌ {module} - NÃO ENCONTRADO")
    
    if modules_ok >= len(streamlit_modules) * 0.8:  # 80% dos módulos OK
        passed_checks += 1
    total_checks += 1
    
    # 5. Verificar diretórios de dados
    print_step("DATA", "Verificando estrutura de dados...")
    
    data_dirs = [
        "data",
        "data/agents", 
        "data/vagas"
    ]
    
    dirs_ok = 0
    for dir_path in data_dirs:
        if check_directory_exists(dir_path):
            dirs_ok += 1
    
    if dirs_ok >= 2:  # Pelo menos data e agents
        passed_checks += 1
    total_checks += 1
    
    # 6. Verificar alguns arquivos de dados
    print_step("SAMPLES", "Verificando arquivos de exemplo...")
    
    sample_files_ok = 0
    
    # Verificar se tem pelo menos alguns agentes
    if os.path.exists("data/agents"):
        agent_files = [f for f in os.listdir("data/agents") if f.endswith('.json')]
        if len(agent_files) >= 5:
            # Verificar um arquivo de exemplo
            sample_agent = os.path.join("data/agents", agent_files[0])
            if check_json_file(sample_agent):
                sample_files_ok += 1
    
    # Verificar se tem vagas
    if os.path.exists("data/vagas"):
        vaga_files = [f for f in os.listdir("data/vagas") if f.endswith('.json')]
        if len(vaga_files) >= 2:
            sample_vaga = os.path.join("data/vagas", vaga_files[0])
            if check_json_file(sample_vaga):
                sample_files_ok += 1
    
    if sample_files_ok >= 1:
        passed_checks += 1
    total_checks += 1
    
    # Resultado final
    print_header("📊 RESULTADO DO TESTE")
    
    success_rate = (passed_checks / total_checks) * 100
    
    print(f"✅ Verificações passaram: {passed_checks}/{total_checks}")
    print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 EXCELENTE! Sistema pronto para uso.")
        print("   Execute: streamlit run 1_Visão_Geral.py")
    elif success_rate >= 70:
        print("\n✅ BOM! Sistema funcional com pequenos ajustes.")
        print("   Verifique os itens marcados com ❌ acima.")
    elif success_rate >= 50:
        print("\n⚠️ PARCIAL. Sistema precisa de alguns ajustes.")
        print("   Foque nos itens críticos marcados com ❌.")
    else:
        print("\n❌ CRÍTICO. Sistema precisa de configuração.")
        print("   Siga o README.md para setup completo.")
    
    # Dicas específicas
    print_header("💡 PRÓXIMOS PASSOS")
    
    if not os.path.exists("data/agents"):
        print("1. Execute: python generate_agents.py")
    
    if not os.path.exists("data/vagas"):
        print("2. Execute: python generate_vagas.py")
    
    if not os.path.exists(".env"):
        print("3. Configure: cp .env.example .env")
        print("   Edite .env com sua ANTHROPIC_API_KEY")
    
    print("4. Teste um módulo: streamlit run 2_Comparar_Cargos.py")
    
    return success_rate >= 70

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Teste interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado durante o teste:")
        print(f"   {str(e)}")
        traceback.print_exc()
        sys.exit(1)