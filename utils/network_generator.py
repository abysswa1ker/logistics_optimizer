"""
Генератор тестових логістичних мереж різних розмірів
"""

import csv
import random
import math
from typing import List, Tuple


class NetworkGenerator:
    """Клас для генерації тестових логістичних мереж"""

    def __init__(self, seed: int = 42):
        """
        Ініціалізація генератора

        Args:
            seed: Seed для генератора випадкових чисел (для відтворюваності)
        """
        self.seed = seed
        random.seed(seed)

    def generate_network(self,
                        n_consumers: int,
                        area_size: int = 100,
                        terminal_cost: float = 8000,
                        processing_cost: float = 15,
                        min_demand: int = 50,
                        max_demand: int = 100,
                        cluster_terminals: bool = True) -> List[dict]:
        """
        Генерує логістичну мережу заданого розміру

        Args:
            n_consumers: Кількість споживачів (розмірність задачі n)
            area_size: Розмір області розміщення (квадрат area_size x area_size)
            terminal_cost: Фіксована вартість відкриття терміналу
            processing_cost: Вартість обробки одиниці товару в терміналі
            min_demand: Мінімальний попит споживача
            max_demand: Максимальний попит споживача
            cluster_terminals: Чи групувати терміналів у кластери

        Returns:
            Список записів мережі (center, terminals, consumers)
        """
        nodes = []

        # 1. Центр розподілу (завжди один, в центрі області)
        center = {
            'id': 0,
            'x': area_size // 2,
            'y': area_size // 2,
            'type': 'center',
            'demand': 0,
            'terminal_cost': 0,
            'processing_cost': 0
        }
        nodes.append(center)

        # 2. Терміналів: приблизно n/3 до n/2 (для створення конкуренції)
        n_terminals = max(3, n_consumers // 3)

        if cluster_terminals:
            # Створюємо 3-5 кластерів терміналів
            n_clusters = min(5, max(3, n_terminals // 2))
            cluster_centers = self._generate_cluster_centers(n_clusters, area_size)

            terminals = []
            terminals_per_cluster = n_terminals // n_clusters
            remaining = n_terminals % n_clusters

            terminal_id = 10
            for i, (cx, cy) in enumerate(cluster_centers):
                # Кількість терміналів в цьому кластері
                count = terminals_per_cluster + (1 if i < remaining else 0)

                for _ in range(count):
                    # Розміщуємо терміналів навколо центру кластера
                    angle = random.uniform(0, 2 * math.pi)
                    radius = random.uniform(2, 8)
                    x = max(5, min(area_size - 5, cx + radius * math.cos(angle)))
                    y = max(5, min(area_size - 5, cy + radius * math.sin(angle)))

                    terminal = {
                        'id': terminal_id,
                        'x': round(x, 1),
                        'y': round(y, 1),
                        'type': 'terminal',
                        'demand': 0,
                        'terminal_cost': terminal_cost,
                        'processing_cost': processing_cost
                    }
                    terminals.append(terminal)
                    terminal_id += 1
        else:
            # Випадкове розміщення терміналів
            terminals = []
            for i in range(n_terminals):
                terminal = {
                    'id': 10 + i,
                    'x': round(random.uniform(10, area_size - 10), 1),
                    'y': round(random.uniform(10, area_size - 10), 1),
                    'type': 'terminal',
                    'demand': 0,
                    'terminal_cost': terminal_cost,
                    'processing_cost': processing_cost
                }
                terminals.append(terminal)

        nodes.extend(terminals)

        # 3. Споживачів: розміщуємо поблизу терміналів
        consumers = []
        consumers_per_terminal = n_consumers // len(terminals)
        remaining_consumers = n_consumers % len(terminals)

        consumer_id = 100
        for i, terminal in enumerate(terminals):
            # Кількість споживачів для цього терміналу
            count = consumers_per_terminal + (1 if i < remaining_consumers else 0)

            for _ in range(count):
                # Розміщуємо споживачів навколо терміналу
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(1, 10)
                x = max(0, min(area_size, terminal['x'] + radius * math.cos(angle)))
                y = max(0, min(area_size, terminal['y'] + radius * math.sin(angle)))

                consumer = {
                    'id': consumer_id,
                    'x': round(x, 1),
                    'y': round(y, 1),
                    'type': 'consumer',
                    'demand': random.randint(min_demand, max_demand),
                    'terminal_cost': 0,
                    'processing_cost': 0
                }
                consumers.append(consumer)
                consumer_id += 1

        nodes.extend(consumers)

        return nodes

    def _generate_cluster_centers(self, n_clusters: int, area_size: int) -> List[Tuple[float, float]]:
        """
        Генерує центри кластерів, рівномірно розподілені по області

        Args:
            n_clusters: Кількість кластерів
            area_size: Розмір області

        Returns:
            Список координат центрів кластерів
        """
        centers = []
        margin = area_size * 0.2

        # Розміщуємо кластери по сітці
        if n_clusters == 3:
            # Трикутник
            centers = [
                (area_size * 0.25, area_size * 0.25),
                (area_size * 0.75, area_size * 0.25),
                (area_size * 0.5, area_size * 0.75)
            ]
        elif n_clusters == 4:
            # Квадрат
            centers = [
                (area_size * 0.25, area_size * 0.25),
                (area_size * 0.75, area_size * 0.25),
                (area_size * 0.25, area_size * 0.75),
                (area_size * 0.75, area_size * 0.75)
            ]
        elif n_clusters == 5:
            # Квадрат + центр
            centers = [
                (area_size * 0.2, area_size * 0.2),
                (area_size * 0.8, area_size * 0.2),
                (area_size * 0.2, area_size * 0.8),
                (area_size * 0.8, area_size * 0.8),
                (area_size * 0.5, area_size * 0.5)
            ]
        else:
            # Випадкове розміщення з мінімальною відстанню
            min_distance = area_size * 0.3
            for _ in range(n_clusters):
                attempts = 0
                while attempts < 100:
                    x = random.uniform(margin, area_size - margin)
                    y = random.uniform(margin, area_size - margin)

                    # Перевіряємо відстань до інших центрів
                    if all(math.sqrt((x - cx)**2 + (y - cy)**2) >= min_distance
                           for cx, cy in centers):
                        centers.append((x, y))
                        break
                    attempts += 1

        return centers

    def save_to_csv(self, nodes: List[dict], filepath: str):
        """
        Зберігає мережу у CSV файл

        Args:
            nodes: Список вузлів мережі
            filepath: Шлях до файлу
        """
        fieldnames = ['id', 'x', 'y', 'type', 'demand', 'terminal_cost', 'processing_cost']

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(nodes)

        print(f"Мережу збережено: {filepath}")
        print(f"  Споживачів: {sum(1 for n in nodes if n['type'] == 'consumer')}")
        print(f"  Терміналів: {sum(1 for n in nodes if n['type'] == 'terminal')}")


def generate_test_networks():
    """Генерує тестові мережі для валідації методів оптимізації"""
    generator = NetworkGenerator(seed=42)

    # Розмірності згідно з таблицею
    dimensions = [15, 20, 25, 30, 35, 40]

    for n in dimensions:
        print(f"\nГенерація мережі розмірності n={n}...")
        nodes = generator.generate_network(
            n_consumers=n,
            area_size=100,
            terminal_cost=8000,
            processing_cost=15,
            min_demand=50,
            max_demand=100,
            cluster_terminals=True
        )

        filepath = f"data/network_n{n}.csv"
        generator.save_to_csv(nodes, filepath)


if __name__ == "__main__":
    generate_test_networks()
