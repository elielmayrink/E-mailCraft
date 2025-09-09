// Configuração da API
const API_BASE_URL = window.location.hostname.includes("localhost")
  ? "http://localhost:8002"
  : "/api";

// Elementos DOM
const emailText = document.getElementById("emailText");
const emailFile = document.getElementById("emailFile");
const fileUploadArea = document.getElementById("fileUploadArea");
const fileInfo = document.getElementById("fileInfo");
const classifyBtn = document.getElementById("classifyBtn");
const resultsSection = document.getElementById("resultsSection");
const loadingOverlay = document.getElementById("loadingOverlay");
const toastContainer = document.getElementById("toastContainer");

// Estado da aplicação
let selectedFile = null;

// Inicialização
document.addEventListener("DOMContentLoaded", function () {
  initializeEventListeners();
  checkAPIStatus();
});

// Event Listeners
function initializeEventListeners() {
  // File upload events
  emailFile.addEventListener("change", handleFileSelect);

  // Drag and drop events
  fileUploadArea.addEventListener("dragover", handleDragOver);
  fileUploadArea.addEventListener("dragleave", handleDragLeave);
  fileUploadArea.addEventListener("drop", handleDrop);

  // Form validation
  emailText.addEventListener("input", validateForm);
  emailFile.addEventListener("change", validateForm);

  // Enter key para classificar
  emailText.addEventListener("keydown", function (e) {
    if (e.ctrlKey && e.key === "Enter") {
      classifyEmail();
    }
  });
}

// File Upload Functions
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) {
    console.log("📁 Chamando processSelectedFile...");
    processSelectedFile(file);
  } else {
    console.log("❌ Nenhum arquivo selecionado");
  }
}

function handleDragOver(event) {
  event.preventDefault();
  fileUploadArea.classList.add("dragover");
}

function handleDragLeave(event) {
  event.preventDefault();
  fileUploadArea.classList.remove("dragover");
}

function handleDrop(event) {
  event.preventDefault();
  fileUploadArea.classList.remove("dragover");

  const files = event.dataTransfer.files;
  if (files.length > 0) {
    const file = files[0];
    if (isValidFileType(file)) {
      processSelectedFile(file);
    } else {
      showToast(
        "Tipo de arquivo não suportado. Use apenas .txt ou .pdf",
        "error"
      );
    }
  } else {
    console.log("❌ Nenhum arquivo no drop");
  }
}

function processSelectedFile(file) {
  selectedFile = file;
  selectedFile = file;

  // Update file info display
  const fileName = document.querySelector(".file-name");
  const fileSize = document.querySelector(".file-size");

  fileName.textContent = file.name;
  fileSize.textContent = formatFileSize(file.size);

  // Show file info, hide upload area
  fileUploadArea.style.display = "none";
  fileInfo.style.display = "flex";

  // Clear text input
  emailText.value = "";

  // Validar formulário após processar arquivo
  const isValid = validateForm();
}

function removeFile() {
  selectedFile = null;
  emailFile.value = "";

  // Show upload area, hide file info
  fileUploadArea.style.display = "block";
  fileInfo.style.display = "none";

  validateForm();
}

function isValidFileType(file) {
  const validTypes = ["text/plain", "application/pdf"];
  const validExtensions = [".txt", ".pdf"];

  const isValidType = validTypes.includes(file.type);
  const isValidExtension = validExtensions.some((ext) =>
    file.name.toLowerCase().endsWith(ext)
  );
  const isValid = isValidType || isValidExtension;

  return isValid;
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

// Form Validation
function validateForm() {
  const hasText = emailText.value.trim().length > 0;
  const hasFile = selectedFile !== null;

  const isValid = hasText || hasFile;
  classifyBtn.disabled = !isValid;

  if (hasText && hasFile) {
    showToast(
      "Você pode usar texto ou arquivo, mas não ambos ao mesmo tempo",
      "warning"
    );
    return false;
  }

  return isValid;
}

// API Functions
async function checkAPIStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (response.ok) {
      const data = await response.json();
      showToast("✅ API conectada com sucesso!", "success");
      return true;
    } else {
      console.error("❌ Health check falhou:", response.status);
      showToast("❌ API não está respondendo", "error");
      return false;
    }
  } catch (error) {
    console.error("❌ Erro no health check:", error);
    showToast("❌ Erro ao conectar com a API: " + error.message, "error");
    return false;
  }
}

async function testAI() {
  try {
    showLoading("Testando conexão com IA...");

    const response = await fetch(`${API_BASE_URL}/test-ai`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: 'Diga apenas "IA funcionando!" em português',
      }),
    });

    const data = await response.json();
    hideLoading();

    if (data.status === "success") {
      showToast(`IA funcionando! Resposta: ${data.answer}`, "success");
    } else {
      showToast(`Erro na IA: ${data.error}`, "error");
    }
  } catch (error) {
    hideLoading();
    showToast("Erro ao testar IA: " + error.message, "error");
  }
}

async function classifyEmail() {
  // Validar formulário
  const isValid = validateForm();
  if (!isValid) {
    showToast("Por favor, insira um texto ou selecione um arquivo", "warning");
    return;
  }

  try {
    showLoading("Classificando email...");

    let response;

    if (selectedFile) {
      // Upload file
      response = await classifyFile();
    } else {
      console.log("📝 Classificando texto");
      // Classify text
      response = await classifyText();
    }

    hideLoading();
    displayResults(response);
  } catch (error) {
    console.error("❌ Erro na classificação:", error);
    hideLoading();
    showToast("Erro ao classificar email: " + error.message, "error");
  }
}

