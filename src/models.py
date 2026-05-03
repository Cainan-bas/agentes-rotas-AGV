from dataclasses import dataclass


Posicao = tuple[int, int]


@dataclass(frozen=True)
class InstanciaAGV:
    id_execucao: int
    inicio: Posicao
    coleta: Posicao
    docas: list[Posicao]
    obstaculos: set[Posicao]
    congestionamentos: set[Posicao]
    pacotes: list[dict]


@dataclass
class ResultadoMissao:
    execucao: int
    algoritmo: str
    sucesso: bool
    custo: float | None
    tempo: float
    caminho: list[Posicao]
    pacotes: list[dict]
    distancia_percorrida: int
    segmentos_resolvidos: int
    segmento_falha: dict | None = None
    erro: str | None = None
