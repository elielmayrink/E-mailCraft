import os
import logging
from typing import Dict, List, Optional
import re

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponseGenerator:
    """
    Gerador de respostas automáticas baseado em templates e IA (Gemini)
    """
    
    def __init__(self):
        self.templates = self._load_templates()
        self.gemini_client = None
        self._setup_gemini()
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Carrega templates de resposta por categoria"""
        return {
            "Produtivo": [
                "Obrigado pelo seu contato. Analisaremos sua solicitação e retornaremos em até 24 horas úteis.",
                "Recebemos sua mensagem e nossa equipe técnica está analisando o caso. Em breve entraremos em contato.",
                "Sua solicitação foi registrada com sucesso. Um de nossos especialistas entrará em contato em breve.",
                "Obrigado por entrar em contato. Estamos processando sua solicitação e retornaremos o mais rápido possível."
            ],
            "Improdutivo": [
                "Obrigado pela sua mensagem. Registramos seu contato em nosso sistema.",
                "Agradecemos o contato. Sua mensagem foi recebida e arquivada.",
                "Obrigado pela comunicação. Registramos sua mensagem em nossos arquivos.",
                "Agradecemos o contato. Sua mensagem foi recebida com sucesso."
            ]
        }
    
    def _setup_gemini(self):
        """Configura cliente Gemini se disponível"""
        try:
            api_key = os.getenv("google_studio_key")
            if api_key:
                from google import genai
                self.gemini_client = genai.Client(api_key=api_key)
                logger.info("Cliente Gemini configurado com sucesso!")
            else:
                logger.info("Gemini API key não encontrada. Usando apenas templates.")
                logger.info("Para usar Gemini, configure a variável google_studio_key")
        except Exception as e:
            logger.error(f"Erro ao configurar Gemini: {e}")
            logger.info("Continuando apenas com templates...")
    
    
    def set_gemini_key(self, api_key: str):
        """Configura API key da Gemini dinamicamente"""
        try:
            from google import genai
            self.gemini_client = genai.Client(api_key=api_key)
            logger.info("Cliente Gemini configurado dinamicamente!")
            return True
        except Exception as e:
            logger.error(f"Erro ao configurar Gemini: {e}")
            logger.error(f"Detalhes do erro: {str(e)}")
            return False
    
    
    def generate(self, category: str, text: str) -> str:
        """
        Gera resposta automática baseada na categoria e conteúdo
        
        Args:
            category (str): Categoria do email ('Produtivo' ou 'Improdutivo')
            text (str): Texto do email original
            
        Returns:
            str: Resposta gerada
        """
        try:
            if category == "Produtivo":
                return self._generate_productive_response(text)
            else:
                return self._generate_unproductive_response(text)
                
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return self._get_fallback_response(category)
    
    def _generate_productive_response(self, text: str) -> str:
        """Gera resposta para emails produtivos"""
        try:
            # Detectar tipo específico de solicitação
            response_type = self._detect_request_type(text)
            
            if response_type == "status":
                return "Obrigado pelo contato. Verificaremos o status da sua solicitação e retornaremos as informações em até 24 horas úteis."
            
            elif response_type == "suporte":
                return "Recebemos sua solicitação de suporte técnico. Nossa equipe especializada está analisando o caso e entrará em contato em breve."
            
            elif response_type == "pagamento":
                return "Obrigado pela sua mensagem sobre questões financeiras. Nossa equipe financeira analisará o caso e retornará em até 48 horas úteis."
            
            elif response_type == "sistema":
                return "Recebemos sua solicitação relacionada ao sistema. Nossa equipe técnica está investigando e retornará com uma solução em breve."
            
            else:
                # Usar IA se disponível para casos complexos
                if self.gemini_client:
                    return self._generate_ai_response(text, "productive")
                else:
                    return self._get_random_template("Produtivo")
                    
        except Exception as e:
            logger.error(f"Erro ao gerar resposta produtiva: {e}")
            return self._get_random_template("Produtivo")
    
    def _generate_unproductive_response(self, text: str) -> str:
        """Gera resposta para emails improdutivos"""
        try:
            # Detectar tipo de mensagem
            if self._is_greeting(text):
                return "Obrigado pela sua mensagem de cumprimento. Registramos seu contato em nosso sistema."
            
            elif self._is_thanks(text):
                return "Agradecemos o seu agradecimento. É um prazer poder ajudá-lo."
            
            elif self._is_holiday(text):
                return "Obrigado pela sua mensagem de felicitações. Desejamos a você também um excelente período."
            
            else:
                return self._get_random_template("Improdutivo")
                
        except Exception as e:
            logger.error(f"Erro ao gerar resposta improdutiva: {e}")
            return self._get_random_template("Improdutivo")
    
    def _detect_request_type(self, text: str) -> str:
        """Detecta o tipo específico de solicitação"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['status', 'situação', 'andamento', 'progresso']):
            return "status"
        
        elif any(word in text_lower for word in ['suporte', 'ajuda', 'problema', 'erro', 'bug']):
            return "suporte"
        
        elif any(word in text_lower for word in ['pagamento', 'fatura', 'cobrança', 'financeiro']):
            return "pagamento"
        
        elif any(word in text_lower for word in ['sistema', 'plataforma', 'aplicação', 'software']):
            return "sistema"
        
        return "general"
    
    def _is_greeting(self, text: str) -> bool:
        """Verifica se é uma mensagem de cumprimento"""
        greetings = ['olá', 'oi', 'bom dia', 'boa tarde', 'boa noite', 'hello', 'hi']
        return any(greeting in text.lower() for greeting in greetings)
    
    def _is_thanks(self, text: str) -> bool:
        """Verifica se é uma mensagem de agradecimento"""
        thanks = ['obrigado', 'obrigada', 'agradeço', 'thanks', 'thank you']
        return any(thank in text.lower() for thank in thanks)
    
    def _is_holiday(self, text: str) -> bool:
        """Verifica se é uma mensagem de feriado"""
        holidays = ['natal', 'ano novo', 'feliz', 'parabéns', 'felicitações']
        return any(holiday in text.lower() for holiday in holidays)
    
    def _generate_ai_response(self, text: str, category: str) -> str:
        """Gera resposta usando IA (Gemini)"""
        try:
            if self.gemini_client:
                return self._generate_gemini_response(text, category)
            else:
                return self._get_random_template(category.title())
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta com IA: {e}")
            return self._get_random_template(category.title())
    
    def _generate_gemini_response(self, text: str, category: str) -> str:
        """Gera resposta usando Gemini API"""
        try:
            prompt = f"""
            Você é um assistente de atendimento ao cliente de uma empresa financeira.
            
            Categoria do email: {category}
            Conteúdo do email: {text[:500]}
            
            Gere uma resposta profissional, concisa e útil em português brasileiro.
            A resposta deve ser adequada para a categoria identificada.
            Máximo 2 frases.
            """
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta com Gemini: {e}")
            return self._get_random_template(category.title())
    
    
    def _get_random_template(self, category: str) -> str:
        """Retorna um template aleatório da categoria"""
        import random
        templates = self.templates.get(category, [])
        if templates:
            return random.choice(templates)
        return "Obrigado pelo seu contato. Registramos sua mensagem em nosso sistema."
    
    def _get_fallback_response(self, category: str) -> str:
        """Resposta de fallback em caso de erro"""
        if category == "Produtivo":
            return "Obrigado pelo seu contato. Analisaremos sua solicitação e retornaremos em breve."
        else:
            return "Obrigado pela sua mensagem. Registramos seu contato em nosso sistema."
    
    def add_custom_template(self, category: str, template: str):
        """Adiciona template personalizado"""
        if category not in self.templates:
            self.templates[category] = []
        self.templates[category].append(template)
        logger.info(f"Template adicionado para categoria: {category}")
    
    def get_templates(self) -> Dict[str, List[str]]:
        """Retorna todos os templates disponíveis"""
        return self.templates.copy()
