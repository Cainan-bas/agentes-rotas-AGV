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
        super(AGVProblem, self).__init__(initial_state=start)
        self.goal_node = goal
        self.obstacles = obs
        self.congestion_zones = congestion
        self.grid_size = size

    def actions(self, state):
        x, y = state
        possiveis = [(x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]
        return [
            p
            for p in possiveis
            if 0 <= p[0] < self.grid_size[0]
            and 0 <= p[1] < self.grid_size[1]
            and p not in self.obstacles
        ]

    def result(self, state, action):
        return action

    def is_goal(self, state):
        return state == self.goal_node

    def cost(self, state, action, state2):
        if state2 in self.congestion_zones:
            return 10
        return 1

    def heuristic(self, state):
        # Distância de Manhattan: h(n) = |x1 - x2| + |y1 - y2|[cite: 3]
        return abs(state[0] - self.goal_node[0]) + abs(state[1] - self.goal_node[1])


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
        f.write("S=Início, G=Fim Missão, X=Obstáculo, ~=Tráfego, D=Doca, C=Coleta\n\n")
        for y in range(prob.grid_size[1] - 1, -1, -1):
            linha = f"{y:02d} |"
            for x in range(prob.grid_size[0]):
                p = (x, y)
                if p == path_total[0]:
                    linha += " S "
                elif p == path_total[-1]:
                    linha += " G "
                elif p == p_coleta:
                    linha += " C "
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


# --- Setup Dinâmico da Instância ---
tamanho = (75, 75)
p_inicio = (random.randint(0, 5), random.randint(0, 5))
p_coleta = (random.randint(30, 40), random.randint(30, 40))

# 4 Docas de entrega em locais fixos mas distintos[cite: 2]
docas_expedicao = [(10, 70), (30, 70), (50, 70), (70, 70)]

obs = set(map(lambda _: (random.randint(0, 74), random.randint(0, 74)), range(750)))
cong = set(map(lambda _: (random.randint(10, 60), random.randint(10, 60)), range(400)))

for p in [p_inicio, p_coleta] + docas_expedicao:
    obs.discard(p)
    cong.discard(p)

# Definição de 3 pacotes com docas específicas e prioridades[cite: 1, 2]
pacotes = [
    {
        "id": 1,
        "doca": docas_expedicao[random.randint(0, 3)],
        "prio": random.randint(1, 2),
    },
    {
        "id": 2,
        "doca": docas_expedicao[random.randint(0, 3)],
        "prio": random.randint(1, 2),
    },
    {
        "id": 3,
        "doca": docas_expedicao[random.randint(0, 3)],
        "prio": random.randint(1, 2),
    },
]

# Ordenação: Prioridade e, em empate, a doca mais próxima do ponto de coleta[cite: 1, 3]
pacotes.sort(
    key=lambda p: (
        p["prio"],
        abs(p["doca"][0] - p_coleta[0]) + abs(p["doca"][1] - p_coleta[1]),
    )
)

algoritmos = [
    ("Largura", breadth_first),
    ("Profundidade", depth_first),
    ("CustoUniforme", uniform_cost),
    ("Gulosa", greedy),
    ("AStar", astar),
]

resumo_final = []

for nome, busca_func in algoritmos:
    print(f"Iniciando missão completa para: {nome}")
    pos_agv_viva = p_inicio
    caminho_total_missao = []
    custo_total_missao = 0
    tempo_total_missao = 0
    sucesso_completo = True

    # O loop só para quando todos os pacotes forem entregues
    for pkg in pacotes:
        t_segmento_start = time.perf_counter()

        # Segmento 1: Da posição atual até o ponto de coleta[cite: 2]
        prob_para_coleta = AGVProblem(pos_agv_viva, p_coleta, obs, cong, tamanho)
        res_para_coleta = busca_func(prob_para_coleta, graph_search=True)

        if res_para_coleta:
            # Segmento 2: Do ponto de coleta até a doca designada[cite: 2]
            prob_para_doca = AGVProblem(p_coleta, pkg["doca"], obs, cong, tamanho)
            res_para_doca = busca_func(prob_para_doca, graph_search=True)

            if res_para_doca:
                tempo_total_missao += time.perf_counter() - t_segmento_start
                custo_total_missao += res_para_coleta.cost + res_para_doca.cost
                # Concatena os caminhos no rastro total
                caminho_total_missao.extend(
                    [n[1] for n in res_para_coleta.path()]
                    + [n[1] for n in res_para_doca.path()][1:]
                )
                # O AGV agora está na doca; esta é sua nova posição inicial[cite: 4]
                pos_agv_viva = pkg["doca"]
            else:
                sucesso_completo = False
                break
        else:
            sucesso_completo = False
            break

    if sucesso_completo:
        resumo_final.append((nome, custo_total_missao, tempo_total_missao))
        gerar_mapa_txt(
            caminho_total_missao,
            prob_para_coleta,
            docas_expedicao,
            f"resultado_{nome}.txt",
        )
    else:
        resumo_final.append((nome, "FALHA NA MISSÃO", "N/A"))

# --- Comparativo Final ---
print("\n" + "=" * 75)
print(f"{'ALGORITMO':<20} | {'CUSTO ACUMULADO':<20} | {'TEMPO DE EXECUÇÃO (s)':<20}")
print("-" * 75)
for n, c, t in resumo_final:
    t_val = f"{t:.6f}" if isinstance(t, float) else t
    print(f"{n:<20} | {str(c):<20} | {t_val:<20}")
print("=" * 75)
