from pathlib import Path

from simpleai.search import astar, breadth_first, depth_first, greedy, uniform_cost


N_EXECUCOES = 50
GRID_SIZE = (50, 50)
DOCAS = [(5, 45), (20, 45), (35, 45), (45, 45)]
N_OBSTACULOS = 400
N_CONGESTIONAMENTOS = 200
N_PACOTES = 3

RESULTADOS_DIR = Path("resultados")

ALGORITMOS = [
    ("Largura", breadth_first),
    ("Profundidade", depth_first),
    ("CustoUniforme", uniform_cost),
    ("Gulosa", greedy),
    ("AStar", astar),
]
