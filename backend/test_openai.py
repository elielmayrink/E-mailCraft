#!/usr/bin/env python3
"""
Teste direto da API Google AI Studio (Gemini)
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('config.env')

def test_gemini():
    """Testa a conexão com Google AI Studio (Gemini)"""
    try:
        from google import genai
        
        api_key = os.getenv("google_studio_key")
        print(f"API Key encontrada: {api_key[:20]}..." if api_key else "API Key não encontrada")
        
        if not api_key:
            print("❌ API Key não configurada")
            return False
        
        # Criar cliente Gemini
        client = genai.Client(api_key=api_key)
        print("✅ Cliente Gemini criado com sucesso!")
        
        # Testar uma chamada simples
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Responda o que é o brasil"
        )
        
        result = response.text
        print(f"✅ Resposta da Gemini: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testando conexão com Google AI Studio (Gemini)...")
    gemini_success = test_gemini()
    print(f"Resultado Gemini: {'✅ Sucesso' if gemini_success else '❌ Falha'}")