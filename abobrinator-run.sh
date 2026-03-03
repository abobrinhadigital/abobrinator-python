#!/bin/bash

# Caminho absoluto para o diretório do script
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_VENV="$BASE_DIR/venv/bin/python"

# Verifica se o executável do Python no venv existe
if [ ! -f "$PYTHON_VENV" ]; then
    echo "Erro: Ambiente virtual não encontrado em $BASE_DIR/venv"
    exit 1
fi

# Muda para o diretório base para garantir a leitura do .env pelo script
cd "$BASE_DIR"

# Executa o abobrinator usando o python do venv diretamente
# Repassa apenas flags opcionais (como --rascunho)
"$PYTHON_VENV" abobrinator.py "$@"