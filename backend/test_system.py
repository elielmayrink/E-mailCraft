#!/usr/bin/env python3
"""
Teste completo do sistema usando apenas Gemini API
"""

import os
from dotenv import load_dotenv
from models.classifier import EmailClassifier
from models.response_generator import ResponseGenerator
from utils.text_processor import TextProcessor

# Carregar variáveis de ambiente
load_dotenv('config.env')

def test_system():
    """Testa o sistema completo"""
    print("🔍 Testando sistema completo com Gemini API...")
    
    try:
        # Inicializar componentes
        print("📦 Inicializando componentes...")
        classifier = EmailClassifier()
        response_generator = ResponseGenerator()
        text_processor = TextProcessor()
        
        # Texto de teste
        test_email = """
        Olá, preciso de ajuda com minha conta. 
        Não consigo acessar o sistema e preciso resolver isso urgentemente.
        Podem me ajudar?
        """
        
        print(f"📧 Email de teste: {test_email.strip()}")
        
        # Processar texto
        print("🔄 Processando texto...")
        processed_text = text_processor.process(test_email)
        
        # Classificar
        print("🏷️ Classificando email...")
        category = classifier.predict(processed_text)
        print(f"✅ Categoria: {category}")
        
        # Gerar resposta
        print("💬 Gerando resposta...")
        response = response_generator.generate(category, processed_text)
        print(f"✅ Resposta gerada: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema: {e}")
        return False

if __name__ == "__main__":
    success = test_system()
    print(f"\nResultado final: {'✅ Sucesso' if success else '❌ Falha'}")
