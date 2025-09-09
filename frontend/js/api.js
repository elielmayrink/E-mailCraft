// Chamadas da API
const API = {
  // Obter headers de autenticação
  async getAuthHeaders() {
    try {
      if (window.authService && window.authService.isAuthenticated()) {
        const userData = await window.authService.getCurrentUser();
        return {
          Authorization: `Bearer ${userData.token}`,
          "Content-Type": "application/json",
        };
      }
      return {
        "Content-Type": "application/json",
      };
    } catch (error) {
      console.error("Erro ao obter headers de autenticação:", error);
      return {
        "Content-Type": "application/json",
      };
    }
  },

  // Verificar status da API
  async checkStatus() {
    try {
      const response = await fetch(`${window.CONFIG.API_BASE_URL}/health`);

      if (response.ok) {
        const data = await response.json();

        window.UI.showToast("✅ API conectada com sucesso!", "success");
        return true;
      } else {
        window.UI.showToast("❌ API não está respondendo", "error");
        return false;
      }
    } catch (error) {
      window.UI.showToast(
        "❌ Erro ao conectar com a API: " + error.message,
        "error"
      );
      return false;
    }
  },

  // Gmail: preview não lidos
  async gmailPreview(limit = 5) {
    try {
      const headers = await this.getAuthHeaders();
      const url = `${window.CONFIG.API_BASE_URL}/gmail/preview?limit=${limit}`;
      const response = await fetch(url, { headers });

      if (response.status === 401) {
        throw new Error("Usuário não autenticado");
      }

      const data = await response.json();
      if (data.auth_url) {
        return { auth_url: data.auth_url };
      }
      return data;
    } catch (error) {
      throw error;
    }
  },

  // Gmail: enviar resposta
  async gmailSend({ to, subject, body, threadId }) {
    try {
      const headers = await this.getAuthHeaders();
      const response = await fetch(`${window.CONFIG.API_BASE_URL}/gmail/send`, {
        method: "POST",
        headers,
        body: JSON.stringify({ to, subject, body, threadId }),
      });

      if (response.status === 401) {
        throw new Error("Usuário não autenticado");
      }

      if (!response.ok) {
        const err = await response.text();
        throw new Error(err);
      }
      return await response.json();
    } catch (error) {
      throw error;
    }
  },

  // Gmail: marcar como lido
  async gmailMarkRead(messageId) {
    try {
      const headers = await this.getAuthHeaders();
      const response = await fetch(
        `${window.CONFIG.API_BASE_URL}/gmail/mark-read`,
        {
          method: "POST",
          headers,
          body: JSON.stringify({ messageId }),
        }
      );

      if (response.status === 401) {
        throw new Error("Usuário não autenticado");
      }

      if (!response.ok) {
        const err = await response.text();
        throw new Error(err);
      }
      return await response.json();
    } catch (error) {
      throw error;
    }
  },

  // Testar IA
  async testAI() {
    try {
      window.UI.showLoading("Testando conexão com IA...");

      const response = await fetch(`${window.CONFIG.API_BASE_URL}/test-ai`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      window.UI.hideLoading();
      window.UI.showToast("✅ IA funcionando corretamente!", "success");
      return data;
    } catch (error) {
      window.UI.hideLoading();
      window.UI.showToast("Erro ao testar IA: " + error.message, "error");
      throw error;
    }
  },

  // Classificar texto
  async classifyText(text) {
    const response = await fetch(
      `${window.CONFIG.API_BASE_URL}/classify-text`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: text.trim(),
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  },

  // Classificar arquivo
  async classifyFile(file) {
    if (!file) {
      throw new Error("Nenhum arquivo selecionado");
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        `${window.CONFIG.API_BASE_URL}/classify-file`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorText = await response.text();

        throw new Error(
          `HTTP error! status: ${response.status} - ${errorText}`
        );
      }

      const result = await response.json();

      return result;
    } catch (error) {
      throw error;
    }
  },

  // Função de teste para debugging
  async testAPI() {
    try {
      const response = await fetch(`${window.CONFIG.API_BASE_URL}/health`);
      const data = await response.json();
      alert(`API Status: ${response.status} - ${JSON.stringify(data)}`);
    } catch (error) {
      alert(`Erro: ${error.message}`);
    }
  },
};

// Exportar API
window.API = API;
