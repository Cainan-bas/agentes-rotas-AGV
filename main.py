import time
import random
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
# MAPA TXT (CORRIGIDO)
# =========================================================
def gerar_mapa_txt(path_total, prob, docas_lista, nome_arq):
    setas = {}

    for i in range(len(path_total) - 1):
        at, prox = path_total[i], path_total[i + 1]
        dx, dy = prox[0] - at[0], prox[1] - at[1]

        if dx == 1:
            setas[at] = "→"
        elif dx == -1:
            setas[at] = "←"
        elif dy == 1:
            setas[at] = "↑"
        elif dy == -1:
            setas[at] = "↓"

    with open(nome_arq, "w", encoding="utf-8") as f:
        f.write(f"Relatório de Missão: {nome_arq}\n")
        f.write("S=Início, G=Fim, C=Coleta, D=Doca, X=Obstáculo, ~=Tráfego\n\n")

        for y in range(prob.grid_size[1] - 1, -1, -1):
            linha = f"{y:02d} |"

            for x in range(prob.grid_size[0]):
                p = (x, y)

                # PRIORIDADE VISUAL CORRETA
                if p == path_total[0]:
                    linha += " S "
                elif p == p_coleta:
                    linha += " C "
                elif p in docas_lista and p == path_total[-1]:
                    linha += " G "  # destino final
                elif p in docas_lista:
                    linha += " D "
                elif p in setas:
                    linha += f" {setas[p]} "
                elif p in prob.obstacles:
                    linha += " X "
                elif p in prob.congestion_zones:
                    linha += " ~ "
                else:
                    linha += " . "

            f.write(linha + "\n")


# =========================================================
# GERAÇÃO DA INSTÂNCIA
# =========================================================

tamanho = (50, 50)

p_inicio = (random.randint(0, 5), random.randint(0, 5))
p_coleta = (random.randint(20, 30), random.randint(20, 30))

# ✔️ 4 docas fixas
docas_expedicao = [(5, 45), (20, 45), (35, 45), (45, 45)]

obs = {(random.randint(0, 49), random.randint(0, 49)) for _ in range(400)}
cong = {(random.randint(10, 40), random.randint(10, 40)) for _ in range(200)}

# garante que pontos importantes não sejam bloqueados
for p in [p_inicio, p_coleta] + docas_expedicao:
    obs.discard(p)
    cong.discard(p)


# =========================================================
# PACOTES
# =========================================================

pacotes = [
    {"id": 1, "doca": random.choice(docas_expedicao), "prio": random.randint(1, 2)},
    {"id": 2, "doca": random.choice(docas_expedicao), "prio": random.randint(1, 2)},
    {"id": 3, "doca": random.choice(docas_expedicao), "prio": random.randint(1, 2)},
]


def distancia_coleta(doca):
    return abs(doca[0] - p_coleta[0]) + abs(doca[1] - p_coleta[1])


# ✔️ prioridade maior primeiro + desempate por distância
pacotes.sort(key=lambda p: (-p["prio"], distancia_coleta(p["doca"])))


# =========================================================
# EXECUÇÃO
# =========================================================

algoritmos = [
    ("Largura", breadth_first),
    ("Profundidade", depth_first),
    ("CustoUniforme", uniform_cost),
    ("Gulosa", greedy),
    ("AStar", astar),
]

resumo_final = []

for nome, busca_func in algoritmos:
    print(f"Iniciando missão: {nome}")

    pos_agv = p_inicio
    caminho_total = []
    custo_total = 0
    tempo_total = 0
    sucesso = True

    for pkg in pacotes:
        t0 = time.perf_counter()

        # até coleta
        prob1 = AGVProblem(pos_agv, p_coleta, obs, cong, tamanho)
        res1 = busca_func(prob1, graph_search=True)

        if not res1:
            sucesso = False
            break

        # coleta até doca
        prob2 = AGVProblem(p_coleta, pkg["doca"], obs, cong, tamanho)
        res2 = busca_func(prob2, graph_search=True)

        if not res2:
            sucesso = False
            break

        tempo_total += time.perf_counter() - t0
        custo_total += res1.cost + res2.cost

        # concatena caminho
        caminho_total.extend(
            [n[1] for n in res1.path()] + [n[1] for n in res2.path()][1:]
        )

        pos_agv = pkg["doca"]

    if sucesso:
        resumo_final.append((nome, custo_total, tempo_total))
        gerar_mapa_txt(caminho_total, prob1, docas_expedicao, f"resultado_{nome}.txt")
    else:
        resumo_final.append((nome, "FALHA", "N/A"))


# =========================================================
# RESULTADO FINAL
# =========================================================

print("\n" + "=" * 70)
print(f"{'ALGORITMO':<20} | {'CUSTO':<15} | {'TEMPO (s)':<15}")
print("-" * 70)

for n, c, t in resumo_final:
    t_val = f"{t:.6f}" if isinstance(t, float) else t
    print(f"{n:<20} | {str(c):<15} | {t_val:<15}")

print("=" * 70)
