#!/bin/bash

echo "🛑 Parando Sistema de Classificação de Emails"
echo ""

# Parar container Docker
echo "📦 Parando Backend (Docker)..."
docker stop case-pratico-backend 2>/dev/null && echo "✅ Backend parado!" || echo "⚠️  Backend já estava parado"

# Remover container
echo "🧹 Removendo container..."
docker rm case-pratico-backend 2>/dev/null && echo "✅ Container removido!" || echo "⚠️  Container já foi removido"

# Parar servidor frontend
echo "🌐 Parando Frontend..."
pkill -f "python3 -m http.server 8001" 2>/dev/null && echo "✅ Frontend parado!" || echo "⚠️  Frontend já estava parado"

# Verificar se as portas estão livres
echo ""
echo "🔍 Verificando portas..."
if lsof -i :8001 >/dev/null 2>&1; then
    echo "⚠️  Porta 8001 ainda em uso"
else
    echo "✅ Porta 8001 liberada"
fi

if lsof -i :8002 >/dev/null 2>&1; then
    echo "⚠️  Porta 8002 ainda em uso"
else
    echo "✅ Porta 8002 liberada"
fi

echo ""
echo "🎯 Sistema parado com sucesso!"
echo "Para iniciar novamente, execute: ./start.sh"
