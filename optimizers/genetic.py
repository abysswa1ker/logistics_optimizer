"""
Генетичний алгоритм для оптимізації логістичної мережі.

Реалізує еволюційний метод на основі генетичного алгоритму (ЕМ-ГА)
для пошуку оптимальної конфігурації активних терміналів.
"""

import random
import time
from typing import Dict, List, Tuple
from copy import deepcopy

from models.network import LogisticsNetwork
from optimizers.base import Optimizer


class GeneticOptimizer(Optimizer):
    """
    Генетичний алгоритм для оптимізації логістичної мережі.

    Використовує бінарне кодування хромосом, де кожен біт представляє
    стан терміналу (активний/неактивний).
    """

    def __init__(
        self,
        network: LogisticsNetwork,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8
    ):
        """
        Ініціалізація генетичного оптимізатора.

        Args:
            network: Логістична мережа для оптимізації
            population_size: Розмір популяції (за замовчуванням 50)
            generations: Кількість поколінь (за замовчуванням 100)
            mutation_rate: Ймовірність мутації (за замовчуванням 0.1)
            crossover_rate: Ймовірність кросоверу (за замовчуванням 0.8)
        """
        super().__init__(network)
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.chromosome_length = len(network.terminals)

    def _initialize_population(self) -> List[List[int]]:
        """
        Створює початкову популяцію випадкових хромосом.

        Кожна хромосома - бінарний вектор довжиною n (кількість терміналів).
        Гарантує що хоча б один термінал активний у кожній хромосомі.

        Returns:
            Список хромосом (бінарних векторів)
        """
        population = []
        for _ in range(self.population_size):
            # Генеруємо випадкову хромосому
            chromosome = [random.randint(0, 1) for _ in range(self.chromosome_length)]

            # Гарантуємо що хоча б один термінал активний
            if sum(chromosome) == 0:
                chromosome[random.randint(0, self.chromosome_length - 1)] = 1

            population.append(chromosome)

        return population

    def _calculate_fitness(self, chromosome: List[int]) -> float:
        """
        Обчислює функцію пристосованості для хромосоми.

        Формула: F(s) = 1 / (1 + C(s))
        де C(s) - загальні витрати мережі для конфігурації s

        Args:
            chromosome: Бінарний вектор стану терміналів

        Returns:
            Значення пристосованості (більше = краще)
        """
        # Перевірка на недопустиме рішення
        if sum(chromosome) == 0:
            return 0.0

        # Застосовуємо конфігурацію до мережі
        self._apply_chromosome(chromosome)

        # Обчислюємо витрати
        costs = self.network.calculate_costs()
        total_cost = costs['total_cost']

        # Обчислюємо пристосованість
        fitness = 1.0 / (1.0 + total_cost)

        return fitness

    def _apply_chromosome(self, chromosome: List[int]) -> None:
        """
        Застосовує конфігурацію хромосоми до мережі.

        Args:
            chromosome: Бінарний вектор стану терміналів
        """
        for i, terminal in enumerate(self.network.terminals):
            terminal.is_active = bool(chromosome[i])

        # Перерозподіляємо споживачів
        self.network.assign_consumers_to_terminals()

    def _tournament_selection(
        self,
        population: List[List[int]],
        fitness_values: List[float],
        tournament_size: int = 3
    ) -> List[int]:
        """
        Турнірна селекція особини з популяції.

        Args:
            population: Популяція хромосом
            fitness_values: Значення пристосованості для кожної хромосоми
            tournament_size: Розмір турніру (за замовчуванням 3)

        Returns:
            Обрана хромосома
        """
        # Випадково вибираємо особин для турніру
        tournament_indices = random.sample(range(len(population)), tournament_size)

        # Знаходимо найкращу особину в турнірі
        best_idx = max(tournament_indices, key=lambda idx: fitness_values[idx])

        return population[best_idx].copy()

    def _uniform_crossover(
        self,
        parent1: List[int],
        parent2: List[int]
    ) -> Tuple[List[int], List[int]]:
        """
        Рівномірний (uniform) кросовер двох батьків.

        Кожен ген обмінюється з ймовірністю 0.5.

        Args:
            parent1: Перший батько
            parent2: Другий батько

        Returns:
            Два нащадки
        """
        child1 = parent1.copy()
        child2 = parent2.copy()

        for i in range(self.chromosome_length):
            if random.random() < 0.5:
                # Обмінюємо гени
                child1[i], child2[i] = child2[i], child1[i]

        # Гарантуємо що хоча б один термінал активний
        if sum(child1) == 0:
            child1[random.randint(0, self.chromosome_length - 1)] = 1
        if sum(child2) == 0:
            child2[random.randint(0, self.chromosome_length - 1)] = 1

        return child1, child2

    def _mutate(self, chromosome: List[int]) -> List[int]:
        """
        Бітова мутація хромосоми.

        Кожен біт інвертується з заданою ймовірністю.

        Args:
            chromosome: Хромосома для мутації

        Returns:
            Мутована хромосома
        """
        mutated = chromosome.copy()

        for i in range(self.chromosome_length):
            if random.random() < self.mutation_rate:
                # Інвертуємо біт
                mutated[i] = 1 - mutated[i]

        # Гарантуємо що хоча б один термінал активний
        if sum(mutated) == 0:
            mutated[random.randint(0, self.chromosome_length - 1)] = 1

        return mutated

    def optimize(self, verbose: bool = True) -> Dict[str, float]:
        """
        Виконує оптимізацію генетичним алгоритмом.

        Args:
            verbose: Виводити прогрес у консоль

        Returns:
            Словник з результатами оптимізації
        """
        start_time = time.time()

        # Зберігаємо початковий стан
        initial_state = [terminal.is_active for terminal in self.network.terminals]
        self.initial_cost = self.network.calculate_costs()['total_cost']

        if verbose:
            print("=" * 60)
            print("ОПТИМІЗАЦІЯ ГЕНЕТИЧНИМ АЛГОРИТМОМ")
            print("=" * 60)
            print(f"Початкові витрати: {self.initial_cost:,.2f}")
            print(f"Параметри: популяція={self.population_size}, "
                  f"покоління={self.generations}")
            print(f"Мутація={self.mutation_rate}, кросовер={self.crossover_rate}")
            print("=" * 60)
            print()

        # Ініціалізація популяції
        population = self._initialize_population()

        # Оцінка початкової популяції
        fitness_values = [self._calculate_fitness(chromo) for chromo in population]

        # Знаходимо найкращу особину
        best_idx = max(range(len(population)), key=lambda i: fitness_values[i])
        best_chromosome = population[best_idx].copy()
        best_fitness = fitness_values[best_idx]

        # Основний цикл еволюції
        for generation in range(self.generations):
            # Створюємо нову популяцію
            new_population = []

            # Елітизм - зберігаємо найкращу особину
            new_population.append(best_chromosome.copy())

            # Генеруємо нащадків
            while len(new_population) < self.population_size:
                # Селекція батьків
                parent1 = self._tournament_selection(population, fitness_values)
                parent2 = self._tournament_selection(population, fitness_values)

                # Кросовер
                if random.random() < self.crossover_rate:
                    child1, child2 = self._uniform_crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()

                # Мутація
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)

                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)

            # Оновлення популяції
            population = new_population

            # Оцінка нової популяції
            fitness_values = [self._calculate_fitness(chromo) for chromo in population]

            # Оновлення найкращої особини
            current_best_idx = max(range(len(population)), key=lambda i: fitness_values[i])
            current_best_fitness = fitness_values[current_best_idx]

            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_chromosome = population[current_best_idx].copy()

            # Вивід прогресу кожні 10 поколінь
            if verbose and (generation + 1) % 10 == 0:
                # Обчислюємо поточні витрати
                self._apply_chromosome(best_chromosome)
                current_cost = self.network.calculate_costs()['total_cost']
                improvement = ((self.initial_cost - current_cost) / self.initial_cost) * 100

                print(f"Покоління {generation + 1:3d}: "
                      f"Пристосованість={best_fitness:.6f}, "
                      f"Витрати={current_cost:,.2f}, "
                      f"Покращення={improvement:.2f}%")

        # Застосовуємо найкраще рішення
        self._apply_chromosome(best_chromosome)
        self.final_cost = self.network.calculate_costs()['total_cost']

        elapsed_time = time.time() - start_time

        if verbose:
            print()
            print("=" * 60)
            print("РЕЗУЛЬТАТИ ГЕНЕТИЧНОГО АЛГОРИТМУ")
            print("=" * 60)
            print()
            print("Фінальна конфігурація терміналів:")
            for i, terminal in enumerate(self.network.terminals):
                status = "✓ АКТИВНИЙ" if terminal.is_active else "✗ НЕАКТИВНИЙ"
                print(f"  Термінал {terminal.id}: {status}")
            print()
            print(f"Час виконання: {elapsed_time:.2f} секунд")
            print()

        return self.get_improvement()
