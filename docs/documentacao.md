# Fluxo do Projeto de Rotas de AGV

## Contexto

Este projeto modela um problema de planejamento de rotas para um AGV em um centro de distribuicao automatizado.

O AGV ja inicia a simulacao com 3 pacotes recebidos e precisa entrega-los em docas especificas. O ambiente e representado por um grid, onde cada celula corresponde a uma area do armazem: corredores normais, corredores rapidos, areas lentas, congestionamentos, obstaculos fixos e bloqueios temporarios.

O objetivo do agente e planejar uma sequencia de movimentos e entregas que respeite:

- a posicao inicial do AGV;
- os obstaculos e bloqueios do armazem;
- os diferentes custos de terreno;
- o peso dos pacotes ainda carregados;
- a prioridade dos pacotes;
- a doca obrigatoria de cada pacote.

O codigo tambem compara diferentes algoritmos de busca da biblioteca SimpleAI:

- Busca em Largura;
- Busca em Profundidade;
- Busca de Custo Uniforme;
- Busca Gulosa;
- A*.

## Representacao do Ambiente

O armazem e representado pela matriz `GRID`, com dimensao `70x70`.

No codigo, o tamanho fica em `GRID_SIZE`:

```python
GRID_SIZE = 70
```

O grid e montado pela funcao `build_grid`, o que evita escrever manualmente 40 linhas com 40 colunas. Essa funcao cria o piso normal e depois adiciona corredores rapidos, areas lentas, congestionamentos, obstaculos e bloqueios.

Cada simbolo tem um significado:

```text
. = piso normal
F = corredor rapido
L = area lenta / manobra dificil
~ = congestionamento
X = obstaculo fixo
B = bloqueio temporario
```

As celulas `X` e `B` nao podem ser atravessadas. As demais celulas podem ser percorridas, mas possuem custos diferentes.

Os custos de terreno ficam em `TERRAIN_COSTS`:

```python
TERRAIN_COSTS = {
    ".": 1.0,
    "F": 0.7,
    "L": 2.0,
    "~": 4.0,
}
```

Assim, andar em um corredor rapido custa menos que andar em piso normal, enquanto areas lentas e congestionadas custam mais.

## Pacotes e Docas

As docas sao definidas em `DOCKS`:

```python
DOCKS = {
    "D1": (5, 65),
    "D2": (65, 4),
    "D3": (68, 68),
    "D4": (50, 35),
}
```

Existem 4 docas, mas o AGV recebe 3 pacotes. Cada pacote possui uma doca de entrega obrigatoria, peso e prioridade:

```python
PACKAGES = {
    "P1": {"dock": "D3", "weight": 6, "priority": 5},
    "P2": {"dock": "D2", "weight": 4, "priority": 3},
    "P3": {"dock": "D1", "weight": 5, "priority": 5},
}
```

Neste exemplo, `P1` e `P3` possuem a mesma prioridade. Quando isso acontece, o AGV escolhe primeiro o pacote cuja doca esta mais proxima da posicao atual.

## Regra de Escolha dos Pacotes

A funcao `choose_next_package` decide qual pacote deve ser entregue em seguida.

A regra e:

1. escolher o pacote com maior prioridade;
2. se houver empate de prioridade, escolher o pacote cuja doca esta mais perto;
3. se ainda houver empate, usar o identificador do pacote como criterio final.

No codigo, isso aparece assim:

```python
return min(
    pending,
    key=lambda package_id: (
        -PACKAGES[package_id]["priority"],
        manhattan(position, package_dock_position(package_id)),
        package_id,
    ),
)
```

O sinal negativo em `-priority` faz com que a maior prioridade venha primeiro, mesmo usando `min`.

## Estado do Problema

Cada estado da busca possui esta estrutura:

```python
(linha, coluna, pacotes_entregues)
```

Exemplo:

```python
(1, 9, ("P3",))
```

Isso significa que o AGV esta na linha `1`, coluna `9`, e ja entregou o pacote `P3`.

Os pacotes que ainda nao aparecem em `pacotes_entregues` continuam sendo considerados como carga do AGV.

## Acoes Possiveis

A classe principal do problema e `AGVDeliveryProblem`, que herda de `SearchProblem`.

A funcao `actions` gera as acoes possiveis em cada estado.

Existem dois tipos de acao:

```python
("mover", direcao)
("entregar", pacote)
```

O AGV pode se mover para cima, baixo, esquerda ou direita, desde que a celula de destino seja valida.

Quando o AGV chega na doca do proximo pacote escolhido pela regra de prioridade, a unica acao gerada e a entrega daquele pacote. Isso garante que a politica de prioridade seja respeitada.

