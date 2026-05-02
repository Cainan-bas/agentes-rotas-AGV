from .constants import (
    AGV_CAPACITY,
    DOCKS,
    GRID_SIZE,
    PACKAGES,
    RESULTS_FILE,
    START,
    TERRAIN_COSTS,
)
from .utils import current_load


def print_scenario():
    print("Cenario: AGV com 3 pacotes ja recebidos e 4 docas disponiveis")
    print(f"Dimensao do grid: {GRID_SIZE}x{GRID_SIZE}")
    print(f"Inicio do AGV: {START}")
    print(f"Capacidade do AGV: {AGV_CAPACITY}")
    print("Regra de prioridade: maior prioridade primeiro; em empate, doca mais proxima.")
    print("Custos de terreno:")

    for terrain, cost in TERRAIN_COSTS.items():
        print(f"  {terrain}: {cost}")

    print("Docas:")
    for dock_id, position in DOCKS.items():
        print(f"  {dock_id}: {position}")

    print("Pacotes carregados:")
    for package_id, package_data in PACKAGES.items():
        dock_id = package_data["dock"]
        print(
            f"  {package_id}: doca={dock_id} {DOCKS[dock_id]} | "
            f"peso={package_data['weight']} | prioridade={package_data['priority']}"
        )


def print_comparison(results):
    print_scenario()
    print()

    header = (
        f"{'Algoritmo':<25}"
        f"{'Achou':<8}"
        f"{'Custo total':<14}"
        f"{'Custo rota':<13}"
        f"{'Mov.':<8}"
        f"{'Ordem':<16}"
        f"{'Visitados':<12}"
        f"{'Iter.':<8}"
        f"{'Fronteira':<10}"
        f"{'Tempo (s)':<10}"
    )
    print(header)
    print("-" * len(header))

    for result in results:
        found = "sim" if result["found"] else "nao"
        cost = f"{result['cost']:.2f}" if result["cost"] is not None else "-"
        path_cost = f"{result['path_cost']:.2f}" if result["found"] else "-"
        moves = result["moves"] if result["moves"] is not None else "-"
        order = "->".join(result["delivery_order"]) or "-"

        print(
            f"{result['algorithm']:<25}"
            f"{found:<8}"
            f"{cost:<14}"
            f"{path_cost:<13}"
            f"{moves!s:<8}"
            f"{order:<16}"
            f"{result['visited_nodes']:<12}"
            f"{result['iterations']:<8}"
            f"{result['max_fringe_size']:<10}"
            f"{result['time']:<10.6f}"
        )


def print_best_result(results):
    best_result = best_result_by_cost(results)

    if best_result is None:
        print("\nNenhum algoritmo encontrou uma solucao.")
        return

    print(
        "\nMelhor resultado por custo: "
        f"{best_result['algorithm']} com custo {best_result['cost']:.2f}, "
        f"{best_result['moves']} movimentos e ordem "
        f"{' -> '.join(best_result['delivery_order'])}."
    )


def best_result_by_cost(results):
    valid_results = [result for result in results if result["found"]]

    if not valid_results:
        return None

    return min(valid_results, key=lambda result: (result["cost"], result["moves"]))


def best_result_by_time(results):
    valid_results = [result for result in results if result["found"]]

    if not valid_results:
        return None

    return min(valid_results, key=lambda result: result["time"])


def print_routes(results):
    for result in results:
        print(f"\n--- {result['algorithm']} ---")

        if not result["found"]:
            print("Nenhuma solucao encontrada.")
            continue

        print(
            f"Custo total={result['cost']:.2f} | "
            f"Custo do caminho={result['path_cost']:.2f} | "
            f"Movimentos={result['moves']} | "
            f"Ordem de entrega={' -> '.join(result['delivery_order'])}"
        )

        for index, (action, state) in enumerate(result["steps"]):
            row, col, delivered = state
            action_text = format_action(action)
            print(
                f"{index:02d}. {action_text:<18} "
                f"posicao=({row}, {col}) "
                f"carga={current_load(delivered):>2}/{AGV_CAPACITY} "
                f"entregues={list(delivered)}"
            )


def format_action(action):
    if action is None:
        return "inicio"

    action_type, value = action

    if action_type == "mover":
        return f"mover {value}"

    if action_type == "entregar":
        dock_id = PACKAGES[value]["dock"]
        return f"entregar {value}/{dock_id}"

    return str(action)


def save_results_markdown(results):
    RESULTS_FILE.write_text(generate_results_markdown(results), encoding="utf-8")
    print(f"\nArquivo de resultados atualizado: {RESULTS_FILE}")


