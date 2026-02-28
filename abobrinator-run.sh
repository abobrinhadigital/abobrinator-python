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

# Verifica se o argumento do arquivo foi passado
if [ -z "$1" ]; then
    echo "Uso: $0 caminho/do/arquivo.txt [--rascunho]"
    exit 1
fi

# Executa o abobrinator usando o python do venv diretamente e repassando os argumentos
"$PYTHON_VENV" abobrinator.py "$@"