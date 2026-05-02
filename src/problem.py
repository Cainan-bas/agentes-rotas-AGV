from simpleai.search import SearchProblem

from .constants import (
    AGV_CAPACITY,
    DELIVERY_ACTION_COST,
    MOVES,
    PACKAGES,
    TERRAIN_COSTS,
)
from .grid import GRID, is_valid_position
from .utils import (
    choose_next_package,
    current_load,
    manhattan,
    package_dock_position,
    pending_priority,
)


class AGVDeliveryProblem(SearchProblem):
    def actions(self, state):
        row, col, delivered = state
        position = (row, col)
        possible_actions = []
        next_package = choose_next_package(position, delivered)

        if next_package is not None and package_dock_position(next_package) == position:
            possible_actions.append(("entregar", next_package))
            return possible_actions

        for move_name, (d_row, d_col) in MOVES.items():
            next_position = (row + d_row, col + d_col)

            if is_valid_position(next_position):
                possible_actions.append(("mover", move_name))

        return possible_actions

    def result(self, state, action):
        row, col, delivered = state
        action_type, value = action

        if action_type == "mover":
            d_row, d_col = MOVES[value]
            return row + d_row, col + d_col, delivered

        if action_type == "entregar":
            return row, col, tuple(sorted(delivered + (value,)))

        return state

    def is_goal(self, state):
        _, _, delivered = state
        return len(delivered) == len(PACKAGES)

    def cost(self, state, action, state2):
        action_type, _ = action

        if action_type == "entregar":
            return DELIVERY_ACTION_COST

        row, col, delivered = state2
        terrain = GRID[row][col]
        terrain_cost = TERRAIN_COSTS[terrain]
        load_factor = 1 + current_load(delivered) / AGV_CAPACITY
        priority_pressure = pending_priority(delivered) * 0.05

        return terrain_cost * load_factor + priority_pressure

    def heuristic(self, state):
        row, col, delivered = state
        next_package = choose_next_package((row, col), delivered)

        if next_package is None:
            return 0

        return manhattan((row, col), package_dock_position(next_package))
