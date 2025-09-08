"""
Aplicação Flask simples para testar compatibilidade com Vercel
"""
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def root():
    return jsonify({
        'status': 'ok',
        'message': 'Flask funcionando na Vercel!',
        'framework': 'Flask'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Health check Flask funcionando!',
        'framework': 'Flask'
    })

@app.route('/debug')
def debug():
    return jsonify({
        'status': 'debug',
        'environment': {
            'VERCEL': os.getenv('VERCEL'),
            'PYTHON_VERSION': os.getenv('PYTHON_VERSION'),
        },
        'message': 'Debug Flask funcionando!',
        'framework': 'Flask'
    })

if __name__ == '__main__':
    app.run(debug=True)
