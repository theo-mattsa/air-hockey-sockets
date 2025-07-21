#!/usr/bin/env python3
"""
Testes de Performance e Estabilidade para Pong Socket Game
Este módulo contém testes para medir latência, throughput e estabilidade do servidor
"""

import socket
import threading
import time
import pickle
import psutil
import os
import sys
import statistics
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import numpy as np

# Adicionar o diretório pai ao path para importar server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class PerformanceTest:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.results = {
            'latency': [],
            'throughput': [],
            'cpu_usage': [],
            'memory_usage': [],
            'connection_times': [],
            'failed_connections': 0,
            'successful_connections': 0
        }
    
    def test_latency(self, num_tests=100):
        """Testa a latência de comunicação com o servidor"""
        print(f"🧪 Testando latência com {num_tests} requests...")
        latencies = []
        
        for i in range(num_tests):
            try:
                start_time = time.time()
                
                # Criar conexão
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5.0)
                sock.connect((self.host, self.port))
                
                # Enviar dados de teste
                test_data = {'type': 'ping', 'timestamp': start_time}
                sock.sendall(pickle.dumps(test_data))
                
                # Receber resposta
                response = sock.recv(1024)
                end_time = time.time()
                
                latency = (end_time - start_time) * 1000  # em millisegundos
                latencies.append(latency)
                
                sock.close()
                
                if i % 10 == 0:
                    print(f"  Progress: {i}/{num_tests}")
                
            except Exception as e:
                print(f"  Erro na iteração {i}: {e}")
                continue
        
        self.results['latency'] = latencies
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            median_latency = statistics.median(latencies)
            
            print(f"📊 Resultados de Latência:")
            print(f"  Média: {avg_latency:.2f}ms")
            print(f"  Mediana: {median_latency:.2f}ms")
            print(f"  Mín: {min_latency:.2f}ms")
            print(f"  Máx: {max_latency:.2f}ms")
            print(f"  Testes realizados: {len(latencies)}/{num_tests}")
    
    def test_concurrent_connections(self, num_connections=50, duration=30):
        """Testa conexões simultâneas"""
        print(f"🔗 Testando {num_connections} conexões simultâneas por {duration}s...")
        
        def create_connection(connection_id):
            try:
                start_time = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10.0)
                sock.connect((self.host, self.port))
                
                connection_time = time.time() - start_time
                self.results['connection_times'].append(connection_time * 1000)
                
                # Manter conexão ativa
                end_time = time.time() + duration
                while time.time() < end_time:
                    try:
                        test_data = {'type': 'heartbeat', 'id': connection_id}
                        sock.sendall(pickle.dumps(test_data))
                        time.sleep(1)
                    except:
                        break
                
                sock.close()
                self.results['successful_connections'] += 1
                
            except Exception as e:
                self.results['failed_connections'] += 1
                print(f"  Falha na conexão {connection_id}: {e}")
        
        # Executar conexões em paralelo
        with ThreadPoolExecutor(max_workers=num_connections) as executor:
            futures = [executor.submit(create_connection, i) for i in range(num_connections)]
            
            # Aguardar conclusão
            for future in futures:
                future.result()
        
        success_rate = (self.results['successful_connections'] / num_connections) * 100
        print(f"📊 Resultados de Conexões Simultâneas:")
        print(f"  Conexões bem-sucedidas: {self.results['successful_connections']}")
        print(f"  Conexões falhadas: {self.results['failed_connections']}")
        print(f"  Taxa de sucesso: {success_rate:.1f}%")
        
        if self.results['connection_times']:
            avg_conn_time = statistics.mean(self.results['connection_times'])
            print(f"  Tempo médio de conexão: {avg_conn_time:.2f}ms")
    
    def monitor_system_resources(self, duration=60, interval=1):
        """Monitora uso de CPU e memória durante o teste"""
        print(f"📈 Monitorando recursos do sistema por {duration}s...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            
            self.results['cpu_usage'].append(cpu_percent)
            self.results['memory_usage'].append(memory_info.percent)
            
            time.sleep(interval)
        
        if self.results['cpu_usage']:
            avg_cpu = statistics.mean(self.results['cpu_usage'])
            max_cpu = max(self.results['cpu_usage'])
            avg_memory = statistics.mean(self.results['memory_usage'])
            max_memory = max(self.results['memory_usage'])
            
            print(f"📊 Uso de Recursos:")
            print(f"  CPU média: {avg_cpu:.1f}%")
            print(f"  CPU máxima: {max_cpu:.1f}%")
            print(f"  Memória média: {avg_memory:.1f}%")
            print(f"  Memória máxima: {max_memory:.1f}%")
    
    def stress_test(self, num_clients=20, duration=120):
        """Teste de stress com múltiplos clientes enviando dados continuamente"""
        print(f"💪 Teste de stress: {num_clients} clientes por {duration}s...")
        
        def stress_client(client_id):
            messages_sent = 0
            errors = 0
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5.0)
                sock.connect((self.host, self.port))
                
                start_time = time.time()
                while time.time() - start_time < duration:
                    try:
                        # Simular dados de jogo
                        game_data = {
                            'type': 'game_update',
                            'player_id': client_id,
                            'paddle_x': 480,
                            'timestamp': time.time()
                        }
                        sock.sendall(pickle.dumps(game_data))
                        messages_sent += 1
                        time.sleep(0.1)  # 10 FPS
                        
                    except Exception as e:
                        errors += 1
                        if errors > 10:  # Muitos erros, sair
                            break
                
                sock.close()
                
            except Exception as e:
                print(f"  Cliente {client_id} falhou: {e}")
                errors += 1
            
            return messages_sent, errors
        
        # Executar clientes de stress
        start_monitor_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_clients) as executor:
            # Iniciar monitoramento de recursos
            monitor_thread = threading.Thread(
                target=self.monitor_system_resources, 
                args=(duration, 1)
            )
            monitor_thread.start()
            
            # Executar clientes
            futures = [executor.submit(stress_client, i) for i in range(num_clients)]
            
            total_messages = 0
            total_errors = 0
            
            for future in futures:
                messages, errors = future.result()
                total_messages += messages
                total_errors += errors
            
            monitor_thread.join()
        
        throughput = total_messages / duration
        error_rate = (total_errors / (total_messages + total_errors)) * 100 if (total_messages + total_errors) > 0 else 0
        
        print(f"📊 Resultados do Teste de Stress:")
        print(f"  Mensagens enviadas: {total_messages}")
        print(f"  Erros: {total_errors}")
        print(f"  Throughput: {throughput:.1f} msg/s")
        print(f"  Taxa de erro: {error_rate:.2f}%")
    
    def generate_report(self):
        """Gera relatório visual dos testes"""
        print("📈 Gerando relatório visual...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Relatório de Performance - Pong Socket Game', fontsize=16)
        
        # Gráfico de Latência
        if self.results['latency']:
            axes[0, 0].hist(self.results['latency'], bins=20, alpha=0.7, color='blue')
            axes[0, 0].set_title('Distribuição de Latência')
            axes[0, 0].set_xlabel('Latência (ms)')
            axes[0, 0].set_ylabel('Frequência')
        
        # Gráfico de CPU
        if self.results['cpu_usage']:
            time_points = range(len(self.results['cpu_usage']))
            axes[0, 1].plot(time_points, self.results['cpu_usage'], color='red')
            axes[0, 1].set_title('Uso de CPU ao Longo do Tempo')
            axes[0, 1].set_xlabel('Tempo (s)')
            axes[0, 1].set_ylabel('CPU (%)')
        
        # Gráfico de Memória
        if self.results['memory_usage']:
            time_points = range(len(self.results['memory_usage']))
            axes[1, 0].plot(time_points, self.results['memory_usage'], color='green')
            axes[1, 0].set_title('Uso de Memória ao Longo do Tempo')
            axes[1, 0].set_xlabel('Tempo (s)')
            axes[1, 0].set_ylabel('Memória (%)')
        
        # Gráfico de Conexões
        if self.results['connection_times']:
            axes[1, 1].hist(self.results['connection_times'], bins=15, alpha=0.7, color='orange')
            axes[1, 1].set_title('Tempo de Estabelecimento de Conexão')
            axes[1, 1].set_xlabel('Tempo (ms)')
            axes[1, 1].set_ylabel('Frequência')
        
        plt.tight_layout()
        plt.savefig('/home/theo/Documents/ufes/redes/pong-sockets/tests/performance_report.png', 
                   dpi=300, bbox_inches='tight')
        print("  Relatório salvo como 'performance_report.png'")
        plt.show()
    
    def run_full_test_suite(self):
        """Executa todos os testes de performance"""
        print("🚀 Iniciando suite completa de testes de performance...")
        print("=" * 60)
        
        # Teste de latência
        self.test_latency(50)
        print()
        
        # Teste de conexões simultâneas
        self.test_concurrent_connections(20, 15)
        print()
        
        # Teste de stress
        self.stress_test(10, 60)
        print()
        
        # Gerar relatório
        self.generate_report()
        
        print("✅ Todos os testes concluídos!")


if __name__ == "__main__":
    # Configurar teste
    tester = PerformanceTest(host='localhost', port=5555)
    
    print("Pong Socket Game - Testes de Performance e Estabilidade")
    print("=" * 60)
    print("IMPORTANTE: Certifique-se de que o servidor está rodando!")
    print()
    
    input("Pressione Enter para começar os testes...")
    
    # Executar testes
    tester.run_full_test_suite()
