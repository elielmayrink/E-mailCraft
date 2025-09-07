// Interface do usuário
console.log("🎨 Carregando ui.js...");
const UI = {
  // Mostrar loading
  showLoading(message = "Carregando...") {
    const { loadingOverlay } = window.DOM;

    if (!loadingOverlay) {
      console.error("❌ loadingOverlay não encontrado!");
      return;
    }

    const loadingText = loadingOverlay.querySelector(".loading-text");
    if (loadingText) {
      loadingText.textContent = message;
    }
    loadingOverlay.style.display = "flex";
  },

  // Esconder loading
  hideLoading() {
    const { loadingOverlay } = window.DOM;

    if (!loadingOverlay) {
      console.error("❌ loadingOverlay não encontrado!");
      return;
    }

    loadingOverlay.style.display = "none";
  },

  // Mostrar toast
  showToast(message, type = "info") {
    const { toastContainer } = window.DOM;
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <div class="toast-content">
        <i class="fas ${this.getToastIcon(type)}"></i>
        <span>${message}</span>
      </div>
      <button class="toast-close" onclick="this.parentElement.remove()">
        <i class="fas fa-times"></i>
      </button>
    `;

    toastContainer.appendChild(toast);

    // Auto remove after duration
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, window.CONFIG.TOAST_DURATION);
  },

  // Obter ícone do toast
  getToastIcon(type) {
    const icons = {
      success: "fa-check-circle",
      error: "fa-exclamation-circle",
      warning: "fa-exclamation-triangle",
      info: "fa-info-circle",
    };
    return icons[type] || icons.info;
  },

  getMethodDisplayName(method) {
    const methodNames = {
      distilbert: "IA Avançada",
      keywords_fallback: "Palavras-chave",
      empty_text: "Texto Vazio",
      error_fallback: "Erro",
    };
    return methodNames[method] || method;
  },

  // Exibir resultados
  displayResults(data) {
    const {
      categoryBadge,
      responseText,
      confidenceText,
      filenameText,
      methodBadge,
      methodDescription,
    } = window.DOM.getResultsElements();

    console.log("🎨 Exibindo resultados:", data);
    console.log("🎨 Elementos encontrados:", {
      categoryBadge,
      responseText,
      confidenceText,
      filenameText,
      methodBadge,
      methodDescription,
    });

    // Update category
    if (categoryBadge) {
      categoryBadge.textContent = data.category;
      categoryBadge.className = `category-badge category-${data.category.toLowerCase()}`;
    }

    // Update response
    if (responseText) {
      responseText.textContent = data.response;
    }

    // Update confidence
    if (confidenceText) {
      const confidence = Math.round((data.confidence || 0.8) * 100);
      confidenceText.textContent = `${confidence}%`;
    }

    // Update filename if available
    if (data.filename && filenameText) {
      filenameText.textContent = data.filename;
      filenameText.style.display = "block";
    } else if (filenameText) {
      filenameText.style.display = "none";
    }

    // Update method info
    if (methodBadge && data.method) {
      methodBadge.textContent = this.getMethodDisplayName(data.method);
      methodBadge.className = `method-badge ${data.method}`;
    }

    if (methodDescription && data.model_info) {
      methodDescription.textContent = data.model_info;
    }

    // Show results
    if (window.DOM.resultsSection) {
      window.DOM.resultsSection.style.display = "block";
      window.DOM.resultsSection.scrollIntoView({ behavior: "smooth" });
    }
  },

  // Esconder resultados
  hideResults() {
    window.DOM.resultsSection.style.display = "none";
  },
};

// Exportar UI
window.UI = UI;
