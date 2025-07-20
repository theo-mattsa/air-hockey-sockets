# Para imediatamente se der erro
set -e

# Ativa o ambiente virtual
echo "Ativando o ambiente virtual..."
source venv/bin/activate

# Roda o servidor
echo "Iniciando o programa server..."
python3 server.py