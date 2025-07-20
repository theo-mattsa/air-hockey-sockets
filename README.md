# Pong Sockets

Um jogo multiplayer de Pong implementado com sockets TCP em Python, utilizando Pygame para a interface gráfica.
O projeto permite que dois jogadores se conectem a um servidor para jogar Pong em tempo real.

## 🎮 Funcionalidades

- **Multiplayer online**: Dois jogadores podem se conectar e jogar simultaneamente
- **Sistema de matchmaking**: O servidor gerencia filas de jogadores esperando por partidas
- **Interface gráfica moderna**: Desenvolvida com Pygame
- **Velocidade progressiva**: A bola acelera conforme o jogo progride
- **Arquitetura cliente-servidor**: Comunicação via sockets TCP

## 📋 Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## ⚙️ Instalação

### Opção 1: Configuração automática (recomendada)

```bash
# Torna o script executável e roda a configuração
chmod +x setup_env.sh
./setup_env.sh
```

### Opção 2: Configuração manual

```bash
# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate      # Linux/macOS
# ou
venv\Scripts\activate         # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 1. Configuração do servidor

Primeiro, configure as variáveis de ambiente criando um arquivo `.env`:

```bash
SERVER_IP=localhost
SERVER_PORT=5555
```

### 2. Iniciar o servidor

```bash
# Opção 1: Script automático
chmod +x run_server.sh
./run_server.sh

# Opção 2: Manual
source venv/bin/activate
python3 server.py
```

### 3. Conectar clientes

Em terminais separados (para cada jogador):

```bash
# Opção 1: Script automático
chmod +x run_client.sh
./run_client.sh

# Opção 2: Manual
source venv/bin/activate
python3 client.py
```

## Arquitetura

### Servidor (`server.py`)

- Gerencia o estado do jogo
- Processa movimentos dos jogadores
- Simula física da bola
- Coordena múltiplas partidas simultâneas
- Implementa sistema de filas para matchmaking

### Cliente (`client.py`)

- Interface gráfica do jogo
- Captura inputs do jogador
- Renderiza estado do jogo recebido do servidor

### Protocolo de Comunicação

- **TCP Sockets**: Comunicação confiável cliente-servidor
- **Pickle**: Serialização do estado do jogo
- **Threading**: Suporte a múltiplos clientes simultâneos

## Configuração Avançada

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
SERVER_IP=localhost     # IP do servidor
SERVER_PORT=5555       # Porta do servidor
```

### Jogando pela rede

Para jogar em rede local ou internet:

1. No servidor, defina `SERVER_IP` como o IP da máquina servidor
2. Nos clientes, use o mesmo IP do servidor
