/**
 * Componentes de Autenticação
 */

class AuthComponents {
  constructor() {
    this.authService = null;
    this.init();
  }

  async init() {
    // Aguardar o AuthService estar disponível
    await this.waitForAuthService();

    // Escutar mudanças no estado de autenticação
    this.authService.onAuthStateChanged((user) => {
      this.updateUI(user);
    });

    // Verificar estado inicial
    this.updateUI(this.authService.currentUser);
  }

  async waitForAuthService() {
    return new Promise((resolve) => {
      const checkAuthService = () => {
        if (window.authService) {
          this.authService = window.authService;
          resolve();
        } else {
          setTimeout(checkAuthService, 100);
        }
      };
      checkAuthService();
    });
  }

  async updateUI(user) {
    const loginSection = document.getElementById("loginSection");
    const userSection = document.getElementById("userSection");
    const gmailSection = document.getElementById("gmailSection");
    const mainContent = document.getElementById("mainContent");

    if (user) {
      // Usuário logado
      this.showUserSection(user);
      this.hideLoginSection();

      // Verificar status do Gmail
      try {
        const gmailStatus = await this.authService.getGmailStatus();
        this.updateGmailSection(gmailStatus);
      } catch (error) {
        console.error("Erro ao verificar status do Gmail:", error);
        this.showGmailNotConnected();
      }
    } else {
      // Usuário não logado
      this.showLoginSection();
      this.hideUserSection();
      this.hideGmailSection();
    }
  }

  showLoginSection() {
    const loginSection = document.getElementById("loginSection");
    if (loginSection) {
      loginSection.style.display = "block";
    }
  }

  hideLoginSection() {
    const loginSection = document.getElementById("loginSection");
    if (loginSection) {
      loginSection.style.display = "none";
    }
  }

  showUserSection(user) {
    const userSection = document.getElementById("userSection");
    if (userSection) {
      userSection.style.display = "block";

      // Atualizar informações do usuário
      const userPhoto = userSection.querySelector("#userPhoto");
      const userName = userSection.querySelector("#userName");
      const userEmail = userSection.querySelector("#userEmail");

      if (userPhoto) {
        userPhoto.src = user.photoURL || "/default-avatar.png";
        userPhoto.alt = user.displayName || "Usuário";
      }

      if (userName) {
        userName.textContent = user.displayName || "Usuário";
      }

      if (userEmail) {
        userEmail.textContent = user.email;
      }
    }
  }

  hideUserSection() {
    const userSection = document.getElementById("userSection");
    if (userSection) {
      userSection.style.display = "none";
    }
  }

  updateGmailSection(gmailStatus) {
    const gmailSection = document.getElementById("gmailSection");
    if (!gmailSection) return;

    gmailSection.style.display = "block";

    const connectButton = gmailSection.querySelector("#connectGmailBtn");
    const disconnectButton = gmailSection.querySelector("#disconnectGmailBtn");
    const statusText = gmailSection.querySelector("#gmailStatus");

    if (gmailStatus.connected) {
      // Gmail conectado
      if (connectButton) connectButton.style.display = "none";
      if (disconnectButton) disconnectButton.style.display = "inline-block";
      if (statusText) {
        statusText.textContent = "Gmail conectado";
        statusText.className = "status-connected";
      }
    } else {
      // Gmail não conectado
      if (connectButton) connectButton.style.display = "inline-block";
      if (disconnectButton) disconnectButton.style.display = "none";
      if (statusText) {
        statusText.textContent = "Gmail não conectado";
        statusText.className = "status-disconnected";
      }
    }
  }

  showGmailNotConnected() {
    const gmailSection = document.getElementById("gmailSection");
    if (gmailSection) {
      gmailSection.style.display = "block";

      const connectButton = gmailSection.querySelector("#connectGmailBtn");
      const disconnectButton = gmailSection.querySelector(
        "#disconnectGmailBtn"
      );
      const statusText = gmailSection.querySelector("#gmailStatus");

      if (connectButton) connectButton.style.display = "inline-block";
      if (disconnectButton) disconnectButton.style.display = "none";
      if (statusText) {
        statusText.textContent = "Gmail não conectado";
        statusText.className = "status-disconnected";
      }
    }
  }

  hideGmailSection() {
    const gmailSection = document.getElementById("gmailSection");
    if (gmailSection) {
      gmailSection.style.display = "none";
    }
  }

  async handleLogin() {
    try {
      this.showLoading("Fazendo login...");
      const result = await this.authService.loginWithGoogle();
      this.hideLoading();
      this.showSuccess("Login realizado com sucesso!");
    } catch (error) {
      this.hideLoading();
      this.showError(`Erro no login: ${error.message}`);
    }
  }

  async handleLogout() {
    try {
      this.showLoading("Fazendo logout...");
      await this.authService.logout();
      this.hideLoading();
      this.showSuccess("Logout realizado com sucesso!");
    } catch (error) {
      this.hideLoading();
      this.showError(`Erro no logout: ${error.message}`);
    }
  }

  async handleConnectGmail() {
    try {
      this.showLoading("Conectando Gmail...");

      // Aqui você pode implementar o fluxo de OAuth do Gmail
      // Por enquanto, vamos simular uma conexão
      const mockCredentials = {
        access_token: "mock_access_token",
        refresh_token: "mock_refresh_token",
        expires_in: 3600,
      };

      await this.authService.connectGmail(mockCredentials);
      this.hideLoading();
      this.showSuccess("Gmail conectado com sucesso!");

      // Atualizar seção do Gmail
      const gmailStatus = await this.authService.getGmailStatus();
      this.updateGmailSection(gmailStatus);
    } catch (error) {
      this.hideLoading();
      this.showError(`Erro ao conectar Gmail: ${error.message}`);
    }
  }

  async handleDisconnectGmail() {
    try {
      this.showLoading("Desconectando Gmail...");
      await this.authService.disconnectGmail();
      this.hideLoading();
      this.showSuccess("Gmail desconectado com sucesso!");

      // Atualizar seção do Gmail
      const gmailStatus = await this.authService.getGmailStatus();
      this.updateGmailSection(gmailStatus);
    } catch (error) {
      this.hideLoading();
      this.showError(`Erro ao desconectar Gmail: ${error.message}`);
    }
  }

  showLoading(message) {
    // Criar ou atualizar elemento de loading
    let loadingElement = document.getElementById("loadingMessage");
    if (!loadingElement) {
      loadingElement = document.createElement("div");
      loadingElement.id = "loadingMessage";
      loadingElement.className = "loading-message";
      document.body.appendChild(loadingElement);
    }

    loadingElement.innerHTML = `
      <div class="loading-content">
        <div class="spinner"></div>
        <p>${message}</p>
      </div>
    `;
    loadingElement.style.display = "flex";
  }

  hideLoading() {
    const loadingElement = document.getElementById("loadingMessage");
    if (loadingElement) {
      loadingElement.style.display = "none";
    }
  }

  showSuccess(message) {
    this.showNotification(message, "success");
  }

  showError(message) {
    this.showNotification(message, "error");
  }

  showNotification(message, type) {
    const notification = document.createElement("div");
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <i class="fas fa-${
          type === "success" ? "check-circle" : "exclamation-circle"
        }"></i>
        <span>${message}</span>
        <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;

    document.body.appendChild(notification);

    // Auto-remover após 5 segundos
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 5000);
  }
}

// Criar instância global
window.authComponents = new AuthComponents();
