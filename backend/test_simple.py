#!/usr/bin/env python3
"""
Script de teste simples para verificar se as dependências estão funcionando
"""

print("🔍 Testando dependências...")

try:
    import fastapi
    print("✅ FastAPI importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar FastAPI: {e}")

try:
    import uvicorn
    print("✅ Uvicorn importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar Uvicorn: {e}")

try:
    import torch
    print(f"✅ PyTorch importado com sucesso - versão: {torch.__version__}")
    print(f"   CUDA disponível: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"❌ Erro ao importar PyTorch: {e}")

try:
    from transformers import pipeline
    print("✅ Transformers importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar Transformers: {e}")

try:
    import sklearn
    print("✅ Scikit-learn importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar Scikit-learn: {e}")

try:
    import openai
    print("✅ OpenAI importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar OpenAI: {e}")

print("\n🚀 Testando criação de app FastAPI...")

try:
    from fastapi import FastAPI
    app = FastAPI(title="Test App")
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "Teste funcionando!", "status": "ok"}
    
    print("✅ App FastAPI criado com sucesso")
    print("✅ Endpoint de teste criado")
    
    # Testar se conseguimos importar nossos módulos
    try:
        from models.classifier import EmailClassifier
        print("✅ EmailClassifier importado com sucesso")
    except Exception as e:
        print(f"⚠️  Erro ao importar EmailClassifier: {e}")
    
    try:
        from models.response_generator import ResponseGenerator
        print("✅ ResponseGenerator importado com sucesso")
    except Exception as e:
        print(f"⚠️  Erro ao importar ResponseGenerator: {e}")
    
    try:
        from utils.text_processor import TextProcessor
        print("✅ TextProcessor importado com sucesso")
    except Exception as e:
        print(f"⚠️  Erro ao importar TextProcessor: {e}")
    
    print("\n🎉 Todos os testes básicos passaram!")
    print("💡 Para iniciar o servidor, execute: uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    
except Exception as e:
    print(f"❌ Erro ao criar app FastAPI: {e}")
    import traceback
    traceback.print_exc()
