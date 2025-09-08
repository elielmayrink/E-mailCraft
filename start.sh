#!/bin/bash

echo "🚀 Iniciando Sistema de Classificação de Emails"
echo ""

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "🛑 Parando todos os serviços..."
    docker stop case-pratico-backend 2>/dev/null || true
    pkill -f "python3 -m http.server 8001" 2>/dev/null || true
    echo "✅ Todos os serviços parados!"
    exit 0
}

# Capturar Ctrl+C para limpeza
trap cleanup SIGINT SIGTERM

# Verificar se Docker está rodando
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Parar containers antigos se existirem
echo "🧹 Limpando containers antigos..."
docker stop case-pratico-backend 2>/dev/null || true
docker rm case-pratico-backend 2>/dev/null || true
pkill -f "python3 -m http.server 8001" 2>/dev/null || true

# Construir e iniciar backend (Docker)
echo "📦 Construindo e iniciando Backend (Docker)..."
docker build -t case-pratico-backend ./backend >/dev/null 2>&1
docker run -d --name case-pratico-backend -p 8002:8002 --env-file ./backend/config.env -v $(pwd)/backend:/app case-pratico-backend

# Executar migrações do banco de dados (Alembic)
echo "🗄️ Executando migrações do banco (alembic upgrade head)..."
docker exec case-pratico-backend bash -lc "alembic upgrade head" || {
    echo "❌ Falha ao executar migrações. Verificando logs do container...";
    docker logs case-pratico-backend;
    exit 1;
}

# Aguardar backend inicializar
echo "⏳ Aguardando Backend inicializar..."
sleep 15

# Testar backend
echo "🔍 Testando Backend..."
if curl -s http://localhost:8002/health >/dev/null; then
    echo "✅ Backend funcionando!"
else
    echo "❌ Erro no Backend. Verificando logs..."
    docker logs case-pratico-backend
    exit 1
fi

# Iniciar frontend
echo "🌐 Iniciando Frontend..."
cd frontend
python3 -m http.server 8001 >/dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

# Aguardar frontend inicializar
sleep 3

# Testar frontend
echo "🔍 Testando Frontend..."
if curl -s http://localhost:8001/ >/dev/null; then
    echo "✅ Frontend funcionando!"
else
    echo "❌ Erro no Frontend"
    exit 1
fi

echo ""
echo "🎉 Sistema iniciado com sucesso!"
echo ""
echo "🌐 URLs de Acesso:"
echo "   📱 Interface Principal: http://localhost:8001"
echo "   🔧 API Backend: http://localhost:8002"
echo "   📚 Documentação API: http://localhost:8002/docs"
echo "   ❤️  Health Check: http://localhost:8002/health"
echo ""
echo "📊 Status dos Serviços:"
echo "   ✅ Backend (Docker): Rodando na porta 8002"
echo "   ✅ Frontend: Rodando na porta 8001"
echo ""
echo "🛑 Para parar todos os serviços, pressione Ctrl+C"
echo ""

# Manter script rodando e mostrar logs
echo "📋 Logs do Backend (Ctrl+C para parar):"
echo "----------------------------------------"
docker logs -f case-pratico-backend
