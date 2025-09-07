// Validação de formulário
const Validation = {
  // Validar tipo de arquivo
  isValidFileType(file) {
    const { VALID_FILE_TYPES, VALID_FILE_EXTENSIONS } = window.CONFIG;

    const isValidType = VALID_FILE_TYPES.includes(file.type);
    const isValidExtension = VALID_FILE_EXTENSIONS.some((ext) =>
      file.name.toLowerCase().endsWith(ext)
    );
    const isValid = isValidType || isValidExtension;

    console.log("🔍 Validando tipo de arquivo:");
    console.log("📁 Arquivo:", file.name);
    console.log("📁 Tipo:", file.type);
    console.log("📁 Extensões válidas:", VALID_FILE_EXTENSIONS);
    console.log("✅ Tipo válido:", isValidType);
    console.log("✅ Extensão válida:", isValidExtension);
    console.log("✅ Arquivo válido:", isValid);

    return isValid;
  },

  // Validar formulário
  validateForm(selectedFile, emailText) {
    const hasText = emailText.value.trim().length > 0;
    const hasFile = selectedFile !== null;

    console.log("🔍 Validando formulário:");
    console.log("📝 Tem texto:", hasText);
    console.log("📁 Tem arquivo:", hasFile);
    console.log("📁 Arquivo:", selectedFile);
    console.log("📁 selectedFile !== null:", selectedFile !== null);
    console.log("📁 typeof selectedFile:", typeof selectedFile);

    const isValid = hasText || hasFile;

    if (hasText && hasFile) {
      window.UI.showToast(
        "Você pode usar texto ou arquivo, mas não ambos ao mesmo tempo",
        "warning"
      );
      return false;
    }

    console.log("✅ Formulário válido:", isValid);
    return isValid;
  },

  // Validar e atualizar botão
  updateButtonState(isValid) {
    const { classifyBtn } = window.DOM;
    classifyBtn.disabled = !isValid;
    console.log("🔘 Botão desabilitado:", classifyBtn.disabled);
  },
};

// Exportar Validation
window.Validation = Validation;