def generate_results_markdown(results):
    best_cost = best_result_by_cost(results)
    best_time = best_result_by_time(results)
    lines = [
        "# Resultados da Execucao",
        "",
        "## Informacoes Gerais",
        "",
        f"O experimento usa um grid `{GRID_SIZE}x{GRID_SIZE}` para representar o centro de distribuicao automatizado.",
        "",
        f"Posicao inicial do AGV: `{START}`.",
        "",
        f"Capacidade maxima do AGV: `{AGV_CAPACITY}` unidades de peso.",
        "",
        "Regra de entrega dos pacotes:",
        "",
        "1. entregar primeiro o pacote com maior prioridade;",
        "2. em caso de empate de prioridade, escolher a doca mais proxima da posicao atual do AGV;",
        "3. se ainda houver empate, usar o identificador do pacote como desempate.",
        "",
        "## Pacotes",
        "",
        "| Pacote | Doca de entrega | Posicao da doca | Peso | Prioridade |",
        "|---|---:|---:|---:|---:|",
    ]

    for package_id, package_data in PACKAGES.items():
        dock_id = package_data["dock"]
        lines.append(
            f"| {package_id} | {dock_id} | {DOCKS[dock_id]} | "
            f"{package_data['weight']} | {package_data['priority']} |"
        )

    lines.extend(
        [
            "",
            "## Docas",
            "",
            "| Doca | Posicao |",
            "|---|---:|",
        ]
    )

    for dock_id, position in DOCKS.items():
        lines.append(f"| {dock_id} | {position} |")

    lines.extend(
        [
            "",
            "Observacao: existem 4 docas disponiveis, mas esta instancia usa 3 pacotes, cada um associado a uma doca de entrega.",
            "",
            "## Custos de Terreno",
            "",
            "| Simbolo | Significado | Custo |",
            "|---|---|---:|",
            "| `.` | piso normal | 1.0 |",
            "| `F` | corredor rapido | 0.7 |",
            "| `L` | area lenta / manobra dificil | 2.0 |",
            "| `~` | congestionamento | 4.0 |",
            "| `X` | obstaculo fixo | nao atravessavel |",
            "| `B` | bloqueio temporario | nao atravessavel |",
            "",
            "O custo total usado pelos algoritmos considera:",
            "",
            "```text",
            "custo do terreno * fator de carga + pressao de prioridade",
            "```",
            "",
            "O custo da rota considera apenas a soma dos terrenos atravessados.",
            "",
            "## Tabela Comparativa",
            "",
            "| Algoritmo | Achou | Custo total | Custo rota | Movimentos | Ordem | Nos visitados | Iteracoes | Fronteira max. | Tempo (s) |",
            "|---|---|---:|---:|---:|---|---:|---:|---:|---:|",
        ]
    )

    for result in results:
        found = "sim" if result["found"] else "nao"
        cost = f"{result['cost']:.2f}" if result["cost"] is not None else "-"
        path_cost = f"{result['path_cost']:.2f}" if result["path_cost"] is not None else "-"
        moves = result["moves"] if result["moves"] is not None else "-"
        order = " -> ".join(result["delivery_order"]) or "-"
        lines.append(
            f"| {result['algorithm']} | {found} | {cost} | {path_cost} | "
            f"{moves} | {order} | {result['visited_nodes']} | "
            f"{result['iterations']} | {result['max_fringe_size']} | "
            f"{result['time']:.6f} |"
        )

    lines.extend(["", "## Melhor Resultado por Custo", ""])

    if best_cost is None:
        lines.append("Nenhum algoritmo encontrou uma solucao.")
    else:
        same_cost_results = [
            result
            for result in results
            if result["found"] and result["cost"] == best_cost["cost"]
        ]
        names = " e ".join(result["algorithm"] for result in same_cost_results)
        lines.extend(
            [
                f"O menor custo total foi `{best_cost['cost']:.2f}`.",
                "",
                f"Esse custo foi alcancado por: `{names}`.",
                "",
                f"Ordem de entrega: `{' -> '.join(best_cost['delivery_order'])}`.",
            ]
        )

        if len(same_cost_results) > 1:
            best_by_nodes = min(same_cost_results, key=lambda result: result["visited_nodes"])
            lines.extend(
                [
                    "",
                    "Como houve empate no custo, o melhor desempate por nos visitados foi:",
                    "",
                    f"`{best_by_nodes['algorithm']}`, com `{best_by_nodes['visited_nodes']}` nos visitados.",
                ]
            )

    lines.extend(["", "## Melhor Resultado por Tempo de Execucao", ""])

    if best_time is None:
        lines.append("Nenhum algoritmo encontrou uma solucao.")
    else:
        lines.extend(
            [
                f"O menor tempo de execucao foi `{best_time['time']:.6f}` segundos.",
                "",
                f"Algoritmo mais rapido nesta execucao: `{best_time['algorithm']}`.",
            ]
        )

        if best_cost is not None and best_time["algorithm"] != best_cost["algorithm"]:
            lines.extend(
                [
                    "",
                    f"Apesar disso, `{best_time['algorithm']}` nao foi o melhor por custo total nesta execucao.",
                ]
            )

    lines.extend(
        [
            "",
            "## Conclusao",
            "",
            "Para esta instancia, os algoritmos de custo tendem a produzir as rotas mais eficientes em custo total.",
            "",
            "O A* e uma boa escolha para defesa do trabalho quando empata no menor custo e explora menos nos que a Busca de Custo Uniforme.",
        ]
    )

    return "\n".join(lines) + "\n"
