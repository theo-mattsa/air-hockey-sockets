# Testes de Performance e Estabilidade - Pong Socket Game

Este diretório contém uma suite completa de testes para avaliar o desempenho e estabilidade do servidor Pong com sockets.

## Estrutura dos Testes

### 📊 `performance_test.py`

**Testes de Performance e Latência**

- **Teste de Latência**: Mede tempo de resposta do servidor
- **Conexões Simultâneas**: Testa capacidade de múltiplas conexões
- **Monitoramento de Recursos**: CPU e memória durante execução
- **Teste de Stress**: Alta carga com múltiplos clientes
- **Relatório Visual**: Gráficos de performance salvos como PNG

### 🛡️ `stability_test.py`

**Testes de Estabilidade e Robustez**

- **Estabilidade de Conexões**: Conexões de longa duração
- **Conexões Rápidas**: Conectar/desconectar rapidamente
- **Dados Malformados**: Testa robustez contra dados inválidos
- **Vazamento de Memória**: Detecta memory leaks
- **Recuperação de Falhas**: Como o servidor lida com erros

### 🎮 `client_simulator.py`

**Simulador de Clientes Reais**

- **Simulação de Jogo**: Clientes jogando Pong realista
- **Teste de Carga Gradual**: Aumento progressivo de clientes
- **Teste de Stress**: Alta frequência de mensagens
- **Métricas Detalhadas**: Taxa de sucesso e throughput

### 🚀 `run_all_tests.sh`

**Script Automatizado**

- Executa todos os testes sequencialmente
- Gerencia servidor automaticamente
- Relatório consolidado dos resultados

## Como Executar

### Pré-requisitos

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências de teste
pip install psutil matplotlib numpy
```

### Execução Individual

**Teste de Performance:**

```bash
cd tests
python performance_test.py
```

**Teste de Estabilidade:**

```bash
cd tests
python stability_test.py
```

**Simulação de Clientes:**

```bash
cd tests
python client_simulator.py
```

### Execução Completa

```bash
cd tests
chmod +x run_all_tests.sh
./run_all_tests.sh
```

## Métricas Avaliadas

### Performance

- ✅ **Latência média**: < 100ms (excelente), < 200ms (bom)
- ✅ **Taxa de sucesso conexões**: > 95% (excelente)
- ✅ **CPU durante stress**: < 80% (sustentável)
- ✅ **Memória**: Uso estável, sem crescimento constante

### Estabilidade

- ✅ **Robustez**: > 90% dados malformados tratados
- ✅ **Recuperação**: Sem crashes durante testes
- ✅ **Conexões longas**: Mantidas por > 5 minutos
- ✅ **Memory leaks**: Uso de memória estável

### Capacidade

- ✅ **Clientes simultâneos**: Mínimo 20 clientes
- ✅ **Throughput**: > 100 mensagens/segundo
- ✅ **Escalabilidade**: Performance degrada graciosamente

## Interpretação dos Resultados

### 🟢 Resultados Bons

- Latência < 100ms
- Taxa de sucesso > 95%
- CPU < 70% durante stress
- Sem crashes detectados
- Throughput > 100 msg/s

### 🟡 Resultados Aceitáveis

- Latência 100-200ms
- Taxa de sucesso 85-95%
- CPU 70-85% durante stress
- Crashes < 1% dos testes
- Throughput 50-100 msg/s

### 🔴 Resultados Problemáticos

- Latência > 200ms
- Taxa de sucesso < 85%
- CPU > 85% sustentado
- Crashes frequentes
- Throughput < 50 msg/s

## Relatórios Gerados

### `performance_report.png`

Gráficos mostrando:

- Distribuição de latência
- Uso de CPU ao longo do tempo
- Uso de memória
- Tempos de conexão

### Logs no Terminal

- Métricas detalhadas em tempo real
- Resumos estatísticos
- Identificação de problemas
- Recomendações de otimização

## Troubleshooting

### Problema: "Connection refused"

```bash
# Verificar se o servidor está rodando
ps aux | grep python
netstat -an | grep 5000

# Iniciar servidor manualmente
python ../server.py
```

### Problema: Dependências faltando

```bash
# Instalar dependências
pip install psutil matplotlib numpy python-dotenv

# Verificar instalação
python -c "import psutil, matplotlib, numpy; print('OK')"
```

### Problema: Testes muito lentos

Ajustar parâmetros nos arquivos:

- Reduzir `num_tests` em `performance_test.py`
- Reduzir `duration` em `stability_test.py`
- Reduzir `max_clients` em `client_simulator.py`

## Melhorias Sugeridas

Baseado nos resultados dos testes, considere:

1. **Se latência alta**: Otimizar processamento de mensagens
2. **Se CPU alta**: Implementar pooling de threads
3. **Se memory leaks**: Revisar cleanup de conexões
4. **Se baixo throughput**: Usar async/await ou buffers

## Automação CI/CD

Para integração contínua, adicione ao seu pipeline:

```yaml
# .github/workflows/tests.yml
- name: Run Performance Tests
  run: |
    source venv/bin/activate
    cd tests
    ./run_all_tests.sh
```

Os testes estão configurados para falhar se métricas críticas não forem atendidas.
