from src.reporting import print_best_result, print_comparison, print_routes, save_results_markdown
from src.runner import run_all_algorithms


def main():
    results = run_all_algorithms()
    print_comparison(results)
    print_best_result(results)
    print_routes(results)
    save_results_markdown(results)


if __name__ == "__main__":
    main()
