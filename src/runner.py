from time import perf_counter

from simpleai.search import astar, breadth_first, depth_first, greedy, uniform_cost
from simpleai.search.viewers import BaseViewer

from .constants import START, TERRAIN_COSTS
from .grid import GRID
from .problem import AGVDeliveryProblem


ALGORITHMS = [
    ("Busca em Largura", breadth_first),
    ("Busca em Profundidade", depth_first),
    ("Busca de Custo Uniforme", uniform_cost),
    ("Busca Gulosa", greedy),
    ("A*", astar),
]


def run_all_algorithms():
    return [run_algorithm(name, algorithm) for name, algorithm in ALGORITHMS]


def run_algorithm(name, algorithm):
    initial_state = (START[0], START[1], tuple())
    problem = AGVDeliveryProblem(initial_state=initial_state)
    viewer = BaseViewer()

    start_time = perf_counter()
    solution = algorithm(problem, graph_search=True, viewer=viewer)
    elapsed_time = perf_counter() - start_time

    if solution is None:
        return {
            "algorithm": name,
            "found": False,
            "cost": None,
            "path_cost": None,
            "moves": None,
            "delivery_order": [],
            "visited_nodes": viewer.stats.get("visited_nodes", 0),
            "iterations": viewer.stats.get("iterations", 0),
            "max_fringe_size": viewer.stats.get("max_fringe_size", 0),
            "time": elapsed_time,
            "steps": [],
        }

    steps = solution.path()

    return {
        "algorithm": name,
        "found": True,
        "cost": solution.cost,
        "path_cost": calculate_path_cost(steps),
        "moves": count_moves(steps),
        "delivery_order": extract_delivery_order(steps),
        "visited_nodes": viewer.stats.get("visited_nodes", 0),
        "iterations": viewer.stats.get("iterations", 0),
        "max_fringe_size": viewer.stats.get("max_fringe_size", 0),
        "time": elapsed_time,
        "steps": steps,
    }


def count_moves(steps):
    return sum(1 for action, _ in steps if action is not None and action[0] == "mover")


def calculate_path_cost(steps):
    total = 0

    for action, state in steps:
        if action is None or action[0] != "mover":
            continue

        row, col, _ = state
        total += TERRAIN_COSTS[GRID[row][col]]

    return total


def extract_delivery_order(steps):
    return [action[1] for action, _ in steps if action is not None and action[0] == "entregar"]
