"""
Тест мережі де ГА має перевагу над МПО
"""

import copy
from services.data_loader import load_network_from_csv, validate_network_data
from models.network import LogisticsNetwork
from main import run_comparison, print_comparison_table

# Завантаження даних
print("Завантаження ga_advantage_network.csv...")
centers, terminals, consumers = load_network_from_csv('data/ga_advantage_network.csv')
validate_network_data(centers, terminals, consumers)

# Створення мережі
network = LogisticsNetwork(
    centers=centers,
    terminals=terminals,
    consumers=consumers,
    transport_cost_per_unit=1.0
)

print(f"\nМережа:")
print(f"  Терміналів: {len(terminals)}")
print(f"  Споживачів: {len(consumers)}")
print(f"  Загальний попит: {sum(c.demand for c in consumers):.2f}")

# Початкові витрати
initial_costs = network.calculate_costs()
print(f"\nПочаткові витрати: {initial_costs['total_cost']:,.2f}")
print(f"  - Фіксовані витрати терміналів: {initial_costs['fixed_costs']:,.2f}")
print(f"  - Транспорт: {initial_costs['transport_total']:,.2f}")

# Запуск порівняння
results = run_comparison(network, initial_costs)
print_comparison_table(results)
