import re
import logging
from typing import Dict, List, Any
import PyPDF2
import io

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextProcessor:
    """
    Processador de texto para limpeza e preparação de emails
    """
    
    def __init__(self):
        self.stop_words = self._load_stop_words()
    
    def _load_stop_words(self) -> set:
        """Carrega lista de stop words em português"""
        return {
            'a', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo',
            'as', 'até', 'com', 'como', 'da', 'das', 'do', 'dos', 'e', 'ela',
            'elas', 'ele', 'eles', 'em', 'entre', 'era', 'eram', 'essa', 'essas',
            'esse', 'esses', 'esta', 'estamos', 'estas', 'estava', 'estavam',
            'este', 'esteja', 'estejam', 'estejamos', 'estes', 'esteve', 'estive',
            'estivemos', 'estiver', 'estivera', 'estiveram', 'estiverem',
            'estivermos', 'estivesse', 'estivessem', 'estivéramos', 'estivéssemos',
            'estou', 'está', 'estão', 'eu', 'foi', 'fomos', 'for', 'fora', 'foram',
            'forem', 'formos', 'fosse', 'fossem', 'fui', 'fôramos', 'fôssemos',
            'haja', 'hajam', 'hajamos', 'havemos', 'havia', 'hei', 'houve',
            'houvemos', 'houver', 'houvera', 'houveram', 'houverei', 'houverem',
            'houveremos', 'houveria', 'houveriam', 'houveríamos', 'houverá',
            'houverão', 'houveríamos', 'houvesse', 'houvessem', 'houvéramos',
            'houvéssemos', 'há', 'hão', 'isso', 'isto', 'já', 'lhe', 'lhes', 'mais',
            'mas', 'me', 'mesmo', 'meu', 'meus', 'minha', 'minhas', 'muito', 'na',
            'nas', 'nem', 'no', 'nos', 'nossa', 'nossas', 'nosso', 'nossos', 'num',
            'numa', 'não', 'nós', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo',
            'pelos', 'por', 'qual', 'quando', 'que', 'quem', 'se', 'seja', 'sejam',
            'sejamos', 'sem', 'ser', 'seria', 'seriam', 'será', 'serão', 'seríamos',
            'seu', 'seus', 'sua', 'suas', 'são', 'só', 'sua', 'suas', 'também',
            'te', 'tem', 'temos', 'tenha', 'tenham', 'tenhamos', 'tenho', 'ter',
            'terei', 'teremos', 'teria', 'teriam', 'terá', 'terão', 'teríamos',
            'teve', 'tinha', 'tinham', 'tive', 'tivemos', 'tiver', 'tivera',
            'tiveram', 'tiverem', 'tivermos', 'tivesse', 'tivessem', 'tivéramos',
            'tivéssemos', 'tu', 'tua', 'tuas', 'tém', 'tínhamos', 'um', 'uma',
            'você', 'vocês', 'vos', 'à', 'às', 'éramos', 'é', 'são'
        }
    
    def process(self, text: str) -> str:
        """
        Processa e limpa o texto do email
        
        Args:
            text (str): Texto original do email
            
        Returns:
            str: Texto processado e limpo
        """
        try:
            if not text:
                return ""
            
            # Converter para minúsculas
            text = text.lower()
            
            # Remover quebras de linha excessivas
            text = re.sub(r'\n+', ' ', text)
            
            # Remover espaços em branco excessivos
            text = re.sub(r'\s+', ' ', text)
            
            # Remover caracteres especiais, mas manter acentos
            text = re.sub(r'[^\w\sáàâãéèêíìîóòôõúùûç]', ' ', text)
            
            # Remover números isolados (mas manter números em contexto)
            text = re.sub(r'\b\d+\b', '', text)
            
            # Remover URLs
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            
            # Remover emails
            text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
            
            # Remover telefones
            text = re.sub(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', '', text)
            
            # Remover stop words
            words = text.split()
            words = [word for word in words if word not in self.stop_words and len(word) > 2]
            
            # Reconstruir texto
            processed_text = ' '.join(words)
            
            # Limpar espaços finais
            processed_text = processed_text.strip()
            
            return processed_text
            
        except Exception as e:
            logger.error(f"Erro ao processar texto: {e}")
            return text  # Retorna texto original em caso de erro
    
    def process_file(self, content: bytes, filename: str) -> str:
        """
        Processa arquivo (PDF ou TXT) e extrai texto
        
        Args:
            content (bytes): Conteúdo do arquivo
            filename (str): Nome do arquivo
            
        Returns:
            str: Texto extraído e processado
        """
        try:
            if filename.lower().endswith('.pdf'):
                return self._extract_pdf_text(content)
            elif filename.lower().endswith('.txt'):
                return self._extract_txt_text(content)
            else:
                raise ValueError(f"Tipo de arquivo não suportado: {filename}")
                
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {filename}: {e}")
            raise
    
    def _extract_pdf_text(self, content: bytes) -> str:
        """Extrai texto de arquivo PDF"""
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + " "
            
            return self.process(text)
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {e}")
            raise
    
    def _extract_txt_text(self, content: bytes) -> str:
        """Extrai texto de arquivo TXT"""
        try:
            # Tentar diferentes encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    text = content.decode(encoding)
                    return self.process(text)
                except UnicodeDecodeError:
                    continue
            
            # Se nenhum encoding funcionar, usar utf-8 com errors='ignore'
            text = content.decode('utf-8', errors='ignore')
            return self.process(text)
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto do TXT: {e}")
            raise
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> list:
        """
        Extrai palavras-chave do texto
        
        Args:
            text (str): Texto processado
            max_keywords (int): Número máximo de palavras-chave
            
        Returns:
            list: Lista de palavras-chave
        """
        try:
            # Contar frequência das palavras
            word_freq = {}
            words = text.split()
            
            for word in words:
                if len(word) > 3:  # Palavras com mais de 3 caracteres
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Ordenar por frequência
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            # Retornar as palavras mais frequentes
            keywords = [word for word, freq in sorted_words[:max_keywords]]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Erro ao extrair palavras-chave: {e}")
            return []
    
    def get_text_stats(self, text: str) -> dict:
        """
        Retorna estatísticas do texto
        
        Args:
            text (str): Texto a ser analisado
            
        Returns:
            dict: Estatísticas do texto
        """
        try:
            words = text.split()
            sentences = text.split('.')
            
            return {
                'word_count': len(words),
                'sentence_count': len([s for s in sentences if s.strip()]),
                'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
                'unique_words': len(set(words)),
                'text_length': len(text)
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {}
