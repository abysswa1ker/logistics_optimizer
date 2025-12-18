"""
Тест режиму порівняння оптимізаційних методів
"""

import copy
from services.data_loader import load_network_from_csv, validate_network_data
from models.network import LogisticsNetwork
from optimizers.coordinate import CoordinateOptimizer
from optimizers.genetic import GeneticOptimizer
import time

# Завантаження даних
print("Завантаження small_network.csv...")
centers, terminals, consumers = load_network_from_csv('data/small_network.csv')
validate_network_data(centers, terminals, consumers)

# Створення мережі
network = LogisticsNetwork(
    centers=centers,
    terminals=terminals,
    consumers=consumers,
    transport_cost_per_unit=1.0
)

print(f"\nМережа: {len(terminals)} терміналів, {len(consumers)} споживачів")

# Початкові витрати
initial_costs = network.calculate_costs()
print(f"Початкові витрати: {initial_costs['total_cost']:,.2f}")

# Тестуємо функцію порівняння
from main import run_comparison, print_comparison_table

results = run_comparison(network, initial_costs)
print_comparison_table(results)

print("\n✓ Тест пройдено успішно!")
