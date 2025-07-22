# Teste de Carga Gradual REAL - Pong Sockets

Simulador que testa o servidor usando o **protocolo real do jogo Pong** com **métricas de performance detalhadas**.

## O que este teste faz?

**Agora simula o jogo Pong real!** 🎮

- **Segue o protocolo real**: Recebe player_id, envia nome, usa pygame.Rect
- **Forma jogos 1v1**: Testa com pares de jogadores (como o jogo real)
- **Usa comunicação real**: Recebe estado → Envia paddle (fluxo correto)
- **Mede performance real**: Quantos jogos simultâneos o servidor aguenta

**Testa cenários reais**:

- Formação de jogos (matchmaking)
- Sincronização entre 2 jogadores
- Protocolo real de comunicação
- Limites reais do servidor

**Resultado prático**: "Meu servidor aguenta 25 jogos simultâneos (50 jogadores)"

## Métricas de Performance

O teste inclui **métricas detalhadas de performance**:

### **Por Etapa:**

- **Mensagens por segundo** (msg/s): Total de mensagens enviadas+recebidas ÷ tempo
- **Jogos por segundo** (jogos/s): Jogos formados ÷ tempo da etapa
- **Taxa de formação**: % de jogos que conseguiram ser formados
- **Taxa de sucesso**: % de clientes que conectaram com sucesso

### 🎯 **Métricas Globais:**

- **Performance geral**: Throughput consolidado de todo o teste
- **Total de jogos**: Quantidade real de jogos 1v1 formados
- **Eficiência**: Relação entre jogos possíveis vs formados

**Exemplo de output:**

```
📊 20 clientes: 100.0% sucesso
🎮 10 jogos formados (100.0% dos 10 possíveis)
📈 Performance: 1200.5 msg/s, 0.33 jogos/s
📈 Performance geral: 980.2 msg/s, 0.28 jogos/s
```

**Configure os parâmetros** quando solicitado:

- Máximo de clientes (padrão: 50) - será ajustado para número par
- Incremento por etapa (padrão: 5) - será ajustado para número par
- Duração de cada etapa em segundos (padrão: 30)

## Como funciona

O teste segue o **protocolo real do Pong**:

1. **Conecta clientes em pares** (cada jogo precisa de 2 jogadores)
2. **Segue o fluxo real**: Recebe player_id → Envia nome → Joga
3. **Usa pygame.Rect**: Igual ao cliente real do jogo
4. **Incrementa por números pares**: 2, 4, 6... para formar jogos completos
5. **Coleta métricas**: Performance detalhada de cada etapa

**Exemplo**: Com configuração padrão (50 clientes, incremento 2, 30s):

- Etapa 1: 2 clientes (1 jogo) por 30s
- Etapa 2: 4 clientes (2 jogos) por 30s
- Etapa 3: 6 clientes (3 jogos) por 30s
- ...
- Etapa 25: 50 clientes (25 jogos) por 30s

## O que cada cliente faz

Cada cliente agora **simula um jogador real**:

1. **Conecta** ao servidor
2. **Recebe player_id** (0 = jogador de baixo, 1 = jogador de cima)
3. **Envia nome** no formato correto (`TestBot_XXXX`)
4. **Aguarda** a formação do jogo (2 jogadores)
5. **Loop do jogo**: Recebe estado → Move paddle → Envia posição (60 FPS)
6. **Usa pygame.Rect** para enviar posição (protocolo real)
7. **Conta mensagens** para métricas de performance

## Arquivos gerados

- **Relatórios**: Salvos na pasta `reports/`
- **Nome do arquivo**: `relatorio_client_simulator_teste_carga_gradual_real_YYYYMMDD_HHMMSS.txt`
- **Métricas incluem**:
  - Clientes conectados e jogos formados por etapa
  - Performance (msg/s, jogos/s)
  - Taxa de sucesso e formação de jogos
  - Throughput geral e eficiência

## Configurações rápidas

Edite o arquivo `config.py` para ajustar:

```python
# Servidor
SERVER_HOST = "localhost"
SERVER_PORT = 8888

# Valores padrão dos testes
DEFAULT_MAX_CLIENTS = 50
DEFAULT_STEP = 5
DEFAULT_STEP_DURATION = 30
```

## Critérios de parada

O teste para se:

- Atingir o número máximo de clientes
- Taxa de sucesso cair abaixo de 50%
- Usuário pressionar Ctrl+C

## Problemas comuns

**Erro de conexão**: Verifique se o servidor está rodando  
**Porta em uso**: Mude a `SERVER_PORT` no config.py  
**Muitos clientes**: Diminua `DEFAULT_MAX_CLIENTS`  
**Pygame não encontrado**: Execute `pip install pygame` (opcional)

## Dependências

- **Python 3.8+**: Obrigatório
- **Pygame**: Opcional (para protocolo real)
  - Com pygame: Usa pygame.Rect como o cliente real
  - Sem pygame: Usa fallback simplificado mas funcional

## Interpretando os Resultados

### **Bons Indicadores:**

- Taxa de sucesso > 95%
- Taxa de formação de jogos > 90%
- Performance estável entre etapas
- Sem quedas bruscas de throughput

### **Sinais de Problema:**

- Taxa de sucesso < 80%
- Queda significativa na formação de jogos
- Throughput degradando com mais clientes
- Muitas desconexões

### **Métricas Típicas:**

- **Servidor básico**: ~10-20 jogos simultâneos
- **Servidor otimizado**: ~50-100 jogos simultâneos
- **Throughput típico**: 500-2000 msg/s
- **Latência aceitável**: Formação de jogos > 90%

Use essas métricas para otimizar seu servidor e identificar gargalos! 🚀
