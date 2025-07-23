# Para imediatamente se der erro
set -e

# Ativa o ambiente virtual
echo "Ativando o ambiente virtual..."
source ../venv/bin/activate

echo "Executando Teste de Carga Gradual..."
python3 teste_carga.py
