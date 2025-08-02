import anthropic
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def check_available_models():
    """Verifica quais modelos estão disponíveis na conta Anthropic"""
    if not ANTHROPIC_API_KEY:
        print("❌ Erro: ANTHROPIC_API_KEY não configurada no arquivo .env")
        return
    
    print("🔍 Verificando modelos disponíveis na sua conta Anthropic...")
    print("-" * 60)
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Lista de modelos para testar (baseado na documentação atual da Anthropic)
    models_to_test = [
        "claude-3-5-sonnet-20241022",  # Mais recente
        "claude-3-5-sonnet-20240620",  # Versão estável
        "claude-3-opus-20240229",      # Modelo mais poderoso
        "claude-3-sonnet-20240229",    # Versão original (pode estar descontinuada)
        "claude-3-haiku-20240307",     # Modelo mais rápido
        "claude-3-5-haiku-20241022",   # Haiku mais recente
    ]
    
    available_models = []
    unavailable_models = []
    
    for model in models_to_test:
        try:
            print(f"🧪 Testando modelo: {model}")
            
            # Fazer uma requisição simples para testar o modelo
            message = client.messages.create(
                model=model,
                max_tokens=10,
                messages=[{
                    "role": "user",
                    "content": "Teste"
                }]
            )
            
            print(f"✅ {model} - DISPONÍVEL")
            available_models.append(model)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ {model} - INDISPONÍVEL: {error_msg}")
            unavailable_models.append((model, error_msg))
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS RESULTADOS:")
    print("=" * 60)
    
    if available_models:
        print(f"\n✅ MODELOS DISPONÍVEIS ({len(available_models)}):")
        for i, model in enumerate(available_models, 1):
            print(f"   {i}. {model}")
    else:
        print("\n❌ NENHUM MODELO DISPONÍVEL")
    
    if unavailable_models:
        print(f"\n❌ MODELOS INDISPONÍVEIS ({len(unavailable_models)}):")
        for i, (model, error) in enumerate(unavailable_models, 1):
            print(f"   {i}. {model}")
            if "404" in error:
                print(f"      → Modelo não encontrado (descontinuado)")
            elif "401" in error or "403" in error:
                print(f"      → Sem permissão de acesso")
            else:
                print(f"      → {error[:100]}...")
    
    print("\n" + "=" * 60)
    
    if available_models:
        print("💡 RECOMENDAÇÃO:")
        best_model = available_models[0]  # Primeiro da lista (mais recente)
        print(f"   Use o modelo: {best_model}")
        print(f"   Substitua 'claude-3-sonnet-20240229' por '{best_model}' no código")
    else:
        print("⚠️  AÇÃO NECESSÁRIA:")
        print("   1. Verifique se sua chave API está correta")
        print("   2. Confirme se sua conta tem créditos disponíveis")
        print("   3. Entre em contato com o suporte da Anthropic")

if __name__ == "__main__":
    check_available_models()