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
from datetime import datetime

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar configurações
from config import SERVER_HOST, SERVER_PORT

class GameClientSimulator:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT, client_id=None):
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
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.results = {
            'successful_clients': 0,
            'failed_clients': 0,
            'total_messages': 0,
            'test_duration': 0
        }
        self.test_report = []  # Lista para armazenar relatório detalhado
    
    def add_to_report(self, message):
        """Adiciona uma linha ao relatório"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.test_report.append(f"[{timestamp}] {message}")
        print(message)  # Também exibe no console
    
    def save_report_to_file(self, test_type="simulation"):
        """Salva o relatório em arquivo TXT"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_client_simulator_{test_type}_{timestamp}.txt"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("           RELATÓRIO DE SIMULAÇÃO DE CLIENTES - PONG SOCKETS\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Tipo de Teste: {test_type.upper()}\n")
            f.write(f"Servidor: {self.host}:{self.port}\n\n")
            
            f.write("RESUMO DOS RESULTADOS:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Clientes bem-sucedidos: {self.results['successful_clients']}\n")
            f.write(f"Clientes com falha: {self.results['failed_clients']}\n")
            f.write(f"Total de mensagens: {self.results['total_messages']}\n")
            f.write(f"Duração do teste: {self.results['test_duration']:.2f}s\n")
            
            if self.results['successful_clients'] + self.results['failed_clients'] > 0:
                total_clients = self.results['successful_clients'] + self.results['failed_clients']
                success_rate = (self.results['successful_clients'] / total_clients) * 100
                f.write(f"Taxa de sucesso: {success_rate:.1f}%\n")
            
            if self.results['test_duration'] > 0 and self.results['total_messages'] > 0:
                throughput = self.results['total_messages'] / self.results['test_duration']
                f.write(f"Throughput: {throughput:.1f} mensagens/segundo\n")
            
            f.write("\nDETALHES DA EXECUÇÃO:\n")
            f.write("-" * 40 + "\n")
            for line in self.test_report:
                f.write(line + "\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("Relatório gerado automaticamente pelo Client Simulator\n")
            f.write("=" * 80 + "\n")
        
        self.add_to_report(f"📄 Relatório salvo em: {filename}")
        return filepath
    
    def run_concurrent_game_simulation(self, num_clients=10, duration=60):
        """Executa simulação com múltiplos clientes jogando"""
        self.add_to_report(f"🎯 Iniciando simulação com {num_clients} clientes por {duration}s...")
        
        def client_worker(client_id):
            simulator = GameClientSimulator(self.host, self.port, client_id)
            success = simulator.simulate_game_session(duration)
            
            if success:
                self.results['successful_clients'] += 1
                self.add_to_report(f"✅ Cliente {client_id} concluído com sucesso")
            else:
                self.results['failed_clients'] += 1
                self.add_to_report(f"❌ Cliente {client_id} falhou")
        
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
        
        self.add_to_report(f"📊 Simulação concluída:")
        self.add_to_report(f"  Clientes bem-sucedidos: {self.results['successful_clients']}")
        self.add_to_report(f"  Clientes com falha: {self.results['failed_clients']}")
        
        if num_clients > 0:
            success_rate = (self.results['successful_clients'] / num_clients) * 100
            self.add_to_report(f"  Taxa de sucesso: {success_rate:.1f}%")
        
        self.add_to_report(f"  Duração real: {self.results['test_duration']:.1f}s")
        
        # Salvar relatório
        self.save_report_to_file("simulacao_jogo")
    
    def run_stress_test(self, num_clients=20, duration=30, message_rate=5):
        """Executa teste de stress com alta frequência de mensagens"""
        self.add_to_report(f"🔥 Iniciando teste de stress: {num_clients} clientes, {message_rate} msg/s, {duration}s...")
        
        def stress_worker(client_id):
            simulator = GameClientSimulator(self.host, self.port, client_id)
            messages = simulator.stress_test_client(duration, message_rate)
            self.results['total_messages'] += messages or 0
            if messages and messages > 0:
                self.add_to_report(f"📤 Cliente {client_id}: {messages} mensagens enviadas")
        
        start_time = time.time()
        threads = []
        for i in range(num_clients):
            thread = threading.Thread(target=stress_worker, args=(f"stress_{i}",))
            threads.append(thread)
            thread.start()
            time.sleep(0.05)  # Delay menor para stress test
        
        for thread in threads:
            thread.join()
        
        self.results['test_duration'] = time.time() - start_time
        total_expected = num_clients * message_rate * duration
        efficiency = (self.results['total_messages'] / total_expected) * 100 if total_expected > 0 else 0
        
        self.add_to_report(f"📊 Resultados do Teste de Stress:")
        self.add_to_report(f"  Mensagens enviadas: {self.results['total_messages']}")
        self.add_to_report(f"  Mensagens esperadas: {total_expected}")
        self.add_to_report(f"  Eficiência: {efficiency:.1f}%")
        
        if self.results['test_duration'] > 0:
            throughput = self.results['total_messages'] / self.results['test_duration']
            self.add_to_report(f"  Throughput: {throughput:.1f} msg/s")
        
        # Salvar relatório
        self.save_report_to_file("teste_stress")
    
    def run_gradual_load_test(self, max_clients=50, step=5, step_duration=30):
        """Teste de carga gradual"""
        self.add_to_report(f"📈 Iniciando teste de carga gradual: 0 até {max_clients} clientes...")
        
        for num_clients in range(step, max_clients + 1, step):
            self.add_to_report(f"🔄 Testando com {num_clients} clientes...")
            
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
            self.add_to_report(f"  📊 {num_clients} clientes: {success_rate:.1f}% sucesso")
            
            # Atualizar resultados globais
            self.results['successful_clients'] += step_results['successful_clients']
            self.results['failed_clients'] += step_results['failed_clients']
            
            # Se a taxa de sucesso cair muito, parar o teste
            if success_rate < 50:
                self.add_to_report(f"⚠️  Taxa de sucesso muito baixa ({success_rate:.1f}%), parando o teste")
                break
            
            time.sleep(2)  # Pausa entre steps
        
        # Salvar relatório
        self.save_report_to_file("teste_carga_gradual")


def main():
    print("🎮 Pong Socket Game - Simulador de Clientes")
    print("=" * 60)
    
    manager = LoadTestManager()
    
    print(f"Servidor configurado: {SERVER_HOST}:{SERVER_PORT}")
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
