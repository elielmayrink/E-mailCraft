/**
 * Configuração do Firebase - Versão Simples
 */

// Configuração do Firebase
const firebaseConfig = {
  apiKey: "AIzaSyCyEBgDEoxpbUTU6HsC_0axMM4R8wsrL5w",
  authDomain: "email-agent-classifier.firebaseapp.com",
  projectId: "email-agent-classifier",
  storageBucket: "email-agent-classifier.firebasestorage.app",
  messagingSenderId: "899183076116",
  appId: "1:899183076116:web:431fe97c42339873215801",
};

// Carregar Firebase via CDN
const firebaseScript = document.createElement("script");
firebaseScript.src =
  "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
firebaseScript.onload = () => {
  const authScript = document.createElement("script");
  authScript.src = "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
  authScript.onload = () => {
    // Inicializar Firebase
    const app = firebase.initializeApp(firebaseConfig);
    const auth = firebase.auth();
    const googleProvider = new firebase.auth.GoogleAuthProvider();

    // Configurar scopes do Gmail
    googleProvider.addScope("https://www.googleapis.com/auth/gmail.readonly");
    googleProvider.addScope("https://www.googleapis.com/auth/gmail.send");
    googleProvider.addScope("https://www.googleapis.com/auth/gmail.modify");

    // Exportar para uso global
    window.firebaseAuth = {
      auth,
      googleProvider,
      signInWithPopup: firebase.auth.signInWithPopup,
      signOut: firebase.auth.signOut,
      onAuthStateChanged: firebase.auth.onAuthStateChanged,
    };

    console.log("✅ Firebase carregado via CDN");
  };
  document.head.appendChild(authScript);
};
document.head.appendChild(firebaseScript);
