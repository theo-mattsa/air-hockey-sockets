#!/usr/bin/env python3
"""
Script de demonstração para executar testes e gerar relatórios TXT
"""

import os
import sys
import time
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(__file__))

# Importar configurações
from config import SERVER_HOST, SERVER_PORT

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def main():
    print_header("GERADOR DE RELATÓRIOS TXT - PONG SOCKETS TESTS")
    
    print(f"\n🔧 Servidor configurado: {SERVER_HOST}:{SERVER_PORT}")
    print("   (Para alterar, edite o arquivo config.py)")
    
    print("\nEste script executa os testes e gera relatórios em formato TXT.")
    print("Certifique-se de que o servidor está rodando antes de executar!")
    print("\nRelatórios disponíveis:")
    print("1. 📊 Client Simulator - Simulação de clientes")
    print("2. ⚡ Performance Test - Testes de performance")
    print("3. 🛡️  Stability Test - Testes de estabilidade")
    print("4. 🚀 Executar todos os testes")
    
    try:
        choice = input("\nEscolha uma opção (1-4): ").strip()
        
        if choice == '1':
            print_header("EXECUTANDO CLIENT SIMULATOR")
            from client_simulator import LoadTestManager
            
            manager = LoadTestManager()
            print("Executando simulação básica...")
            manager.run_concurrent_game_simulation(5, 30)
            
        elif choice == '2':
            print_header("EXECUTANDO PERFORMANCE TEST")
            from performance_test import PerformanceTest
            
            tester = PerformanceTest()
            print("Executando teste de latência...")
            tester.test_latency(20)
            
        elif choice == '3':
            print_header("EXECUTANDO STABILITY TEST")
            from stability_test import StabilityTest
            
            tester = StabilityTest()
            print("Executando teste de conexões rápidas...")
            tester.test_rapid_connections(20)
            
        elif choice == '4':
            print_header("EXECUTANDO TODOS OS TESTES")
            
            # Client Simulator
            print("\n1/3 - Executando Client Simulator...")
            from client_simulator import LoadTestManager
            manager = LoadTestManager()
            manager.run_concurrent_game_simulation(3, 20)
            time.sleep(2)
            
            # Performance Test
            print("\n2/3 - Executando Performance Test...")
            from performance_test import PerformanceTest
            perf_tester = PerformanceTest()
            perf_tester.test_latency(10)
            time.sleep(2)
            
            # Stability Test
            print("\n3/3 - Executando Stability Test...")
            from stability_test import StabilityTest
            stab_tester = StabilityTest()
            stab_tester.test_rapid_connections(10)
            
            print("\n✅ Todos os testes concluídos!")
            
        else:
            print("❌ Opção inválida!")
            return
            
        print("\n" + "=" * 70)
        print("📄 RELATÓRIOS GERADOS:")
        print("=" * 70)
        
        # Listar arquivos de relatório recentes
        test_dir = os.path.dirname(__file__)
        files = os.listdir(test_dir)
        report_files = [f for f in files if f.startswith('relatorio_') and f.endswith('.txt')]
        
        # Ordenar por data de modificação (mais recentes primeiro)
        report_files.sort(key=lambda x: os.path.getmtime(os.path.join(test_dir, x)), reverse=True)
        
        if report_files:
            print("Relatórios mais recentes:")
            for i, filename in enumerate(report_files[:5], 1):
                filepath = os.path.join(test_dir, filename)
                mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                print(f"  {i}. {filename}")
                print(f"     Criado: {mod_time.strftime('%d/%m/%Y %H:%M:%S')}")
        else:
            print("Nenhum relatório encontrado.")
            
        print(f"\nRelatórios salvos em: {test_dir}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Execução interrompida pelo usuário")
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("Certifique-se de que todos os módulos estão no diretório correto.")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()
