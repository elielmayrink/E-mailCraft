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

    return isValid;
  },

  // Validar formulário
  validateForm(selectedFile, emailText) {
    const hasText = emailText.value.trim().length > 0;
    const hasFile = selectedFile !== null;

    const isValid = hasText || hasFile;

    if (hasText && hasFile) {
      window.UI.showToast(
        "Você pode usar texto ou arquivo, mas não ambos ao mesmo tempo",
        "warning"
      );
      return false;
    }

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
