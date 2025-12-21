"""
Створення тестової мережі для демонстрації оптимізації координат терміналів.

Особливості:
- Споживачі згруповані в чіткі кластери
- Термінали розміщені НЕОПТИМАЛЬНО (далеко від центрів кластерів)
- Низькі фіксовані витрати терміналів (щоб їх не вимикали)
- Покаже силу МПО в оптимізації координат
"""

import csv
import math

def create_coordinate_optimization_network():
    """
    Створює мережу де основна економія досягається через переміщення терміналів,
    а не через їх вимикання.
    """
    nodes = []

    # Центр розподілу в центрі області
    nodes.append({
        'id': 0,
        'x': 50.0,
        'y': 50.0,
        'type': 'center',
        'demand': 0,
        'terminal_cost': 0,
        'processing_cost': 0
    })

    # Визначаємо 4 кластери споживачів
    cluster_centers = [
        (20.0, 20.0),  # Нижній лівий
        (80.0, 20.0),  # Нижній правий
        (20.0, 80.0),  # Верхній лівий
        (80.0, 80.0),  # Верхній правий
    ]

    # Розміщуємо термінали НЕОПТИМАЛЬНО - між кластерами, а не в їх центрах
    # Це дозволить МПО показати значне покращення через переміщення
    terminal_positions = [
        (35.0, 35.0),  # Між лівими кластерами
        (65.0, 35.0),  # Між правими кластерами
        (35.0, 65.0),  # Між верхніми кластерами
        (65.0, 65.0),  # В центрі області
    ]

    # Створюємо термінали з НИЗЬКИМИ фіксованими витратами
    # щоб алгоритм не намагався їх вимикати
    for i, (x, y) in enumerate(terminal_positions):
        nodes.append({
            'id': 10 + i,
            'x': x,
            'y': y,
            'type': 'terminal',
            'demand': 0,
            'terminal_cost': 3000,  # Низькі фіксовані витрати
            'processing_cost': 10,
        })

    # Створюємо споживачів в кластерах
    consumer_id = 100

    for cluster_idx, (cx, cy) in enumerate(cluster_centers):
        # По 5 споживачів в кожному кластері
        for i in range(5):
            # Розміщуємо споживачів близько до центру кластера
            angle = (i / 5) * 2 * math.pi
            radius = 3.0  # Малий радіус - щільний кластер

            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            nodes.append({
                'id': consumer_id,
                'x': round(x, 1),
                'y': round(y, 1),
                'type': 'consumer',
                'demand': 80,  # Високий попит для збільшення транспортних витрат
                'terminal_cost': 0,
                'processing_cost': 0
            })
            consumer_id += 1

    return nodes


def save_network():
    """Зберігає мережу у CSV файл"""
    nodes = create_coordinate_optimization_network()

    filepath = 'data/coordinate_optimization_demo.csv'
    fieldnames = ['id', 'x', 'y', 'type', 'demand', 'terminal_cost', 'processing_cost']

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(nodes)

    consumers = sum(1 for n in nodes if n['type'] == 'consumer')
    terminals = sum(1 for n in nodes if n['type'] == 'terminal')

    print(f"✓ Мережу збережено: {filepath}")
    print(f"  Споживачів: {consumers} (згруповані в 4 кластери)")
    print(f"  Терміналів: {terminals} (розміщені неоптимально)")
    print(f"\nОсобливості мережі:")
    print(f"  - Споживачі в щільних кластерах (радіус 3.0)")
    print(f"  - Термінали між кластерами (неоптимально)")
    print(f"  - Низькі фіксовані витрати (3000 замість 8000)")
    print(f"  - Високий попит (80 на споживача)")
    print(f"\nОчікувана економія:")
    print(f"  МПО - значна (переміщення терміналів до центрів кластерів)")
    print(f"  ЕМ-ГА - менша (тільки вибір терміналів, координати фіксовані)")


if __name__ == "__main__":
    save_network()
