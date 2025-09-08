# 🔐 Configuração do Firebase Auth

## 📋 Pré-requisitos

1. **Conta Google** com acesso ao Firebase Console
2. **Projeto Firebase** criado
3. **Autenticação Google** habilitada no Firebase

## 🚀 Passo a Passo

### 1. Criar Projeto Firebase

1. Acesse [Firebase Console](https://console.firebase.google.com/)
2. Clique em "Adicionar projeto"
3. Digite o nome do projeto (ex: "email-agent-classifier")
4. Habilite/desabilite Google Analytics conforme necessário
5. Clique em "Criar projeto"

### 2. Configurar Autenticação

1. No painel do projeto, clique em "Authentication"
2. Clique em "Começar"
3. Vá para a aba "Sign-in method"
4. Clique em "Google"
5. Ative o provedor Google
6. Configure o email de suporte do projeto
7. Salve as configurações

### 3. Obter Configurações do Projeto

1. No painel do projeto, clique na engrenagem ⚙️
2. Selecione "Configurações do projeto"
3. Role para baixo até "Seus aplicativos"
4. Clique em "Adicionar app" e selecione "Web" (ícone `</>`)
5. Digite um nome para o app (ex: "Email Agent Frontend")
6. **NÃO** marque "Também configurar o Firebase Hosting"
7. Clique em "Registrar app"
8. Copie as configurações do Firebase

### 4. Configurar Frontend

1. Copie o arquivo `firebase-config-example.js` para `firebase-config.js`:

   ```bash
   cp firebase-config-example.js firebase-config.js
   ```

2. Edite o arquivo `firebase-config.js` e substitua os valores:
   ```javascript
   const firebaseConfig = {
     apiKey: "SUA_API_KEY_AQUI",
     authDomain: "seu-projeto-id.firebaseapp.com",
     projectId: "seu-projeto-id",
     storageBucket: "seu-projeto-id.appspot.com",
     messagingSenderId: "123456789012",
     appId: "1:123456789012:web:abcdef1234567890abcdef",
   };
   ```

### 5. Configurar Backend

1. No Firebase Console, vá para "Configurações do projeto"
2. Clique na aba "Contas de serviço"
3. Clique em "Gerar nova chave privada"
4. Baixe o arquivo JSON da conta de serviço
5. Configure as variáveis de ambiente no backend:

```bash
# No arquivo .env do backend
FIREBASE_PROJECT_ID=seu-projeto-id
FIREBASE_PRIVATE_KEY_ID=seu-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nsua-chave-privada\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@seu-projeto.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=seu-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40seu-projeto.iam.gserviceaccount.com
```

## 🔧 Configurações Adicionais

### Domínios Autorizados

1. No Firebase Console, vá para "Authentication"
2. Clique na aba "Settings"
3. Em "Domínios autorizados", adicione:
   - `localhost` (para desenvolvimento)
   - Seu domínio de produção

### Scopes do Gmail

O sistema já está configurado para solicitar as permissões necessárias do Gmail:

- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.send`
- `https://www.googleapis.com/auth/gmail.modify`

## 🧪 Testando a Configuração

1. Inicie o backend:

   ```bash
   cd backend
   python main.py
   ```

2. Abra o frontend em um servidor local:

   ```bash
   cd frontend
   python -m http.server 8080
   ```

3. Acesse `http://localhost:8080`
4. Clique em "Entrar com Google"
5. Faça login com sua conta Google
6. Verifique se o usuário aparece na interface

## 🚨 Solução de Problemas

### Erro: "Firebase: Error (auth/api-key-not-valid)"

- Verifique se a `apiKey` está correta no `firebase-config.js`

### Erro: "Firebase: Error (auth/unauthorized-domain)"

- Adicione `localhost` aos domínios autorizados no Firebase Console

### Erro: "Token inválido" no backend

- Verifique se todas as variáveis de ambiente do Firebase estão configuradas
- Verifique se a chave privada está no formato correto (com `\n` para quebras de linha)

### Erro: "Usuário não autenticado"

- Verifique se o usuário fez login no frontend
- Verifique se o token está sendo enviado corretamente

## 📚 Recursos Adicionais

- [Documentação Firebase Auth](https://firebase.google.com/docs/auth)
- [Firebase Console](https://console.firebase.google.com/)
- [Configuração de autenticação Google](https://firebase.google.com/docs/auth/web/google-signin)
