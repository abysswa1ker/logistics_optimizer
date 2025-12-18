"""
Тестовий скрипт для генетичного алгоритму.
"""

from services.data_loader import load_network_from_csv, validate_network_data
from models.network import LogisticsNetwork
from optimizers.genetic import GeneticOptimizer

# Завантаження даних
print("Завантаження тестової мережі...")
centers, terminals, consumers = load_network_from_csv('data/small_network.csv')
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

# Запуск генетичного алгоритму
print("\n" + "=" * 60)
optimizer = GeneticOptimizer(
    network=network,
    population_size=30,
    generations=50,
    mutation_rate=0.1,
    crossover_rate=0.8
)

results = optimizer.optimize(verbose=True)

# Результати
print("=" * 60)
print("ПІДСУМОК")
print("=" * 60)
print(f"Початкові витрати: {results['initial_cost']:,.2f}")
print(f"Фінальні витрати:  {results['final_cost']:,.2f}")
print(f"Покращення:        {results['absolute_improvement']:,.2f}")
print(f"Покращення (%):    {results['percentage_improvement']:.2f}%")
print("=" * 60)
