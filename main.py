# -*- coding: utf-8 -*-
"""
Головний файл програми оптимізації логістичної мережі
"""

from services.data_loader import load_network_from_csv, validate_network_data, print_network_summary
from models.network import LogisticsNetwork
from optimizers.coordinate import CoordinateOptimizer


def main():
    """
    Основна функція програми
    """
    print("\n" + "=" * 60)
    print("ПРОГРАМА ОПТИМІЗАЦІЇ ЛОГІСТИЧНОЇ МЕРЕЖІ - MVP")
    print("=" * 60)

    # Крок 1: Завантаження даних
    print("\n[1/3] Завантаження даних з CSV...")
    try:
        centers, terminals, consumers = load_network_from_csv('data/network_data.csv')
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

    # Запуск оптимізації МПО
    print("\n\n" + "=" * 60)
    print("ЗАПУСК ОПТИМІЗАЦІЇ")
    print("=" * 60)

    optimizer = CoordinateOptimizer(
        network=network,
        step_size=2.0,
        max_iterations=50,
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

    print("\n" + "=" * 60)
    print("MVP ЗАВЕРШЕНО: ОПТИМІЗАЦІЯ ПРАЦЮЄ!")
    print("=" * 60)


if __name__ == "__main__":
    main()
