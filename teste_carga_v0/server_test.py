#!/usr/bin/env python3
"""
Simulador de Cliente para Testes de Carga Gradual
"""

import socket
import threading
import time
import pickle
import random
import os
from datetime import datetime
from dotenv import load_dotenv

global_lock = threading.Lock()

class GameClientSimulator:
    def __init__(self, host:str, port:int, client_name:str):
        self.host = host
        self.port = port
        self.connected = False
        self.socket = None
        self.client_name = client_name
        
    def connect(self):
        """Conecta ao servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Cliente {self.client_name} conectado")
            return True
        except Exception as e:
            print(f"Erro ao conectar cliente {self.client_name}: {e}")
            return False
    
    def send_data(self, data):
        """Envia dados para o servidor"""
        try:
            if self.connected:
                self.socket.sendall(pickle.dumps(data))
        except Exception as e:
            print(f"Erro ao enviar dados (Cliente {self.client_name}): {e}")
            self.connected = False
    
    def receive_data(self):
        """Recebe dados do servidor"""
        try:
            if self.connected:
                data = self.socket.recv(4096)
                if data:
                    return pickle.loads(data)
        except Exception as e:
            if self.connected:
                print(f"Erro ao receber dados (Cliente {self.client_id}): {e}")
            self.connected = False
        return None
    
    def simulate_game_session(self, duration:int=60):
        """Simula uma sessão de jogo"""
        print(f"Cliente {self.client_name} iniciando sessão de {duration}s")
        
        if not self.connect():
            return False
        
        start_time = time.time()
        
        try:            
            # Thread para receber dados
            def receive_loop():
                while self.connected and time.time() - start_time < duration:
                    self.receive_data()
                    time.sleep(0.01)
            
            receive_thread = threading.Thread(target=receive_loop)
            receive_thread.start()
            
            # Loop principal de jogo
            while self.connected and time.time() - start_time < duration:           
                self.send_data("\0testando\0")
                time.sleep(0.01)
            
            receive_thread.join()
            
        except Exception as e:
            print(f"Erro durante simulação (Cliente {self.client_name}): {e}")
            return False
        
        finally:
            if self.socket:
                self.socket.close()
            self.connected = False
        
        return True

class LoadTestManager:
    def __init__(self, host:str, port:int):
        self.host = host
        self.port = port
        self.results = {
            'successful_clients': 0,
            'failed_clients': 0,
            'test_duration': 0
        }
        self.test_report = list()
    
    def add_to_report(self, message:str):
        """Adiciona uma linha ao relatório"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.test_report.append(f"[{timestamp}] {message}")
        print(message)
    
    def save_report_to_file(self):
        """Salva o relatório em arquivo TXT"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_carga_gradual_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE TESTE DE CARGA GRADUAL\n")
            
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Servidor: {self.host}:{self.port}\n\n")
            
            f.write("RESUMO DOS RESULTADOS:\n")
            f.write(f"Clientes bem-sucedidos: {self.results['successful_clients']}\n")
            f.write(f"Clientes com falha: {self.results['failed_clients']}\n")
            f.write(f"Duração do teste: {self.results['test_duration']:.2f}s\n")
            
            if self.results['successful_clients'] + self.results['failed_clients'] > 0:
                total_clients = self.results['successful_clients'] + self.results['failed_clients']
                success_rate = (self.results['successful_clients'] / total_clients) * 100
                f.write(f"Taxa de sucesso global: {success_rate:.1f}%\n")
            
            f.write("\nDETALHES DA EXECUÇÃO:\n")
            for line in self.test_report:
                f.write(line + "\n")

        
        self.add_to_report(f"Relatório salvo em: {filename}")
    
    def run_gradual_load_test(self, max_clients:int=50, step:int=5, step_duration:int=30):
        """Executa teste de carga gradual"""
        self.add_to_report(f"Iniciando teste de carga gradual: 0 até {max_clients} clientes")
        self.add_to_report(f"Configuração: Passo = {step} clientes, Duração/step = {step_duration}s")
        
        start_time = time.time()
        
        for num_clients in range(step, max_clients + 1, step):
            step_start = time.time()
            self.add_to_report(f"Testando com {num_clients} clientes...")
            
            step_results = {'success': 0, 'fail': 0}
            threads = []
            
            # Criar e iniciar threads para os clientes
            for i in range(num_clients):
                thread = threading.Thread(
                    target=self.client_worker,
                    args=(f"grad_{num_clients}_{i}", step_duration, step_results)
                )
                threads.append(thread)
                thread.start()
                time.sleep(0.05)  # Intervalo entre conexões
            
            # Aguardar término das threads
            for thread in threads:
                thread.join()
            
            # Calcular resultados do passo atual
            step_duration_actual = time.time() - step_start
            success_rate = (step_results['success'] / num_clients) * 100
            
            self.add_to_report(f"Clientes bem-sucedidos: {step_results['success']}/{num_clients} ({success_rate:.1f}%)")
            self.add_to_report(f"Duração real do passo: {step_duration_actual:.1f}s")
            
            # Atualizar resultados globais
            self.results['successful_clients'] += step_results['success']
            self.results['failed_clients'] += step_results['fail']
            
            time.sleep(2)  # Intervalo entre etapas
        
        # Finalizar relatório
        self.results['test_duration'] = time.time() - start_time
        self.add_to_report("\nTESTE CONCLUÍDO")
        self.add_to_report(f"Clientes bem-sucedidos: {self.results['successful_clients']}")
        self.add_to_report(f"Clientes com falha: {self.results['failed_clients']}")
        
        if self.results['successful_clients'] + self.results['failed_clients'] > 0:
            total = self.results['successful_clients'] + self.results['failed_clients']
            global_success = (self.results['successful_clients'] / total) * 100
            self.add_to_report(f"Taxa de sucesso global: {global_success:.1f}%")
        
        self.add_to_report(f"Duração total: {self.results['test_duration']:.1f}s")
        self.save_report_to_file()
    
    def client_worker(self, client_name:str, duration:int, step_results:dict):
        global global_lock
        """Função de trabalho para cada cliente"""
        simulator = GameClientSimulator(self.host, self.port, client_name)
        if simulator.simulate_game_session(duration):
            with global_lock:
                step_results['success'] += 1
        else:
            with global_lock:
                step_results['fail'] += 1

def main():
    # Importar configurações
    load_dotenv()
    SERVER_HOST=os.getenv("SERVER_IP")
    SERVER_PORT=int(os.getenv("SERVER_PORT"))

    print(f"Servidor alvo: {SERVER_HOST}:{SERVER_PORT}")
    
    manager = LoadTestManager(host=SERVER_HOST, port=SERVER_PORT)
    
    # Configurações do teste (personalizáveis)
    manager.run_gradual_load_test(
        max_clients=60,      # Número máximo de clientes
        step=10,              # Incremento por etapa
        step_duration=10     # Duração de cada etapa (segundos)
    )


if __name__ == "__main__":
    main()