#!/usr/bin/env python3
"""
Teste de Estabilidade para Pong Socket Game
Testa a estabilidade do servidor sob diferentes condições de stress
"""

import socket
import threading
import time
import pickle
import os
import sys
import random
from concurrent.futures import ThreadPoolExecutor

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class StabilityTest:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.results = {
            'total_connections': 0,
            'failed_connections': 0,
            'successful_connections': 0,
            'connection_errors': [],
            'test_duration': 0,
            'disconnections': 0,
            'server_crashes': 0
        }
    
    def test_connection_stability(self, duration=300):
        """Testa a estabilidade das conexões ao longo do tempo"""
        print(f"🔒 Testando estabilidade das conexões por {duration}s...")
        
        start_time = time.time()
        self.results['test_duration'] = duration
        
        def maintain_connection(client_id):
            connection_start = time.time()
            disconnections = 0
            
            while time.time() - start_time < duration:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10.0)
                    sock.connect((self.host, self.port))
                    
                    self.results['successful_connections'] += 1
                    
                    # Manter conexão por um tempo aleatório (30-120s)
                    connection_duration = random.randint(30, 120)
                    connection_end = time.time() + connection_duration
                    
                    while time.time() < connection_end and time.time() - start_time < duration:
                        try:
                            # Enviar heartbeat
                            data = {
                                'type': 'heartbeat',
                                'client_id': client_id,
                                'timestamp': time.time()
                            }
                            sock.sendall(pickle.dumps(data))
                            time.sleep(random.uniform(1, 3))
                            
                        except Exception as e:
                            print(f"  Erro no heartbeat (Cliente {client_id}): {e}")
                            disconnections += 1
                            break
                    
                    sock.close()
                    
                    # Pausa antes de reconectar
                    time.sleep(random.uniform(2, 10))
                    
                except Exception as e:
                    self.results['failed_connections'] += 1
                    self.results['connection_errors'].append(str(e))
                    disconnections += 1
                    time.sleep(5)  # Pausa maior em caso de erro
            
            self.results['disconnections'] += disconnections
        
        # Simular vários clientes conectando/desconectando
        num_clients = 15
        with ThreadPoolExecutor(max_workers=num_clients) as executor:
            futures = [executor.submit(maintain_connection, i) for i in range(num_clients)]
            
            for future in futures:
                future.result()
        
        self.results['total_connections'] = (self.results['successful_connections'] + 
                                           self.results['failed_connections'])
        
        success_rate = 0
        if self.results['total_connections'] > 0:
            success_rate = (self.results['successful_connections'] / 
                           self.results['total_connections']) * 100
        
        print(f"📊 Resultados do Teste de Estabilidade:")
        print(f"  Duração: {duration}s")
        print(f"  Conexões totais: {self.results['total_connections']}")
        print(f"  Conexões bem-sucedidas: {self.results['successful_connections']}")
        print(f"  Conexões falhadas: {self.results['failed_connections']}")
        print(f"  Taxa de sucesso: {success_rate:.1f}%")
        print(f"  Desconexões: {self.results['disconnections']}")
    
    def test_rapid_connections(self, num_attempts=200):
        """Testa conexões rápidas e sucessivas"""
        print(f"⚡ Testando {num_attempts} conexões rápidas...")
        
        successful = 0
        failed = 0
        
        for i in range(num_attempts):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2.0)
                sock.connect((self.host, self.port))
                
                # Enviar dados básicos
                data = {'type': 'quick_test', 'iteration': i}
                sock.sendall(pickle.dumps(data))
                
                sock.close()
                successful += 1
                
                if i % 20 == 0:
                    print(f"  Progress: {i}/{num_attempts}")
                
            except Exception as e:
                failed += 1
                if i < 10:  # Mostrar apenas os primeiros erros
                    print(f"  Erro na iteração {i}: {e}")
            
            # Pequena pausa para não sobrecarregar
            time.sleep(0.01)
        
        success_rate = (successful / num_attempts) * 100
        print(f"📊 Resultados de Conexões Rápidas:")
        print(f"  Sucessos: {successful}")
        print(f"  Falhas: {failed}")
        print(f"  Taxa de sucesso: {success_rate:.1f}%")
    
    def test_malformed_data(self, num_tests=50):
        """Testa envio de dados malformados para verificar robustez"""
        print(f"🔧 Testando robustez com {num_tests} dados malformados...")
        
        malformed_data = [
            b"dados_nao_pickle",
            b"",
            b"x" * 10000,  # Dados muito grandes
            pickle.dumps({"tipo_invalido": "teste"}),
            pickle.dumps(None),
            pickle.dumps([1, 2, 3, 4, 5]),
            b"\x00\x01\x02\x03",  # Bytes aleatórios
        ]
        
        server_crashes = 0
        handled_gracefully = 0
        
        for i in range(num_tests):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5.0)
                sock.connect((self.host, self.port))
                
                # Escolher dados malformados aleatórios
                bad_data = random.choice(malformed_data)
                sock.sendall(bad_data)
                
                # Tentar receber resposta
                try:
                    response = sock.recv(1024)
                    handled_gracefully += 1
                except:
                    pass  # Servidor pode não responder para dados inválidos
                
                sock.close()
                
            except ConnectionRefusedError:
                server_crashes += 1
                print(f"  🚨 Servidor pode ter crashado na iteração {i}")
                time.sleep(2)  # Dar tempo para o servidor se recuperar
                
            except Exception as e:
                if i < 5:  # Mostrar apenas os primeiros erros
                    print(f"  Erro esperado na iteração {i}: {type(e).__name__}")
        
        self.results['server_crashes'] = server_crashes
        
        print(f"📊 Resultados do Teste de Robustez:")
        print(f"  Tratados graciosamente: {handled_gracefully}")
        print(f"  Possíveis crashes do servidor: {server_crashes}")
        print(f"  Taxa de robustez: {((num_tests - server_crashes) / num_tests) * 100:.1f}%")
    
    def test_memory_leak(self, duration=180):
        """Simula operações para detectar vazamentos de memória"""
        print(f"🧠 Testando vazamentos de memória por {duration}s...")
        
        start_time = time.time()
        connection_count = 0
        
        while time.time() - start_time < duration:
            try:
                # Criar e fechar conexões rapidamente
                for _ in range(10):
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1.0)
                    sock.connect((self.host, self.port))
                    
                    # Enviar dados variados
                    data = {
                        'type': 'memory_test',
                        'data': 'x' * random.randint(100, 1000),
                        'timestamp': time.time()
                    }
                    sock.sendall(pickle.dumps(data))
                    sock.close()
                    connection_count += 1
                
                if connection_count % 100 == 0:
                    elapsed = time.time() - start_time
                    print(f"  {connection_count} conexões criadas em {elapsed:.1f}s")
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  Erro no teste de memória: {e}")
                time.sleep(1)
        
        print(f"📊 Teste de Memória Concluído:")
        print(f"  Conexões criadas: {connection_count}")
        print(f"  Duração: {duration}s")
        print(f"  Conexões por segundo: {connection_count / duration:.1f}")
    
    def run_stability_suite(self):
        """Executa todos os testes de estabilidade"""
        print("🛡️  Iniciando suite de testes de estabilidade...")
        print("=" * 60)
        
        try:
            # Teste de conexões rápidas
            self.test_rapid_connections(100)
            print()
            
            # Teste de dados malformados
            self.test_malformed_data(30)
            print()
            
            # Teste de vazamento de memória
            self.test_memory_leak(120)
            print()
            
            # Teste de estabilidade de longo prazo
            self.test_connection_stability(180)
            print()
            
        except KeyboardInterrupt:
            print("\n⚠️  Testes interrompidos pelo usuário")
        
        print("✅ Suite de estabilidade concluída!")
        self.print_summary()
    
    def print_summary(self):
        """Imprime resumo dos resultados"""
        print("\n" + "=" * 60)
        print("📋 RESUMO DOS TESTES DE ESTABILIDADE")
        print("=" * 60)
        
        if self.results['total_connections'] > 0:
            success_rate = (self.results['successful_connections'] / 
                           self.results['total_connections']) * 100
            print(f"Taxa geral de sucesso: {success_rate:.1f}%")
        
        print(f"Crashes detectados: {self.results['server_crashes']}")
        print(f"Desconexões: {self.results['disconnections']}")
        
        if self.results['connection_errors']:
            print(f"Tipos de erro mais comuns:")
            error_types = {}
            for error in self.results['connection_errors'][:10]:  # Primeiros 10
                error_type = error.split(':')[0] if ':' in error else error
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in sorted(error_types.items(), 
                                          key=lambda x: x[1], reverse=True):
                print(f"  - {error_type}: {count} ocorrências")


if __name__ == "__main__":
    # Configurar teste
    tester = StabilityTest(host='localhost', port=5000)
    
    print("Pong Socket Game - Testes de Estabilidade")
    print("=" * 60)
    print("IMPORTANTE: Certifique-se de que o servidor está rodando!")
    print("Estes testes vão testar a robustez do servidor.")
    print()
    
    input("Pressione Enter para começar os testes de estabilidade...")
    
    # Executar testes
    tester.run_stability_suite()
