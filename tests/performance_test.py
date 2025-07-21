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
from datetime import datetime

# Adicionar o diretório pai ao path para importar server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar configurações
from config import SERVER_HOST, SERVER_PORT, REPORTS_DIR

class PerformanceTest:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
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
        self.test_report = []  # Lista para armazenar relatório detalhado
    
    def add_to_report(self, message):
        """Adiciona uma linha ao relatório"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.test_report.append(f"[{timestamp}] {message}")
        print(message)  # Também exibe no console
    
    def save_report_to_file(self, test_type="performance"):
        """Salva o relatório em arquivo TXT"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_performance_{test_type}_{timestamp}.txt"
        
        # Criar diretório se não existir
        os.makedirs(REPORTS_DIR, exist_ok=True)
        filepath = os.path.join(REPORTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("              RELATÓRIO DE PERFORMANCE - PONG SOCKETS\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Tipo de Teste: {test_type.upper()}\n")
            f.write(f"Servidor: {self.host}:{self.port}\n\n")
            
            f.write("MÉTRICAS DE PERFORMANCE:\n")
            f.write("-" * 40 + "\n")
            
            # Latência
            if self.results['latency']:
                avg_latency = statistics.mean(self.results['latency'])
                min_latency = min(self.results['latency'])
                max_latency = max(self.results['latency'])
                median_latency = statistics.median(self.results['latency'])
                
                f.write(f"LATÊNCIA:\n")
                f.write(f"  Média: {avg_latency:.2f}ms\n")
                f.write(f"  Mediana: {median_latency:.2f}ms\n")
                f.write(f"  Mínima: {min_latency:.2f}ms\n")
                f.write(f"  Máxima: {max_latency:.2f}ms\n\n")
            
            # Conexões
            f.write(f"CONEXÕES:\n")
            f.write(f"  Bem-sucedidas: {self.results['successful_connections']}\n")
            f.write(f"  Falhadas: {self.results['failed_connections']}\n")
            
            total_connections = self.results['successful_connections'] + self.results['failed_connections']
            if total_connections > 0:
                success_rate = (self.results['successful_connections'] / total_connections) * 100
                f.write(f"  Taxa de sucesso: {success_rate:.1f}%\n")
            
            if self.results['connection_times']:
                avg_conn_time = statistics.mean(self.results['connection_times'])
                f.write(f"  Tempo médio de conexão: {avg_conn_time:.2f}ms\n")
            f.write("\n")
            
            # Recursos do Sistema
            if self.results['cpu_usage']:
                avg_cpu = statistics.mean(self.results['cpu_usage'])
                max_cpu = max(self.results['cpu_usage'])
                f.write(f"USO DE RECURSOS:\n")
                f.write(f"  CPU média: {avg_cpu:.1f}%\n")
                f.write(f"  CPU máxima: {max_cpu:.1f}%\n")
            
            if self.results['memory_usage']:
                avg_memory = statistics.mean(self.results['memory_usage'])
                max_memory = max(self.results['memory_usage'])
                f.write(f"  Memória média: {avg_memory:.1f}%\n")
                f.write(f"  Memória máxima: {max_memory:.1f}%\n\n")
            
            # Análise e Recomendações
            f.write("ANÁLISE DOS RESULTADOS:\n")
            f.write("-" * 40 + "\n")
            
            if self.results['latency']:
                avg_latency = statistics.mean(self.results['latency'])
                if avg_latency < 100:
                    f.write("✅ Latência EXCELENTE (< 100ms)\n")
                elif avg_latency < 200:
                    f.write("🟡 Latência BOA (100-200ms)\n")
                else:
                    f.write("🔴 Latência ALTA (> 200ms) - Otimização necessária\n")
            
            if total_connections > 0:
                if success_rate > 95:
                    f.write("✅ Taxa de conexão EXCELENTE (> 95%)\n")
                elif success_rate > 85:
                    f.write("🟡 Taxa de conexão BOA (85-95%)\n")
                else:
                    f.write("🔴 Taxa de conexão BAIXA (< 85%) - Investigação necessária\n")
            
            if self.results['cpu_usage']:
                if avg_cpu < 70:
                    f.write("✅ Uso de CPU SUSTENTÁVEL (< 70%)\n")
                elif avg_cpu < 85:
                    f.write("🟡 Uso de CPU MODERADO (70-85%)\n")
                else:
                    f.write("🔴 Uso de CPU ALTO (> 85%) - Otimização recomendada\n")
            
            f.write("\nDETALHES DA EXECUÇÃO:\n")
            f.write("-" * 40 + "\n")
            for line in self.test_report:
                f.write(line + "\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("Relatório gerado automaticamente pelo Performance Test\n")
            f.write("=" * 80 + "\n")
        
        self.add_to_report(f"📄 Relatório salvo em: {filename}")
        return filepath
    
    def test_latency(self, num_tests=100):
        """Testa a latência de comunicação com o servidor"""
        self.add_to_report(f"🧪 Iniciando teste de latência com {num_tests} requests...")
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
                    self.add_to_report(f"  Progresso: {i}/{num_tests} - Latência atual: {latency:.2f}ms")
                
            except Exception as e:
                self.add_to_report(f"  ❌ Erro na iteração {i}: {e}")
                continue
        
        self.results['latency'] = latencies
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            median_latency = statistics.median(latencies)
            
            self.add_to_report(f"📊 Resultados de Latência:")
            self.add_to_report(f"  Média: {avg_latency:.2f}ms")
            self.add_to_report(f"  Mediana: {median_latency:.2f}ms")
            self.add_to_report(f"  Mín: {min_latency:.2f}ms")
            self.add_to_report(f"  Máx: {max_latency:.2f}ms")
            self.add_to_report(f"  Testes realizados: {len(latencies)}/{num_tests}")
        
        # Salvar relatório específico de latência
        self.save_report_to_file("latencia")
    
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
        
        # Salvar no diretório de relatórios
        report_path = os.path.join(REPORTS_DIR, 'performance_report.png')
        os.makedirs(REPORTS_DIR, exist_ok=True)
        plt.savefig(report_path, dpi=300, bbox_inches='tight')
        print(f"  Relatório salvo como '{report_path}'")
        plt.show()
    
    def run_full_test_suite(self):
        """Executa todos os testes de performance"""
        self.add_to_report("🚀 Iniciando suite completa de testes de performance...")
        self.add_to_report("=" * 60)
        
        # Teste de latência
        self.test_latency(50)
        self.add_to_report("")
        
        # Teste de conexões simultâneas
        self.test_concurrent_connections(20, 15)
        self.add_to_report("")
        
        # Teste de stress
        self.stress_test(10, 60)
        self.add_to_report("")
        
        # Gerar relatório
        self.generate_report()
        
        # Salvar relatório completo
        self.save_report_to_file("suite_completa")
        
        self.add_to_report("✅ Todos os testes concluídos!")


if __name__ == "__main__":
    # Configurar teste
    tester = PerformanceTest()
    
    print("Pong Socket Game - Testes de Performance e Estabilidade")
    print("=" * 60)
    print(f"Servidor configurado: {SERVER_HOST}:{SERVER_PORT}")
    print("IMPORTANTE: Certifique-se de que o servidor está rodando!")
    print()
    
    input("Pressione Enter para começar os testes...")
    
    # Executar testes
    tester.run_full_test_suite()
