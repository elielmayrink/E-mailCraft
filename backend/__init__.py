# Arquivo de inicialização do backend
import sys
import os
from pathlib import Path

# Garantir que o diretório backend e o projeto estejam no PYTHONPATH
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent

# Adicionar diretórios ao sys.path se não estiverem presentes
for path_to_add in [str(current_dir), str(project_root)]:
    if path_to_add not in sys.path:
        sys.path.insert(0, path_to_add)