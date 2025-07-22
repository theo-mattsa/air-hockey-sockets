import os

# Configurações do Servidor
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5555

# Configurações dos Testes
DEFAULT_MAX_CLIENTS = 50
DEFAULT_STEP = 5
DEFAULT_STEP_DURATION = 30

# Diretório dos Relatórios
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")