async function classifyText() {
  const response = await fetch(`${API_BASE_URL}/classify-text`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text: emailText.value.trim(),
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

async function classifyFile() {
  if (!selectedFile) {
    console.error("❌ Nenhum arquivo selecionado!");
    throw new Error("Nenhum arquivo selecionado");
  }

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const response = await fetch(`${API_BASE_URL}/classify-file`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("❌ Erro na resposta:", errorText);
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error("❌ Erro na requisição:", error);
    throw error;
  }
}

// Results Display
function displayResults(data) {
  // Update category
  const categoryBadge = document.getElementById("categoryBadge");
  categoryBadge.textContent = data.category;
  categoryBadge.className = `category-badge ${data.category.toLowerCase()}`;

  // Update confidence
  const confidence = data.confidence || 0.8;
  const confidenceFill = document.getElementById("confidenceFill");
  const confidenceText = document.getElementById("confidenceText");

  confidenceFill.style.width = `${confidence * 100}%`;
  confidenceText.textContent = `${Math.round(confidence * 100)}%`;

  // Update response
  const responseText = document.getElementById("responseText");
  responseText.textContent = data.response;

  // Update file info if applicable
  const fileResultItem = document.getElementById("fileResultItem");
  const processedFileName = document.getElementById("processedFileName");

  if (data.filename) {
    processedFileName.textContent = data.filename;
    fileResultItem.style.display = "flex";
  } else {
    fileResultItem.style.display = "none";
  }

  // Show results
  resultsSection.style.display = "block";
  resultsSection.scrollIntoView({ behavior: "smooth" });

  showToast("Email classificado com sucesso!", "success");
}

// Utility Functions
function showLoading(message = "Processando...") {
  const loadingContent = loadingOverlay.querySelector(".loading-content");
  const loadingTitle = loadingContent.querySelector("h3");
  const loadingText = loadingContent.querySelector("p");

  loadingTitle.textContent = message;
  loadingText.textContent =
    "Nossa IA está analisando o conteúdo e gerando uma resposta personalizada";

  loadingOverlay.style.display = "flex";
  classifyBtn.disabled = true;
}

function hideLoading() {
  loadingOverlay.style.display = "none";
  classifyBtn.disabled = false;
}

function resetForm() {
  // Clear text
  emailText.value = "";

  // Clear file
  removeFile();

  // Hide results
  resultsSection.style.display = "none";

  // Reset form state
  validateForm();

  showToast("Formulário resetado", "info");
}

function copyResponse() {
  const responseText = document.getElementById("responseText").textContent;

  navigator.clipboard
    .writeText(responseText)
    .then(() => {
      showToast("Resposta copiada para a área de transferência!", "success");
    })
    .catch(() => {
      showToast("Erro ao copiar resposta", "error");
    });
}

function downloadResults() {
  const category = document.getElementById("categoryBadge").textContent;
  const confidence = document.getElementById("confidenceText").textContent;
  const response = document.getElementById("responseText").textContent;
  const filename =
    document.getElementById("processedFileName").textContent ||
    "email_classificado";

  const results = {
    categoria: category,
    confianca: confidence,
    resposta: response,
    arquivo: filename,
    timestamp: new Date().toISOString(),
  };

  const blob = new Blob([JSON.stringify(results, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = `resultado_classificacao_${Date.now()}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showToast("Resultados baixados com sucesso!", "success");
}

// Toast Notifications
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  const icon = getToastIcon(type);
  toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
    `;

  toastContainer.appendChild(toast);

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (toast.parentNode) {
      toast.parentNode.removeChild(toast);
    }
  }, 5000);

  // Click to dismiss
  toast.addEventListener("click", () => {
    if (toast.parentNode) {
      toast.parentNode.removeChild(toast);
    }
  });
}

function getToastIcon(type) {
  const icons = {
    success: "fa-check-circle",
    error: "fa-exclamation-circle",
    warning: "fa-exclamation-triangle",
    info: "fa-info-circle",
  };
  return icons[type] || icons.info;
}

// Keyboard shortcuts
document.addEventListener("keydown", function (e) {
  // Ctrl/Cmd + Enter to classify
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    if (!classifyBtn.disabled) {
      classifyEmail();
    }
  }

  // Escape to close loading
  if (e.key === "Escape" && loadingOverlay.style.display === "flex") {
    hideLoading();
  }
});

// Test function for debugging
window.testAPI = async function () {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();
    alert(`API Status: ${response.status} - ${JSON.stringify(data)}`);
  } catch (error) {
    console.error("❌ Erro:", error);
    alert(`Erro: ${error.message}`);
  }
};

// Prevent form submission on Enter in textarea
emailText.addEventListener("keydown", function (e) {
  if (e.key === "Enter" && !e.ctrlKey && !e.metaKey) {
    e.preventDefault();
  }
});

// Auto-resize textarea
emailText.addEventListener("input", function () {
  this.style.height = "auto";
  this.style.height = this.scrollHeight + "px";
});

// Initialize textarea height
emailText.style.height = "auto";
emailText.style.height = emailText.scrollHeight + "px";
