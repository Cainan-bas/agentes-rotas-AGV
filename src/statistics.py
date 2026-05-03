from statistics import mean


def criar_estatisticas(algoritmos):
    return {
        nome: {
            "custos": [],
            "tempos": [],
            "distancias": [],
            "sucessos": 0,
            "falhas": 0,
        }
        for nome, _ in algoritmos
    }


def registrar_resultado(estatisticas, resultado):
    dados = estatisticas[resultado.algoritmo]

    if resultado.sucesso:
        dados["custos"].append(resultado.custo)
        dados["tempos"].append(resultado.tempo)
        dados["distancias"].append(resultado.distancia_percorrida)
        dados["sucessos"] += 1
    else:
        dados["falhas"] += 1


def resumir_estatisticas(estatisticas):
    resumo = []
    for nome, dados in estatisticas.items():
        custos = dados["custos"]
        tempos = dados["tempos"]
        distancias = dados["distancias"]

        resumo.append(
            {
                "algoritmo": nome,
                "custo_medio": mean(custos) if custos else None,
                "custo_min": min(custos) if custos else None,
                "custo_max": max(custos) if custos else None,
                "tempo_medio": mean(tempos) if tempos else None,
                "tempo_min": min(tempos) if tempos else None,
                "tempo_max": max(tempos) if tempos else None,
                "distancia_media": mean(distancias) if distancias else None,
                "sucessos": dados["sucessos"],
                "falhas": dados["falhas"],
            }
        )
    return resumo


def imprimir_tabela(resumo):
    print("\n" + "=" * 137)
    print(
        f"{'ALGORITMO':<16} | "
        f"{'CUSTO MEDIO':>12} | {'CUSTO MIN':>9} | {'CUSTO MAX':>9} | "
        f"{'TEMPO MEDIO':>12} | {'TEMPO MIN':>10} | {'TEMPO MAX':>10} | "
        f"{'DIST MEDIA':>10} | {'SUCESSOS':>8} | {'FALHAS':>6}"
    )
    print("-" * 137)

    for linha in resumo:
        if linha["custo_medio"] is None:
            print(
                f"{linha['algoritmo']:<16} | "
                f"{'--':>12} | {'--':>9} | {'--':>9} | "
                f"{'--':>12} | {'--':>10} | {'--':>10} | "
                f"{'--':>10} | {linha['sucessos']:>8} | {linha['falhas']:>6}"
            )
            continue

        print(
            f"{linha['algoritmo']:<16} | "
            f"{linha['custo_medio']:>12.2f} | {linha['custo_min']:>9.2f} | {linha['custo_max']:>9.2f} | "
            f"{linha['tempo_medio']:>12.6f} | {linha['tempo_min']:>10.6f} | {linha['tempo_max']:>10.6f} | "
            f"{linha['distancia_media']:>10.2f} | {linha['sucessos']:>8} | {linha['falhas']:>6}"
        )

    print("=" * 137)
