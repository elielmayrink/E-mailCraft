# Estrutura Modular do Frontend

Este diretório contém os arquivos JavaScript organizados de forma modular para melhor manutenibilidade e organização do código.

## 📁 Estrutura de Arquivos

### `config.js`

- **Propósito**: Configurações globais da aplicação
- **Conteúdo**: URLs da API, tipos de arquivo válidos, configurações de UI
- **Exporta**: `window.CONFIG`

### `dom.js`

- **Propósito**: Gerenciamento de elementos DOM
- **Conteúdo**: Referências para todos os elementos HTML, inicialização do DOM
- **Exporta**: `window.DOM`

### `validation.js`

- **Propósito**: Validações de formulário e arquivos
- **Conteúdo**: Validação de tipos de arquivo, validação de formulário
- **Exporta**: `window.Validation`

### `file-handler.js`

- **Propósito**: Gerenciamento de upload de arquivos
- **Conteúdo**: Drag & drop, seleção de arquivos, processamento de arquivos
- **Exporta**: `window.FileHandler`

### `api.js`

- **Propósito**: Chamadas para a API do backend
- **Conteúdo**: Health check, classificação de texto/arquivo, testes
- **Exporta**: `window.API`

### `ui.js`

- **Propósito**: Interface do usuário e feedback visual
- **Conteúdo**: Loading, toasts, exibição de resultados
- **Exporta**: `window.UI`

### `app.js`

- **Propósito**: Aplicação principal e coordenação
- **Conteúdo**: Inicialização, event listeners, fluxo principal
- **Exporta**: `window.App`

## 🔄 Fluxo de Carregamento

Os arquivos são carregados na seguinte ordem no `index.html`:

1. `config.js` - Configurações
2. `dom.js` - Elementos DOM
3. `validation.js` - Validações
4. `file-handler.js` - Upload de arquivos
5. `api.js` - Chamadas da API
6. `ui.js` - Interface do usuário
7. `app.js` - Aplicação principal

## 🎯 Vantagens da Estrutura Modular

- **Manutenibilidade**: Cada arquivo tem uma responsabilidade específica
- **Reutilização**: Módulos podem ser reutilizados em outras partes
- **Debugging**: Mais fácil localizar e corrigir problemas
- **Colaboração**: Diferentes desenvolvedores podem trabalhar em módulos diferentes
- **Testes**: Cada módulo pode ser testado independentemente

## 🚀 Como Usar

A aplicação é inicializada automaticamente quando o DOM estiver pronto. Todos os módulos são expostos globalmente através do objeto `window` para facilitar o acesso e debugging.

### Exemplo de uso:

```javascript
// Testar API
window.testAPI();

// Acessar configurações
console.log(window.CONFIG.API_BASE_URL);

// Acessar elementos DOM
console.log(window.DOM.emailText);
```
