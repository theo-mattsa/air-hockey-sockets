#!/usr/bin/env python3
"""
Simulador de Cliente para Testes
Simula múltiplos clientes jogando Pong para testes de carga
"""

import socket
import threading
import time
import pickle
import random
import os
import sys

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class GameClientSimulator:
    def __init__(self, host='localhost', port=5000, client_id=None):
        self.host = host
        self.port = port
        self.client_id = client_id or f"bot_{random.randint(1000, 9999)}"
        self.connected = False
        self.game_state = None
        self.socket = None
        self.player_name = f"TestBot_{self.client_id}"
        
    def connect(self):
        """Conecta ao servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"✅ Cliente {self.client_id} conectado")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar cliente {self.client_id}: {e}")
            return False
    
    def send_data(self, data):
        """Envia dados para o servidor"""
        try:
            if self.socket and self.connected:
                self.socket.sendall(pickle.dumps(data))
                return True
        except Exception as e:
            print(f"❌ Erro ao enviar dados (Cliente {self.client_id}): {e}")
            self.connected = False
            return False
    
    def receive_data(self):
        """Recebe dados do servidor"""
        try:
            if self.socket and self.connected:
                data = self.socket.recv(4096)
                if data:
                    return pickle.loads(data)
        except Exception as e:
            if self.connected:  # Só mostra erro se ainda estava conectado
                print(f"❌ Erro ao receber dados (Cliente {self.client_id}): {e}")
            self.connected = False
        return None
    
    def simulate_game_session(self, duration=60):
        """Simula uma sessão de jogo"""
        print(f"🎮 Cliente {self.client_id} iniciando sessão de {duration}s")
        
        if not self.connect():
            return False
        
        start_time = time.time()
        messages_sent = 0
        messages_received = 0
        
        try:
            # Enviar nome do jogador
            name_data = {
                'type': 'player_name',
                'name': self.player_name
            }
            self.send_data(name_data)
            
            # Thread para receber dados
            def receive_loop():
                nonlocal messages_received
                while self.connected and time.time() - start_time < duration:
                    data = self.receive_data()
                    if data:
                        messages_received += 1
                        self.game_state = data
                    time.sleep(0.01)
            
            receive_thread = threading.Thread(target=receive_loop)
            receive_thread.start()
            
            # Loop principal de jogo
            while self.connected and time.time() - start_time < duration:
                # Simular movimentos do paddle
                paddle_x = random.randint(100, 860)  # Movimento aleatório
                
                game_data = {
                    'type': 'paddle_move',
                    'player_id': self.client_id,
                    'paddle_x': paddle_x,
                    'timestamp': time.time()
                }
                
                if self.send_data(game_data):
                    messages_sent += 1
                
                # Simular FPS do jogo (60 FPS)
                time.sleep(1/60)
            
            receive_thread.join(timeout=1)
            
        except Exception as e:
            print(f"❌ Erro durante simulação (Cliente {self.client_id}): {e}")
        
        finally:
            if self.socket:
                self.socket.close()
            self.connected = False
        
        print(f"📊 Cliente {self.client_id} - Mensagens enviadas: {messages_sent}, recebidas: {messages_received}")
        return True
    
    def stress_test_client(self, duration=30, message_rate=10):
        """Cliente para teste de stress"""
        print(f"💪 Cliente stress {self.client_id} - {message_rate} msg/s por {duration}s")
        
        if not self.connect():
            return False
        
        start_time = time.time()
        messages_sent = 0
        
        try:
            while self.connected and time.time() - start_time < duration:
                # Dados de teste de stress
                stress_data = {
                    'type': 'stress_test',
                    'client_id': self.client_id,
                    'sequence': messages_sent,
                    'timestamp': time.time(),
                    'payload': 'x' * random.randint(50, 200)  # Payload variável
                }
                
                if self.send_data(stress_data):
                    messages_sent += 1
                
                time.sleep(1/message_rate)
                
        except Exception as e:
            print(f"❌ Erro no stress test (Cliente {self.client_id}): {e}")
        
        finally:
            if self.socket:
                self.socket.close()
            self.connected = False
        
        print(f"📊 Stress client {self.client_id} - Mensagens enviadas: {messages_sent}")
        return messages_sent


class LoadTestManager:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.results = {
            'successful_clients': 0,
            'failed_clients': 0,
            'total_messages': 0,
            'test_duration': 0
        }
    
    def run_concurrent_game_simulation(self, num_clients=10, duration=60):
        """Executa simulação com múltiplos clientes jogando"""
        print(f"🎯 Simulando {num_clients} clientes jogando por {duration}s...")
        
        def client_worker(client_id):
            simulator = GameClientSimulator(self.host, self.port, client_id)
            success = simulator.simulate_game_session(duration)
            
            if success:
                self.results['successful_clients'] += 1
            else:
                self.results['failed_clients'] += 1
        
        start_time = time.time()
        
        # Criar threads para cada cliente
        threads = []
        for i in range(num_clients):
            thread = threading.Thread(target=client_worker, args=(f"game_{i}",))
            threads.append(thread)
            thread.start()
            time.sleep(0.1)  # Pequeno delay entre conexões
        
        # Aguardar todos os clientes
        for thread in threads:
            thread.join()
        
        self.results['test_duration'] = time.time() - start_time
        
        print(f"📊 Resultados da Simulação de Jogo:")
        print(f"  Clientes bem-sucedidos: {self.results['successful_clients']}")
        print(f"  Clientes com falha: {self.results['failed_clients']}")
        print(f"  Taxa de sucesso: {(self.results['successful_clients'] / num_clients) * 100:.1f}%")
        print(f"  Duração real: {self.results['test_duration']:.1f}s")
    
    def run_stress_test(self, num_clients=20, duration=30, message_rate=5):
        """Executa teste de stress com alta frequência de mensagens"""
        print(f"🔥 Teste de stress: {num_clients} clientes, {message_rate} msg/s, {duration}s...")
        
        def stress_worker(client_id):
            simulator = GameClientSimulator(self.host, self.port, client_id)
            messages = simulator.stress_test_client(duration, message_rate)
            self.results['total_messages'] += messages or 0
        
        threads = []
        for i in range(num_clients):
            thread = threading.Thread(target=stress_worker, args=(f"stress_{i}",))
            threads.append(thread)
            thread.start()
            time.sleep(0.05)  # Delay menor para stress test
        
        for thread in threads:
            thread.join()
        
        total_expected = num_clients * message_rate * duration
        efficiency = (self.results['total_messages'] / total_expected) * 100 if total_expected > 0 else 0
        
        print(f"📊 Resultados do Teste de Stress:")
        print(f"  Mensagens enviadas: {self.results['total_messages']}")
        print(f"  Mensagens esperadas: {total_expected}")
        print(f"  Eficiência: {efficiency:.1f}%")
        print(f"  Throughput: {self.results['total_messages'] / duration:.1f} msg/s")
    
    def run_gradual_load_test(self, max_clients=50, step=5, step_duration=30):
        """Teste de carga gradual"""
        print(f"📈 Teste de carga gradual: 0 até {max_clients} clientes...")
        
        for num_clients in range(step, max_clients + 1, step):
            print(f"\n🔄 Testando com {num_clients} clientes...")
            
            # Reset results for this step
            step_results = {
                'successful_clients': 0,
                'failed_clients': 0
            }
            
            def client_worker(client_id):
                simulator = GameClientSimulator(self.host, self.port, client_id)
                success = simulator.simulate_game_session(step_duration)
                
                if success:
                    step_results['successful_clients'] += 1
                else:
                    step_results['failed_clients'] += 1
            
            threads = []
            for i in range(num_clients):
                thread = threading.Thread(target=client_worker, args=(f"grad_{num_clients}_{i}",))
                threads.append(thread)
                thread.start()
                time.sleep(0.1)
            
            for thread in threads:
                thread.join()
            
            success_rate = (step_results['successful_clients'] / num_clients) * 100
            print(f"  📊 {num_clients} clientes: {success_rate:.1f}% sucesso")
            
            # Se a taxa de sucesso cair muito, parar o teste
            if success_rate < 50:
                print(f"⚠️  Taxa de sucesso muito baixa ({success_rate:.1f}%), parando o teste")
                break
            
            time.sleep(2)  # Pausa entre steps


def main():
    print("🎮 Pong Socket Game - Simulador de Clientes")
    print("=" * 60)
    
    manager = LoadTestManager(host='localhost', port=5000)
    
    print("IMPORTANTE: Certifique-se de que o servidor está rodando!")
    print()
    print("Opções de teste:")
    print("1. Simulação de jogo normal (10 clientes, 60s)")
    print("2. Teste de stress (20 clientes, alta frequência)")
    print("3. Teste de carga gradual (até 30 clientes)")
    print("4. Teste personalizado")
    print()
    
    try:
        choice = input("Escolha uma opção (1-4): ").strip()
        
        if choice == '1':
            manager.run_concurrent_game_simulation(10, 60)
        
        elif choice == '2':
            manager.run_stress_test(20, 30, 10)
        
        elif choice == '3':
            manager.run_gradual_load_test(30, 5, 20)
        
        elif choice == '4':
            num_clients = int(input("Número de clientes: "))
            duration = int(input("Duração (segundos): "))
            manager.run_concurrent_game_simulation(num_clients, duration)
        
        else:
            print("Opção inválida. Executando teste padrão...")
            manager.run_concurrent_game_simulation(5, 30)
    
    except KeyboardInterrupt:
        print("\n⚠️  Teste interrompido pelo usuário")
    except ValueError:
        print("❌ Valores inválidos. Executando teste padrão...")
        manager.run_concurrent_game_simulation(5, 30)


if __name__ == "__main__":
    main()
