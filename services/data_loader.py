# -*- coding: utf-8 -*-
"""
Завантаження даних з CSV файлів
"""

import csv
from typing import List, Tuple
from models.element import Center, Terminal, Consumer, Element


def load_network_from_csv(file_path: str) -> Tuple[List[Center], List[Terminal], List[Consumer]]:
    """
    Завантажує дані мережі з CSV файлу

    Формат CSV:
    id,x,y,type,demand,terminal_cost,processing_cost

    Args:
        file_path: Шлях до CSV файлу

    Returns:
        Кортеж з трьох списків: (центри, термінали, споживачі)
    """
    centers = []
    terminals = []
    consumers = []

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            element_id = int(row['id'])
            x = float(row['x'])
            y = float(row['y'])
            element_type = row['type'].lower()

            if element_type == 'center':
                centers.append(Center(id=element_id, x=x, y=y))

            elif element_type == 'terminal':
                terminal_cost = float(row['terminal_cost'])
                processing_cost = float(row['processing_cost'])
                terminals.append(Terminal(
                    id=element_id,
                    x=x,
                    y=y,
                    terminal_cost=terminal_cost,
                    processing_cost=processing_cost
                ))

            elif element_type == 'consumer':
                demand = float(row['demand'])
                consumers.append(Consumer(
                    id=element_id,
                    x=x,
                    y=y,
                    demand=demand
                ))

    return centers, terminals, consumers


def validate_network_data(centers: List[Center], terminals: List[Terminal],
                          consumers: List[Consumer]) -> bool:
    """
    Валідація завантажених даних

    Args:
        centers: Список центрів
        terminals: Список терміналів
        consumers: Список споживачів

    Returns:
        True якщо дані валідні, інакше викидає виключення
    """
    if not centers:
        raise ValueError("Мережа повинна мати хоча б один розподільчий центр")

    if not terminals:
        raise ValueError("Мережа повинна мати хоча б один термінал")

    if not consumers:
        raise ValueError("Мережа повинна мати хоча б одного споживача")

    # Перевірка унікальності ID
    all_ids = [e.id for e in centers + terminals + consumers]
    if len(all_ids) != len(set(all_ids)):
        raise ValueError("ID елементів повинні бути унікальними")

    # Перевірка позитивних значень
    for terminal in terminals:
        if terminal.terminal_cost < 0 or terminal.processing_cost < 0:
            raise ValueError(f"Термінал {terminal.id} має негативні витрати")

    for consumer in consumers:
        if consumer.demand <= 0:
            raise ValueError(f"Споживач {consumer.id} має некоректний попит")

    return True


def print_network_summary(centers: List[Center], terminals: List[Terminal],
                         consumers: List[Consumer]) -> None:
    """
    Виводить короткий огляд завантаженої мережі
    """
    print("\n=== ЗАВАНТАЖЕНА МЕРЕЖА ===")
    print(f"Розподільчих центрів: {len(centers)}")
    print(f"Терміналів: {len(terminals)}")
    print(f"Споживачів: {len(consumers)}")

    total_demand = sum(c.demand for c in consumers)
    print(f"Загальний попит: {total_demand:.2f}")

    print("\nЦентри:")
    for center in centers:
        print(f"  {center}")

    print("\nТермінали:")
    for terminal in terminals:
        print(f"  {terminal}")

    print(f"\nСпоживачі (перші 5):")
    for consumer in consumers[:5]:
        print(f"  {consumer}")
    if len(consumers) > 5:
        print(f"  ... та ще {len(consumers) - 5}")
