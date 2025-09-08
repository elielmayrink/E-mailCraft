import logging
from typing import Dict, Any
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailClassifier:
    """
    Classificador de emails usando Gemini AI para categorizar em Produtivo/Improdutivo
    """
    
    def __init__(self, gemini_client=None):
        self.model_name = "distilbert-base-uncased"
        self.classifier = None
        self.tokenizer = None
        self.last_confidence = 0.0
        self.gemini_client = gemini_client
        self._load_model()
    
    def set_gemini_client(self, gemini_client):
        """Define o cliente Gemini"""
        self.gemini_client = gemini_client
        logger.info("Cliente Gemini configurado no classificador!")
    
    def _load_model(self):
        """Inicializa classificação sem dependências pesadas por padrão."""
        # Para Vercel/serverless, evitamos carregar transformers/torch
        self.classifier = None
        self._load_fallback_model()
        
        # Sempre carregar palavras-chave como fallback adicional
        self._load_keywords()
    
    def _load_keywords(self):
        """Carrega palavras-chave para fallback"""
        self.keywords_productive = [
            'status', 'solicitação', 'suporte', 'problema', 'erro', 'ajuda',
            'atualização', 'informação', 'dados', 'sistema', 'conta', 'pagamento',
            'fatura', 'cobrança', 'serviço', 'técnico', 'resolução', 'urgente',
            'preciso', 'solicito', 'pedido', 'orçamento', 'proposta', 'contrato'
        ]
        self.keywords_unproductive = [
            'obrigado', 'obrigada', 'feliz', 'natal', 'ano novo', 'parabéns',
            'agradecimento', 'cumprimento', 'saudação', 'olá', 'oi', 'tchau',
            'até logo', 'boa tarde', 'bom dia', 'boa noite', 'felicitações'
        ]
        logger.info("Palavras-chave carregadas para fallback!")
    
    def _load_fallback_model(self):
        """Carrega modelo de fallback mais simples"""
        try:
            logger.info("Carregando modelo de fallback leve (palavras-chave)...")
            self.fallback_model = True
            logger.info("Modelo de fallback carregado!")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de fallback: {e}")
            raise
    
    def classify_with_gemini(self, text: str) -> str:
        """
        Classifica email usando Gemini AI com prompt específico
        
        Args:
            text (str): Texto do email
            
        Returns:
            str: "Produtivo" ou "Improdutivo"
        """
        try:
            if not self.gemini_client:
                logger.warning("Cliente Gemini não configurado, usando fallback")
                return self._predict_fallback(text)
            
            # Prompt otimizado para classificação de emails
            prompt = f"""Você é um especialista em classificação de emails corporativos.

DEFINIÇÕES CLARAS:
- PRODUTIVO: Emails que REQUEREM AÇÃO ou RESPOSTA da empresa. Exemplos: solicitações, problemas técnicos, pedidos de orçamento, reclamações, suporte, atualizações de status, propostas comerciais
- IMPRODUTIVO: Emails que NÃO REQUEREM AÇÃO da empresa. Exemplos: cumprimentos, agradecimentos, felicitações, saudações simples, mensagens de despedida, mensagens sociais

EXEMPLOS ESPECÍFICOS:
PRODUTIVO: "Preciso de ajuda com o sistema de pagamento", "Solicito orçamento para projeto", "Erro no sistema de cobrança", "Problema técnico no servidor", "Quero contratar seus serviços"
IMPRODUTIVO: "Feliz Natal e próspero ano novo!", "Obrigado pelo atendimento", "Bom dia", "Parabéns pelo aniversário", "Até logo", "Boa tarde"

REGRA IMPORTANTE: Se o email é apenas um cumprimento, agradecimento ou saudação SEM solicitar nada específico, é IMPRODUTIVO.

EMAIL PARA CLASSIFICAR: {text}

Responda apenas: PRODUTIVO ou IMPRODUTIVO"""

            # Fazer chamada para Gemini
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            result = response.text.strip().upper()
            logger.info(f"Resposta bruta do Gemini: '{response.text.strip()}' -> '{result}'")
            
            # Validar resposta
            if result == "PRODUTIVO":
                self.last_confidence = 0.9  # Alta confiança para Gemini
                logger.info("Classificação: PRODUTIVO")
                return "Produtivo"
            elif result == "IMPRODUTIVO":
                self.last_confidence = 0.9  # Alta confiança para Gemini
                logger.info("Classificação: IMPRODUTIVO")
                return "Improdutivo"
            else:
                logger.warning(f"Resposta inesperada do Gemini: '{result}'")
                return self._predict_fallback(text)
                
        except Exception as e:
            logger.error(f"Erro na classificação Gemini: {e}")
            return self._predict_fallback(text)
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Classifica o texto do email
        
        Args:
            text (str): Texto do email a ser classificado
            
        Returns:
            Dict[str, Any]: Dicionário com categoria, confiança e método usado
        """
        try:
            if not text or len(text.strip()) == 0:
                return {
                    "category": "Improdutivo",
                    "confidence": 0.5,
                    "method": "empty_text",
                    "model_info": "Texto vazio - classificado como improdutivo"
                }
            
            # Limitar tamanho do texto
            text = text[:1000]  # Limite maior para Gemini
            
            # Tentar Gemini primeiro (método principal)
            if self.gemini_client:
                try:
                    result = self.classify_with_gemini(text)
                    return {
                        "category": result,
                        "confidence": self.last_confidence,
                        "method": "gemini",
                        "model_info": "Gemini AI - Classificação inteligente"
                    }
                except Exception as e:
                    logger.warning(f"Gemini falhou, usando fallback: {e}")
            
            # Fallback para palavras-chave (sem dependências pesadas)
            result = self._predict_fallback(text)
            return {
                "category": result,
                "confidence": self.last_confidence,
                "method": "keywords_fallback",
                "model_info": "Classificação por palavras-chave (fallback)"
            }
                
        except Exception as e:
            logger.error(f"Erro na classificação: {e}")
            return {
                "category": "Improdutivo",
                "confidence": 0.5,
                "method": "error_fallback",
                "model_info": f"Erro na classificação - {str(e)}"
            }
    
    def _predict_bert(self, text: str) -> str:
        """Removido em ambiente serverless; mantido por compatibilidade."""
        logger.info("Classificação BERT desabilitada neste deploy. Usando fallback.")
        return self._predict_fallback(text)
    
    def _predict_fallback(self, text: str) -> str:
        """Classificação usando palavras-chave (fallback)"""
        try:
            text_lower = text.lower()
            
            # Contar palavras-chave produtivas
            productive_count = sum(1 for word in self.keywords_productive if word in text_lower)
            
            # Contar palavras-chave improdutivas
            unproductive_count = sum(1 for word in self.keywords_unproductive if word in text_lower)
            
            # Calcular confiança baseada na diferença
            total_keywords = productive_count + unproductive_count
            if total_keywords == 0:
                self.last_confidence = 0.5
                return "Improdutivo"  # Default para textos neutros
            
            confidence = abs(productive_count - unproductive_count) / total_keywords
            self.last_confidence = confidence
            
            # Decidir baseado na contagem
            if productive_count > unproductive_count:
                return "Produtivo"
            else:
                return "Improdutivo"
                
        except Exception as e:
            logger.error(f"Erro na classificação fallback: {e}")
            self.last_confidence = 0.5
            return "Improdutivo"
    
    def get_confidence(self) -> float:
        """Retorna a confiança da última classificação"""
        return self.last_confidence
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo"""
        return {
            "model_name": self.model_name,
            "gemini_available": self.gemini_client is not None,
            "fallback_mode": hasattr(self, 'fallback_model') and self.fallback_model,
            "last_confidence": self.last_confidence
        }
