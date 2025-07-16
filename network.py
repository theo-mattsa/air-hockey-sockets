# network.py
import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = "0.0.0.0"
        self.port = 5555
        self.addr = (self.server_ip, self.port)
        self.player_id = self.connect()

    def get_player_id(self):
        """Retorna o ID do jogador (0 ou 1)."""
        return self.player_id

    def connect(self):
        """
        Conecta ao servidor e retorna o ID do jogador.
        """
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(f"Não foi possível conectar ao servidor: {e}")
            return None

    def send(self, data):
        """
        Envia dados para o servidor e recebe a resposta.
        """
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096)) 
        except socket.error as e:
            print(f"Erro de comunicação: {e}")
            return None