# 🤝 Guia de Contribuição - AutoU

## 🎯 Como Contribuir para o Projeto

Este guia te ensina **passo a passo** como configurar o projeto na sua máquina local, mesmo se você nunca fez isso antes!

## 📋 Pré-requisitos

Antes de começar, você precisa ter instalado:

- **Python 3.10+** ([Download aqui](https://www.python.org/downloads/))
- **Git** ([Download aqui](https://git-scm.com/downloads))
- **Conta Google** (para Firebase, Gmail e Gemini)

## 🚀 Passo a Passo Completo

### 1️⃣ **Clone o Projeto**

```bash
# Abra o terminal e digite:
git clone https://github.com/seu-usuario/case-pratico-autoU.git
cd case-pratico-autoU
```

### 2️⃣ **Criar Projeto no Firebase**

#### 2.1 Acesse o Firebase Console

1. Vá para [https://console.firebase.google.com/](https://console.firebase.google.com/)
2. Clique em **"Criar um projeto"**
3. Digite o nome: `email-agent-classifier`
4. Clique em **"Continuar"**

#### 2.2 Configurar Google Analytics (Opcional)

1. Desmarque **"Habilitar Google Analytics"** (não precisamos)
2. Clique em **"Criar projeto"**
3. Aguarde alguns segundos

#### 2.3 Configurar Autenticação

1. No menu lateral, clique em **"Authentication"**
2. Clique em **"Começar"**
3. Vá para a aba **"Sign-in method"**
4. Clique em **"Google"**
5. Ative o toggle **"Habilitar"**
6. Escolha um **"Nome do projeto de suporte"** (pode ser o mesmo)
7. Clique em **"Salvar"**

#### 2.4 Obter Credenciais do Firebase

1. Vá para **"Configurações do projeto"** (ícone de engrenagem)
2. Clique na aba **"Contas de serviço"**
3. Clique em **"Gerar nova chave privada"**
4. Baixe o arquivo JSON (guarde bem!)
5. Anote o **"Project ID"** (aparece no topo da página)

### 3️⃣ **Criar Projeto no Google Cloud (Gmail)**

#### 3.1 Acesse o Google Cloud Console

1. Vá para [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Clique em **"Selecionar um projeto"** (canto superior direito)
3. Clique em **"Novo projeto"**
4. Nome: `gmail-oauth-project`
5. Clique em **"Criar"**

#### 3.2 Habilitar Gmail API

1. No menu lateral, vá em **"APIs e serviços" > "Biblioteca"**
2. Procure por **"Gmail API"**
3. Clique em **"Gmail API"**
4. Clique em **"Habilitar"**

#### 3.3 Configurar OAuth2

1. Vá em **"APIs e serviços" > "Credenciais"**
2. Clique em **"Criar credenciais" > "ID do cliente OAuth 2.0"**
3. Tipo de aplicação: **"Aplicativo da Web"**
4. Nome: `Gmail OAuth Client`
5. **URIs de redirecionamento autorizados:**
   - Adicione: `http://localhost:8002/gmail/oauth2callback`
6. Clique em **"Criar"**
7. **IMPORTANTE:** Anote o **Client ID** e **Client Secret**

### 4️⃣ **Configurar Gemini AI**

#### 4.1 Acesse o Google AI Studio

1. Vá para [https://aistudio.google.com/](https://aistudio.google.com/)
2. Faça login com sua conta Google
3. Clique em **"Get API key"**
4. Clique em **"Create API key"**
5. Escolha o projeto criado anteriormente
6. Clique em **"Create API key"**
7. **IMPORTANTE:** Copie e guarde a API key

### 5️⃣ **Configurar o Projeto Local**

#### 5.1 Instalar Dependências

```bash
# No terminal, dentro da pasta do projeto:
cd backend
pip install -r requirements.txt
```

#### 5.2 Criar Arquivo de Configuração

```bash
# Copie o arquivo de exemplo:
cp env.example config.env
```

#### 5.3 Editar Configurações

Abra o arquivo `backend/config.env` e preencha com suas credenciais:

```bash
# Database (não precisa mudar)
DATABASE_URL=sqlite:///./email_agent.db

# Firebase Admin SDK (do passo 2.4)
FIREBASE_PROJECT_ID=seu-project-id-aqui
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nSUA_CHAVE_PRIVADA_AQUI\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@seu-projeto.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY_ID=sua-private-key-id
FIREBASE_CLIENT_ID=seu-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40seu-projeto.iam.gserviceaccount.com

# Gmail OAuth2 (do passo 3.3)
GMAIL_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=seu-client-secret
GMAIL_PROJECT_ID=seu-project-id
GMAIL_REDIRECT_URI=http://localhost:8002/gmail/oauth2callback

# JWT (pode deixar como está)
JWT_SECRET_KEY=sua-chave-secreta-super-segura
JWT_ALGORITHM=HS256

# Gemini AI (do passo 4.1)
google_studio_key=SUA_API_KEY_GEMINI_AQUI
```

### 6️⃣ **Configurar Banco de Dados**

```bash
# No terminal, dentro da pasta backend:
alembic upgrade head
```

### 7️⃣ **Iniciar o Sistema**

#### 7.1 Iniciar Backend

```bash
# No terminal, dentro da pasta backend:
python3 main.py
```

#### 7.2 Iniciar Frontend (novo terminal)

```bash
# Abra um novo terminal:
cd frontend
python3 -m http.server 8001
```

### 8️⃣ **Testar o Sistema**

1. Abra o navegador em: `http://localhost:8001`
2. Clique em **"Entrar com Google"**
3. Faça login com sua conta Google
4. Clique em **"Conectar ao Gmail"**
5. Autorize o acesso ao Gmail
6. Teste a classificação de emails!

## 🎉 Pronto!

Se você seguiu todos os passos, o sistema deve estar funcionando perfeitamente!

## 🆘 Problemas Comuns

### ❌ "Erro de autenticação"

- Verifique se todas as credenciais estão corretas no `config.env`
- Certifique-se de que o Firebase está configurado corretamente

### ❌ "Gmail não conecta"

- Verifique se o Gmail API está habilitado
- Confirme se a URI de redirecionamento está correta

### ❌ "Gemini não funciona"

- Verifique se a API key está correta
- Certifique-se de que a API key tem permissões adequadas

### ❌ "Banco de dados não funciona"

- Execute: `alembic upgrade head`
- Verifique se o arquivo `email_agent.db` foi criado

## 📞 Precisa de Ajuda?

Se você tiver problemas:

1. **Verifique os logs** no terminal
2. **Confira as credenciais** no arquivo `config.env`
3. **Teste cada serviço** individualmente
4. **Abra uma issue** no GitHub com detalhes do erro

## 🎯 Próximos Passos

Agora que o sistema está funcionando, você pode:

- **Explorar o código** para entender como funciona
- **Fazer melhorias** na interface
- **Adicionar novas funcionalidades**
- **Corrigir bugs** encontrados
- **Otimizar a performance**

## 🚀 Contribuindo com Código

1. **Fork** o projeto
2. **Crie uma branch** para sua feature: `git checkout -b minha-feature`
3. **Faça suas alterações**
4. **Teste** tudo funcionando
5. **Commit** suas mudanças: `git commit -m "Adiciona nova feature"`
6. **Push** para sua branch: `git push origin minha-feature`
7. **Abra um Pull Request**

## 📝 Boas Práticas

- **Sempre teste** suas mudanças
- **Documente** novas funcionalidades
- **Siga** o padrão de código existente
- **Escreva** commits descritivos
- **Peça ajuda** se precisar!

---

**Bem-vindo ao projeto AutoU! 🎉**