## Transicao de Estado

A funcao `result` calcula o novo estado depois de uma acao.

Se a acao for movimento, a posicao muda:

```python
return row + d_row, col + d_col, delivered
```

Se a acao for entrega, a posicao permanece a mesma, mas o pacote entra na lista de entregues:

```python
return row, col, tuple(sorted(delivered + (value,)))
```

## Estado Objetivo

O problema termina quando todos os pacotes foram entregues:

```python
return len(delivered) == len(PACKAGES)
```

Ou seja, o AGV nao precisa terminar em uma posicao especifica depois da ultima entrega. Basta que todos os pacotes tenham sido entregues em suas docas corretas.

## Calculo de Custo

O custo de entregar um pacote e zero:

```python
DELIVERY_ACTION_COST = 0
```

O custo relevante esta no deslocamento. Para cada movimento, o codigo considera:

- o custo do terreno;
- o peso ainda carregado pelo AGV;
- a prioridade dos pacotes ainda pendentes.

A formula usada e:

```python
terrain_cost * load_factor + priority_pressure
```

O `terrain_cost` vem de `TERRAIN_COSTS`.

O `load_factor` aumenta o custo quando o AGV esta mais pesado:

```python
load_factor = 1 + current_load(delivered) / AGV_CAPACITY
```

Se a capacidade e `15` e o AGV esta carregando peso `15`, o fator de carga vira `2.0`. Conforme os pacotes sao entregues, a carga diminui e os proximos movimentos ficam mais baratos.

O `priority_pressure` adiciona uma pequena penalidade enquanto ainda existem pacotes prioritarios pendentes:

```python
priority_pressure = pending_priority(delivered) * 0.05
```

Isso representa a pressao operacional de ainda haver entregas importantes em aberto.

## Heuristica

A heuristica usada nas buscas informadas e a distancia de Manhattan.

Ela estima a distancia entre a posicao atual do AGV e a doca do proximo pacote escolhido pela regra de prioridade:

```python
return manhattan((row, col), package_dock_position(next_package))
```

A distancia de Manhattan e adequada para grids com movimentos ortogonais, pois o AGV so anda em quatro direcoes:

- cima;
- baixo;
- esquerda;
- direita.

## Execucao dos Algoritmos

A funcao `run_algorithm` executa um algoritmo por vez.

Ela cria o estado inicial:

```python
initial_state = (START[0], START[1], tuple())
```

Isso significa que o AGV comeca em `START` e nenhum pacote foi entregue ainda.

Depois, executa o algoritmo:

```python
solution = algorithm(problem, graph_search=True, viewer=viewer)
```

O parametro `graph_search=True` faz a SimpleAI evitar revisitar estados ja explorados, o que reduz ciclos e repeticoes.

Para cada algoritmo, o codigo coleta:

- se encontrou solucao;
- custo total;
- quantidade de movimentos;
- ordem de entrega;
- nos visitados;
- iteracoes;
- tamanho maximo da fronteira;
- tempo de execucao;
- passos da solucao.

## Saida Gerada

A funcao `print_comparison` imprime uma tabela comparativa entre os algoritmos.

A tabela separa duas metricas de custo:

- `Custo total`: custo usado pelo algoritmo, considerando terreno, carga restante e pressao de prioridade.
- `Custo rota`: custo puro do caminho percorrido, somando apenas os custos dos terrenos atravessados.

O custo puro do caminho e calculado por `calculate_path_cost`, que percorre os passos da solucao e soma o custo do terreno de destino em cada movimento:

```python
total += TERRAIN_COSTS[GRID[row][col]]
```

A funcao `print_best_result` mostra o melhor resultado pelo menor custo.

A funcao `print_routes` imprime o passo a passo de cada solucao, mostrando:

- acao executada;
- posicao atual;
- carga restante do AGV;
- pacotes ja entregues.

## Interpretacao Esperada

Em geral:

- Busca em Largura tende a encontrar rotas com poucos movimentos, mas ignora custos diferentes de terreno.
- Busca em Profundidade pode encontrar solucoes muito longas e caras.
- Busca de Custo Uniforme considera os custos reais e tende a encontrar menor custo.
- Busca Gulosa usa apenas a heuristica, entao pode ser rapida, mas nem sempre encontra a rota mais barata.
- A* combina custo acumulado e heuristica, geralmente encontrando boas solucoes com menos exploracao que custo uniforme.

Neste problema, custo uniforme e A* costumam ser os melhores para justificar rotas eficientes, porque consideram os custos do ambiente e a heuristica de Manhattan.
