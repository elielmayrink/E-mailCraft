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

  // Renderizar lista do Gmail
  renderGmailList(data) {
    const container = document.getElementById("gmailList");
    if (!container) return;
    if (data.auth_url) {
      container.innerHTML = `
        <div class="alert alert-warning">
          <p>Autenticação necessária. Clique para autorizar o acesso ao Gmail.</p>
          <a class="btn btn-primary" href="${data.auth_url}" target="_blank">
            <i class="fas fa-link"></i> Autorizar no Google
          </a>
        </div>
      `;
      return;
    }

    const items = data.items || [];
    if (items.length === 0) {
      container.innerHTML = `<p>Nenhum email não lido encontrado.</p>`;
      return;
    }

    container.innerHTML = items
      .map(
        (m, idx) => `
        <div class="gmail-item" data-index="${idx}" style="border:1px solid #eee; padding:12px; border-radius:8px; margin-bottom:12px; overflow:hidden; word-wrap:break-word; max-width:100%; box-sizing:border-box;">
          <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap;">
            <div>
              <strong>De:</strong> ${
                m.from || "(desconhecido)"
              } &nbsp;|&nbsp; <strong>Assunto:</strong> ${
          m.subject || "(sem assunto)"
        }
            </div>
            <span class="category-badge category-${(
              m.category || ""
            ).toLowerCase()}">${m.category}</span>
          </div>
          <div style="background:#fafafa; padding:8px; border-radius:6px; margin-top:8px; border:1px solid #e0e0e0; overflow:hidden; word-wrap:break-word; overflow-wrap:break-word; word-break:break-all; white-space:pre-wrap; font-family:monospace; font-size:13px; line-height:1.4; max-width:100%; box-sizing:border-box;">${
            m.snippet || ""
          }</div>
          <div style="margin-top:8px;">
            <strong>Sugestão de resposta:</strong>
            <div class="response-box" style="margin-top:4px;">
              <textarea class="gmail-reply" rows="3" style="width:100%">${
                m.suggested_response || ""
              }</textarea>
            </div>
          </div>
          <div style="margin-top:8px; display:flex; gap:8px; flex-wrap:wrap;">
             <button class="btn btn-primary gmail-send" data-to="${
               (m.from || "").split("<")[1]?.replace(">", "") || ""
             }" data-subject="${m.subject || ""}" data-thread="${
          m.threadId || ""
        }" data-message-id="${
          m.id || ""
        }" style="display:flex; align-items:center; justify-content:center; gap:6px;">
                Enviar
             </button>
             <button class="btn btn-secondary gmail-skip" data-message-id="${
               m.id || ""
             }" style="display:flex; align-items:center; justify-content:center; gap:6px;">
               Marcar como lido
             </button>
          </div>
        </div>
      `
      )
      .join("");

    // Bind eventos dos botões
    container.querySelectorAll(".gmail-send").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        const item = e.target.closest(".gmail-item");
        const reply = item.querySelector(".gmail-reply").value;
        const to = btn.getAttribute("data-to");
        const subject = btn.getAttribute("data-subject");
        const threadId = btn.getAttribute("data-thread") || undefined;
        const messageId = btn.getAttribute("data-message-id");
        try {
          UI.showLoading("Enviando resposta...");
          const res = await window.API.gmailSend({
            to,
            subject,
            body: reply,
            threadId,
          });
          // Marcar como lido após enviar
          if (messageId) {
            await window.API.gmailMarkRead(messageId);
          }
          UI.hideLoading();
          UI.showToast("Resposta enviada e marcada como lida!", "success");
          item.remove();
        } catch (err) {
          UI.hideLoading();
          UI.showToast("Falha ao enviar: " + err.message, "error");
        }
      });
    });

    container.querySelectorAll(".gmail-skip").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const item = btn.closest(".gmail-item");
        const messageId = btn.getAttribute("data-message-id");
        try {
          // Marcar como lido ao pular
          if (messageId) {
            UI.showLoading("Marcando como lido...");
            await window.API.gmailMarkRead(messageId);
            UI.hideLoading();
            UI.showToast("Email marcado como lido", "success");
          }
          item.remove();
        } catch (err) {
          UI.hideLoading();
          UI.showToast("Falha ao marcar como lido: " + err.message, "error");
          item.remove(); // Remove mesmo se falhar
        }
      });
    });
  },
};

// Exportar UI
window.UI = UI;
