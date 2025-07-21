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
import pygame
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar configurações
from config import SERVER_HOST, SERVER_PORT, REPORTS_DIR

# Inicializar pygame para criar Rect objects
pygame.init()

class StabilityTest:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
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
        self.results_lock = threading.Lock()  # Proteção contra race conditions
        self.test_report = []  # Lista para armazenar relatório detalhado
    
    def add_to_report(self, message):
        """Adiciona uma linha ao relatório"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.test_report.append(f"[{timestamp}] {message}")
        print(message)  # Também exibe no console
    
    def save_report_to_file(self, test_type="stability"):
        """Salva o relatório em arquivo TXT"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_stability_{test_type}_{timestamp}.txt"
        
        # Criar diretório de relatórios se não existir
        os.makedirs(REPORTS_DIR, exist_ok=True)
        filepath = os.path.join(REPORTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("              RELATÓRIO DE ESTABILIDADE - PONG SOCKETS\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Tipo de Teste: {test_type.upper()}\n")
            f.write(f"Servidor: {self.host}:{self.port}\n\n")
            
            f.write("MÉTRICAS DE ESTABILIDADE:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Duração do teste: {self.results['test_duration']:.2f}s\n")
            f.write(f"Conexões totais: {self.results['total_connections']}\n")
            f.write(f"Conexões bem-sucedidas: {self.results['successful_connections']}\n")
            f.write(f"Conexões falhadas: {self.results['failed_connections']}\n")
            f.write(f"Desconexões: {self.results['disconnections']}\n")
            f.write(f"Crashes detectados: {self.results['server_crashes']}\n")
            
            if self.results['total_connections'] > 0:
                success_rate = (self.results['successful_connections'] / self.results['total_connections']) * 100
                f.write(f"Taxa de sucesso: {success_rate:.1f}%\n")
            
            f.write("\nANÁLISE DE ESTABILIDADE:\n")
            f.write("-" * 40 + "\n")
            
            # Análise da taxa de sucesso
            if self.results['total_connections'] > 0:
                if success_rate > 95:
                    f.write("✅ ESTABILIDADE EXCELENTE (> 95% sucesso)\n")
                elif success_rate > 85:
                    f.write("🟡 ESTABILIDADE BOA (85-95% sucesso)\n")
                else:
                    f.write("🔴 ESTABILIDADE BAIXA (< 85% sucesso)\n")
            
            # Análise de crashes
            if self.results['server_crashes'] == 0:
                f.write("✅ ROBUSTEZ EXCELENTE (sem crashes detectados)\n")
            elif self.results['server_crashes'] < 3:
                f.write("🟡 ROBUSTEZ MODERADA (poucos crashes)\n")
            else:
                f.write("🔴 ROBUSTEZ BAIXA (múltiplos crashes detectados)\n")
            
            # Análise de erros
            if self.results['connection_errors']:
                f.write(f"\nTIPOS DE ERRO MAIS COMUNS:\n")
                error_types = {}
                for error in self.results['connection_errors'][:20]:
                    error_type = error.split(':')[0] if ':' in error else error[:50]
                    error_types[error_type] = error_types.get(error_type, 0) + 1
                
                for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                    f.write(f"  • {error_type}: {count} ocorrências\n")
            
            f.write("\nDETALHES DA EXECUÇÃO:\n")
            f.write("-" * 40 + "\n")
            for line in self.test_report:
                f.write(line + "\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("Relatório gerado automaticamente pelo Stability Test\n")
            f.write("=" * 80 + "\n")
        
        self.add_to_report(f"📄 Relatório salvo em: {filename}")
        return filepath
    
    def _follow_server_protocol(self, sock, client_name="TestClient"):
        """Segue o protocolo correto do servidor"""
        try:
            # 1. Receber player_id do servidor
            player_id_data = sock.recv(2048)
            if not player_id_data:
                return False
            player_id = pickle.loads(player_id_data)
            
            # 2. Enviar nome do jogador
            sock.send(pickle.dumps(client_name))
            
            return True
        except Exception as e:
            return False
    
    def test_connection_stability(self, duration=300):
        """Testa a estabilidade das conexões ao longo do tempo"""
        self.add_to_report(f"🔒 Iniciando teste de estabilidade das conexões por {duration}s...")
        
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
                    
                    # Seguir protocolo correto do servidor
                    client_name = f"TestClient{client_id}"
                    if not self._follow_server_protocol(sock, client_name):
                        raise Exception("Falha no protocolo inicial")
                    
                    with self.results_lock:
                        self.results['successful_connections'] += 1
                    
                    self.add_to_report(f"✅ Cliente {client_id} conectado com sucesso")
                    
                    # Manter conexão por um tempo aleatório (30-120s)
                    connection_duration = random.randint(30, 120)
                    connection_end = time.time() + connection_duration
                    
                    # Simular movimento da raquete
                    paddle_x = 480  # Centro da tela
                    
                    while time.time() < connection_end and time.time() - start_time < duration:
                        try:
                            # Receber estado do jogo
                            game_state_data = sock.recv(2048)
                            if not game_state_data:
                                break
                            
                            game_state = pickle.loads(game_state_data)
                            
                            # Enviar posição da raquete (simular movimento)
                            paddle_x += random.randint(-20, 20)
                            paddle_x = max(60, min(900, paddle_x))  # Limites da tela
                            
                            paddle_rect = pygame.Rect(paddle_x - 60, 20, 120, 10)
                            sock.send(pickle.dumps(paddle_rect))
                            
                            time.sleep(random.uniform(0.1, 0.5))
                            
                        except Exception as e:
                            self.add_to_report(f"❌ Erro no loop do jogo (Cliente {client_id}): {e}")
                            disconnections += 1
                            break
                    
                    sock.close()
                    
                    # Pausa antes de reconectar
                    time.sleep(random.uniform(2, 10))
                    
                except Exception as e:
                    with self.results_lock:
                        self.results['failed_connections'] += 1
                        self.results['connection_errors'].append(str(e))
                    disconnections += 1
                    self.add_to_report(f"❌ Cliente {client_id} falhou: {e}")
                    time.sleep(5)  # Pausa maior em caso de erro
            
            with self.results_lock:
                self.results['disconnections'] += disconnections
        
        # Simular vários clientes conectando/desconectando
        num_clients = 10  # Reduzido para evitar sobrecarga
        with ThreadPoolExecutor(max_workers=num_clients) as executor:
            futures = [executor.submit(maintain_connection, i) for i in range(num_clients)]
            
            for future in futures:
                future.result()
        
        with self.results_lock:
            self.results['total_connections'] = (self.results['successful_connections'] + 
                                               self.results['failed_connections'])
        
        success_rate = 0
        if self.results['total_connections'] > 0:
            success_rate = (self.results['successful_connections'] / 
                           self.results['total_connections']) * 100
        
        self.add_to_report(f"📊 Resultados do Teste de Estabilidade:")
        self.add_to_report(f"  Duração: {duration}s")
        self.add_to_report(f"  Conexões totais: {self.results['total_connections']}")
        self.add_to_report(f"  Conexões bem-sucedidas: {self.results['successful_connections']}")
        self.add_to_report(f"  Conexões falhadas: {self.results['failed_connections']}")
        self.add_to_report(f"  Taxa de sucesso: {success_rate:.1f}%")
        self.add_to_report(f"  Desconexões: {self.results['disconnections']}")
        
        # Salvar relatório específico
        self.save_report_to_file("conexoes")
    
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
                
                # Seguir protocolo básico
                client_name = f"QuickTest{i}"
                if self._follow_server_protocol(sock, client_name):
                    successful += 1
                else:
                    failed += 1
                
                sock.close()
                
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
                for _ in range(5):  # Reduzido para 5 conexões por vez
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1.0)
                    sock.connect((self.host, self.port))
                    
                    # Seguir protocolo básico
                    client_name = f"MemTest{connection_count}"
                    if self._follow_server_protocol(sock, client_name):
                        # Enviar algumas posições de raquete
                        for _ in range(3):
                            paddle_rect = pygame.Rect(400, 20, 120, 10)
                            sock.send(pickle.dumps(paddle_rect))
                            
                            # Tentar receber estado do jogo
                            try:
                                sock.recv(2048)
                            except:
                                pass
                            
                            time.sleep(0.01)
                    
                    sock.close()
                    connection_count += 1
                
                if connection_count % 50 == 0:
                    elapsed = time.time() - start_time
                    print(f"  {connection_count} conexões criadas em {elapsed:.1f}s")
                
                time.sleep(0.2)  # Pausa maior entre lotes
                
            except Exception as e:
                print(f"  Erro no teste de memória: {e}")
                time.sleep(1)
        
        print(f"📊 Teste de Memória Concluído:")
        print(f"  Conexões criadas: {connection_count}")
        print(f"  Duração: {duration}s")
        print(f"  Conexões por segundo: {connection_count / duration:.1f}")
    
    def run_stability_suite(self):
        """Executa todos os testes de estabilidade"""
        self.add_to_report("🛡️  Iniciando suite de testes de estabilidade...")
        self.add_to_report("=" * 60)
        
        try:
            # Teste de conexões rápidas
            self.test_rapid_connections(100)
            self.add_to_report("")
            
            # Teste de dados malformados
            self.test_malformed_data(30)
            self.add_to_report("")
            
            # Teste de vazamento de memória
            self.test_memory_leak(120)
            self.add_to_report("")
            
            # Teste de estabilidade de longo prazo
            self.test_connection_stability(180)
            self.add_to_report("")
            
        except KeyboardInterrupt:
            self.add_to_report("⚠️  Testes interrompidos pelo usuário")
        
        self.add_to_report("✅ Suite de estabilidade concluída!")
        self.print_summary()
        
        # Salvar relatório completo
        self.save_report_to_file("suite_completa")
    
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
    tester = StabilityTest()
    
    print("Pong Socket Game - Testes de Estabilidade")
    print("=" * 60)
    print(f"Servidor configurado: {SERVER_HOST}:{SERVER_PORT}")
    print("IMPORTANTE: Certifique-se de que o servidor está rodando!")
    print("Estes testes vão testar a robustez do servidor.")
    print()
    
    input("Pressione Enter para começar os testes de estabilidade...")
    
    # Executar testes
    tester.run_stability_suite()
