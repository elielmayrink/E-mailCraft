# 📧 Frontend - Sistema de Classificação de Emails

Frontend moderno e responsivo para o sistema de classificação automática de emails usando Gemini AI.

## 🚀 Características

- **Design Moderno**: Interface limpa e intuitiva inspirada nos melhores formulários web
- **Upload de Arquivos**: Suporte para arquivos .txt e .pdf com drag & drop
- **Responsivo**: Funciona perfeitamente em desktop, tablet e mobile
- **Feedback Visual**: Notificações toast, loading states e animações suaves
- **Integração com IA**: Conectado com a API Gemini para classificação e geração de respostas

## 📁 Estrutura de Arquivos

```
frontend/
├── index.html          # Página principal
├── styles.css          # Estilos CSS modernos
├── script.js           # JavaScript para interação
├── README.md           # Este arquivo
└── test-emails/        # Arquivos de teste
    ├── email-produtivo.txt
    ├── email-improdutivo.txt
    └── email-solicitacao.txt
```

## 🛠️ Como Usar

### 1. Iniciar o Backend

```bash
cd backend
python3 main.py
```

### 2. Abrir o Frontend

Abra o arquivo `index.html` em um navegador web ou use um servidor local:

```bash
# Usando Python
python3 -m http.server 8001

# Usando Node.js
npx serve .

# Usando PHP
php -S localhost:8001
```

### 3. Testar o Sistema

#### Opção 1: Texto Direto

1. Cole o texto do email na área de texto
2. Clique em "Classificar Email"
3. Veja os resultados da classificação

#### Opção 2: Upload de Arquivo

1. Arraste e solte um arquivo .txt ou .pdf na área de upload
2. Ou clique em "Escolher Arquivo" para selecionar
3. Clique em "Classificar Email"
4. Veja os resultados

## 🎯 Funcionalidades

### Upload de Arquivos

- **Drag & Drop**: Arraste arquivos diretamente para a área de upload
- **Seleção Manual**: Clique para escolher arquivos do computador
- **Validação**: Apenas arquivos .txt e .pdf são aceitos
- **Preview**: Visualização do nome e tamanho do arquivo

### Classificação

- **Categorização**: Emails classificados como "Produtivo" ou "Improdutivo"
- **Confiança**: Indicador visual da confiança da classificação
- **Resposta IA**: Geração automática de respostas usando Gemini AI

### Interface

- **Loading States**: Indicadores visuais durante o processamento
- **Toast Notifications**: Feedback imediato para ações do usuário
- **Responsivo**: Adapta-se a diferentes tamanhos de tela
- **Acessibilidade**: Suporte a navegação por teclado

## ⌨️ Atalhos de Teclado

- **Ctrl/Cmd + Enter**: Classificar email
- **Escape**: Fechar loading overlay
- **Enter**: Nova linha no textarea (não submete o formulário)

## 🎨 Design

O design foi inspirado nos melhores formulários web modernos, com:

- Gradientes suaves e cores harmoniosas
- Sombras e bordas arredondadas
- Animações e transições suaves
- Tipografia clara e legível
- Ícones Font Awesome para melhor UX

## 🔧 Personalização

### Cores

As cores podem ser personalizadas editando as variáveis CSS em `styles.css`:

```css
:root {
  --primary-color: #6366f1;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  /* ... outras variáveis */
}
```

### API

Para alterar a URL da API, edite a constante em `script.js`:

```javascript
const API_BASE_URL = "http://localhost:8000";
```

## 📱 Responsividade

O frontend é totalmente responsivo e funciona em:

- **Desktop**: Layout completo com todas as funcionalidades
- **Tablet**: Layout adaptado com elementos reorganizados
- **Mobile**: Layout otimizado para telas pequenas

## 🧪 Arquivos de Teste

Incluídos na pasta `test-emails/`:

- `email-produtivo.txt`: Email que requer ação (problema técnico)
- `email-improdutivo.txt`: Email social (felicitações)
- `email-solicitacao.txt`: Email de negócios (solicitação de orçamento)

## 🚨 Solução de Problemas

### API não conecta

- Verifique se o backend está rodando na porta 8000
- Confirme se a URL da API está correta
- Verifique o console do navegador para erros

### Upload não funciona

- Verifique se o arquivo é .txt ou .pdf
- Confirme se o arquivo não está corrompido
- Teste com os arquivos de exemplo incluídos

### Classificação incorreta

- O modelo usa palavras-chave como fallback
- Para melhor precisão, treine um modelo específico
- Teste com diferentes tipos de email

## 🔮 Próximas Melhorias

- [ ] Suporte a mais tipos de arquivo
- [ ] Histórico de classificações
- [ ] Exportação em diferentes formatos
- [ ] Temas personalizáveis
- [ ] Modo escuro
- [ ] Integração com mais APIs de IA
