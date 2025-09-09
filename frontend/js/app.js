// Aplicação principal
const App = {
  // Inicializar aplicação
  async init() {
    // Inicializar DOM
    window.DOM.init();

    // Aguardar Firebase estar carregado
    await this.waitForFirebase();

    // Inicializar event listeners
    this.initializeEventListeners();

    // Verificar status da API
    window.API.checkStatus();
  },

  // Aguardar Firebase estar carregado
  async waitForFirebase() {
    return new Promise((resolve) => {
      const checkFirebase = () => {
        if (
          typeof window.firebaseAuth !== "undefined" &&
          typeof window.authService !== "undefined" &&
          typeof window.authComponents !== "undefined"
        ) {
          resolve();
        } else {
          setTimeout(checkFirebase, 100);
        }
      };
      checkFirebase();
    });
  },

  // Inicializar event listeners
  initializeEventListeners() {
    const { emailFile, fileUploadArea, classifyBtn, emailText } = window.DOM;

    // File upload events
    emailFile.addEventListener("change", (e) =>
      window.FileHandler.handleFileSelect(e)
    );

    // Select file button
    const selectFileBtn = document.getElementById("selectFileBtn");
    if (selectFileBtn) {
      selectFileBtn.addEventListener("click", () => {
        emailFile.click();
      });
    }

    // Drag and drop events
    fileUploadArea.addEventListener("dragover", (e) =>
      window.FileHandler.handleDragOver(e)
    );
    fileUploadArea.addEventListener("dragleave", (e) =>
      window.FileHandler.handleDragLeave(e)
    );
    fileUploadArea.addEventListener("drop", (e) =>
      window.FileHandler.handleDrop(e)
    );

    // Form validation
    emailText.addEventListener("input", () => this.validateForm());
    emailFile.addEventListener("change", () => this.validateForm());

    // Classify button
    classifyBtn.addEventListener("click", () => this.classifyEmail());

    // Enter key para classificar
    emailText.addEventListener("keydown", (e) => {
      if (e.ctrlKey && e.key === "Enter") {
        this.classifyEmail();
      }
    });

    // Gmail buttons
    if (window.DOM.gmailAuthBtn) {
      window.DOM.gmailAuthBtn.addEventListener("click", async () => {
        try {
          // Verificar se usuário está autenticado
          if (!window.authService.isAuthenticated()) {
            window.UI.showToast(
              "Faça login primeiro para acessar o Gmail",
              "error"
            );
            return;
          }

          window.UI.showLoading("Conectando ao Gmail...");
          const data = await window.API.gmailPreview(5);
          window.UI.hideLoading();
          window.UI.renderGmailList(data);
          if (!data.auth_url && data.items?.length) {
            window.UI.showToast("Emails carregados do Gmail!", "success");
          }
        } catch (err) {
          window.UI.hideLoading();
          if (err.message === "Usuário não autenticado") {
            window.UI.showToast(
              "Faça login primeiro para acessar o Gmail",
              "error"
            );
          } else {
            window.UI.showToast(
              "Erro ao conectar Gmail: " + err.message,
              "error"
            );
          }
        }
      });
    }

    if (window.DOM.gmailRefreshBtn) {
      window.DOM.gmailRefreshBtn.addEventListener("click", async () => {
        try {
          // Verificar se usuário está autenticado
          if (!window.authService.isAuthenticated()) {
            window.UI.showToast(
              "Faça login primeiro para acessar o Gmail",
              "error"
            );
            return;
          }

          window.UI.showLoading("Atualizando emails...");
          const data = await window.API.gmailPreview(5);
          window.UI.hideLoading();
          window.UI.renderGmailList(data);
        } catch (err) {
          window.UI.hideLoading();
          if (err.message === "Usuário não autenticado") {
            window.UI.showToast(
              "Faça login primeiro para acessar o Gmail",
              "error"
            );
          } else {
            window.UI.showToast(
              "Erro ao atualizar Gmail: " + err.message,
              "error"
            );
          }
        }
      });
    }
  },

  // Validar formulário
  validateForm() {
    const isValid = window.Validation.validateForm(
      window.FileHandler.selectedFile,
      window.DOM.emailText
    );
    window.Validation.updateButtonState(isValid);
  },

  // Classificar email
  async classifyEmail() {
    // Validar formulário
    const isValid = window.Validation.validateForm(
      window.FileHandler.selectedFile,
      window.DOM.emailText
    );
    if (!isValid) {
      window.UI.showToast(
        "Por favor, insira um texto ou selecione um arquivo",
        "warning"
      );
      return;
    }

    try {
      window.UI.showLoading("Classificando email...");

      let response;

      if (window.FileHandler.selectedFile) {
        // Upload file
        response = await window.API.classifyFile(
          window.FileHandler.selectedFile
        );
      } else {
        // Classify text
        response = await window.API.classifyText(window.DOM.emailText.value);
      }

      window.UI.hideLoading();
      window.UI.displayResults(response);
    } catch (error) {
      console.error("❌ Erro na classificação:", error);
      window.UI.hideLoading();
      window.UI.showToast(
        "Erro ao classificar email: " + error.message,
        "error"
      );
    }
  },
};

// Inicializar aplicação quando DOM estiver pronto
document.addEventListener("DOMContentLoaded", () => {
  App.init();
});

// Exportar App para uso global
window.App = App;

// Funções globais para os botões do HTML
window.removeFile = () => window.FileHandler.removeFile();
window.testAI = () => window.API.testAI();
window.testAPI = window.API.testAPI;

// Funções que precisam ser implementadas
window.copyResponse = () => {
  const responseText = document.getElementById("responseText");
  if (responseText) {
    navigator.clipboard.writeText(responseText.textContent);
    window.UI.showToast(
      "Resposta copiada para a área de transferência!",
      "success"
    );
  }
};

window.resetForm = () => {
  window.FileHandler.removeFile();
  window.DOM.emailText.value = "";
  window.UI.hideResults();
  window.Validation.updateButtonState(false);
};

window.downloadResults = () => {
  const results = {
    category: document.getElementById("categoryBadge")?.textContent,
    response: document.getElementById("responseText")?.textContent,
    confidence: document.getElementById("confidenceText")?.textContent,
    filename: document.getElementById("processedFileName")?.textContent,
    method: document.getElementById("methodBadge")?.textContent,
    model_info: document.getElementById("methodDescription")?.textContent,
    timestamp: new Date().toISOString(),
  };

  const blob = new Blob([JSON.stringify(results, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `resultados-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);

  window.UI.showToast("Resultados baixados com sucesso!", "success");
};
