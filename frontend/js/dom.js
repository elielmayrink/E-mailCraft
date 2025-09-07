// Elementos DOM
console.log("🏗️ Carregando dom.js...");
const DOM = {
  // Form elements
  emailText: null,
  emailFile: null,
  classifyBtn: null,

  // File upload elements
  fileUploadArea: null,
  fileInfo: null,

  // Results elements
  resultsSection: null,

  // UI elements
  loadingOverlay: null,
  toastContainer: null,
  gmailAuthBtn: null,
  gmailRefreshBtn: null,

  // Initialize DOM elements
  init() {
    this.emailText = document.getElementById("emailText");
    this.emailFile = document.getElementById("emailFile");
    this.classifyBtn = document.getElementById("classifyBtn");
    this.fileUploadArea = document.getElementById("fileUploadArea");
    this.fileInfo = document.getElementById("fileInfo");
    this.resultsSection = document.getElementById("resultsSection");
    this.loadingOverlay = document.getElementById("loadingOverlay");
    this.toastContainer = document.getElementById("toastContainer");
    this.gmailAuthBtn = document.getElementById("gmailAuthBtn");
    this.gmailRefreshBtn = document.getElementById("gmailRefreshBtn");

    console.log("🔍 Verificando elementos DOM:");
    console.log("📝 emailText:", this.emailText);
    console.log("📁 emailFile:", this.emailFile);
    console.log("🔘 classifyBtn:", this.classifyBtn);
    console.log("📤 fileUploadArea:", this.fileUploadArea);
    console.log("📋 fileInfo:", this.fileInfo);
    console.log("📊 resultsSection:", this.resultsSection);
    console.log("⏳ loadingOverlay:", this.loadingOverlay);
    console.log("🔔 toastContainer:", this.toastContainer);
    console.log("📧 gmailAuthBtn:", this.gmailAuthBtn);
    console.log("📧 gmailRefreshBtn:", this.gmailRefreshBtn);

    console.log("✅ Elementos DOM inicializados");
  },

  // Get file info elements
  getFileInfoElements() {
    return {
      fileName: document.querySelector(".file-name"),
      fileSize: document.querySelector(".file-size"),
    };
  },

  // Get results elements
  getResultsElements() {
    return {
      categoryBadge: document.getElementById("categoryBadge"),
      responseText: document.getElementById("responseText"),
      confidenceText: document.getElementById("confidenceText"),
      filenameText: document.getElementById("processedFileName"),
      methodBadge: document.getElementById("methodBadge"),
      methodDescription: document.getElementById("methodDescription"),
    };
  },
};

// Exportar DOM
window.DOM = DOM;
