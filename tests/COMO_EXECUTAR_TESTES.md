# 🧪 COMO EXECUTAR OS TESTES - PASSO A PASSO

## ⚡ EXECUÇÃO RÁPIDA (RECOMENDADO)

**Tudo automatizado - apenas execute:**

```bash
./run_tests.sh
```

Esse comando vai:

- ✅ Ativar ambiente virtual automaticamente
- ✅ Instalar dependências necessárias
- ✅ Subir o servidor automaticamente
- ✅ Executar todos os testes
- ✅ Gerar relatórios
- ✅ Finalizar servidor automaticamente

## 📋 O QUE VOCÊ NÃO PRECISA FAZER

❌ **NÃO** precisa ativar o venv manualmente  
❌ **NÃO** precisa subir o servidor antes  
❌ **NÃO** precisa instalar dependências  
❌ **NÃO** precisa finalizar o servidor depois

**Tudo é automático!** 🎯

## 🎮 DEMONSTRAÇÃO RÁPIDA

Para ver se tudo está funcionando:

```bash
python3 test_demo.py
```

## 📊 TIPOS DE TESTE DISPONÍVEIS

### 1. **Teste Completo** (automático)

```bash
./run_tests.sh
```

- Teste de performance (latência, throughput)
- Teste de estabilidade (robustez, memory leaks)
- Simulação de clientes (carga real)
- Relatórios com gráficos

### 2. **Testes Individuais** (manual)

```bash
# Ativar ambiente
source venv/bin/activate

# Em uma aba: subir servidor
python3 server.py

# Em outra aba: executar testes
cd tests
python3 performance_test.py    # Performance
python3 stability_test.py      # Estabilidade
python3 client_simulator.py    # Simulação
```

## 📈 RELATÓRIOS GERADOS

### 📄 **No Terminal**

- Métricas em tempo real
- Latência média/min/max
- Taxa de sucesso das conexões
- Uso de CPU e memória
- Throughput (mensagens/segundo)

### 🖼️ **Gráfico Visual**

- `tests/performance_report.png`
- Histograma de latência
- Gráfico de CPU ao longo do tempo
- Gráfico de memória
- Tempo de conexões

### 📊 **Exemplo de Saída**

```
📊 Resultados de Latência:
  Média: 45.2ms
  Mediana: 42.1ms
  Mín: 12.3ms
  Máx: 89.7ms
  Testes realizados: 98/100

📊 Uso de Recursos:
  CPU média: 23.5%
  CPU máxima: 67.2%
  Memória média: 12.1%
  Memória máxima: 15.8%

🎉 TODOS OS TESTES PASSARAM!
```

## 🚨 SOLUÇÃO DE PROBLEMAS

### Problema: "Diretório venv não encontrado"

```bash
python3 -m venv venv
pip install pygame python-dotenv
```

### Problema: "Connection refused"

```bash
# Verificar se porta 5555 está livre
netstat -an | grep 5555

# Matar processos na porta 5555
sudo lsof -ti:5555 | xargs kill -9
```

### Problema: Dependências faltando

```bash
source venv/bin/activate
pip install psutil matplotlib numpy
```

### Problema: Permissão negada

```bash
chmod +x run_tests.sh
chmod +x test_demo.py
chmod +x tests/run_all_tests.sh
```

## 🎯 MÉTRICAS DE QUALIDADE

### ✅ **Resultados Bons**

- Latência < 100ms
- Taxa de sucesso > 95%
- CPU < 70% durante stress
- Sem crashes detectados

### ⚠️ **Resultados Problemáticos**

- Latência > 200ms
- Taxa de sucesso < 85%
- CPU > 85% sustentado
- Crashes frequentes

## 🔄 AUTOMAÇÃO PARA DESENVOLVIMENTO

Para executar testes automaticamente durante desenvolvimento:

```bash
# Monitorar mudanças e executar testes
while true; do
    ./run_tests.sh
    echo "Aguardando 60s..."
    sleep 60
done
```

## 📝 EXEMPLO COMPLETO DE EXECUÇÃO

```bash
# 1. Navegar para o projeto
cd /home/theo/Documents/ufes/redes/pong-sockets

# 2. Executar testes (tudo automático)
./run_tests.sh

# Saída esperada:
# 🧪 Pong Socket Game - Suite de Testes Completa
# ==============================================
# 🔧 Ativando ambiente virtual...
# ✅ Ambiente virtual ativado: /home/theo/.../venv
# 📦 Instalando dependências de teste...
# 🚀 Iniciando servidor em modo de teste...
# ✅ Servidor rodando (PID: 12345)
#
# 📋 Executando testes...
# ========================
# 1️⃣  TESTE DE ESTABILIDADE
# 2️⃣  SIMULAÇÃO DE CLIENTES
# 3️⃣  TESTE DE PERFORMANCE
#
# 🎉 TODOS OS TESTES PASSARAM!
# 📁 Relatórios salvos em: tests/
# 🖼️  Gráficos: tests/performance_report.png
```

**É isso! Simples assim! 🚀**
