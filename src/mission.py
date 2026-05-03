import time

from .config import GRID_SIZE
from .instance import ordenar_pacotes
from .models import ResultadoMissao
from .problem import AGVProblem


def extrair_caminho(resultado):
    return [state for _, state in resultado.path()]


def juntar_caminho(caminho_total, trecho):
    if not caminho_total:
        return list(trecho)
    return caminho_total + trecho[1:]


def executar_segmento(instancia, algoritmo, origem, destino):
    problema = AGVProblem(
        origem,
        destino,
        instancia.obstaculos,
        instancia.congestionamentos,
        GRID_SIZE,
    )
    return algoritmo(problema, graph_search=True)


def executar_missao(instancia, nome_algoritmo, algoritmo):
    """
    Executa a missao completa em segmentos.

    Para cada pacote: posicao atual -> coleta -> doca do pacote.
    Depois da entrega, a posicao atual passa a ser a doca atendida.
    """

    pacotes = ordenar_pacotes(instancia.pacotes, instancia.coleta)
    posicao_atual = instancia.inicio
    custo_total = 0
    caminho_total = []
    segmentos_resolvidos = 0
    inicio_tempo = time.perf_counter()

    try:
        for pacote in pacotes:
            segmentos = [
                ("ate_coleta", posicao_atual, instancia.coleta, pacote),
                ("ate_doca", instancia.coleta, pacote["doca"], pacote),
            ]

            for tipo, origem, destino, pacote_atual in segmentos:
                resultado = executar_segmento(instancia, algoritmo, origem, destino)
                if resultado is None:
                    tempo_total = time.perf_counter() - inicio_tempo
                    return ResultadoMissao(
                        execucao=instancia.id_execucao,
                        algoritmo=nome_algoritmo,
                        sucesso=False,
                        custo=None,
                        tempo=tempo_total,
                        caminho=caminho_total,
                        pacotes=pacotes,
                        distancia_percorrida=max(0, len(caminho_total) - 1),
                        segmentos_resolvidos=segmentos_resolvidos,
                        segmento_falha={
                            "tipo": tipo,
                            "origem": origem,
                            "destino": destino,
                            "pacote": pacote_atual,
                        },
                    )

                custo_total += resultado.cost
                segmentos_resolvidos += 1
                caminho_total = juntar_caminho(
                    caminho_total,
                    extrair_caminho(resultado),
                )

            posicao_atual = pacote["doca"]

    except Exception as exc:
        tempo_total = time.perf_counter() - inicio_tempo
        return ResultadoMissao(
            execucao=instancia.id_execucao,
            algoritmo=nome_algoritmo,
            sucesso=False,
            custo=None,
            tempo=tempo_total,
            caminho=caminho_total,
            pacotes=pacotes,
            distancia_percorrida=max(0, len(caminho_total) - 1),
            segmentos_resolvidos=segmentos_resolvidos,
            erro=repr(exc),
        )

    tempo_total = time.perf_counter() - inicio_tempo
    return ResultadoMissao(
        execucao=instancia.id_execucao,
        algoritmo=nome_algoritmo,
        sucesso=True,
        custo=custo_total,
        tempo=tempo_total,
        caminho=caminho_total,
        pacotes=pacotes,
        distancia_percorrida=max(0, len(caminho_total) - 1),
        segmentos_resolvidos=segmentos_resolvidos,
    )
