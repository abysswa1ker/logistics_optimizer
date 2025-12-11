# -*- coding: utf-8 -*-
"""
Головний файл програми оптимізації логістичної мережі
"""

from services.data_loader import load_network_from_csv, validate_network_data, print_network_summary
from models.network import LogisticsNetwork


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

    print("\n" + "=" * 60)
    print("БАЗОВА ІНФРАСТРУКТУРА ПРАЦЮЄ!")
    print("=" * 60)
    print("\nНаступні кроки:")
    print("  1. Реалізувати обчислення витрат (cost_calculator.py)")
    print("  2. Реалізувати алгоритм МПО (coordinate.py)")
    print("  3. Додати оптимізацію до main.py")


if __name__ == "__main__":
    main()
