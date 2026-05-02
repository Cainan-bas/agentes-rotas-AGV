import time
import random
from statistics import mean
from simpleai.search import (
    SearchProblem,
    astar,
    breadth_first,
    depth_first,
    uniform_cost,
    greedy,
)


class AGVProblem(SearchProblem):
    def __init__(self, start, goal, obs, congestion, size):
        super().__init__(initial_state=start)
        self.goal_node = goal
        self.obstacles = obs
        self.congestion_zones = congestion
        self.grid_size = size

    def actions(self, state):
        x, y = state
        moves = [(x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]
        return [
            p
            for p in moves
            if 0 <= p[0] < self.grid_size[0]
            and 0 <= p[1] < self.grid_size[1]
            and p not in self.obstacles
        ]

    def result(self, state, action):
        return action

    def is_goal(self, state):
        return state == self.goal_node

    def cost(self, state, action, state2):
        return 10 if state2 in self.congestion_zones else 1

    def heuristic(self, state):
        return abs(state[0] - self.goal_node[0]) + abs(state[1] - self.goal_node[1])


# =========================================================
# CONFIG
# =========================================================

N_EXECUCOES = 50
tamanho = (50, 50)

algoritmos = [
    ("Largura", breadth_first),
    ("Profundidade", depth_first),
    ("CustoUniforme", uniform_cost),
    ("Gulosa", greedy),
    ("AStar", astar),
]

# guarda resultados
estatisticas = {nome: {"custos": [], "tempos": []} for nome, _ in algoritmos}


# =========================================================
# LOOP DE EXECUÇÕES
# =========================================================

for execucao in range(N_EXECUCOES):
    print(f"Execução {execucao + 1}/{N_EXECUCOES}")

    # mapa aleatório
    p_inicio = (random.randint(0, 5), random.randint(0, 5))
    p_coleta = (random.randint(20, 30), random.randint(20, 30))

    docas = [(5, 45), (20, 45), (35, 45), (45, 45)]

    obs = {(random.randint(0, 49), random.randint(0, 49)) for _ in range(400)}
    cong = {(random.randint(10, 40), random.randint(10, 40)) for _ in range(200)}

    for p in [p_inicio, p_coleta] + docas:
        obs.discard(p)
        cong.discard(p)

    # pacotes
    pacotes = [
        {"id": 1, "doca": random.choice(docas), "prio": random.randint(1, 2)},
        {"id": 2, "doca": random.choice(docas), "prio": random.randint(1, 2)},
        {"id": 3, "doca": random.choice(docas), "prio": random.randint(1, 2)},
    ]

    def dist(d):
        return abs(d[0] - p_coleta[0]) + abs(d[1] - p_coleta[1])

    pacotes.sort(key=lambda p: (-p["prio"], dist(p["doca"])))

    # roda todos os algoritmos
    for nome, busca_func in algoritmos:
        pos = p_inicio
        custo_total = 0
        tempo_total = 0
        sucesso = True

        for pkg in pacotes:
            t0 = time.perf_counter()

            prob1 = AGVProblem(pos, p_coleta, obs, cong, tamanho)
            res1 = busca_func(prob1, graph_search=True)

            if not res1:
                sucesso = False
                break

            prob2 = AGVProblem(p_coleta, pkg["doca"], obs, cong, tamanho)
            res2 = busca_func(prob2, graph_search=True)

            if not res2:
                sucesso = False
                break

            tempo_total += time.perf_counter() - t0
            custo_total += res1.cost + res2.cost

            pos = pkg["doca"]

        if sucesso:
            estatisticas[nome]["custos"].append(custo_total)
            estatisticas[nome]["tempos"].append(tempo_total)


# =========================================================
# RESULTADOS
# =========================================================

print("\n" + "=" * 80)
print(
    f"{'ALGORITMO':<18} | {'CUSTO MÉDIO':<12} | {'MIN':<8} | {'MAX':<8} | {'TEMPO MÉDIO':<14} | {'MIN':<10} | {'MAX':<10}"
)
print("-" * 80)

for nome in estatisticas:
    custos = estatisticas[nome]["custos"]
    tempos = estatisticas[nome]["tempos"]

    if len(custos) == 0:
        print(f"{nome:<18} | FALHA")
        continue

    print(
        f"{nome:<18} | "
        f"{mean(custos):<12.2f} | {min(custos):<8} | {max(custos):<8} | "
        f"{mean(tempos):<14.6f} | {min(tempos):<10.6f} | {max(tempos):<10.6f}"
    )

print("=" * 80)
