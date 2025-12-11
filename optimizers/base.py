# -*- coding: utf-8 -*-
"""
Базовий клас для оптимізаторів
"""

from abc import ABC, abstractmethod
from typing import Dict, List
from models.network import LogisticsNetwork


class Optimizer(ABC):
    """
    Абстрактний базовий клас для всіх оптимізаторів
    """

    def __init__(self, network: LogisticsNetwork):
        """
        Ініціалізація оптимізатора

        Args:
            network: Логістична мережа для оптимізації
        """
        self.network = network
        self.initial_cost = None
        self.final_cost = None
        self.optimization_history = []

    @abstractmethod
    def optimize(self) -> Dict[str, float]:
        """
        Виконує оптимізацію мережі

        Returns:
            Словник з результатами оптимізації
        """
        pass

    def get_improvement(self) -> Dict[str, float]:
        """
        Обчислює покращення після оптимізації

        Returns:
            Словник з метриками покращення
        """
        if self.initial_cost is None or self.final_cost is None:
            return {}

        absolute_improvement = self.initial_cost - self.final_cost
        percentage_improvement = (absolute_improvement / self.initial_cost) * 100

        return {
            'initial_cost': self.initial_cost,
            'final_cost': self.final_cost,
            'absolute_improvement': absolute_improvement,
            'percentage_improvement': percentage_improvement
        }

    def print_results(self) -> None:
        """
        Виводить результати оптимізації
        """
        improvement = self.get_improvement()

        if not improvement:
            print("Оптимізація ще не виконана")
            return

        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТИ ОПТИМІЗАЦІЇ")
        print("=" * 60)
        print(f"\nПочаткові витрати:     {improvement['initial_cost']:,.2f}")
        print(f"Фінальні витрати:      {improvement['final_cost']:,.2f}")
        print(f"\n{'─' * 60}")
        print(f"Покращення:            {improvement['absolute_improvement']:,.2f}")
        print(f"Покращення (%):        {improvement['percentage_improvement']:.2f}%")
        print("=" * 60)
