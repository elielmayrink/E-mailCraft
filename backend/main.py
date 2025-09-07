from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from models.classifier import EmailClassifier
from models.response_generator import ResponseGenerator
from utils.text_processor import TextProcessor

# Carregar variáveis de ambiente do arquivo config.env
load_dotenv('config.env')

app = FastAPI(title="Email Classification API", version="1.0.0")

# CORS middleware para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes (será feito nas funções)
classifier = None
response_generator = None
text_processor = None

def get_components():
    """Inicializa os componentes se necessário"""
    global classifier, response_generator, text_processor
    if classifier is None:
        classifier = EmailClassifier()
    if response_generator is None:
        response_generator = ResponseGenerator()
        # Configurar cliente Gemini no classificador se disponível
        if hasattr(response_generator, 'gemini_client') and response_generator.gemini_client:
            classifier.set_gemini_client(response_generator.gemini_client)
    if text_processor is None:
        text_processor = TextProcessor()
    return classifier, response_generator, text_processor

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial com interface simples"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Classification System</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 15px; border-radius: 4px; }
            .productive { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .unproductive { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>📧 Sistema de Classificação de Emails</h1>
        <div class="container">
            <form id="emailForm">
                <div class="form-group">
                    <label for="emailText">Texto do Email:</label>
                    <textarea id="emailText" rows="10" placeholder="Cole aqui o conteúdo do email..."></textarea>
                </div>
                <div class="form-group">
                    <label for="emailFile">Ou faça upload de um arquivo (.txt ou .pdf):</label>
                    <input type="file" id="emailFile" accept=".txt,.pdf">
                </div>
                <button type="submit">Classificar Email</button>
            </form>
            <div id="result" class="result" style="display: none;"></div>
        </div>
        
        <script>
            document.getElementById('emailForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const resultDiv = document.getElementById('result');
                const emailText = document.getElementById('emailText').value;
                const emailFile = document.getElementById('emailFile').files[0];
                
                if (!emailText && !emailFile) {
                    alert('Por favor, insira o texto do email ou faça upload de um arquivo.');
                    return;
                }
                
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = 'Processando...';
                
                try {
                    let response;
                    if (emailFile) {
                        const formData = new FormData();
                        formData.append('file', emailFile);
                        response = await fetch('/classify-file', {
                            method: 'POST',
                            body: formData
                        });
                    } else {
                        response = await fetch('/classify-text', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ text: emailText })
                        });
                    }
                    
                    const data = await response.json();
                    
                    if (data.category === 'Produtivo') {
                        resultDiv.className = 'result productive';
                    } else {
                        resultDiv.className = 'result unproductive';
                    }
                    
                    resultDiv.innerHTML = `
                        <h3>Categoria: ${data.category}</h3>
                        <p><strong>Resposta Sugerida:</strong></p>
                        <p>${data.response}</p>
                    `;
                } catch (error) {
                    resultDiv.className = 'result';
                    resultDiv.innerHTML = 'Erro ao processar o email. Tente novamente.';
                }
            });
        </script>
    </body>
    </html>
    """

@app.post("/classify-text")
async def classify_text(data: dict):
    """Classifica email a partir de texto"""
    try:
        text = data.get("text", "")
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Texto do email é obrigatório")
        
        # Obter componentes
        classifier, response_generator, text_processor = get_components()
        
        # Processar texto
        processed_text = text_processor.process(text)
        
        # Classificar
        classification_result = classifier.predict(processed_text)
        category = classification_result["category"]
        
        # Gerar resposta
        response = response_generator.generate(category, processed_text)
        
        return {
            "category": category,
            "response": response,
            "confidence": classification_result["confidence"],
            "method": classification_result["method"],
            "model_info": classification_result["model_info"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar email: {str(e)}")

@app.post("/classify-file")
async def classify_file(file: UploadFile = File(...)):
    """Classifica email a partir de arquivo"""
    try:
        # Verificar tipo de arquivo
        if not file.filename.endswith(('.txt', '.pdf')):
            raise HTTPException(status_code=400, detail="Apenas arquivos .txt e .pdf são suportados")
        
        # Obter componentes
        classifier, response_generator, text_processor = get_components()
        
        # Ler conteúdo do arquivo
        content = await file.read()
        
        # Processar arquivo
        text = text_processor.process_file(content, file.filename)
        
        # Classificar
        classification_result = classifier.predict(text)
        category = classification_result["category"]
        
        # Gerar resposta
        response = response_generator.generate(category, text)
        
        return {
            "category": category,
            "response": response,
            "confidence": classification_result["confidence"],
            "method": classification_result["method"],
            "model_info": classification_result["model_info"],
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")



@app.post("/test-ai")
async def test_ai(data: dict):
    """Teste simples da IA (Gemini API)"""
    try:
        from google import genai
        
        # Obter API key
        api_key = os.getenv("google_studio_key")
        if not api_key:
            return {"error": "API key não configurada"}
        
        # Criar cliente Gemini
        client = genai.Client(api_key=api_key)
        
        # Fazer uma pergunta simples
        question = data.get("question", "Diga apenas 'Olá, IA funcionando!' em português")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=question
        )
        
        result = response.text
        
        return {
            "status": "success",
            "question": question,
            "answer": result,
            "model": "gemini-2.5-flash"
        }
        
    except Exception as e:
        return {"error": f"Erro: {str(e)}"}

@app.post("/configure-ai")
async def configure_ai(data: dict):
    """Configura API key da IA (Gemini)"""
    try:
        api_key = data.get("api_key", "")
        if not api_key:
            raise HTTPException(status_code=400, detail="API key é obrigatória")
        
        success = response_generator.set_gemini_key(api_key)
        if success:
            return {"status": "success", "message": "IA configurada com sucesso!"}
        else:
            raise HTTPException(status_code=500, detail="Erro ao configurar IA")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {"status": "healthy", "message": "API funcionando corretamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
