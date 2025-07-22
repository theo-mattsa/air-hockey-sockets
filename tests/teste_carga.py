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
from config import SERVER_HOST, SERVER_PORT, REPORTS_DIR, DEFAULT_MAX_CLIENTS, DEFAULT_STEP, DEFAULT_STEP_DURATION

# Importar pygame para usar Rect (protocolo real do jogo)
try:
    import pygame
    pygame.init()  # Inicializar pygame sem display
    PYGAME_AVAILABLE = True
except ImportError:
    print("⚠️  Pygame não encontrado. Usando simulação simplificada.")
    PYGAME_AVAILABLE = False

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
        """Simula uma sessão real do jogo Pong"""
        print(f"🎮 Cliente {self.client_id} iniciando sessão de {duration}s")
        
        # Medir tempo de conexão
        connection_start = time.time()
        if not self.connect():
            return False, 0, 0, 0  # success, messages_sent, messages_received, connection_time
        connection_time = time.time() - connection_start
        
        start_time = time.time()
        messages_sent = 0
        messages_received = 0
        player_id = None
        
        try:
            # 1. PROTOCOLO REAL: Receber player_id do servidor (0 ou 1)
            player_id_data = self.socket.recv(2048)
            if player_id_data:
                player_id = pickle.loads(player_id_data)
                print(f"👤 Cliente {self.client_id} é jogador {player_id + 1}")
            
            # 2. PROTOCOLO REAL: Enviar nome do jogador (formato correto)
            self.socket.send(pickle.dumps(self.player_name))
            print(f"📝 Nome enviado: {self.player_name}")
            
            # 3. Loop principal seguindo o protocolo real
            while self.connected and time.time() - start_time < duration:
                try:
                    # Primeiro: RECEBER estado do jogo do servidor
                    data = self.socket.recv(4096)
                    if data:
                        game_state = pickle.loads(data)
                        messages_received += 1
                    
                    # Segundo: ENVIAR posição do paddle
                    paddle_x = random.randint(100, 860)
                    
                    if PYGAME_AVAILABLE and player_id is not None:
                        # Usar pygame.Rect como o cliente real
                        paddle_y = 580 if player_id == 0 else 20  # Player 1 embaixo, Player 2 em cima
                        my_paddle = pygame.Rect(paddle_x, paddle_y, 120, 10)
                        self.socket.send(pickle.dumps(my_paddle))
                    else:
                        # Fallback: simular estrutura similar
                        paddle_data = {
                            'x': paddle_x,
                            'y': 580 if player_id == 0 else 20,
                            'width': 120,
                            'height': 10
                        }
                        self.socket.send(pickle.dumps(paddle_data))
                    
                    messages_sent += 1
                    
                    # Simular FPS do jogo (60 FPS)
                    time.sleep(1/60)
                    
                except Exception as e:
                    if self.connected:
                        print(f"❌ Erro na comunicação (Cliente {self.client_id}): {e}")
                    break
            
        except Exception as e:
            print(f"❌ Erro no protocolo inicial (Cliente {self.client_id}): {e}")
            return False, 0, 0, connection_time
        
        finally:
            if self.socket:
                self.socket.close()
            self.connected = False
        
        print(f"📊 Cliente {self.client_id} (Jogador {player_id + 1 if player_id is not None else '?'}) - Mensagens enviadas: {messages_sent}, recebidas: {messages_received}")
        return True, messages_sent, messages_received, connection_time


