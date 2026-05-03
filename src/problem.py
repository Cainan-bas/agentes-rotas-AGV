from simpleai.search import SearchProblem

from .models import Posicao
from .utils import manhattan


class AGVProblem(SearchProblem):
    """Problema de busca entre dois pontos do grid."""

    def __init__(
        self,
        start: Posicao,
        goal: Posicao,
        obstacles: set[Posicao],
        congestion_zones: set[Posicao],
        grid_size: Posicao,
    ):
        super().__init__(initial_state=start)
        self.goal = goal
        self.obstacles = obstacles
        self.congestion_zones = congestion_zones
        self.grid_size = grid_size

    def actions(self, state):
        x, y = state
        candidates = [
            (x, y + 1),
            (x, y - 1),
            (x + 1, y),
            (x - 1, y),
        ]

        return [
            pos
            for pos in candidates
            if self._inside_grid(pos) and pos not in self.obstacles
        ]

    def result(self, state, action):
        return action

    def is_goal(self, state):
        return state == self.goal

    def cost(self, state, action, state2):
        return 10 if state2 in self.congestion_zones else 1

    def heuristic(self, state):
        return manhattan(state, self.goal)

    def _inside_grid(self, pos):
        x, y = pos
        return 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]
