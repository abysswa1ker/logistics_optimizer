# -*- coding: utf-8 -*-
"""
Головний файл програми оптимізації логістичної мережі
"""

import os
import copy
from pathlib import Path
from services.data_loader import load_network_from_csv, validate_network_data, print_network_summary
from models.network import LogisticsNetwork
from optimizers.coordinate import CoordinateOptimizer
from services.visualization import NetworkVisualizer


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

    # Запуск оптимізації МПО
    print("\n\n" + "=" * 60)
    print("ЗАПУСК ОПТИМІЗАЦІЇ")
    print("=" * 60)

    optimizer = CoordinateOptimizer(
        network=network,
        step_size=5.0,  # Збільшено для швидшого переміщення
        max_iterations=100,  # Збільшено для повної оптимізації
        tolerance=0.1
    )

    # Виконуємо оптимізацію
    results = optimizer.optimize(verbose=True)

    # Виводимо оптимізовану мережу
    print("\n" + "=" * 60)
    print("СТАН МЕРЕЖІ ПІСЛЯ ОПТИМІЗАЦІЇ")
    print("=" * 60)
    network.print_network_state()

    # Виводимо фінальні витрати
    print("\n" + "=" * 60)
    print("ФІНАЛЬНІ ВИТРАТИ")
    print("=" * 60)
    final_costs = network.calculate_costs()
    network.cost_calculator.print_cost_breakdown(final_costs)

    # Виводимо результати оптимізації
    optimizer.print_results()

    # Візуалізація
    print("\n" + "=" * 60)
    print("ГЕНЕРАЦІЯ ГРАФІКІВ")
    print("=" * 60)

    visualizer = NetworkVisualizer()

    # Порівняння мереж до/після
    network_comparison_path = f'results/{file_basename}_network_comparison.png'
    visualizer.compare_networks(
        network_before=network_before,
        network_after=network,
        costs_before=initial_costs,
        costs_after=final_costs,
        save_path=network_comparison_path
    )

    # Порівняння витрат
    cost_comparison_path = f'results/{file_basename}_cost_comparison.png'
    visualizer.plot_cost_comparison(
        costs_before=initial_costs,
        costs_after=final_costs,
        save_path=cost_comparison_path
    )

    print("\n" + "=" * 60)
    print("MVP ЗАВЕРШЕНО: ОПТИМІЗАЦІЯ ТА ВІЗУАЛІЗАЦІЯ ПРАЦЮЮТЬ!")
    print("=" * 60)
    print(f"\n✓ Результати збережено:")
    print(f"  - {network_comparison_path}")
    print(f"  - {cost_comparison_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
