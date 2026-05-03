import csv
import json

from .instance import ordenar_pacotes
from .map_renderer import gerar_mapa_txt
from .statistics import resumir_estatisticas


def preparar_pasta_resultados(pasta):
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "graficos").mkdir(parents=True, exist_ok=True)


def salvar_resultados_execucao(pasta_execucao, instancia, resultados):
    pasta_execucao.mkdir(parents=True, exist_ok=True)
    salvar_instancia_markdown(pasta_execucao / "instancia.md", instancia)
    salvar_resultados_csv(pasta_execucao / "resultados.csv", resultados)
    salvar_resultados_json(pasta_execucao / "resultados.json", resultados)

    for resultado in resultados:
        if resultado.sucesso or resultado.segmento_falha is not None:
            gerar_mapa_txt(
                instancia,
                resultado.caminho,
                pasta_execucao / f"mapa_{resultado.algoritmo}.txt",
            )


def salvar_instancia_markdown(arquivo, instancia):
    pacotes_ordenados = ordenar_pacotes(instancia.pacotes, instancia.coleta)

    with open(arquivo, "w", encoding="utf-8") as md:
        md.write(f"# Execucao {instancia.id_execucao}\n\n")
        md.write(f"- Inicio: `{instancia.inicio}`\n")
        md.write(f"- Coleta: `{instancia.coleta}`\n")
        md.write(f"- Docas: `{instancia.docas}`\n")
        md.write(f"- Obstaculos: `{len(instancia.obstaculos)}`\n")
        md.write(f"- Zonas de congestionamento: `{len(instancia.congestionamentos)}`\n\n")
        md.write("## Pacotes ordenados\n\n")
        md.write("| ID | Doca | Prioridade |\n")
        md.write("|---:|:-----|-----------:|\n")
        for pacote in pacotes_ordenados:
            md.write(f"| {pacote['id']} | `{pacote['doca']}` | {pacote['prio']} |\n")


def salvar_resultados_csv(arquivo, resultados):
    with open(arquivo, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=campos_resultado())
        writer.writeheader()
        for resultado in resultados:
            writer.writerow(linha_resultado(resultado))


def salvar_resultados_json(arquivo, resultados):
    with open(arquivo, "w", encoding="utf-8") as jsonfile:
        json.dump([linha_resultado(resultado) for resultado in resultados], jsonfile, indent=2)


def campos_resultado():
    return [
        "execucao",
        "algoritmo",
        "sucesso",
        "custo",
        "tempo",
        "distancia_percorrida",
        "segmentos_resolvidos",
        "segmento_falha",
        "erro",
    ]


def linha_resultado(resultado):
    return {
        "execucao": resultado.execucao,
        "algoritmo": resultado.algoritmo,
        "sucesso": resultado.sucesso,
        "custo": resultado.custo if resultado.custo is not None else "",
        "tempo": resultado.tempo,
        "distancia_percorrida": resultado.distancia_percorrida,
        "segmentos_resolvidos": resultado.segmentos_resolvidos,
        "segmento_falha": resultado.segmento_falha or "",
        "erro": resultado.erro or "",
    }


def salvar_resumo_csv(arquivo, resumo):
    with open(arquivo, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "algoritmo",
                "custo_medio",
                "custo_min",
                "custo_max",
                "tempo_medio",
                "tempo_min",
                "tempo_max",
                "distancia_media",
                "sucessos",
                "falhas",
            ],
        )
        writer.writeheader()
        writer.writerows(resumo)


def salvar_relatorio_markdown(arquivo, resumo, graficos, falha_analisada, total_execucoes):
    with open(arquivo, "w", encoding="utf-8") as md:
        md.write("# Relatorio geral do experimento\n\n")
        md.write(f"Total de execucoes: `{total_execucoes}`\n\n")
        md.write("## Resultados agregados\n\n")
        md.write("| Algoritmo | Custo medio | Custo min | Custo max | Tempo medio (s) | Tempo min | Tempo max | Distancia media | Sucessos | Falhas |\n")
        md.write("|:----------|------------:|----------:|----------:|----------------:|----------:|----------:|----------------:|---------:|-------:|\n")
        for linha in resumo:
            md.write(
                f"| {linha['algoritmo']} | "
                f"{_fmt(linha['custo_medio'])} | {_fmt(linha['custo_min'])} | {_fmt(linha['custo_max'])} | "
                f"{_fmt(linha['tempo_medio'], 6)} | {_fmt(linha['tempo_min'], 6)} | {_fmt(linha['tempo_max'], 6)} | "
                f"{_fmt(linha['distancia_media'])} | {linha['sucessos']} | {linha['falhas']} |\n"
            )

        md.write("\n## Graficos\n\n")
        for titulo, arquivo_grafico in [
            ("Custo medio por algoritmo", graficos.get("custo_medio")),
            ("Tempo medio por algoritmo", graficos.get("tempo_medio")),
            ("Falhas por algoritmo", graficos.get("falhas")),
            ("Custo total por execucao", graficos.get("custo_por_execucao")),
        ]:
            if arquivo_grafico:
                md.write(f"### {titulo}\n\n")
                md.write(f"![{titulo}]({arquivo_grafico.as_posix()})\n\n")

        md.write("## Analise de falha\n\n")
        if falha_analisada is None:
            md.write(
                "Nenhuma falha foi registrada nesta bateria de execucoes. "
                "Todos os algoritmos encontraram rota para todos os segmentos das missoes testadas.\n"
            )
            return

        instancia, resultado, mapa_relativo = falha_analisada
        md.write(f"- Execucao: `{resultado.execucao}`\n")
        md.write(f"- Algoritmo: `{resultado.algoritmo}`\n")
        md.write(f"- Inicio: `{instancia.inicio}`\n")
        md.write(f"- Coleta: `{instancia.coleta}`\n")
        md.write(f"- Docas: `{instancia.docas}`\n")
        md.write(f"- Obstaculos: `{len(instancia.obstaculos)}`\n")
        md.write(f"- Congestionamentos: `{len(instancia.congestionamentos)}`\n")
        md.write(f"- Segmentos resolvidos antes da falha: `{resultado.segmentos_resolvidos}`\n")
        md.write(f"- Segmento de falha: `{resultado.segmento_falha}`\n")
        if resultado.erro:
            md.write(f"- Erro: `{resultado.erro}`\n")
        md.write(f"- Mapa: [{mapa_relativo}]({mapa_relativo})\n")


def encontrar_primeira_falha(instancias, resultados):
    for resultado in resultados:
        if not resultado.sucesso:
            return instancias[resultado.execucao], resultado
    return None


def montar_resumo(estatisticas):
    return resumir_estatisticas(estatisticas)


def _fmt(valor, casas=2):
    if valor is None:
        return "--"
    return f"{valor:.{casas}f}"
