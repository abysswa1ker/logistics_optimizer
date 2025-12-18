"""
Тест генетичного алгоритму на sparse_network.csv
"""

from services.data_loader import load_network_from_csv, validate_network_data
from models.network import LogisticsNetwork
from optimizers.genetic import GeneticOptimizer

# Завантаження даних
print("Завантаження sparse_network...")
centers, terminals, consumers = load_network_from_csv('data/sparse_network.csv')
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

# Запуск генетичного алгоритму
optimizer = GeneticOptimizer(
    network=network,
    population_size=50,
    generations=100,
    mutation_rate=0.15,
    crossover_rate=0.8
)

results = optimizer.optimize(verbose=True)

# Підсумок
optimizer.print_results()
