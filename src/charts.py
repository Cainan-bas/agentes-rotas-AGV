import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def _linhas_com_valor(resumo, chave):
    return [linha for linha in resumo if linha[chave] is not None]


def gerar_graficos(resumo, resultados_por_execucao, pasta_graficos):
    pasta_graficos.mkdir(parents=True, exist_ok=True)
    graficos = {}

    graficos["custo_medio"] = _grafico_barras(
        _linhas_com_valor(resumo, "custo_medio"),
        "custo_medio",
        "Custo medio por algoritmo",
        "Custo medio",
        pasta_graficos / "custo_medio.png",
    )
    graficos["tempo_medio"] = _grafico_barras(
        _linhas_com_valor(resumo, "tempo_medio"),
        "tempo_medio",
        "Tempo medio por algoritmo",
        "Tempo medio (s)",
        pasta_graficos / "tempo_medio.png",
    )
    graficos["falhas"] = _grafico_barras(
        resumo,
        "falhas",
        "Falhas por algoritmo",
        "Quantidade de falhas",
        pasta_graficos / "falhas.png",
    )
    graficos["custo_por_execucao"] = _grafico_linhas_custo(
        resultados_por_execucao,
        pasta_graficos / "custo_por_execucao.png",
    )

    return graficos


def _grafico_barras(linhas, chave, titulo, eixo_y, arquivo):
    algoritmos = [linha["algoritmo"] for linha in linhas]
    valores = [linha[chave] for linha in linhas]

    plt.figure(figsize=(10, 5))
    plt.bar(algoritmos, valores, color="#3b82f6")
    plt.title(titulo)
    plt.ylabel(eixo_y)
    plt.xlabel("Algoritmo")
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(arquivo, dpi=140)
    plt.close()
    return arquivo


def _grafico_linhas_custo(resultados_por_execucao, arquivo):
    series = {}
    for resultado in resultados_por_execucao:
        if not resultado.sucesso:
            continue
        series.setdefault(resultado.algoritmo, []).append(
            (resultado.execucao, resultado.custo)
        )

    plt.figure(figsize=(11, 5))
    for algoritmo, pontos in series.items():
        pontos_ordenados = sorted(pontos)
        execucoes = [ponto[0] for ponto in pontos_ordenados]
        custos = [ponto[1] for ponto in pontos_ordenados]
        plt.plot(execucoes, custos, marker="o", markersize=2.5, linewidth=1.2, label=algoritmo)

    plt.title("Custo total por execucao")
    plt.ylabel("Custo total")
    plt.xlabel("Execucao")
    plt.grid(True, linestyle="--", alpha=0.35)
    plt.legend()
    plt.tight_layout()
    plt.savefig(arquivo, dpi=140)
    plt.close()
    return arquivo