class LoadTestManager:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.results = {
            'successful_clients': 0,
            'failed_clients': 0,
            'total_messages': 0,
            'test_duration': 0,
            'total_steps': 0,
            'step_times': [],  # Duração de cada etapa
            'connection_times': [],  # Tempos de conexão
            'step_details': []  # Detalhes de cada etapa
        }
        self.test_start_time = None
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
        
        # Criar diretório se não existir
        os.makedirs(REPORTS_DIR, exist_ok=True)
        filepath = os.path.join(REPORTS_DIR, filename)
        
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
            
            # Métricas de performance
            total_clients = self.results['successful_clients'] + self.results['failed_clients']
            total_games = self.results['successful_clients'] // 2
            
            if total_clients > 0:
                success_rate = (self.results['successful_clients'] / total_clients) * 100
                f.write(f"Taxa de sucesso: {success_rate:.1f}%\n")
            
            f.write(f"Total de jogos formados: {total_games}\n")
            
            if self.results['test_duration'] > 0:
                if self.results['total_messages'] > 0:
                    throughput = self.results['total_messages'] / self.results['test_duration']
                    f.write(f"Throughput: {throughput:.1f} mensagens/segundo\n")
                
                if total_games > 0:
                    games_throughput = total_games / self.results['test_duration']
                    f.write(f"Taxa de jogos: {games_throughput:.2f} jogos/segundo\n")
            
            f.write("\nDETALHES DA EXECUÇÃO:\n")
            f.write("-" * 40 + "\n")
            for line in self.test_report:
                f.write(line + "\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("Relatório gerado automaticamente pelo Client Simulator\n")
            f.write("=" * 80 + "\n")
        
        self.add_to_report(f"📄 Relatório salvo em: {filename}")
        return filepath
    
    def run_gradual_load_test(self, max_clients=50, step=5, step_duration=30):
        """Teste de carga gradual com protocolo real do Pong"""
        # Inicializar tempo do teste
        self.test_start_time = time.time()
        
        # Garantir números pares (cada jogo precisa de 2 jogadores)
        if max_clients % 2 != 0:
            max_clients += 1
            self.add_to_report(f"📝 Ajustado max_clients para {max_clients} (números pares para jogos 1v1)")
        
        if step % 2 != 0:
            step += 1
            self.add_to_report(f"� Ajustado step para {step} (números pares para jogos 1v1)")
        
        self.add_to_report(f"🎮 Iniciando teste de carga gradual REAL: 0 até {max_clients} clientes ({max_clients//2} jogos simultâneos)...")
        
        for num_clients in range(step, max_clients + 1, step):
            num_games = num_clients // 2
            self.add_to_report(f"🔄 Testando {num_clients} clientes ({num_games} jogos simultâneos)...")
            
            # Reset results for this step
            step_results = {
                'successful_clients': 0,
                'failed_clients': 0,
                'total_messages': 0
            }
            
            def client_worker(client_id):
                simulator = GameClientSimulator(self.host, self.port, client_id)
                success, msg_sent, msg_received, _ = simulator.simulate_game_session(step_duration)
                
                if success:
                    step_results['successful_clients'] += 1
                    step_results['total_messages'] += (msg_sent + msg_received)
                else:
                    step_results['failed_clients'] += 1
            
            threads = []
            for i in range(num_clients):
                thread = threading.Thread(target=client_worker, args=(f"pong_{num_clients}_{i}",))
                threads.append(thread)
                thread.start()
                time.sleep(0.1)  # Pequeno delay para formar pares
            
            for thread in threads:
                thread.join()
            
            # Calcular métricas de performance
            success_rate = (step_results['successful_clients'] / num_clients) * 100
            successful_games = step_results['successful_clients'] // 2
            
            # Métricas simples de performance
            messages_per_second = step_results['total_messages'] / step_duration if step_duration > 0 else 0
            games_per_second = successful_games / step_duration if step_duration > 0 else 0
            game_formation_rate = (successful_games / num_games) * 100 if num_games > 0 else 0
            
            self.add_to_report(f"  📊 {num_clients} clientes: {success_rate:.1f}% sucesso")
            self.add_to_report(f"  🎮 {successful_games} jogos formados ({game_formation_rate:.1f}% dos {num_games} possíveis)")
            self.add_to_report(f"  📈 Performance: {messages_per_second:.1f} msg/s, {games_per_second:.2f} jogos/s")
            
            # Atualizar resultados globais
            self.results['successful_clients'] += step_results['successful_clients']
            self.results['failed_clients'] += step_results['failed_clients']
            self.results['total_messages'] += step_results['total_messages']
            
            # Se a taxa de sucesso cair muito, parar o teste
            if success_rate < 50:
                self.add_to_report(f"⚠️  Taxa de sucesso muito baixa ({success_rate:.1f}%), parando o teste")
                break
            
            time.sleep(2)  # Pausa entre steps
        
        # Calcular duração total do teste
        self.results['test_duration'] = time.time() - self.test_start_time
        
        # Estatísticas finais
        total_games_attempted = self.results['successful_clients'] // 2
        self.add_to_report(f"🎮 Total de jogos formados: {total_games_attempted}")
        
        # Métricas finais de performance
        if self.results['test_duration'] > 0:
            overall_throughput = self.results['total_messages'] / self.results['test_duration']
            overall_games_rate = total_games_attempted / self.results['test_duration']
            self.add_to_report(f"📈 Performance geral: {overall_throughput:.1f} msg/s, {overall_games_rate:.2f} jogos/s")
        
        # Salvar relatório
        self.save_report_to_file("teste_carga_gradual_real")


def main():
    print("🎮 Pong Socket Game - Teste de Carga Gradual REAL")
    print("=" * 60)
    
    manager = LoadTestManager()
    
    print(f"Servidor configurado: {SERVER_HOST}:{SERVER_PORT}")
    if PYGAME_AVAILABLE:
        print("✅ Pygame disponível - Usando protocolo real do jogo")
    else:
        print("⚠️  Pygame não encontrado - Usando simulação simplificada")
    print("IMPORTANTE: Certifique-se de que o servidor está rodando!")
    print()
    print("Configuração do teste de carga gradual (jogos 1v1):")
    
    try:
        max_clients = int(input(f"Máximo de clientes (padrão {DEFAULT_MAX_CLIENTS}): ") or str(DEFAULT_MAX_CLIENTS))
        step = int(input(f"Incremento por etapa (padrão {DEFAULT_STEP}): ") or str(DEFAULT_STEP))
        step_duration = int(input(f"Duração de cada etapa em segundos (padrão {DEFAULT_STEP_DURATION}): ") or str(DEFAULT_STEP_DURATION))
        
        print(f"\n🚀 Iniciando teste: 0 até {max_clients} clientes, incremento de {step}, {step_duration}s por etapa")
        print("Pressione Ctrl+C para interromper o teste\n")
        
        manager.run_gradual_load_test(max_clients, step, step_duration)
    
    except KeyboardInterrupt:
        print("\n⚠️  Teste interrompido pelo usuário")
    except ValueError:
        print("❌ Valores inválidos. Executando teste com configuração padrão...")
        manager.run_gradual_load_test(DEFAULT_MAX_CLIENTS, DEFAULT_STEP, DEFAULT_STEP_DURATION)


if __name__ == "__main__":
    main()
