// Gerenciamento de arquivos
const FileHandler = {
  selectedFile: null,

  // Formatar tamanho do arquivo
  formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";

    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  },

  // Processar arquivo selecionado
  processSelectedFile(file) {
    console.log("📁 Processando arquivo selecionado:", file);
    console.log("📁 selectedFile antes:", this.selectedFile);

    this.selectedFile = file;
    console.log("📁 selectedFile após atribuição:", this.selectedFile);

    // Update file info display
    const { fileName, fileSize } = window.DOM.getFileInfoElements();
    fileName.textContent = file.name;
    fileSize.textContent = this.formatFileSize(file.size);

    // Show file info, hide upload area
    const { fileUploadArea, fileInfo } = window.DOM;
    fileUploadArea.style.display = "none";
    fileInfo.style.display = "flex";

    // Clear text input
    window.DOM.emailText.value = "";

    console.log("✅ Arquivo processado com sucesso");
    console.log("📁 selectedFile após processamento:", this.selectedFile);
    console.log("📁 selectedFile !== null:", this.selectedFile !== null);

    // Validar formulário após processar arquivo
    const isValid = window.Validation.validateForm(
      this.selectedFile,
      window.DOM.emailText
    );
    window.Validation.updateButtonState(isValid);
    console.log("🔍 Validação após processar arquivo:", isValid);
  },

  // Remover arquivo
  removeFile() {
    console.log("🗑️ Removendo arquivo...");
    this.selectedFile = null;
    window.DOM.emailFile.value = "";

    // Show upload area, hide file info
    const { fileUploadArea, fileInfo } = window.DOM;
    fileUploadArea.style.display = "block";
    fileInfo.style.display = "none";

    console.log("✅ Arquivo removido");
    const isValid = window.Validation.validateForm(
      this.selectedFile,
      window.DOM.emailText
    );
    window.Validation.updateButtonState(isValid);
  },

  // Manipular seleção de arquivo
  handleFileSelect(event) {
    console.log("📁 handleFileSelect chamado");
    console.log("📁 event.target.files:", event.target.files);
    const file = event.target.files[0];
    console.log("📁 Arquivo selecionado:", file);
    if (file) {
      console.log("📁 Chamando processSelectedFile...");
      this.processSelectedFile(file);
    } else {
      console.log("❌ Nenhum arquivo selecionado");
    }
  },

  // Manipular drag over
  handleDragOver(event) {
    event.preventDefault();
    window.DOM.fileUploadArea.classList.add("dragover");
  },

  // Manipular drag leave
  handleDragLeave(event) {
    event.preventDefault();
    window.DOM.fileUploadArea.classList.remove("dragover");
  },

  // Manipular drop
  handleDrop(event) {
    console.log("📁 handleDrop chamado");
    event.preventDefault();
    window.DOM.fileUploadArea.classList.remove("dragover");

    const files = event.dataTransfer.files;
    console.log("📁 Arquivos no drop:", files);
    if (files.length > 0) {
      const file = files[0];
      console.log("📁 Arquivo do drop:", file);
      if (window.Validation.isValidFileType(file)) {
        console.log("📁 Arquivo válido, chamando processSelectedFile...");
        this.processSelectedFile(file);
      } else {
        console.log("❌ Arquivo inválido");
        window.UI.showToast(
          "Tipo de arquivo não suportado. Use apenas .txt ou .pdf",
          "error"
        );
      }
    } else {
      console.log("❌ Nenhum arquivo no drop");
    }
  },
};

// Exportar FileHandler
window.FileHandler = FileHandler;
