from .config import GRID_SIZE
from .instance import ordenar_pacotes


def simbolo_seta(origem, destino):
    dx = destino[0] - origem[0]
    dy = destino[1] - origem[1]

    if dx == 1:
        return "v"
    if dx == -1:
        return "^"
    if dy == 1:
        return ">"
    if dy == -1:
        return "<"
    return "."


def linhas_mapa(instancia, caminho):
    fim = caminho[-1] if caminho else instancia.inicio
    setas = {}

    for origem, destino in zip(caminho, caminho[1:]):
        setas[origem] = simbolo_seta(origem, destino)

    linhas = []
    for x in range(GRID_SIZE[0]):
        linha = []
        for y in range(GRID_SIZE[1]):
            pos = (x, y)

            # Pontos especiais aparecem por cima da rota, congestionamento
            # e obstaculos para facilitar a leitura do mapa.
            if pos == instancia.inicio:
                char = "S"
            elif pos == instancia.coleta:
                char = "C"
            elif pos in instancia.docas and pos == fim:
                char = "DG"
            elif pos in instancia.docas:
                char = "D"
            elif pos == fim:
                char = "G"
            elif pos in instancia.obstaculos:
                char = "X"
            elif pos in instancia.congestionamentos:
                char = "~"
            elif pos in setas:
                char = setas[pos]
            else:
                char = "."

            linha.append(f"{char:<2}")
        linhas.append("".join(linha))

    return linhas


def gerar_mapa_txt(instancia, caminho, arquivo):
    """Gera um arquivo .txt com o mapa e a rota percorrida pelo AGV."""

    with open(arquivo, "w", encoding="utf-8") as mapa:
        mapa.write("Legenda: S=inicio, C=coleta, D=doca, G=fim, X=obstaculo, ~=congestionamento\n")
        mapa.write("Celulas especiais podem combinar marcadores, como DG para doca final.\n")
        mapa.write(f"Inicio: {instancia.inicio}\n")
        mapa.write(f"Coleta: {instancia.coleta}\n")
        mapa.write(f"Docas: {instancia.docas}\n")
        mapa.write(f"Pacotes: {ordenar_pacotes(instancia.pacotes, instancia.coleta)}\n\n")
        mapa.write("\n".join(linhas_mapa(instancia, caminho)))
        mapa.write("\n")
