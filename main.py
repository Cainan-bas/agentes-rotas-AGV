from src.charts import gerar_graficos
from src.config import ALGORITMOS, N_EXECUCOES, RESULTADOS_DIR
from src.instance import gerar_instancia_aleatoria
from src.map_renderer import gerar_mapa_txt
from src.mission import executar_missao
from src.reporting import (
    encontrar_primeira_falha,
    montar_resumo,
    preparar_pasta_resultados,
    salvar_relatorio_markdown,
    salvar_resultados_execucao,
    salvar_resumo_csv,
)
from src.statistics import criar_estatisticas, imprimir_tabela, registrar_resultado


def main():
    preparar_pasta_resultados(RESULTADOS_DIR)

    estatisticas = criar_estatisticas(ALGORITMOS)
    instancias = {}
    resultados_gerais = []

    for numero_execucao in range(1, N_EXECUCOES + 1):
        print(f"Execucao {numero_execucao}/{N_EXECUCOES}")
        instancia = gerar_instancia_aleatoria(numero_execucao)
        instancias[numero_execucao] = instancia

        resultados_execucao = []
        for nome, algoritmo in ALGORITMOS:
            resultado = executar_missao(instancia, nome, algoritmo)
            registrar_resultado(estatisticas, resultado)
            resultados_execucao.append(resultado)
            resultados_gerais.append(resultado)

        pasta_execucao = RESULTADOS_DIR / f"execucao_{numero_execucao:03d}"
        salvar_resultados_execucao(pasta_execucao, instancia, resultados_execucao)

    resumo = montar_resumo(estatisticas)
    salvar_resumo_csv(RESULTADOS_DIR / "resumo_geral.csv", resumo)

    graficos = gerar_graficos(
        resumo,
        resultados_gerais,
        RESULTADOS_DIR / "graficos",
    )

    falha = encontrar_primeira_falha(instancias, resultados_gerais)
    falha_analisada = None
    if falha is not None:
        instancia_falha, resultado_falha = falha
        mapa_falha = (
            RESULTADOS_DIR
            / f"execucao_{resultado_falha.execucao:03d}"
            / f"mapa_falha_{resultado_falha.algoritmo}.txt"
        )
        gerar_mapa_txt(instancia_falha, resultado_falha.caminho, mapa_falha)
        falha_analisada = (
            instancia_falha,
            resultado_falha,
            mapa_falha.relative_to(RESULTADOS_DIR).as_posix(),
        )

    salvar_relatorio_markdown(
        RESULTADOS_DIR / "relatorio_geral.md",
        resumo,
        {nome: caminho.relative_to(RESULTADOS_DIR) for nome, caminho in graficos.items()},
        falha_analisada,
        N_EXECUCOES,
    )

    imprimir_tabela(resumo)
    print(f"\nResultados gerados em: {RESULTADOS_DIR}")
    print(f"Relatorio geral: {RESULTADOS_DIR / 'relatorio_geral.md'}")


if __name__ == "__main__":
    main()
