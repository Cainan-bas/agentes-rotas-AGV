from simpleai.search import SearchProblem, astar
from simpleai.search.viewers import BaseViewer


GOAL = (4, 0)  # Posição final do AGV
START = (0, 0)  # Posição inicial do AGV
MAP = [
    [0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 1, 1, 0],
]  # Grafo ou grid?
obstacles = []  # Lista com a posição dos obstaculos no mapa| Acho que não vai precisar
directions = [
    (0, 1),  # direita
    (0, -1),  # esquerda
    (1, 0),  # baixo
    (-1, 0),  # cima
]

path = []


class AGVProblem(SearchProblem):
    def actions(self, state):
        x, y = state
        available_moves = []
        for dx, dy in directions:
            # Isso aqui verifica quais as direções ele pode tomar, considerando 0 como caminho aberto e 1 obstáculo
            # Não sei como implementar o custo aqui
            next_x, next_y = x + dx, y + dy
            if (
                next_x >= 0
                and next_x < len(MAP)
                and next_y >= 0
                and next_y < len(MAP[0])
                and MAP[next_x][next_y] == 0
            ):
                available_moves.append((next_x, next_y))

        return available_moves

    def result(self, state, action):
        # Resultado após tomar uma ação
        print(f"Movendo de {state} para {action}")
        return action

    def is_goal(self, state):
        return state == GOAL

    def heuristic(self, state):
        x, y = state
        return abs(x - GOAL[0]) + abs(y - GOAL[1])


def main():
    viewer_astar = BaseViewer()
    # viewer_breadth_first = BaseViewer()
    # viewer_depth_first = BaseViewer()
    # viewer_greedy = BaseViewer()
    # viewer_uniform_cost = BaseViewer()
    result = astar(
        AGVProblem(initial_state=START), graph_search=True, viewer=viewer_astar
    )

    print(result)
    print(viewer_astar.stats)


if __name__ == "__main__":
    main()
