# -*- coding: utf-8 -*-
"""
Метод покоординатної оптимізації (МПО)
"""

import copy
from typing import Dict, Tuple
from optimizers.base import Optimizer
from models.network import LogisticsNetwork


class CoordinateOptimizer(Optimizer):
    """
    Оптимізатор на основі методу покоординатного спуску
    """

    def __init__(self, network: LogisticsNetwork, 
                 step_size: float = 1.0,
                 max_iterations: int = 100,
                 tolerance: float = 0.01):
        """
        Ініціалізація МПО

        Args:
            network: Логістична мережа
            step_size: Розмір кроку для зміни координат
            max_iterations: Максимальна кількість ітерацій
            tolerance: Мінімальне покращення для продовження (%)
        """
        super().__init__(network)
        self.step_size = step_size
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def optimize(self, verbose: bool = True) -> Dict[str, float]:
        """
        Виконує оптимізацію методом покоординатного спуску

        Args:
            verbose: Виводити проміжні результати

        Returns:
            Словник з результатами оптимізації
        """
        # Зберігаємо початкові витрати
        self.initial_cost = self.network.calculate_costs()['total_cost']
        current_cost = self.initial_cost
        previous_cost = self.initial_cost

        if verbose:
            print(f"\n{'='*60}")
            print("ОПТИМІЗАЦІЯ МЕТОДОМ МПО")
            print(f"{'='*60}")
            print(f"Початкові витрати: {self.initial_cost:,.2f}")
            print(f"Параметри: крок={self.step_size}, макс_ітерацій={self.max_iterations}, tolerance={self.tolerance}%")
            print(f"{'='*60}\n")

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            iteration_start_cost = current_cost
            improved = False

            # Оптимізація координат кожного терміналу
            for terminal in self.network.terminals:
                if not terminal.is_active:
                    continue

                # Пробуємо оптимізувати позицію терміналу
                new_cost = self._optimize_terminal_position(terminal, current_cost)

                if new_cost < current_cost:
                    improvement_pct = ((current_cost - new_cost) / current_cost) * 100
                    if verbose:
                        print(f"Ітерація {iteration}: Термінал {terminal.id} " +
                              f"переміщено, покращення: {improvement_pct:.3f}%")
                    current_cost = new_cost
                    improved = True

            # Перевірка на можливість вимкнути термінали (тільки кожні 5 ітерацій)
            if iteration % 5 == 0:
                deactivated = self._try_deactivate_terminals(current_cost, verbose)
                if deactivated:
                    new_cost = self.network.calculate_costs()['total_cost']
                    if new_cost < current_cost:
                        current_cost = new_cost
                        improved = True

            # Перевірка покращення на поточній ітерації
            iteration_improvement = ((iteration_start_cost - current_cost) / iteration_start_cost) * 100

            # Якщо немає покращень на ітерації, зупиняємо
            if not improved:
                if verbose:
                    print(f"\nНемає покращень на ітерації {iteration}. Зупинка.")
                break

            # Виводимо прогрес
            if verbose and iteration_improvement > 0:
                total_improvement = ((self.initial_cost - current_cost) / self.initial_cost) * 100
                print(f"  → Загальне покращення: {total_improvement:.2f}%")

        self.final_cost = current_cost

        if verbose:
            print(f"\n{'='*60}")
            print(f"Оптимізація завершена за {iteration} ітерацій")
            print(f"{'='*60}")

        return self.get_improvement()

    def _optimize_terminal_position(self, terminal, current_cost: float) -> float:
        """
        Оптимізує позицію одного терміналу

        Args:
            terminal: Термінал для оптимізації
            current_cost: Поточні витрати

        Returns:
            Нові витрати після оптимізації
        """
        best_cost = current_cost
        best_x, best_y = terminal.x, terminal.y

        # Зберігаємо початкові координати
        original_x, original_y = terminal.x, terminal.y

        # Пробуємо рухатись у 4 напрямках: вгору, вниз, вліво, вправо
        directions = [
            (self.step_size, 0),   # вправо
            (-self.step_size, 0),  # вліво
            (0, self.step_size),   # вгору
            (0, -self.step_size),  # вниз
        ]

        for dx, dy in directions:
            # Пробуємо нову позицію
            terminal.x = original_x + dx
            terminal.y = original_y + dy

            # Перерозподіляємо споживачів до найближчих терміналів
            self.network.assign_consumers_to_terminals()

            # Обчислюємо нові витрати
            new_cost = self.network.calculate_costs()['total_cost']

            # Якщо витрати менші, зберігаємо
            if new_cost < best_cost:
                best_cost = new_cost
                best_x = terminal.x
                best_y = terminal.y

        # Встановлюємо найкращу знайдену позицію
        terminal.x = best_x
        terminal.y = best_y

        # Якщо змінилась позиція, перерозподіляємо споживачів
        if best_x != original_x or best_y != original_y:
            self.network.assign_consumers_to_terminals()

        return best_cost

    def _try_deactivate_terminals(self, current_cost: float, verbose: bool = False) -> bool:
        """
        Перевіряє чи вигідно вимкнути якісь термінали

        Args:
            current_cost: Поточні витрати
            verbose: Виводити повідомлення

        Returns:
            True якщо хоча б один термінал було вимкнено
        """
        deactivated = False

        for terminal in self.network.terminals:
            if not terminal.is_active:
                continue

            # Тимчасово вимикаємо термінал
            terminal.is_active = False

            # Перерозподіляємо споживачів
            try:
                self.network.assign_consumers_to_terminals()

                # Обчислюємо нові витрати
                new_cost = self.network.calculate_costs()['total_cost']

                # Якщо витрати менші, залишаємо вимкненим
                if new_cost < current_cost:
                    if verbose:
                        print(f"Термінал {terminal.id} вимкнено, покращення: " +
                              f"{((current_cost - new_cost) / current_cost * 100):.3f}%")
                    deactivated = True
                    current_cost = new_cost
                else:
                    # Повертаємо назад
                    terminal.is_active = True
                    self.network.assign_consumers_to_terminals()

            except ValueError:
                # Якщо не можна вимкнути (немає інших активних терміналів), повертаємо назад
                terminal.is_active = True
                self.network.assign_consumers_to_terminals()

        return deactivated
