import socket
import threading
import time
import pickle
import random
import os
import sys
from datetime import datetime

# Importações para Análise e Gráficos 
import psutil
import matplotlib.pyplot as plt

# Configuração Inicial
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import SERVER_HOST, SERVER_PORT, REPORTS_DIR, DEFAULT_MAX_CLIENTS, DEFAULT_STEP, DEFAULT_STEP_DURATION
except ImportError:
    print("AVISO: Não foi possível encontrar o arquivo 'config.py'. Usando valores padrão.")
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 65432
    REPORTS_DIR = "reports"
    DEFAULT_MAX_CLIENTS = 50
    DEFAULT_STEP = 10
    DEFAULT_STEP_DURATION = 30


# Importar e inicializar pygame (se disponível)
try:
    import pygame
    pygame.init()
    PYGAME_AVAILABLE = True
except ImportError:
    print("Pygame não encontrado. Usando simulação de dados simplificada.")
    PYGAME_AVAILABLE = False

# Classe de simulação de cliente
class GameClientSimulator:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT, client_id=None):
        self.host = host
        self.port = port
        self.client_id = client_id or f"bot_{random.randint(1000, 9999)}"
        self.connected = False
        self.socket = None
        self.player_name = f"TestBot_{self.client_id}"

    def connect(self):
        """Tenta conectar o cliente ao servidor."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            self.socket.connect((self.host, self.port))
            self.connected = True
            return True
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            return False

    def simulate_game_session(self, duration=60):
        """Simula uma sessão completa de jogo, seguindo o protocolo."""
        if not self.connect():
            return False, 0, 0

        start_time = time.time()
        messages_sent = 0
        messages_received = 0
        player_id = None

        try:
            #  Receber ID do jogador
            player_id_data = self.socket.recv(2048)
            if player_id_data:
                player_id = pickle.loads(player_id_data)

            # Enviar nome do jogador
            self.socket.send(pickle.dumps(self.player_name))

            # Loop principal de jogo
            while self.connected and time.time() - start_time < duration:
                # Receber estado do jogo
                data = self.socket.recv(4096)
                if not data: break
                game_state = pickle.loads(data)
                messages_received += 1

                # Enviar posição do paddle (simulada)
                paddle_x = random.randint(100, 860)
                if PYGAME_AVAILABLE and player_id is not None:
                    paddle_y = 580 if player_id == 0 else 20
                    my_paddle = pygame.Rect(paddle_x, paddle_y, 120, 10)
                    self.socket.send(pickle.dumps(my_paddle))
                else:
                    paddle_data = {'x': paddle_x, 'y': 580 if player_id == 0 else 20}
                    self.socket.send(pickle.dumps(paddle_data))
                messages_sent += 1

                time.sleep(1/60) # 60 FPS

        except (pickle.UnpicklingError, ConnectionAbortedError, ConnectionResetError):
            self.connected = False
        finally:
            if self.socket:
                self.socket.close()
            self.connected = False

        return True, messages_sent, messages_received


# Classe gerenciadora do teste de carga 
class LoadTestManager:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.results = {
            'successful_clients': 0,
            'failed_clients': 0,
            'test_duration': 0,
            'step_details': []
        }
        self.test_start_time = None
        self.test_report = []
        self.monitoring_active = False

    def add_to_report(self, message):
        """Adiciona uma mensagem ao log do teste."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.test_report.append(f"[{timestamp}] {message}")
        print(message)

    def generate_performance_graphs(self, test_type="simulation"):
        """Gera e salva gráficos de performance com os resultados do teste."""
        if not self.results['step_details']:
            self.add_to_report("Nenhum dado de etapa foi coletado, pulando a geração de gráficos.")
            return

        clients = [d['num_clients'] for d in self.results['step_details']]
        avg_cpu = [d['avg_cpu'] for d in self.results['step_details']]
        max_cpu = [d['max_cpu'] for d in self.results['step_details']]
        avg_mem = [d['avg_mem'] for d in self.results['step_details']]
        success_rate = [d['success_rate'] for d in self.results['step_details']]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        fig.suptitle(f'Análise de Performance - Teste de Carga ({test_type.replace("_", " ").title()})', fontsize=16)

        ax1.plot(clients, avg_cpu, 'o-', label='CPU Média (%)', color='royalblue')
        ax1.plot(clients, max_cpu, 's--', label='CPU Pico (%)', color='darkorange', alpha=0.8)
        ax1.plot(clients, avg_mem, '^-', label='Memória Média (%)', color='forestgreen')
        ax1.set_ylabel("Uso de Recurso (%)")
        ax1.set_title("Consumo de Recursos vs. Clientes Simultâneos")
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.6)

        ax2.plot(clients, success_rate, 'o-', label='Taxa de Sucesso', color='crimson')
        ax2.set_xlabel("Número de Clientes Simultâneos")
        ax2.set_ylabel("Taxa de Sucesso (%)")
        ax2.set_title("Estabilidade do Servidor vs. Clientes Simultâneos")
        ax2.set_ylim(0, 105)
        ax2.grid(True, linestyle='--', alpha=0.6)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"grafico_performance_{test_type}_{timestamp}.png"
        os.makedirs(REPORTS_DIR, exist_ok=True)
        filepath = os.path.join(REPORTS_DIR, filename)
        
        plt.savefig(filepath)
        plt.close(fig)
        self.add_to_report(f"Gráfico de performance salvo em: {filepath}")

    def save_report_to_file(self, test_type="simulation"):
        """Salva o relatório de texto detalhado."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_client_simulator_{test_type}_{timestamp}.txt"
        os.makedirs(REPORTS_DIR, exist_ok=True)
        filepath = os.path.join(REPORTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\nRELATÓRIO DE SIMULAÇÃO DE CLIENTES\n" + "="*80 + "\n\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Servidor Alvo: {self.host}:{self.port}\n\n")
            f.write("RESUMO GERAL:\n" + "-"*40 + "\n")
            f.write(f"Duração total do teste: {self.results['test_duration']:.2f}s\n")
            f.write(f"Total de clientes bem-sucedidos: {self.results['successful_clients']}\n")
            f.write(f"Total de clientes com falha: {self.results['failed_clients']}\n\n")
            f.write("ANÁLISE DETALHADA POR ETAPA:\n" + "-"*40 + "\n")
            for step_data in self.results['step_details']:
                f.write(f"Etapa com {step_data['num_clients']} Clientes:\n")
                f.write(f"  - Sucesso: {step_data['success_rate']:.1f}% ({step_data['successful_clients']}/{step_data['num_clients']})\n")
                f.write(f"  - Recursos (na máquina local):\n")
                f.write(f"    - CPU Média: {step_data['avg_cpu']:.1f}% | CPU Pico: {step_data['max_cpu']:.1f}%\n")
                f.write(f"    - Memória Média: {step_data['avg_mem']:.1f}%\n\n")
            f.write("\nLOG DETALHADO DA EXECUÇÃO:\n" + "-" * 40 + "\n")
            for line in self.test_report:
                f.write(line + "\n")
        
        self.add_to_report(f"Relatório de texto salvo em: {filepath}")

    def run_gradual_load_test(self, max_clients, step, step_duration):
        """Executa o teste de carga gradual com monitoramento de recursos."""
        self.test_start_time = time.time()
        
        if max_clients % 2 != 0: max_clients += 1
        if step % 2 != 0: step += 1
        
        self.add_to_report(f"🚀 Iniciando teste de carga gradual com monitoramento...")
        
        for num_clients in range(step, max_clients + 1, step):
            self.add_to_report(f"\nEtapa: {num_clients} clientes por {step_duration}s...")
            step_results = {'successful_clients': 0, 'failed_clients': 0}
            resource_readings = {'cpu': [], 'mem': []}
            
            def _monitor_resources(readings_dict):
                while self.monitoring_active:
                    readings_dict['cpu'].append(psutil.cpu_percent(interval=None))
                    readings_dict['mem'].append(psutil.virtual_memory().percent)
                    time.sleep(1)

            self.monitoring_active = True
            monitor_thread = threading.Thread(target=_monitor_resources, args=(resource_readings,))
            monitor_thread.start()

            def client_worker(client_id):
                simulator = GameClientSimulator(self.host, self.port, client_id)
                success, _, _ = simulator.simulate_game_session(step_duration)
                if success: step_results['successful_clients'] += 1
                else: step_results['failed_clients'] += 1
            
            threads = [threading.Thread(target=client_worker, args=(f"bot_{i}",)) for i in range(num_clients)]
            for t in threads: t.start()
            for t in threads: t.join()

            self.monitoring_active = False
            monitor_thread.join()
            
            avg_cpu = sum(resource_readings['cpu']) / len(resource_readings['cpu']) if resource_readings['cpu'] else 0
            max_cpu = max(resource_readings['cpu']) if resource_readings['cpu'] else 0
            avg_mem = sum(resource_readings['mem']) / len(resource_readings['mem']) if resource_readings['mem'] else 0
            success_rate = (step_results['successful_clients'] / num_clients) * 100
            
            self.add_to_report(f"  Sucesso: {success_rate:.1f}% ({step_results['successful_clients']}/{num_clients})")
            self.add_to_report(f"  CPU: {avg_cpu:.1f}% (Média), {max_cpu:.1f}% (Pico) | Memória: {avg_mem:.1f}% (Média)")

            self.results['step_details'].append({
                'num_clients': num_clients, 'successful_clients': step_results['successful_clients'],
                'success_rate': success_rate, 'avg_cpu': avg_cpu, 'max_cpu': max_cpu, 'avg_mem': avg_mem
            })
            self.results['successful_clients'] += step_results['successful_clients']
            self.results['failed_clients'] += step_results['failed_clients']
            
            if success_rate < 50 and num_clients > step: # Evita parar no primeiro passo se ele for ruim
                self.add_to_report("Taxa de sucesso muito baixa. Interrompendo o teste.")
                break
            time.sleep(3)
        
        self.results['test_duration'] = time.time() - self.test_start_time
        self.add_to_report(f"\nTeste de carga finalizado em {self.results['test_duration']:.2f} segundos.")
        self.save_report_to_file("teste_carga_gradual")
        self.generate_performance_graphs("teste_carga_gradual")


def main():
    print("=" * 60)
    print("Simulador de Carga para Servidor de Jogo com Análise de Performance 🎮")
    print("=" * 60)
    
    manager = LoadTestManager()
    
    print(f"Servidor configurado: {SERVER_HOST}:{SERVER_PORT}")
    print("IMPORTANTE: Certifique-se de que o servidor de jogo está rodando!")
    
    try:
        max_clients = int(input(f"Máximo de clientes (padrão {DEFAULT_MAX_CLIENTS}): ") or DEFAULT_MAX_CLIENTS)
        step = int(input(f"Incremento por etapa (padrão {DEFAULT_STEP}): ") or DEFAULT_STEP)
        step_duration = int(input(f"Duração de cada etapa/seg (padrão {DEFAULT_STEP_DURATION}): ") or DEFAULT_STEP_DURATION)
        
        print(f"\n🚀 Iniciando teste: 0 até {max_clients} clientes, incremento de {step}, {step_duration}s por etapa.")
        print("Pressione Ctrl+C para interromper o teste a qualquer momento.\n")
        
        manager.run_gradual_load_test(max_clients, step, step_duration)
    
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário.")
    except ValueError:
        print("\nEntrada inválida. Por favor, insira apenas números.")
    finally:
        print("\nPrograma finalizado.")

if __name__ == "__main__":
    main()