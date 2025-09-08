#!/bin/bash

echo "🚀 Deploy do Sistema de Classificação de Emails"
echo ""

# Verificar se está em modo produção
if [ "$1" = "prod" ]; then
    echo "🏭 Modo Produção ativado"
    ENV_MODE="production"
else
    echo "🧪 Modo Desenvolvimento"
    ENV_MODE="development"
fi

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

# Verificar dependências
echo "🔍 Verificando dependências..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker primeiro."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale o Python3 primeiro."
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

echo "✅ Todas as dependências OK!"

# Limpar ambiente anterior
echo "🧹 Limpando ambiente anterior..."
docker stop case-pratico-backend 2>/dev/null || true
docker rm case-pratico-backend 2>/dev/null || true
pkill -f "python3 -m http.server 8001" 2>/dev/null || true

# Construir e iniciar backend
echo "📦 Construindo Backend..."
docker build -t case-pratico-backend ./backend

if [ $? -ne 0 ]; then
    echo "❌ Erro ao construir Backend"
    exit 1
fi

echo "🚀 Iniciando Backend..."
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
sleep 20

# Testar backend
echo "🔍 Testando Backend..."
for i in {1..5}; do
    if curl -s http://localhost:8002/health >/dev/null; then
        echo "✅ Backend funcionando!"
        break
    else
        echo "⏳ Tentativa $i/5 - Aguardando Backend..."
        sleep 5
    fi
    
    if [ $i -eq 5 ]; then
        echo "❌ Backend não respondeu. Verificando logs..."
        docker logs case-pratico-backend
        exit 1
    fi
done

# Iniciar frontend
echo "🌐 Iniciando Frontend..."
cd frontend
python3 -m http.server 8001 >/dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

# Aguardar frontend
sleep 3

# Testar frontend
echo "🔍 Testando Frontend..."
if curl -s http://localhost:8001/ >/dev/null; then
    echo "✅ Frontend funcionando!"
else
    echo "❌ Erro no Frontend"
    exit 1
fi

# Mostrar informações finais
echo ""
echo "🎉 Deploy realizado com sucesso!"
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
echo "   🏷️  Modo: $ENV_MODE"
echo ""
echo "🛑 Para parar: ./stop.sh ou Ctrl+C"
echo ""

# Se for produção, mostrar logs
if [ "$ENV_MODE" = "production" ]; then
    echo "📋 Logs do Backend (Produção):"
    echo "----------------------------------------"
    docker logs -f case-pratico-backend
else
    echo "💡 Dica: Para ver logs em tempo real, execute:"
    echo "   docker logs -f case-pratico-backend"
    echo ""
    echo "🔄 Sistema rodando em background..."
    echo "   Pressione Ctrl+C para parar"
    
    # Manter script rodando
    while true; do
        sleep 30
        if ! docker ps | grep -q case-pratico-backend; then
            echo "❌ Backend parou inesperadamente!"
            break
        fi
    done
fi
