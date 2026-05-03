from .models import Posicao


def manhattan(a: Posicao, b: Posicao) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def formatar_posicao(pos: Posicao) -> str:
    return f"({pos[0]}, {pos[1]})"
