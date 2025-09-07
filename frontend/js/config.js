// Configuração da API
console.log("📋 Carregando config.js...");
const API_BASE_URL = "http://localhost:8002";

// Configurações de arquivo
const VALID_FILE_TYPES = ["text/plain", "application/pdf"];
const VALID_FILE_EXTENSIONS = [".txt", ".pdf"];

// Configurações de UI
const TOAST_DURATION = 5000;
const LOADING_DELAY = 300;

// Exportar configurações
window.CONFIG = {
  API_BASE_URL,
  VALID_FILE_TYPES,
  VALID_FILE_EXTENSIONS,
  TOAST_DURATION,
  LOADING_DELAY,
};
