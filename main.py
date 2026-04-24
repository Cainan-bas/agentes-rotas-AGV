from simpleai.search import SearchProblem, astar
from simpleai.search.viewers import BaseViewer


GOAL = "Posição da doca"
START = "Posição inicial do AGV"
MAP = [[]]  # Grafo ou grid?
visited = set()  # Caminhos já visitados para evitar ciclos
obstacles = []  # Lista com a posição dos obstaculos no mapa(se for grafo pode ser uma lista de adjacências
#               se for grid pode ser uma lista de coordenadas)


class AGVProblem(SearchProblem):
    def actions(self, state):
        pass

    def result(self, state, action):
        # Resultado após tomar uma ação
        return state + action
        pass

    def is_goal(self, state):
        return state == GOAL

    def heuristic(self, state):
        return 0
        pass


def main():
    viewer_astar = BaseViewer()
    problem = AGVProblem(initial_state=START)
    result = astar(problem, graph_search=True, viewer=viewer_astar)
    print(result.state)
    pass


if __name__ == "__main__":
    main()
