# Resultados da Execucao

## Informacoes Gerais

O experimento usa um grid `70x70` para representar o centro de distribuicao automatizado.

Posicao inicial do AGV: `(0, 0)`.

Capacidade maxima do AGV: `15` unidades de peso.

Regra de entrega dos pacotes:

1. entregar primeiro o pacote com maior prioridade;
2. em caso de empate de prioridade, escolher a doca mais proxima da posicao atual do AGV;
3. se ainda houver empate, usar o identificador do pacote como desempate.

## Pacotes

| Pacote | Doca de entrega | Posicao da doca | Peso | Prioridade |
|---|---:|---:|---:|---:|
| P1 | D3 | (68, 68) | 6 | 5 |
| P2 | D2 | (65, 4) | 4 | 3 |
| P3 | D1 | (5, 65) | 5 | 5 |

## Docas

| Doca | Posicao |
|---|---:|
| D1 | (5, 65) |
| D2 | (65, 4) |
| D3 | (68, 68) |
| D4 | (50, 35) |

Observacao: existem 4 docas disponiveis, mas esta instancia usa 3 pacotes, cada um associado a uma doca de entrega.

## Custos de Terreno

| Simbolo | Significado | Custo |
|---|---|---:|
| `.` | piso normal | 1.0 |
| `F` | corredor rapido | 0.7 |
| `L` | area lenta / manobra dificil | 2.0 |
| `~` | congestionamento | 4.0 |
| `X` | obstaculo fixo | nao atravessavel |
| `B` | bloqueio temporario | nao atravessavel |

O custo total usado pelos algoritmos considera:

```text
custo do terreno * fator de carga + pressao de prioridade
```

O custo da rota considera apenas a soma dos terrenos atravessados.

## Tabela Comparativa

| Algoritmo | Achou | Custo total | Custo rota | Movimentos | Ordem | Nos visitados | Iteracoes | Fronteira max. | Tempo (s) |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|
| Busca em Largura | sim | 384.94 | 183.80 | 203 | P3 -> P1 -> P2 | 13093 | 13093 | 121 | 1.654537 |
| Busca em Profundidade | sim | 3648.60 | 1716.30 | 1731 | P1 -> P3 -> P2 | 7912 | 7912 | 2873 | 20.712392 |
| Busca de Custo Uniforme | sim | 342.02 | 160.20 | 213 | P3 -> P1 -> P2 | 11838 | 11838 | 160 | 2.753534 |
| Busca Gulosa | sim | 416.74 | 195.80 | 215 | P3 -> P1 -> P2 | 8230 | 8230 | 303 | 2.571680 |
| A* | sim | 342.02 | 160.20 | 213 | P3 -> P1 -> P2 | 7706 | 7706 | 161 | 2.010953 |

## Melhor Resultado por Custo

O menor custo total foi `342.02`.

Esse custo foi alcancado por: `Busca de Custo Uniforme e A*`.

Ordem de entrega: `P3 -> P1 -> P2`.

Como houve empate no custo, o melhor desempate por nos visitados foi:

`A*`, com `7706` nos visitados.

## Melhor Resultado por Tempo de Execucao

O menor tempo de execucao foi `1.654537` segundos.

Algoritmo mais rapido nesta execucao: `Busca em Largura`.

Apesar disso, `Busca em Largura` nao foi o melhor por custo total nesta execucao.

## Conclusao

Para esta instancia, os algoritmos de custo tendem a produzir as rotas mais eficientes em custo total.

O A* e uma boa escolha para defesa do trabalho quando empata no menor custo e explora menos nos que a Busca de Custo Uniforme.
