/**
 * Configuração do Firebase
 * Substitua os valores pelas suas credenciais do Firebase
 */

// Configuração do Firebase (substitua pelos seus valores)
const firebaseConfig = {
  apiKey: "AIzaSyCyEBgDEoxpbUTU6HsC_0axMM4R8wsrL5w",
  authDomain: "email-agent-classifier.firebaseapp.com",
  projectId: "email-agent-classifier",
  storageBucket: "email-agent-classifier.firebasestorage.app",
  messagingSenderId: "899183076116",
  appId: "1:899183076116:web:431fe97c42339873215801",
};

// Carregar Firebase via CDN (versão compatível)
const firebaseScript = document.createElement("script");
firebaseScript.src =
  "https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js";
firebaseScript.onload = () => {
  const authScript = document.createElement("script");
  authScript.src =
    "https://www.gstatic.com/firebasejs/9.23.0/firebase-auth-compat.js";
  authScript.onload = () => {
    // Inicializar Firebase usando a versão compatível
    const app = firebase.initializeApp(firebaseConfig);
    const auth = firebase.auth();
    const googleProvider = new firebase.auth.GoogleAuthProvider();

    // Configurar scopes do Gmail
    googleProvider.addScope("https://www.googleapis.com/auth/gmail.readonly");
    googleProvider.addScope("https://www.googleapis.com/auth/gmail.send");
    googleProvider.addScope("https://www.googleapis.com/auth/gmail.modify");

    // Exportar para uso em outros arquivos
    window.firebaseAuth = {
      auth,
      googleProvider,
      signInWithPopup: (auth, provider) =>
        firebase.auth().signInWithPopup(provider),
      signOut: (auth) => firebase.auth().signOut(),
      onAuthStateChanged: (auth, callback) =>
        firebase.auth().onAuthStateChanged(callback),
    };
  };
  document.head.appendChild(authScript);
};
document.head.appendChild(firebaseScript);
