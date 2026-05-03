import random

from .config import DOCAS, GRID_SIZE, N_CONGESTIONAMENTOS, N_OBSTACULOS, N_PACOTES
from .models import InstanciaAGV
from .utils import manhattan


def gerar_posicao_livre(grid_size, proibidas):
    while True:
        pos = (
            random.randint(0, grid_size[0] - 1),
            random.randint(0, grid_size[1] - 1),
        )
        if pos not in proibidas:
            return pos


def gerar_conjunto_aleatorio(quantidade, grid_size, proibidas):
    posicoes = set()
    while len(posicoes) < quantidade:
        pos = gerar_posicao_livre(grid_size, proibidas | posicoes)
        posicoes.add(pos)
    return posicoes


def gerar_instancia_aleatoria(id_execucao):
    """Cria uma instancia nova mantendo as quatro docas em posicoes fixas."""

    proibidas = set(DOCAS)
    inicio = gerar_posicao_livre(GRID_SIZE, proibidas)
    proibidas.add(inicio)

    coleta = gerar_posicao_livre(GRID_SIZE, proibidas)
    proibidas.add(coleta)

    obstaculos = gerar_conjunto_aleatorio(N_OBSTACULOS, GRID_SIZE, proibidas)
    proibidas |= obstaculos

    congestionamentos = gerar_conjunto_aleatorio(
        N_CONGESTIONAMENTOS,
        GRID_SIZE,
        proibidas,
    )

    pacotes = [
        {
            "id": pacote_id,
            "doca": random.choice(DOCAS),
            "prio": random.randint(1, 3),
        }
        for pacote_id in range(1, N_PACOTES + 1)
    ]

    return InstanciaAGV(
        id_execucao=id_execucao,
        inicio=inicio,
        coleta=coleta,
        docas=list(DOCAS),
        obstaculos=obstaculos,
        congestionamentos=congestionamentos,
        pacotes=pacotes,
    )


def ordenar_pacotes(pacotes, ponto_coleta):
    """Maior prioridade primeiro; empate pela doca mais proxima da coleta."""

    return sorted(
        pacotes,
        key=lambda pacote: (
            -pacote["prio"],
            manhattan(pacote["doca"], ponto_coleta),
        ),
    )
