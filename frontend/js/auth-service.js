/**
 * Serviço de Autenticação Firebase
 */

class AuthService {
  constructor() {
    this.currentUser = null;
    this.authStateListeners = [];
    this.init();
  }

  async init() {
    // Aguardar o Firebase estar carregado
    if (typeof window.firebaseAuth === "undefined") {
      await this.waitForFirebase();
    }

    // Escutar mudanças no estado de autenticação
    window.firebaseAuth.onAuthStateChanged(window.firebaseAuth.auth, (user) => {
      this.currentUser = user;
      this.notifyAuthStateListeners(user);
    });

    console.log("✅ AuthService inicializado");
  }

  async waitForFirebase() {
    return new Promise((resolve) => {
      const checkFirebase = () => {
        if (typeof window.firebaseAuth !== "undefined") {
          resolve();
        } else {
          setTimeout(checkFirebase, 100);
        }
      };
      checkFirebase();
    });
  }

  async loginWithGoogle() {
    try {
      const result = await window.firebaseAuth.signInWithPopup(
        window.firebaseAuth.auth,
        window.firebaseAuth.googleProvider
      );

      const user = result.user;
      const token = await user.getIdToken();

      // Enviar token para o backend para verificar/criar usuário
      const response = await fetch(
        `${window.CONFIG.API_BASE_URL}/auth/verify-token`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Falha na verificação do token");
      }

      const userData = await response.json();

      return {
        user: {
          uid: user.uid,
          email: user.email,
          name: user.displayName,
          photo: user.photoURL,
        },
        token: token,
        backendData: userData,
      };
    } catch (error) {
      console.error("Erro no login:", error);
      throw new Error(`Login falhou: ${error.message}`);
    }
  }

  async logout() {
    try {
      await window.firebaseAuth.signOut(window.firebaseAuth.auth);
      this.currentUser = null;
      this.notifyAuthStateListeners(null);
    } catch (error) {
      console.error("Erro no logout:", error);
      throw new Error(`Logout falhou: ${error.message}`);
    }
  }

  async getCurrentUser() {
    if (this.currentUser) {
      const token = await this.currentUser.getIdToken();
      console.log("🔑 Token obtido:", token.substring(0, 20) + "...");
      console.log("👤 Usuário Firebase:", this.currentUser.email);
      return {
        user: {
          uid: this.currentUser.uid,
          email: this.currentUser.email,
          name: this.currentUser.displayName,
          photo: this.currentUser.photoURL,
        },
        token: token,
      };
    }
    console.log("❌ Nenhum usuário atual");
    return null;
  }

  async getCurrentUserInfo() {
    try {
      const userData = await this.getCurrentUser();
      if (!userData) {
        throw new Error("Usuário não autenticado");
      }

      const response = await fetch(`${window.CONFIG.API_BASE_URL}/auth/me`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${userData.token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Falha ao obter informações do usuário");
      }

      return await response.json();
    } catch (error) {
      console.error("Erro ao obter informações do usuário:", error);
      throw error;
    }
  }

  async connectGmail() {
    try {
      const userData = await this.getCurrentUser();
      if (!userData) {
        throw new Error("Usuário não autenticado");
      }

      console.log(
        "🔑 Token para Gmail connect:",
        userData.token.substring(0, 20) + "..."
      );
      console.log("👤 Usuário atual:", userData.user.email);

      // Obter a URL de autorização do backend
      const response = await fetch(
        `${window.CONFIG.API_BASE_URL}/gmail/auth-url`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${userData.token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Falha ao obter URL de autorização do Gmail");
      }

      const data = await response.json();
      const authUrl = data.auth_url;

      console.log("🔗 URL de autorização:", authUrl);

      // Redirecionar o usuário para a URL de autorização do Google
      window.location.href = authUrl;

      return { message: "Redirecionando para autorização do Gmail..." };
    } catch (error) {
      console.error("Erro ao conectar Gmail:", error);
      throw error;
    }
  }

  async disconnectGmail() {
    try {
      const userData = await this.getCurrentUser();
      if (!userData) {
        throw new Error("Usuário não autenticado");
      }

      const response = await fetch(
        `${window.CONFIG.API_BASE_URL}/gmail/disconnect`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${userData.token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Falha ao desconectar Gmail");
      }

      return await response.json();
    } catch (error) {
      console.error("Erro ao desconectar Gmail:", error);
      throw error;
    }
  }

  async getGmailStatus() {
    try {
      const userData = await this.getCurrentUser();
      if (!userData) {
        throw new Error("Usuário não autenticado");
      }

      const response = await fetch(
        `${window.CONFIG.API_BASE_URL}/gmail/status`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${userData.token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Falha ao obter status do Gmail");
      }

      return await response.json();
    } catch (error) {
      console.error("Erro ao obter status do Gmail:", error);
      throw error;
    }
  }

  // Sistema de listeners para mudanças de estado
  onAuthStateChanged(callback) {
    this.authStateListeners.push(callback);
  }

  async getGmailCredentials() {
    try {
      if (!this.currentUser) {
        throw new Error("Usuário não autenticado");
      }

      // Obter credenciais do Gmail via Firebase
      // O Firebase já tem acesso ao Gmail quando o usuário faz login com Google
      const gmailToken = await this.currentUser.getIdToken();

      // Para o MVP, vamos simular credenciais do Gmail
      // Em produção, você precisaria implementar OAuth2 flow específico para Gmail
      return {
        token: gmailToken,
        refresh_token: gmailToken,
        token_uri: "https://oauth2.googleapis.com/token",
        client_id:
          "1070298098644-kb8ahnuifnsoj1i192i8dfd3aamkjdv3.apps.googleusercontent.com",
        client_secret: "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",
        scopes: [
          "https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.modify",
        ],
        expiry: new Date(Date.now() + 3600000).toISOString(), // 1 hora
        type: "authorized_user",
      };
    } catch (error) {
      console.error("Erro ao obter credenciais do Gmail:", error);
      throw new Error("Falha ao obter credenciais do Gmail");
    }
  }

  notifyAuthStateListeners(user) {
    this.authStateListeners.forEach((callback) => {
      try {
        callback(user);
      } catch (error) {
        console.error("Erro no listener de autenticação:", error);
      }
    });
  }

  isAuthenticated() {
    return this.currentUser !== null;
  }
}

// Criar instância global
window.authService = new AuthService();
