#!/usr/bin/env python3
"""
Teste específico de classificação de emails
"""

import os
from dotenv import load_dotenv
from models.classifier import EmailClassifier
from models.response_generator import ResponseGenerator
from utils.text_processor import TextProcessor

# Carregar variáveis de ambiente
load_dotenv('config.env')

def test_email_classification():
    """Testa classificação de diferentes tipos de email"""
    print("🔍 Testando classificação de emails...")
    
    try:
        # Inicializar componentes
        classifier = EmailClassifier()
        response_generator = ResponseGenerator()
        text_processor = TextProcessor()
        
        # Emails de teste
        test_emails = [
            {
                "text": "Preciso de suporte técnico urgente. Meu sistema não está funcionando e preciso resolver isso hoje.",
                "expected": "Produtivo"
            },
            {
                "text": "Olá, bom dia! Como vocês estão?",
                "expected": "Improdutivo"
            },
            {
                "text": "Gostaria de saber o status da minha solicitação de pagamento. Quando será processada?",
                "expected": "Produtivo"
            },
            {
                "text": "Obrigado pelo atendimento de ontem. Vocês foram muito prestativos!",
                "expected": "Improdutivo"
            }
        ]
        
        for i, email_data in enumerate(test_emails, 1):
            print(f"\n📧 Teste {i}:")
            print(f"Texto: {email_data['text']}")
            print(f"Esperado: {email_data['expected']}")
            
            # Processar e classificar
            processed_text = text_processor.process(email_data['text'])
            category = classifier.predict(processed_text)
            confidence = classifier.get_confidence()
            
            print(f"Resultado: {category} (confiança: {confidence:.2f})")
            
            # Gerar resposta
            response = response_generator.generate(category, processed_text)
            print(f"Resposta: {response}")
            
            # Verificar se está correto
            if category == email_data['expected']:
                print("✅ Classificação correta!")
            else:
                print("❌ Classificação incorreta!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_email_classification()
    print(f"\nResultado final: {'✅ Sucesso' if success else '❌ Falha'}")
