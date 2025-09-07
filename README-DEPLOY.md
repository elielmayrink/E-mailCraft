# 🚀 Sistema de Classificação de Emails - Deploy

## 📋 Comandos de Deploy

### 🎯 **Comando Principal (Recomendado)**

```bash
./start.sh
```

**O que faz:**

- ✅ Para containers antigos
- ✅ Constrói e inicia Backend (Docker)
- ✅ Inicia Frontend (Python HTTP Server)
- ✅ Testa ambos os serviços
- ✅ Mostra logs em tempo real
- ✅ Para tudo com Ctrl+C

### 🏭 **Deploy para Produção**

```bash
./deploy.sh prod
```

**O que faz:**

- ✅ Verifica dependências
- ✅ Limpa ambiente anterior
- ✅ Constrói Backend com Docker
- ✅ Inicia Frontend
- ✅ Testa todos os serviços
- ✅ Modo produção com logs

### 🧪 **Deploy para Desenvolvimento**

```bash
./deploy.sh
```

**O que faz:**

- ✅ Mesmo que produção, mas em modo desenvolvimento
- ✅ Roda em background
- ✅ Monitora status dos serviços

### 🛑 **Parar Todos os Serviços**

```bash
./stop.sh
```

**O que faz:**

- ✅ Para container Docker
- ✅ Para servidor Frontend
- ✅ Remove containers
- ✅ Libera portas

## 🌐 URLs de Acesso

Após executar qualquer comando de deploy:

- **📱 Interface Principal**: http://localhost:8001
- **🔧 API Backend**: http://localhost:8002
- **📚 Documentação API**: http://localhost:8002/docs
- **❤️ Health Check**: http://localhost:8002/health

## 📊 Status dos Serviços

### Backend (Docker)

- **Porta**: 8002
- **Container**: `case-pratico-backend`
- **Imagem**: `case-pratico-backend`
- **Status**: `docker ps`

### Frontend (Python HTTP Server)

- **Porta**: 8001
- **Processo**: `python3 -m http.server 8001`
- **Status**: `lsof -i :8001`

## 🔧 Comandos Úteis

### Ver Logs

```bash
# Logs do Backend
docker logs -f case-pratico-backend

# Logs em tempo real
docker logs -f case-pratico-backend
```

### Verificar Status

```bash
# Containers Docker
docker ps

# Portas em uso
lsof -i :8001
lsof -i :8002

# Testar API
curl http://localhost:8002/health
```

### Limpeza Completa

```bash
# Parar tudo
./stop.sh

# Limpar Docker
docker system prune -f

# Remover imagem
docker rmi case-pratico-backend
```

## 🚨 Troubleshooting

### Erro: "Port already in use"

```bash
./stop.sh
./start.sh
```

### Erro: "Docker not running"

```bash
# Iniciar Docker
sudo systemctl start docker

# Verificar status
docker info
```

### Erro: "Container not found"

```bash
# Reconstruir
docker build -t case-pratico-backend ./backend
./start.sh
```

### Frontend não carrega

```bash
# Verificar se está rodando
lsof -i :8001

# Reiniciar frontend
pkill -f "python3 -m http.server 8001"
cd frontend && python3 -m http.server 8001 &
```

## 📝 Exemplo de Uso Completo

```bash
# 1. Iniciar sistema
./start.sh

# 2. Acessar interface
# Abrir http://localhost:8001 no navegador

# 3. Testar classificação
# - Colar texto de email
# - Ou fazer upload de arquivo
# - Clicar em "Classificar Email"

# 4. Ver resultados
# - Categoria (Produtivo/Improdutivo)
# - Confiança da análise
# - Resposta sugerida
# - Método usado (IA/Palavras-chave)

# 5. Parar sistema
# Pressionar Ctrl+C ou executar ./stop.sh
```

## 🎯 Para Deploy em Produção

1. **Configurar variáveis de ambiente**:

   ```bash
   # Editar backend/config.env
   google_studio_key="sua_api_key_aqui"
   ```

2. **Executar deploy**:

   ```bash
   ./deploy.sh prod
   ```

3. **Configurar proxy reverso** (opcional):

   ```nginx
   # Nginx
   location / {
       proxy_pass http://localhost:8001;
   }

   location /api/ {
       proxy_pass http://localhost:8002/;
   }
   ```

4. **Monitorar logs**:
   ```bash
   docker logs -f case-pratico-backend
   ```

## ✅ Checklist de Deploy

- [ ] Docker instalado e rodando
- [ ] Python3 instalado
- [ ] Arquivo `backend/config.env` configurado
- [ ] Portas 8001 e 8002 livres
- [ ] Scripts executáveis (`chmod +x`)
- [ ] Teste de conectividade
- [ ] Logs sem erros
- [ ] Interface acessível
- [ ] API respondendo
- [ ] Classificação funcionando

**🎉 Sistema pronto para uso!**
