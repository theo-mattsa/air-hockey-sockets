#!/bin/bash

# Script para executar todos os testes de performance e estabilidade
# Ativa automaticamente o ambiente virtual do projeto

echo "🧪 Pong Socket Game - Suite de Testes Completa"
echo "=============================================="

# Ir para o diretório do projeto
cd "$(dirname "$0")/.."

# Verificar se o ambiente virtual existe
if [[ ! -d "venv" ]]; then
    echo "❌ Erro: Diretório venv não encontrado!"
    echo "Execute: python3 -m venv venv"
    exit 1
fi

# Ativar ambiente virtual automaticamente
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Verificar se foi ativado com sucesso
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Erro: Não foi possível ativar o ambiente virtual!"
    exit 1
fi

echo "✅ Ambiente virtual ativado: $VIRTUAL_ENV"

echo "📦 Instalando dependências de teste..."
python3 -m pip install psutil matplotlib numpy > /dev/null 2>&1

echo ""
echo "🚀 Iniciando servidor em modo de teste..."

# Iniciar servidor em background
python3 server.py &
SERVER_PID=$!

# Aguardar servidor inicializar
echo "⏳ Aguardando servidor inicializar..."
sleep 3

# Verificar se servidor está rodando
if ! ps -p $SERVER_PID > /dev/null; then
    echo "❌ Erro: Servidor não conseguiu inicializar!"
    exit 1
fi

echo "✅ Servidor rodando (PID: $SERVER_PID)"
echo ""

# Função para cleanup
cleanup() {
    echo ""
    echo "🧹 Finalizando servidor..."
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    echo "✅ Cleanup concluído"
}

# Registrar cleanup para execução no exit
trap cleanup EXIT

echo "📋 Executando testes..."
echo "========================"

# Teste 1: Estabilidade (mais rápido)
echo ""
echo "1️⃣  TESTE DE ESTABILIDADE"
echo "-------------------------"
cd tests
python3 stability_test.py
STABILITY_EXIT=$?

# Teste 2: Simulação de clientes
echo ""
echo "2️⃣  SIMULAÇÃO DE CLIENTES"
echo "-------------------------"
# Usar teste automático
echo "1" | python3 client_simulator.py
CLIENT_EXIT=$?

# Teste 3: Performance (pode demorar mais)
echo ""
echo "3️⃣  TESTE DE PERFORMANCE"
echo "------------------------"
echo "" | python3 performance_test.py
PERFORMANCE_EXIT=$?

cd ..

# Resumo dos resultados
echo ""
echo "📊 RESUMO DOS TESTES"
echo "===================="

if [ $STABILITY_EXIT -eq 0 ]; then
    echo "✅ Teste de Estabilidade: PASSOU"
else
    echo "❌ Teste de Estabilidade: FALHOU"
fi

if [ $CLIENT_EXIT -eq 0 ]; then
    echo "✅ Simulação de Clientes: PASSOU"
else
    echo "❌ Simulação de Clientes: FALHOU"
fi

if [ $PERFORMANCE_EXIT -eq 0 ]; then
    echo "✅ Teste de Performance: PASSOU"
else
    echo "❌ Teste de Performance: FALHOU"
fi

echo ""
echo "📁 Relatórios salvos em: tests/"
echo "🖼️  Gráficos: tests/performance_report.png"

# Exit code baseado nos testes
if [ $STABILITY_EXIT -eq 0 ] && [ $CLIENT_EXIT -eq 0 ] && [ $PERFORMANCE_EXIT -eq 0 ]; then
    echo "🎉 TODOS OS TESTES PASSARAM!"
    exit 0
else
    echo "⚠️  ALGUNS TESTES FALHARAM!"
    exit 1
fi
