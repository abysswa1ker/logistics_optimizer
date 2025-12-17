# -*- coding: utf-8 -*-
"""
Обчислення витрат логістичної мережі
"""

from typing import List, Dict, Tuple
from models.element import Center, Terminal, Consumer
from services.distance import euclidean_distance


class CostCalculator:
    """
    Калькулятор витрат для логістичної мережі
    """

    def __init__(self, transport_cost_per_unit: float = 1.0):
        """
        Ініціалізація калькулятора

        Args:
            transport_cost_per_unit: Вартість транспортування за одиницю відстані на одиницю товару
        """
        self.transport_cost_per_unit = transport_cost_per_unit

    def calculate_terminal_fixed_costs(self, terminals: List[Terminal]) -> float:
        """
        Обчислює фіксовані витрати на утримання активних терміналів

        Args:
            terminals: Список терміналів

        Returns:
            Загальна вартість утримання активних терміналів
        """
        return sum(t.terminal_cost for t in terminals if t.is_active)

    def calculate_processing_costs(self, terminals: List[Terminal], 
                                   consumers: List[Consumer]) -> float:
        """
        Обчислює витрати на обробку товарів у терміналах

        Args:
            terminals: Список терміналів
            consumers: Список споживачів

        Returns:
            Загальна вартість обробки
        """
        total_cost = 0.0

        # Групуємо споживачів за терміналами
        for terminal in terminals:
            if not terminal.is_active:
                continue

            # Знаходимо всіх споживачів для цього терміналу
            terminal_consumers = [c for c in consumers if c.assigned_terminal == terminal.id]

            # Обчислюємо вартість обробки
            total_demand = sum(c.demand for c in terminal_consumers)
            total_cost += terminal.processing_cost * total_demand

        return total_cost

    def calculate_transportation_costs(self, center: Center, terminals: List[Terminal],
                                       consumers: List[Consumer]) -> Tuple[float, float, float]:
        """
        Обчислює витрати на транспортування

        Args:
            center: Розподільчий центр
            terminals: Список терміналів
            consumers: Список споживачів

        Returns:
            Кортеж (center_to_terminal_cost, terminal_to_consumer_cost, total_cost)
        """
        center_to_terminal_cost = 0.0
        terminal_to_consumer_cost = 0.0

        for terminal in terminals:
            if not terminal.is_active:
                continue

            # Знаходимо споживачів для цього терміналу
            terminal_consumers = [c for c in consumers if c.assigned_terminal == terminal.id]

            if not terminal_consumers:
                continue

            # Загальний попит для цього терміналу
            total_demand = sum(c.demand for c in terminal_consumers)

            # Вартість Center → Terminal (зменшений коефіцієнт для кращої оптимізації)
            # Транспорт оптом від центру дешевший ніж роздрібна доставка споживачам
            distance_center_terminal = euclidean_distance(center, terminal)
            center_to_terminal_cost += distance_center_terminal * self.transport_cost_per_unit * total_demand * 0.1

            # Вартість Terminal → Consumers
            for consumer in terminal_consumers:
                distance_terminal_consumer = euclidean_distance(terminal, consumer)
                terminal_to_consumer_cost += distance_terminal_consumer * self.transport_cost_per_unit * consumer.demand

        total_cost = center_to_terminal_cost + terminal_to_consumer_cost
        return center_to_terminal_cost, terminal_to_consumer_cost, total_cost

    def calculate_total_cost(self, center: Center, terminals: List[Terminal],
                            consumers: List[Consumer]) -> Dict[str, float]:
        """
        Обчислює загальні витрати мережі

        Args:
            center: Розподільчий центр
            terminals: Список терміналів
            consumers: Список споживачів

        Returns:
            Словник з детальною розбивкою витрат
        """
        # Фіксовані витрати терміналів
        fixed_costs = self.calculate_terminal_fixed_costs(terminals)

        # Витрати на обробку
        processing_costs = self.calculate_processing_costs(terminals, consumers)

        # Витрати на транспортування
        center_to_terminal, terminal_to_consumer, transport_total = \
            self.calculate_transportation_costs(center, terminals, consumers)

        # Загальні витрати
        total_cost = fixed_costs + processing_costs + transport_total

        return {
            'fixed_costs': fixed_costs,
            'processing_costs': processing_costs,
            'transport_center_to_terminal': center_to_terminal,
            'transport_terminal_to_consumer': terminal_to_consumer,
            'transport_total': transport_total,
            'total_cost': total_cost
        }

    def print_cost_breakdown(self, costs: Dict[str, float]) -> None:
        """
        Виводить детальну розбивку витрат

        Args:
            costs: Словник з витратами від calculate_total_cost
        """
        print("\n" + "=" * 60)
        print("РОЗБИВКА ВИТРАТ МЕРЕЖІ")
        print("=" * 60)
        print(f"\n1. Фіксовані витрати терміналів: {costs['fixed_costs']:,.2f}")
        print(f"2. Витрати на обробку:           {costs['processing_costs']:,.2f}")
        print(f"3. Транспортування:")
        print(f"   - Центр → Термінали:          {costs['transport_center_to_terminal']:,.2f}")
        print(f"   - Термінали → Споживачі:      {costs['transport_terminal_to_consumer']:,.2f}")
        print(f"   - Разом транспортування:      {costs['transport_total']:,.2f}")
        print(f"\n{'─' * 60}")
        print(f"ЗАГАЛЬНІ ВИТРАТИ:                {costs['total_cost']:,.2f}")
        print("=" * 60)
