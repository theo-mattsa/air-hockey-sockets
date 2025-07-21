# 🔧 CONFIGURAÇÃO DOS TESTES

## Como Configurar IP e Porta

Para alterar o servidor que os testes vão usar, edite o arquivo `config.py`:

```python
# Configuração simples para os testes
# Modifique estes valores conforme necessário

# Configurações do servidor
SERVER_HOST = "localhost"    # ← Altere aqui o IP
SERVER_PORT = 5555          # ← Altere aqui a porta
```

## 🌐 TESTES COM SERVIDOR REMOTO vs LOCAL

### 📊 Comparativo de Cenários

| Tipo de Teste        | Servidor Local                  | Servidor Remoto                          | Recomendação |
| -------------------- | ------------------------------- | ---------------------------------------- | ------------ |
| **Client Simulator** | ⚠️ Limitado por recursos locais | ✅ **RECOMENDADO** - Teste realístico    | **Remoto**   |
| **Performance Test** | ❌ Latência irreal (~0.1ms)     | ✅ **RECOMENDADO** - Latência real       | **Remoto**   |
| **Stability Test**   | ⚠️ Não testa rede               | ✅ **RECOMENDADO** - Testa rede + código | **Remoto**   |

### 🎯 **RESUMO: Para testes mais realísticos e com menor viés, use SEMPRE servidor remoto!**

## 📈 RECOMENDAÇÕES PARA TESTES REALÍSTICOS

### ✅ **CENÁRIO IDEAL - Servidor Remoto**

```python
SERVER_HOST = "192.168.1.100"  # IP de outra máquina
SERVER_PORT = 5555
```

**Por que é melhor:**

- 🌐 **Latência real de rede** (1-50ms vs 0.1ms local)
- 🔄 **Throughput limitado pela rede** (mais realístico)
- 💾 **Recursos separados** (CPU/RAM não competem)
- 🛡️ **Testa conectividade de rede** (drops, timeouts)
- 📊 **Resultados próximos da produção**

### ⚠️ **VIESES DO SERVIDOR LOCAL**

- **Latência artificial**: 0.1ms (produção: 10-100ms)
- **Throughput irreal**: Limitado apenas por RAM/CPU
- **Recursos competindo**: Cliente e servidor na mesma máquina
- **Não testa rede**: Falha em detectar problemas de conectividade

## 🧪 TIPOS DE TESTE E SERVIDOR REMOTO

### 1. **Client Simulator** 🎮

**❌ Servidor Local:**

```
✗ 50 clientes simultâneos = 100% CPU local
✗ Throughput: 5000 msg/s (irreal)
✗ Taxa de sucesso: 100% (não detecta problemas reais)
```

**✅ Servidor Remoto:**

```
✓ 50 clientes = Teste realístico de capacidade
✓ Throughput: 500 msg/s (limitado pela rede)
✓ Taxa de sucesso: 92% (detecta timeouts reais)
```

### 2. **Performance Test** ⚡

**❌ Servidor Local:**

```
✗ Latência média: 0.3ms (não útil)
✗ 99% success rate (mascarado)
✗ CPU: 90% (recursos compartilhados)
```

**✅ Servidor Remoto:**

```
✓ Latência média: 15ms (realística)
✓ 94% success rate (mostra problemas reais)
✓ CPU servidor: 45% (isolado)
```

### 3. **Stability Test** 🛡️

**❌ Servidor Local:**

```
✗ Não detecta problemas de rede
✗ Timeouts mascarados
✗ Reconexão sempre funciona
```

**✅ Servidor Remoto:**

```
✓ Detecta drops de rede
✓ Timeouts realísticos
✓ Testa reconexão real
```

## 🔧 CONFIGURAÇÃO PARA DIFERENTES CENÁRIOS

### Desenvolvimento Local (Debug apenas)

```python
SERVER_HOST = "localhost"
SERVER_PORT = 5555
```

### Teste de Performance (Recomendado)

```python
SERVER_HOST = "192.168.1.100"  # IP da máquina do servidor
SERVER_PORT = 5555
```

### Teste de Produção (Cloud/VPS)

```python
SERVER_HOST = "servidor.exemplo.com"
SERVER_PORT = 5555
```

### Teste de WAN (Internet)

```python
SERVER_HOST = "203.0.113.1"  # IP público
SERVER_PORT = 5555
```

## 🚨 PRÉ-REQUISITOS PARA SERVIDOR REMOTO

### 1. **Conectividade**

```bash
# Teste básico de conectividade
ping 192.168.1.100

# Teste específico da porta
telnet 192.168.1.100 5555
```

### 2. **Firewall**

- Servidor deve aceitar conexões na porta 5555
- Firewall local e remoto devem permitir tráfego
- Roteador deve permitir comunicação entre máquinas

### 3. **Servidor Ativo**

```bash
# Na máquina do servidor
python server.py
# Deve mostrar: Servidor rodando em 0.0.0.0:5555
```

## 📊 INTERPRETAÇÃO DOS RESULTADOS

### Com Servidor Local

```
⚠️ Latência: 0.5ms (irreal)
⚠️ Throughput: 8000 msg/s (limitado por CPU local)
⚠️ Taxa de erro: 0% (mascarado)
```

### Com Servidor Remoto

```
✅ Latência: 12ms (realística para LAN)
✅ Throughput: 450 msg/s (limitado por rede - real)
✅ Taxa de erro: 3% (problemas reais detectados)
```

## 💡 DICAS PARA MELHORES RESULTADOS

### 1. **Use Rede Estável**

- Ethernet > WiFi
- Rede local > Internet
- Evite saturação da rede durante testes

### 2. **Configure Ambiente Adequado**

- Servidor dedicado (não compartilhado)
- Recursos suficientes na máquina do servidor
- Evite outros tráfegos intensos na rede

### 3. **Execute Múltiplas Vezes**

- Testes únicos podem ter variações
- Execute 3-5 vezes e calcule média
- Compare resultados ao longo do tempo

## Exemplos de Configuração

### Servidor Local (desenvolvimento)

```python
SERVER_HOST = "localhost"
SERVER_PORT = 5555
```

### Servidor Remoto (recomendado para testes)

```python
SERVER_HOST = "192.168.1.100"  # IP da máquina do servidor
SERVER_PORT = 5555
```

### Porta Diferente

```python
SERVER_HOST = "localhost"
SERVER_PORT = 8080          # Porta personalizada
```

## Uso

Após alterar o `config.py`, todos os testes usarão automaticamente as novas configurações:

```bash
# Todos estes comandos usarão o IP/porta do config.py
python client_simulator.py
python performance_test.py
python stability_test.py
python gerar_relatorios.py
```

## Verificar Configuração

Para ver qual servidor está configurado, execute qualquer teste. A primeira linha mostrará:

```
Servidor configurado: 192.168.1.100:5555
```

## 🎯 CONCLUSÃO

**Para testes úteis e realísticos:**

1. ✅ **USE servidor remoto** sempre que possível
2. ✅ **EVITE servidor local** para performance/stability tests
3. ✅ **INTERPRETE resultados** considerando latência de rede
4. ✅ **DOCUMENTE o ambiente** de teste (local vs remoto)

**Servidor remoto = Resultados próximos da realidade = Testes mais valiosos!** 🚀
