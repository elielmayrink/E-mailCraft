// Aplicação principal
const App = {
  // Inicializar aplicação
  init() {
    console.log("🚀 Inicializando aplicação...");

    // Inicializar DOM
    window.DOM.init();

    // Inicializar event listeners
    this.initializeEventListeners();

    // Verificar status da API
    window.API.checkStatus();

    console.log("✅ Aplicação inicializada");
  },

  // Inicializar event listeners
  initializeEventListeners() {
    console.log("🔧 Inicializando event listeners...");

    const { emailFile, fileUploadArea, classifyBtn, emailText } = window.DOM;

    // File upload events
    emailFile.addEventListener("change", (e) =>
      window.FileHandler.handleFileSelect(e)
    );
    console.log("✅ Event listener para emailFile adicionado");

    // Select file button
    const selectFileBtn = document.getElementById("selectFileBtn");
    if (selectFileBtn) {
      selectFileBtn.addEventListener("click", () => {
        emailFile.click();
      });
      console.log("✅ Event listener para selectFileBtn adicionado");
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
    console.log("✅ Event listeners para drag and drop adicionados");

    // Form validation
    emailText.addEventListener("input", () => this.validateForm());
    emailFile.addEventListener("change", () => this.validateForm());
    console.log("✅ Event listeners para validação adicionados");

    // Classify button
    classifyBtn.addEventListener("click", () => this.classifyEmail());
    console.log("✅ Event listener para classifyBtn adicionado");

    // Enter key para classificar
    emailText.addEventListener("keydown", (e) => {
      if (e.ctrlKey && e.key === "Enter") {
        this.classifyEmail();
      }
    });
    console.log("✅ Event listener para keyboard shortcuts adicionado");

    console.log("✅ Todos os event listeners inicializados");

    // Gmail buttons
    if (window.DOM.gmailAuthBtn) {
      window.DOM.gmailAuthBtn.addEventListener("click", async () => {
        try {
          window.UI.showLoading("Conectando ao Gmail...");
          const data = await window.API.gmailPreview(5);
          window.UI.hideLoading();
          window.UI.renderGmailList(data);
          if (!data.auth_url && data.items?.length) {
            window.UI.showToast("Emails carregados do Gmail!", "success");
          }
        } catch (err) {
          window.UI.hideLoading();
          window.UI.showToast(
            "Erro ao conectar Gmail: " + err.message,
            "error"
          );
        }
      });
    }

    if (window.DOM.gmailRefreshBtn) {
      window.DOM.gmailRefreshBtn.addEventListener("click", async () => {
        try {
          window.UI.showLoading("Atualizando emails...");
          const data = await window.API.gmailPreview(5);
          window.UI.hideLoading();
          window.UI.renderGmailList(data);
        } catch (err) {
          window.UI.hideLoading();
          window.UI.showToast(
            "Erro ao atualizar Gmail: " + err.message,
            "error"
          );
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
    console.log("🔍 Iniciando classificação...");
    console.log("📁 Arquivo selecionado:", window.FileHandler.selectedFile);
    console.log("📝 Texto:", window.DOM.emailText.value.trim());

    // Validar formulário
    const isValid = window.Validation.validateForm(
      window.FileHandler.selectedFile,
      window.DOM.emailText
    );
    console.log("🔍 Validação retornou:", isValid);
    if (!isValid) {
      console.log("❌ Formulário inválido, mostrando toast");
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
        console.log(
          "📤 Fazendo upload do arquivo:",
          window.FileHandler.selectedFile.name
        );
        // Upload file
        response = await window.API.classifyFile(
          window.FileHandler.selectedFile
        );
      } else {
        console.log("📝 Classificando texto");
        // Classify text
        response = await window.API.classifyText(window.DOM.emailText.value);
      }

      console.log("✅ Resposta recebida:", response);
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
  console.log("🚀 DOM carregado, inicializando aplicação...");
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
