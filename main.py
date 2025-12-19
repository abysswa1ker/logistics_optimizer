# -*- coding: utf-8 -*-
"""
Головний файл програми оптимізації логістичної мережі
"""

import os
import copy
import time
from pathlib import Path
from services.data_loader import load_network_from_csv, validate_network_data, print_network_summary
from models.network import LogisticsNetwork
from optimizers.coordinate import CoordinateOptimizer
from optimizers.genetic import GeneticOptimizer
from services.visualization import NetworkVisualizer
from services.export import ResultsExporter


def get_csv_files(data_dir: str = 'data') -> list:
    """
    Отримує список CSV файлів з директорії

    Args:
        data_dir: Директорія з даними

    Returns:
        Список шляхів до CSV файлів
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        return []

    csv_files = list(data_path.glob('*.csv'))
    return sorted(csv_files)


def display_file_menu(csv_files: list) -> int:
    """
    Відображає меню вибору файлів

    Args:
        csv_files: Список CSV файлів

    Returns:
        Індекс обраного файлу або -1 для виходу
    """
    print("\n" + "=" * 60)
    print("ДОСТУПНІ ФАЙЛИ ДАНИХ")
    print("=" * 60)

    if not csv_files:
        print("Немає CSV файлів у директорії data/")
        return -1

    for idx, file_path in enumerate(csv_files, 1):
        print(f"{idx}. {file_path.name}")

    print(f"{len(csv_files) + 1}. Вихід")
    print("=" * 60)

    while True:
        try:
            choice = input(f"\nОберіть файл (1-{len(csv_files) + 1}): ").strip()
            choice_num = int(choice)

            if choice_num == len(csv_files) + 1:
                return -1

            if 1 <= choice_num <= len(csv_files):
                return choice_num - 1
            else:
                print(f"Будь ласка, введіть число від 1 до {len(csv_files) + 1}")
        except ValueError:
            print("Будь ласка, введіть коректне число")
        except KeyboardInterrupt:
            print("\n\nПрограму перервано користувачем")
            return -1


def display_optimization_mode_menu() -> str:
    """
    Відображає меню вибору режиму оптимізації

    Returns:
        'mpo' для МПО, 'ga' для ГА, 'compare' для порівняння, '' для виходу
    """
    print("\n" + "=" * 60)
    print("ВИБЕРІТЬ РЕЖИМ ОПТИМІЗАЦІЇ")
    print("=" * 60)
    print("1. Тільки МПО (Метод покоординатного спуску)")
    print("2. Тільки ЕМ-ГА (Еволюційний метод - генетичний алгоритм)")
    print("3. Порівняння обох методів")
    print("4. Вихід")
    print("=" * 60)

    while True:
        try:
            choice = input("\nОберіть режим (1-4): ").strip()
            choice_num = int(choice)

            if choice_num == 1:
                return 'mpo'
            elif choice_num == 2:
                return 'ga'
            elif choice_num == 3:
                return 'compare'
            elif choice_num == 4:
                return ''
            else:
                print("Будь ласка, введіть число від 1 до 4")
        except ValueError:
            print("Будь ласка, введіть коректне число")
        except KeyboardInterrupt:
            print("\n\nПрограму перервано користувачем")
            return ''


def run_comparison(network: LogisticsNetwork, initial_costs: dict):
    """
    Запускає порівняльний аналіз МПО та ЕМ-ГА

    Args:
        network: Логістична мережа
        initial_costs: Початкові витрати мережі

    Returns:
        Словник з результатами обох методів
    """
    print("\n" + "=" * 60)
    print("ПОРІВНЯЛЬНИЙ АНАЛІЗ МЕТОДІВ ОПТИМІЗАЦІЇ")
    print("=" * 60)
    print("\nБудуть послідовно запущені два методи на однакових вхідних даних:")
    print("  1. МПО (Метод покоординатного спуску)")
    print("  2. ЕМ-ГА (Еволюційний метод - генетичний алгоритм)")
    print("=" * 60)

    results = {}

    # Запуск МПО
    print("\n\n" + "=" * 60)
    print("МЕТОД 1: МПО (МЕТОД ПОКООРДИНАТНОГО СПУСКУ)")
    print("=" * 60)

    # Створюємо копію мережі для МПО
    network_mpo = copy.deepcopy(network)

    start_time = time.time()
    optimizer_mpo = CoordinateOptimizer(
        network=network_mpo,
        step_size=5.0,
        max_iterations=100,
        tolerance=0.1
    )
    mpo_results = optimizer_mpo.optimize(verbose=True)
    mpo_time = time.time() - start_time

    # Підраховуємо активні термінали
    mpo_active_terminals = sum(1 for t in network_mpo.terminals if t.is_active)

    results['mpo'] = {
        'initial_cost': mpo_results['initial_cost'],
        'final_cost': mpo_results['final_cost'],
        'absolute_improvement': mpo_results['absolute_improvement'],
        'percentage_improvement': mpo_results['percentage_improvement'],
        'iterations': mpo_results.get('iterations', ''),
        'active_terminals': mpo_active_terminals,
        'execution_time': mpo_time,
        'network': network_mpo
    }

    # Запуск ЕМ-ГА
    print("\n\n" + "=" * 60)
    print("МЕТОД 2: ЕМ-ГА (ЕВОЛЮЦІЙНИЙ МЕТОД - ГЕНЕТИЧНИЙ АЛГОРИТМ)")
    print("=" * 60)

    # Створюємо копію мережі для ГА
    network_ga = copy.deepcopy(network)

    start_time = time.time()
    optimizer_ga = GeneticOptimizer(
        network=network_ga,
        population_size=50,
        generations=100,
        mutation_rate=0.1,
        crossover_rate=0.8
    )
    ga_results = optimizer_ga.optimize(verbose=True)
    ga_time = time.time() - start_time

    # Підраховуємо активні термінали
    ga_active_terminals = sum(1 for t in network_ga.terminals if t.is_active)

    results['ga'] = {
        'initial_cost': ga_results['initial_cost'],
        'final_cost': ga_results['final_cost'],
        'absolute_improvement': ga_results['absolute_improvement'],
        'percentage_improvement': ga_results['percentage_improvement'],
        'active_terminals': ga_active_terminals,
        'execution_time': ga_time,
        'network': network_ga
    }

    return results


def print_comparison_table(results: dict):
    """
    Виводить порівняльну таблицю результатів

    Args:
        results: Словник з результатами обох методів
    """
    print("\n\n" + "=" * 80)
    print("ПОРІВНЯЛЬНА ТАБЛИЦЯ РЕЗУЛЬТАТІВ")
    print("=" * 80)

    # Заголовок таблиці
    print(f"\n{'Показник':<40} {'МПО':>15} {'ЕМ-ГА':>15}")
    print("-" * 80)

    mpo = results['mpo']
    ga = results['ga']

    # Рядки таблиці
    print(f"{'Початкові витрати (грн)':<40} {mpo['initial_cost']:>15,.2f} {ga['initial_cost']:>15,.2f}")
    print(f"{'Фінальні витрати (грн)':<40} {mpo['final_cost']:>15,.2f} {ga['final_cost']:>15,.2f}")
    print(f"{'Абсолютне покращення (грн)':<40} {mpo['absolute_improvement']:>15,.2f} {ga['absolute_improvement']:>15,.2f}")
    print(f"{'Відносне покращення (%)':<40} {mpo['percentage_improvement']:>15,.2f} {ga['percentage_improvement']:>15,.2f}")
    print(f"{'Активних терміналів після оптимізації':<40} {mpo['active_terminals']:>15} {ga['active_terminals']:>15}")
    print(f"{'Час виконання (сек)':<40} {mpo['execution_time']:>15,.2f} {ga['execution_time']:>15,.2f}")

    print("=" * 80)

    # Визначаємо кращий метод
    print("\n" + "=" * 80)
    print("ВИСНОВОК")
    print("=" * 80)

    # Порівнюємо за фінальними витратами (нижчі = краще)
    if mpo['final_cost'] < ga['final_cost']:
        better_method = "МПО"
        cost_diff = ga['final_cost'] - mpo['final_cost']
        print(f"\n🏆 Кращий результат показав метод: {better_method}")
        print(f"\n   МПО досяг на {cost_diff:,.2f} грн нижчих витрат, ніж ЕМ-ГА")
        print(f"   ({mpo['final_cost']:,.2f} грн проти {ga['final_cost']:,.2f} грн)")
    elif ga['final_cost'] < mpo['final_cost']:
        better_method = "ЕМ-ГА"
        cost_diff = mpo['final_cost'] - ga['final_cost']
        print(f"\n🏆 Кращий результат показав метод: {better_method}")
        print(f"\n   ЕМ-ГА досяг на {cost_diff:,.2f} грн нижчих витрат, ніж МПО")
        print(f"   ({ga['final_cost']:,.2f} грн проти {mpo['final_cost']:,.2f} грн)")
    else:
        print(f"\n🤝 Обидва методи показали однакові фінальні витрати")
        print(f"   ({mpo['final_cost']:,.2f} грн)")

    # Додаткові спостереження
    print(f"\nДодаткові спостереження:")

    # Порівняння швидкості
    if mpo['execution_time'] < ga['execution_time']:
        time_diff = ga['execution_time'] - mpo['execution_time']
        print(f"  • МПО працював швидше на {time_diff:.2f} сек")
    elif ga['execution_time'] < mpo['execution_time']:
        time_diff = mpo['execution_time'] - ga['execution_time']
        print(f"  • ЕМ-ГА працював швидше на {time_diff:.2f} сек")

    # Порівняння кількості активних терміналів
    if mpo['active_terminals'] != ga['active_terminals']:
        print(f"  • МПО залишив {mpo['active_terminals']} активних терміналів, "
              f"ЕМ-ГА - {ga['active_terminals']}")

    print("=" * 80)


def main():
    """
    Основна функція програми
    """
    print("\n" + "=" * 60)
    print("ПРОГРАМА ОПТИМІЗАЦІЇ ЛОГІСТИЧНОЇ МЕРЕЖІ - MVP")
    print("=" * 60)

    # Отримуємо список CSV файлів
    csv_files = get_csv_files('data')

    if not csv_files:
        print("\n✗ Не знайдено CSV файлів у директорії data/")
        print("Створіть файл з даними у форматі CSV та спробуйте знову")
        return

    # Відображаємо меню та отримуємо вибір користувача
    selected_idx = display_file_menu(csv_files)

    if selected_idx == -1:
        print("\nПрограму завершено")
        return

    selected_file = csv_files[selected_idx]
    file_basename = selected_file.stem  # Ім'я файлу без розширення

    print(f"\n✓ Обрано файл: {selected_file.name}")

    # Крок 1: Завантаження даних
    print("\n" + "=" * 60)
    print("ПРОГРАМА ОПТИМІЗАЦІЇ ЛОГІСТИЧНОЇ МЕРЕЖІ - MVP")
    print("=" * 60)
    print("\n[1/3] Завантаження даних з CSV...")
    try:
        centers, terminals, consumers = load_network_from_csv(str(selected_file))
        print("✓ Дані успішно завантажено")
    except Exception as e:
        print(f"✗ Помилка завантаження даних: {e}")
        return

    # Крок 2: Валідація даних
    print("\n[2/3] Валідація даних...")
    try:
        validate_network_data(centers, terminals, consumers)
        print("✓ Дані валідні")
    except Exception as e:
        print(f"✗ Помилка валідації: {e}")
        return

    # Крок 3: Створення мережі
    print("\n[3/3] Створення логістичної мережі...")
    try:
        network = LogisticsNetwork(centers, terminals, consumers)
        print("✓ Мережа створена та ініціалізована")
    except Exception as e:
        print(f"✗ Помилка створення мережі: {e}")
        return

    # Виводимо короткий огляд
    print_network_summary(centers, terminals, consumers)

    # Виводимо детальний стан мережі
    network.print_network_state()

    # Обчислюємо та виводимо початкові витрати
    print("\n" + "=" * 60)
    print("ПОЧАТКОВІ ВИТРАТИ")
    print("=" * 60)
    initial_costs = network.calculate_costs()
    network.cost_calculator.print_cost_breakdown(initial_costs)

    # Зберігаємо копію початкової мережі для візуалізації
    network_before = copy.deepcopy(network)

    # Вибір режиму оптимізації
    optimization_mode = display_optimization_mode_menu()

    if not optimization_mode:
        print("\nПрограму завершено")
        return

    # Виконуємо оптимізацію згідно обраного режиму
    if optimization_mode == 'compare':
        # Режим порівняння
        comparison_results = run_comparison(network, initial_costs)
        print_comparison_table(comparison_results)

        # Використовуємо результат кращого методу для візуалізації
        mpo_cost = comparison_results['mpo']['final_cost']
        ga_cost = comparison_results['ga']['final_cost']

        if mpo_cost <= ga_cost:
            network_after = comparison_results['mpo']['network']
            optimizer_name = "МПО - кращий"
        else:
            network_after = comparison_results['ga']['network']
            optimizer_name = "ЕМ-ГА - кращий"

        final_costs = network_after.calculate_costs()

    elif optimization_mode == 'mpo':
        # Тільки МПО
        print("\n\n" + "=" * 60)
        print("ЗАПУСК ОПТИМІЗАЦІЇ: МПО")
        print("=" * 60)

        start_time = time.time()
        optimizer = CoordinateOptimizer(
            network=network,
            step_size=5.0,
            max_iterations=100,
            tolerance=0.1
        )

        results = optimizer.optimize(verbose=True)
        execution_time = time.time() - start_time
        optimizer.print_results()

        network_after = network
        final_costs = network.calculate_costs()
        optimizer_name = "МПО"

        # Зберігаємо параметри та результати для експорту
        mpo_parameters = {
            'step_size': 5.0,
            'max_iterations': 100,
            'tolerance': 0.1
        }
        mpo_results = results

    else:  # optimization_mode == 'ga'
        # Тільки ЕМ-ГА
        print("\n\n" + "=" * 60)
        print("ЗАПУСК ОПТИМІЗАЦІЇ: ЕМ-ГА")
        print("=" * 60)

        start_time = time.time()
        optimizer = GeneticOptimizer(
            network=network,
            population_size=50,
            generations=100,
            mutation_rate=0.1,
            crossover_rate=0.8
        )

        results = optimizer.optimize(verbose=True)
        execution_time = time.time() - start_time
        optimizer.print_results()

        network_after = network
        final_costs = network.calculate_costs()
        optimizer_name = "ЕМ-ГА"

        # Зберігаємо параметри та результати для експорту
        ga_parameters = {
            'population_size': 50,
            'generations': 100,
            'mutation_rate': 0.1,
            'crossover_rate': 0.8
        }
        ga_results = results

    # Візуалізація (для всіх режимів)
    print("\n" + "=" * 60)
    print("ГЕНЕРАЦІЯ ГРАФІКІВ")
    print("=" * 60)

    visualizer = NetworkVisualizer()

    # Порівняння мереж до/після
    mode_suffix = {'mpo': 'mpo', 'ga': 'ga', 'compare': 'comparison'}[optimization_mode]
    network_comparison_path = f'results/{file_basename}_{mode_suffix}_network_comparison.png'
    visualizer.compare_networks(
        network_before=network_before,
        network_after=network_after,
        costs_before=initial_costs,
        costs_after=final_costs,
        save_path=network_comparison_path,
        optimizer_name=optimizer_name
    )

    # Порівняння витрат
    cost_comparison_path = f'results/{file_basename}_{mode_suffix}_cost_comparison.png'
    visualizer.plot_cost_comparison(
        costs_before=initial_costs,
        costs_after=final_costs,
        save_path=cost_comparison_path
    )

    # Додатковий графік порівняння методів (тільки для режиму порівняння)
    methods_comparison_path = None
    if optimization_mode == 'compare':
        methods_comparison_path = f'results/{file_basename}_methods_comparison.png'
        costs_mpo = comparison_results['mpo']['network'].calculate_costs()
        costs_ga = comparison_results['ga']['network'].calculate_costs()
        visualizer.plot_methods_comparison(
            costs_before=initial_costs,
            costs_mpo=costs_mpo,
            costs_ga=costs_ga,
            save_path=methods_comparison_path
        )

    # Експорт результатів
    print("\n" + "=" * 60)
    print("ЕКСПОРТ РЕЗУЛЬТАТІВ")
    print("=" * 60)

    exporter = ResultsExporter()

    if optimization_mode == 'compare':
        # Експорт порівняння
        mpo_export_data = {
            'parameters': {
                'step_size': 5.0,
                'max_iterations': 100,
                'tolerance': 0.1
            },
            'results': comparison_results['mpo'],
            'network': comparison_results['mpo']['network'],
            'execution_time': comparison_results['mpo']['execution_time']
        }

        ga_export_data = {
            'parameters': {
                'population_size': 50,
                'generations': 100,
                'mutation_rate': 0.1,
                'crossover_rate': 0.8
            },
            'results': comparison_results['ga'],
            'network': comparison_results['ga']['network'],
            'execution_time': comparison_results['ga']['execution_time']
        }

        export_path = exporter.export_comparison(
            dataset_name=file_basename,
            mpo_data=mpo_export_data,
            ga_data=ga_export_data,
            network_before=network_before
        )
        print(f"✓ Порівняльні результати експортовано: {export_path}")

    elif optimization_mode == 'mpo':
        # Експорт МПО
        export_path = exporter.export_single_optimization(
            dataset_name=file_basename,
            optimizer_type='МПО',
            parameters=mpo_parameters,
            results=mpo_results,
            network_before=network_before,
            network_after=network_after,
            execution_time=execution_time
        )
        print(f"✓ Результати МПО експортовано: {export_path}")

    else:  # ga
        # Експорт ЕМ-ГА
        export_path = exporter.export_single_optimization(
            dataset_name=file_basename,
            optimizer_type='ЕМ-ГА',
            parameters=ga_parameters,
            results=ga_results,
            network_before=network_before,
            network_after=network_after,
            execution_time=execution_time
        )
        print(f"✓ Результати ЕМ-ГА експортовано: {export_path}")

    print("\n" + "=" * 60)
    print("ПРОГРАМУ ЗАВЕРШЕНО")
    print("=" * 60)
    print(f"\n✓ Результати збережено:")
    print(f"  - {network_comparison_path}")
    print(f"  - {cost_comparison_path}")
    if methods_comparison_path:
        print(f"  - {methods_comparison_path}")
    print(f"  - {export_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
