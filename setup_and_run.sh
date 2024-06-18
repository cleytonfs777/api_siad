#!/bin/bash

# Nome do ambiente virtual
VENV_DIR=".venv"

# Verifica se o ambiente virtual existe
if [ ! -d "$VENV_DIR" ]; then
  echo "Criando ambiente virtual..."
  python3 -m venv $VENV_DIR
fi

# Ativa o ambiente virtual
source $VENV_DIR/bin/activate

# Instala as dependências do requirements.txt
pip install --upgrade pip
pip install -r requirements.txt

# Roda o script bot.py
python bot.py
