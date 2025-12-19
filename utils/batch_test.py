"""
Пакетне тестування оптимізаторів на мережах різних розмірів
"""

import time
import sys
import os
import copy

# Додаємо батьківську директорію до шляху
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from models.network import LogisticsNetwork
from optimizers.coordinate import CoordinateOptimizer
from optimizers.genetic import GeneticOptimizer
from services.export import ResultsExporter
from services.data_loader import load_network_from_csv


def run_optimization_test(network_path: str, n: int):
    """
    Запускає тест оптимізації для заданої мережі

    Args:
        network_path: Шлях до файлу мережі
        n: Розмірність задачі (кількість споживачів)

    Returns:
        Словник з результатами тестування
    """
    print(f"\n{'=' * 60}")
    print(f"ТЕСТУВАННЯ МЕРЕЖІ n={n}")
    print(f"{'=' * 60}")

    # Завантаження мережі
    print(f"Завантаження: {network_path}")
    centers, terminals, consumers = load_network_from_csv(network_path)
    network = LogisticsNetwork(centers, terminals, consumers)

    # Підрахунок початкової вартості
    initial_costs = network.calculate_costs()
    print(f"Початкова вартість: {initial_costs['total_cost']:.2f}")

    results = {
        'n': n,
        'initial_cost': initial_costs['total_cost']
    }

    # ========== ТЕСТ МПО ==========
    print(f"\n--- МЕТОД ПАРАЛЕЛЬНОЇ ОПТИМІЗАЦІЇ (МПО) ---")
    network_mpo = copy.deepcopy(network)

    mpo = CoordinateOptimizer(
        network=network_mpo,
        max_iterations=100
    )

    start_time = time.time()
    mpo_results = mpo.optimize(verbose=False)
    mpo_time = time.time() - start_time

    mpo_costs = network_mpo.calculate_costs()

    # Відносна похибка δC = (C_метод - C_optimal) / C_optimal * 100%
    # Для спрощення вважаємо оптимальним результат МПО (як еталон)
    mpo_error = 0.0  # МПО приймаємо за еталон

    print(f"Кінцева вартість: {mpo_costs['total_cost']:.2f}")
    print(f"Покращення: {mpo_results['percentage_improvement']:.2f}%")
    print(f"Час виконання: {mpo_time:.2f} с")
    print(f"Ітерацій: {mpo_results.get('iterations', 'N/A')}")

    results['mpo_cost'] = mpo_costs['total_cost']
    results['mpo_improvement'] = mpo_results['percentage_improvement']
    results['mpo_time'] = mpo_time
    results['mpo_iterations'] = mpo_results.get('iterations', 0)
    results['mpo_error'] = mpo_error

    # ========== ТЕСТ ЕМ-ГА ==========
    print(f"\n--- ЕВОЛЮЦІЙНО-МОДИФІКОВАНИЙ ГЕНЕТИЧНИЙ АЛГОРИТМ (ЕМ-ГА) ---")
    network_ga = copy.deepcopy(network)

    ga = GeneticOptimizer(
        network=network_ga,
        population_size=100,
        generations=50,
        mutation_rate=0.1,
        crossover_rate=0.8
    )

    start_time = time.time()
    ga_results = ga.optimize(verbose=False)
    ga_time = time.time() - start_time

    ga_costs = network_ga.calculate_costs()

    # Відносна похибка ЕМ-ГА відносно МПО
    # δC_GA = (C_GA - C_MPO) / C_MPO * 100%
    if mpo_costs['total_cost'] > 0:
        ga_error = ((ga_costs['total_cost'] - mpo_costs['total_cost']) /
                    mpo_costs['total_cost'] * 100)
    else:
        ga_error = 0.0

    print(f"Кінцева вартість: {ga_costs['total_cost']:.2f}")
    print(f"Покращення: {ga_results['percentage_improvement']:.2f}%")
    print(f"Час виконання: {ga_time:.2f} с")
    print(f"Поколінь: 50")
    print(f"Відносна похибка до МПО: {ga_error:.2f}%")

    results['ga_cost'] = ga_costs['total_cost']
    results['ga_improvement'] = ga_results['percentage_improvement']
    results['ga_time'] = ga_time
    results['ga_generations'] = 50
    results['ga_error'] = ga_error

    return results


