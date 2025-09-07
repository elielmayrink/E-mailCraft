# 📧 AutoU – Sistema de Classificação de Emails

Assistente completo para classificar emails (Produtivo vs. Improdutivo), sugerir respostas e testar integrações com IA (Gemini). Inclui backend FastAPI em Docker e frontend estático simples.

## 🗂️ Estrutura

```
case-pratico-autoU/
├── backend/              # API FastAPI (Docker)
├── frontend/             # UI estática (HTTP server)
├── docker-compose.yml    # Alternativa para subir o backend
├── start.sh              # Inicia tudo (recomendado)
├── stop.sh               # Para tudo
├── deploy.sh             # Deploy dev/prod
└── README.md             # Este guia
```

## ✅ Requisitos

- Docker e Docker daemon ativos
- Python 3.10+

Opcional (para rodar sem scripts): curl, lsof

## 🚀 Início Rápido (recomendado)

```bash
./start.sh
```

O que acontece:

- Constrói e inicia o backend em Docker na porta 8002
- Sobe o frontend com `python3 -m http.server` na porta 8001
- Faz checagens de saúde e mostra URLs

Acesse:

- Interface: http://localhost:8001
- API: http://localhost:8002
- Docs (Swagger): http://localhost:8002/docs
- Health: http://localhost:8002/health

Para parar:

```bash
./stop.sh
```

## 🏭 Deploy

- Desenvolvimento (background):

```bash
./deploy.sh
```

- Produção (mostra logs):

```bash
./deploy.sh prod
```

## 🐳 Usando Docker Compose (opcional)

O `docker-compose.yml` sobe apenas o backend:

```bash
docker compose up --build -d
# Frontend
cd frontend && python3 -m http.server 8001 &
```

URLs: iguais ao Início Rápido.

## 🧰 Execução Manual (sem scripts)

- Backend (Docker):

```bash
docker build -t case-pratico-backend ./backend
docker run -d --name case-pratico-backend -p 8002:8002 --env-file ./backend/config.env -v $(pwd)/backend:/app case-pratico-backend
```

- Frontend (HTTP server):

```bash
cd frontend
python3 -m http.server 8001 &
```

## ⚙️ Configuração

Crie `backend/config.env` (baseado no `backend/env.example` se houver):

```
google_studio_key="SUA_API_KEY_GEMINI"
```

- A API key é opcional para classificação; usada para geração de respostas/testes via Gemini.

## 🔌 Endpoints Principais (FastAPI)

- `GET /` – Página HTML simples para teste rápido
- `POST /classify-text` – Corpo: `{ "text": "conteúdo do email" }`
- `POST /classify-file` – Form-Data: `file: .txt | .pdf`
- `POST /test-ai` – Teste simples com Gemini. Corpo: `{ "question": "..." }`
- `POST /configure-ai` – Configura a API key em runtime. Corpo: `{ "api_key": "..." }`
- `GET /health` – Health check

Docs interativas: http://localhost:8002/docs

## 🖥️ Frontend

A UI pública fica em `frontend/` com página `index.html`. No Início Rápido ela é servida em http://localhost:8001.

## 🧪 Fluxo de Uso

1. Inicie com `./start.sh`
2. Acesse http://localhost:8001
3. Insira texto ou faça upload (.txt/.pdf) e clique em “Classificar Email”
4. Veja: categoria, confiança, resposta sugerida e método
5. Pare com `./stop.sh`

## 🛠️ Troubleshooting

- Porta em uso (8001/8002):

```bash
./stop.sh && ./start.sh
```

- Docker não está rodando:

```bash
sudo systemctl start docker && docker info
```

- Backend não sobe com Compose:

```bash
docker compose logs -f backend
```

- Ver logs do backend (Docker):

```bash
docker logs -f case-pratico-backend
```

- Limpeza completa de Docker (cautela):

```bash
docker system prune -f
# opcional
docker rmi case-pratico-backend
```

## 🔒 Segurança

- Em produção, restrinja `CORS` e proteja `config.env`.
- Use um proxy reverso (Nginx) se expor publicamente.

## 📄 Licença

Defina a licença desejada (ex.: MIT) e adicione `LICENSE` na raiz.
