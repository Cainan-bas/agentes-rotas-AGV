from pathlib import Path


GRID_SIZE = 70
START = (0, 0)
AGV_CAPACITY = 15
DELIVERY_ACTION_COST = 0
RESULTS_FILE = Path(__file__).resolve().parents[1] / "./docs/resultados.md"

TERRAIN_COSTS = {
    ".": 1.0,
    "F": 0.7,
    "L": 2.0,
    "~": 4.0,
}

DOCKS = {
    "D1": (5, 65),
    "D2": (65, 4),
    "D3": (68, 68),
    "D4": (50, 35),
}

PACKAGES = {
    "P1": {"dock": "D3", "weight": 6, "priority": 5},
    "P2": {"dock": "D2", "weight": 4, "priority": 3},
    "P3": {"dock": "D1", "weight": 5, "priority": 5},
}

MOVES = {
    "cima": (-1, 0),
    "baixo": (1, 0),
    "esquerda": (0, -1),
    "direita": (0, 1),
}
