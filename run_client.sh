# Para imediatamente se der erro
set -e

# Ativa o ambiente virtual
echo "Ativando o ambiente virtual..."
source venv/bin/activate

# Roda o cliente
echo "Iniciando o programa client..."
python3 client.py