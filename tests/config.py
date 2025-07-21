# Configuração simples para os testes
# Modifique estes valores conforme necessário

# Configurações do servidor
SERVER_HOST = "172.28.154.143"
SERVER_PORT = 5555

# Diretório para salvar relatórios
import os
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "relatorios")

# Para usar um servidor remoto, altere para:
# SERVER_HOST = "192.168.1.100"  # IP do servidor
# SERVER_PORT = 5555             # Porta do servidor