def run_batch_tests():
    """Запускає пакетне тестування всіх мереж"""
    print("=" * 60)
    print("ПАКЕТНЕ ТЕСТУВАННЯ МЕТОДІВ ОПТИМІЗАЦІЇ")
    print("=" * 60)

    # Мережі для тестування
    test_networks = [
        (os.path.join(PROJECT_ROOT, 'data', 'network_n15.csv'), 15),
        (os.path.join(PROJECT_ROOT, 'data', 'network_n20.csv'), 20),
        (os.path.join(PROJECT_ROOT, 'data', 'network_n25.csv'), 25),
        (os.path.join(PROJECT_ROOT, 'data', 'network_n30.csv'), 30),
        (os.path.join(PROJECT_ROOT, 'data', 'network_n35.csv'), 35),
        (os.path.join(PROJECT_ROOT, 'data', 'network_n40.csv'), 40),
    ]

    all_results = []

    for network_path, n in test_networks:
        try:
            result = run_optimization_test(network_path, n)
            all_results.append(result)
        except Exception as e:
            print(f"\nПОМИЛКА при тестуванні {network_path}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # ========== ЗВЕДЕНА ТАБЛИЦЯ ==========
    print(f"\n{'=' * 80}")
    print("ЗВЕДЕНА ТАБЛИЦЯ РЕЗУЛЬТАТІВ")
    print(f"{'=' * 80}")

    print(f"\n{'n':>3} | {'δC(МПО)':>10} | {'δC(ЕМ-ГА)':>10} | {'T(МПО)':>10} | {'T(ЕМ-ГА)':>10}")
    print(f"{'-' * 3}-+-{'-' * 10}-+-{'-' * 10}-+-{'-' * 10}-+-{'-' * 10}")

    for result in all_results:
        print(f"{result['n']:3d} | {result['mpo_error']:9.2f}% | "
              f"{result['ga_error']:9.2f}% | {result['mpo_time']:9.2f}s | "
              f"{result['ga_time']:9.2f}s")

    # Порівняння з очікуваними значеннями
    expected_data = {
        15: {'mpo_error': 0.17, 'ga_error': 1.86, 'mpo_time': 0.52, 'ga_time': 0.22},
        20: {'mpo_error': 0.32, 'ga_error': 2.54, 'mpo_time': 3.03, 'ga_time': 0.71},
        25: {'mpo_error': 0.56, 'ga_error': 3.12, 'mpo_time': 5.24, 'ga_time': 1.86},
        30: {'mpo_error': 0.72, 'ga_error': 3.61, 'mpo_time': 11.86, 'ga_time': 3.91},
        35: {'mpo_error': 0.88, 'ga_error': 4.81, 'mpo_time': 21.35, 'ga_time': 8.13},
        40: {'mpo_error': 0.99, 'ga_error': 6.84, 'mpo_time': 35.26, 'ga_time': 14.01},
    }

    print(f"\n{'=' * 80}")
    print("ПОРІВНЯННЯ З ОЧІКУВАНИМИ ЗНАЧЕННЯМИ")
    print(f"{'=' * 80}")
    print(f"\n{'Параметр':20} | {'n=15':>8} | {'n=20':>8} | {'n=25':>8} | "
          f"{'n=30':>8} | {'n=35':>8} | {'n=40':>8}")
    print(f"{'-' * 20}-+-{'-' * 8}-+-{'-' * 8}-+-{'-' * 8}-+-{'-' * 8}-+-{'-' * 8}-+-{'-' * 8}")

    # Час МПО
    print(f"{'T(МПО) очікуване':20} | ", end="")
    for n in [15, 20, 25, 30, 35, 40]:
        print(f"{expected_data[n]['mpo_time']:7.2f}s | ", end="")
    print()

    print(f"{'T(МПО) фактичне':20} | ", end="")
    for result in all_results:
        print(f"{result['mpo_time']:7.2f}s | ", end="")
    print()

    print()

    # Час ЕМ-ГА
    print(f"{'T(ЕМ-ГА) очікуване':20} | ", end="")
    for n in [15, 20, 25, 30, 35, 40]:
        print(f"{expected_data[n]['ga_time']:7.2f}s | ", end="")
    print()

    print(f"{'T(ЕМ-ГА) фактичне':20} | ", end="")
    for result in all_results:
        print(f"{result['ga_time']:7.2f}s | ", end="")
    print()

    print()

    # Похибка ЕМ-ГА
    print(f"{'δC(ЕМ-ГА) очікуване':20} | ", end="")
    for n in [15, 20, 25, 30, 35, 40]:
        print(f"{expected_data[n]['ga_error']:7.2f}% | ", end="")
    print()

    print(f"{'δC(ЕМ-ГА) фактичне':20} | ", end="")
    for result in all_results:
        print(f"{result['ga_error']:7.2f}% | ", end="")
    print()

    print(f"\n{'=' * 80}")
    print("ВИСНОВКИ")
    print(f"{'=' * 80}")
    print("\nПОЯСНЕННЯ:")
    print("- δC(МПО) = 0% тому що МПО приймається за еталонне рішення")
    print("- δC(ЕМ-ГА) показує відхилення результату ЕМ-ГА від МПО у відсотках")
    print("- T(n) - час виконання оптимізації в секундах")
    print("\nОЧІКУВАННЯ:")
    print("- ЕМ-ГА швидше за МПО (менший час T)")
    print("- ЕМ-ГА має більшу похибку δC (гірша якість рішення)")
    print("- З ростом n зростають час та похибка для обох методів")

    # Експорт у CSV
    print(f"\n{'=' * 80}")
    print("ЕКСПОРТ РЕЗУЛЬТАТІВ")
    print(f"{'=' * 80}")

    exporter = ResultsExporter(export_dir=os.path.join(PROJECT_ROOT, "results", "batch_tests"))

    import csv
    filepath = os.path.join(PROJECT_ROOT, "results", "batch_tests", "performance_comparison.csv")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        f.write('sep=,\n')
        writer = csv.writer(f)

        # Заголовки
        writer.writerow([
            'n',
            'Initial Cost',
            'MPO Cost',
            'GA Cost',
            'MPO Improvement %',
            'GA Improvement %',
            'MPO Error %',
            'GA Error %',
            'MPO Time (s)',
            'GA Time (s)',
            'MPO Iterations',
            'GA Generations'
        ])

        # Дані
        for result in all_results:
            writer.writerow([
                result['n'],
                round(result['initial_cost'], 2),
                round(result['mpo_cost'], 2),
                round(result['ga_cost'], 2),
                round(result['mpo_improvement'], 2),
                round(result['ga_improvement'], 2),
                round(result['mpo_error'], 2),
                round(result['ga_error'], 2),
                round(result['mpo_time'], 2),
                round(result['ga_time'], 2),
                result['mpo_iterations'],
                result['ga_generations']
            ])

    print(f"\nРезультати експортовано: {filepath}")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    run_batch_tests()
