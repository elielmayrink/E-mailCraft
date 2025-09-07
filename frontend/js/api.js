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
      console.log("🔍 Testando conectividade com API...");
      console.log("🌐 URL:", `${window.CONFIG.API_BASE_URL}/health`);
      console.log("🔑 API_BASE_URL:", window.CONFIG.API_BASE_URL);

      const response = await fetch(`${window.CONFIG.API_BASE_URL}/health`);
      console.log(
        "📡 Resposta do health:",
        response.status,
        response.statusText
      );

      if (response.ok) {
        const data = await response.json();
        console.log("✅ Dados do health:", data);
        window.UI.showToast("✅ API conectada com sucesso!", "success");
        return true;
      } else {
        console.error("❌ Health check falhou:", response.status);
        window.UI.showToast("❌ API não está respondendo", "error");
        return false;
      }
    } catch (error) {
      console.error("❌ Erro no health check:", error);
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
      console.error("Erro no preview do Gmail:", error);
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
      console.error("Erro ao enviar email:", error);
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
      console.error("Erro ao marcar como lido:", error);
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
    console.log("📤 Iniciando upload do arquivo...");
    console.log("📁 Arquivo:", file);
    console.log("🌐 URL:", `${window.CONFIG.API_BASE_URL}/classify-file`);
    console.log("🔑 API_BASE_URL:", window.CONFIG.API_BASE_URL);

    if (!file) {
      console.error("❌ Nenhum arquivo selecionado!");
      throw new Error("Nenhum arquivo selecionado");
    }

    const formData = new FormData();
    formData.append("file", file);

    console.log("📋 FormData criado, enviando requisição...");
    console.log("📋 FormData entries:", Array.from(formData.entries()));

    try {
      const response = await fetch(
        `${window.CONFIG.API_BASE_URL}/classify-file`,
        {
          method: "POST",
          body: formData,
        }
      );

      console.log(
        "📡 Resposta recebida:",
        response.status,
        response.statusText
      );
      console.log("📡 Response headers:", response.headers);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("❌ Erro na resposta:", errorText);
        throw new Error(
          `HTTP error! status: ${response.status} - ${errorText}`
        );
      }

      const result = await response.json();
      console.log("✅ Resultado processado:", result);
      return result;
    } catch (error) {
      console.error("❌ Erro na requisição:", error);
      throw error;
    }
  },

  // Função de teste para debugging
  async testAPI() {
    console.log("🧪 Testando API...");
    console.log("🌐 URL:", `${window.CONFIG.API_BASE_URL}/health`);
    console.log("🔑 API_BASE_URL:", window.CONFIG.API_BASE_URL);
    try {
      const response = await fetch(`${window.CONFIG.API_BASE_URL}/health`);
      console.log("📡 Resposta:", response.status, response.statusText);
      const data = await response.json();
      console.log("📋 Dados:", data);
      alert(`API Status: ${response.status} - ${JSON.stringify(data)}`);
    } catch (error) {
      console.error("❌ Erro:", error);
      alert(`Erro: ${error.message}`);
    }
  },
};

// Exportar API
window.API = API;
