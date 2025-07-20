# Para imediatamente se algum comando falhar
set -e

ENV_DIR="venv"

echo "Criando ambiente virtual..."
python3 -m venv $ENV_DIR

echo "Ambiente virtual criado!"

# Ativa o ambiente virtual
echo "Ativando o ambiente virtual..."
source $ENV_DIR/bin/activate

# Verifica se o requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo "Arquivo requirements.txt não encontrado. Abortando."
    deactivate
    exit 1
fi

# Instala as dependências do requirements.txt
echo "Instalando dependências do requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Ambiente pronto!"