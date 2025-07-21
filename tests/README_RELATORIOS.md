# 📄 RELATÓRIOS AUTOMÁTICOS EM TXT

Os arquivos de teste agora geram automaticamente relatórios detalhados em formato TXT sempre que são executados.

## 🚀 Como Usar

### Execução Individual dos Testes

```bash
# Teste de simulação de clientes (gera relatório TXT)
python client_simulator.py

# Teste de performance (gera relatório TXT)
python performance_test.py

# Teste de estabilidade (gera relatório TXT)
python stability_test.py
```

### Execução com Script Auxiliar

```bash
# Script interativo para gerar relatórios
python gerar_relatorios.py
```

### Execução Programática

```python
from client_simulator import LoadTestManager

# Criar e executar teste
manager = LoadTestManager('localhost', 5555)
manager.run_concurrent_game_simulation(10, 60)
# Relatório é gerado automaticamente
```

## 📋 Tipos de Relatório Gerados

### 1. Client Simulator

- **Arquivo**: `relatorio_client_simulator_[tipo]_[timestamp].txt`
- **Conteúdo**:
  - Resultados de simulação de clientes
  - Taxa de sucesso de conexões
  - Throughput de mensagens
  - Log detalhado de execução

### 2. Performance Test

- **Arquivo**: `relatorio_performance_[tipo]_[timestamp].txt`
- **Conteúdo**:
  - Métricas de latência (média, mediana, min/max)
  - Taxa de sucesso de conexões
  - Uso de CPU e memória
  - Análise automática dos resultados

### 3. Stability Test

- **Arquivo**: `relatorio_stability_[tipo]_[timestamp].txt`
- **Conteúdo**:
  - Métricas de estabilidade
  - Análise de robustez
  - Tipos de erros mais comuns
  - Detecção de crashes do servidor

## 📊 Formato dos Relatórios

Todos os relatórios seguem o mesmo formato padronizado:

```
===============================================================================
                        TÍTULO DO RELATÓRIO
===============================================================================

Data/Hora: DD/MM/AAAA HH:MM:SS
Tipo de Teste: NOME_DO_TESTE
Servidor: host:porta

MÉTRICAS PRINCIPAIS:
----------------------------------------
[Dados numéricos organizados]

ANÁLISE DOS RESULTADOS:
----------------------------------------
[Análise automática com ✅ 🟡 🔴]

DETALHES DA EXECUÇÃO:
----------------------------------------
[Log completo com timestamps]

===============================================================================
Relatório gerado automaticamente pelo [Nome do Teste]
===============================================================================
```

## 📈 Análise Automática

Os relatórios incluem análise automática dos resultados:

### ✅ Excelente

- Latência < 100ms
- Taxa de sucesso > 95%
- CPU < 70%

### 🟡 Bom/Moderado

- Latência 100-200ms
- Taxa de sucesso 85-95%
- CPU 70-85%

### 🔴 Problemático

- Latência > 200ms
- Taxa de sucesso < 85%
- CPU > 85%

## 🗂️ Organização dos Arquivos

Os relatórios são salvos com nomenclatura padronizada:

```
relatorio_[modulo]_[tipo_teste]_[AAAAMMDD_HHMMSS].txt

Exemplos:
- relatorio_client_simulator_simulacao_jogo_20250721_143052.txt
- relatorio_performance_latencia_20250721_143100.txt
- relatorio_stability_conexoes_20250721_143200.txt
```

## 📖 Exemplos de Relatórios

Veja os arquivos de exemplo incluídos:

- `exemplo_relatorio_client_simulator.txt`
- `exemplo_relatorio_performance.txt`
- `exemplo_relatorio_stability.txt`

## 🔧 Personalização

Para personalizar os relatórios, edite os métodos `save_report_to_file()` em cada arquivo de teste:

```python
def save_report_to_file(self, test_type="custom"):
    # Personalizar formato e conteúdo aqui
    pass
```

## 🚨 Solução de Problemas

### Erro: "Permission denied"

```bash
# Verificar permissões do diretório
ls -la tests/
chmod 755 tests/
```

### Relatórios não são gerados

- Verificar se o teste executou até o final
- Verificar espaço em disco disponível
- Verificar permissões de escrita no diretório

### Relatórios vazios ou incompletos

- Verificar se o servidor estava rodando
- Verificar logs de erro no console
- Executar teste com parâmetros reduzidos

## 📞 Suporte

Para problemas ou dúvidas sobre os relatórios:

1. Verificar logs no console durante execução
2. Revisar arquivos de exemplo
3. Executar `python gerar_relatorios.py` para teste rápido

---

**Nota**: Os relatórios são gerados automaticamente a cada execução. Para análise histórica, mantenha os arquivos organizados por data/hora.
