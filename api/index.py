"""
Arquivo principal para Vercel - versão simplificada para debug
"""
from fastapi import FastAPI

# Aplicação FastAPI simplificada para testar a Vercel (sem root_path)
app = FastAPI(title="Debug API")

@app.get("/")
def root():
    return {
        "status": "ok", 
        "message": "FastAPI funcionando na Vercel!",
        "version": "debug-simplified"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "Health check funcionando!",
        "service": "debug-api"
    }

@app.get("/debug")
def debug():
    import os
    return {
        "status": "debug",
        "environment": {
            "VERCEL": os.getenv("VERCEL"),
            "PYTHON_VERSION": os.getenv("PYTHON_VERSION"),
        },
        "root_path": app.root_path,
        "message": "Debug endpoint funcionando!"
    }
