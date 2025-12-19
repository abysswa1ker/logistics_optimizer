# -*- coding: utf-8 -*-
"""
Метод покоordinатної оптимізації (МПО)
"""

import copy
from typing import Dict, Tuple, List
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
            step_size: Не використовується в новій реалізації (для сумісності)
            max_iterations: Максимальна кількість повних проходів
            tolerance: Мінімальне покращення між проходами для продовження (абсолютне значення)
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
        previous_pass_cost = self.initial_cost

        if verbose:
            print(f"\n{'='*60}")
            print("ОПТИМІЗАЦІЯ МЕТОДОМ МПО")
            print(f"{'='*60}")
            print(f"Початкові витрати: {self.initial_cost:,.2f}")
            print(f"Параметри: макс_проходів={self.max_iterations}, tolerance={self.tolerance}")
            print(f"{'='*60}\n")

        # Формуємо список можливих локацій (позиції споживачів + центр)
        possible_locations = self._get_possible_locations()

        if verbose:
            print(f"Можливих локацій для терміналів: {len(possible_locations)}")
            print(f"Активних терміналів: {sum(1 for t in self.network.terminals if t.is_active)}")
            print("-" * 60)

        pass_number = 0

        # Повні проходи по всіх терміналах
        while pass_number < self.max_iterations:
            pass_number += 1
            pass_start_cost = current_cost

            if verbose:
                print(f"\nПрохід {pass_number}:")

            # Оптимізуємо кожен активний термінал
            for terminal_idx, terminal in enumerate(self.network.terminals):
                if not terminal.is_active:
                    continue

                # Перебираємо всі можливі локації для цього терміналу
                best_cost = current_cost
                best_location = (terminal.x, terminal.y)
                original_x, original_y = terminal.x, terminal.y

                for loc_x, loc_y in possible_locations:
                    # Пропускаємо поточну позицію
                    if loc_x == original_x and loc_y == original_y:
                        continue

                    # Пробуємо нову локацію
                    terminal.x = loc_x
                    terminal.y = loc_y

                    # Перерозподіляємо споживачів
                    self.network.assign_consumers_to_terminals()

                    # Обчислюємо витрати
                    new_cost = self.network.calculate_costs()['total_cost']

                    # Зберігаємо найкращу локацію
                    if new_cost < best_cost:
                        best_cost = new_cost
                        best_location = (loc_x, loc_y)

                # Встановлюємо найкращу знайдену позицію
                terminal.x, terminal.y = best_location
                self.network.assign_consumers_to_terminals()

                # Оновлюємо поточну вартість
                if best_cost < current_cost:
                    improvement = current_cost - best_cost
                    improvement_pct = (improvement / current_cost) * 100
                    current_cost = best_cost

                    if verbose:
                        print(f"  Термінал {terminal.id}: переміщено на ({best_location[0]:.0f}, {best_location[1]:.0f}), "
                              f"покращення {improvement_pct:.2f}%")

            # Перевірка збіжності після повного проходу
            pass_improvement = pass_start_cost - current_cost

            if verbose:
                total_improvement_pct = ((self.initial_cost - current_cost) / self.initial_cost) * 100
                print(f"  → Покращення на проході: {pass_improvement:.2f}")
                print(f"  → Загальне покращення: {total_improvement_pct:.2f}%")

            # Якщо покращення менше tolerance, зупиняємось
            if pass_improvement < self.tolerance:
                if verbose:
                    print(f"\nЗбіжність досягнута: покращення {pass_improvement:.2f} < tolerance {self.tolerance}")
                break

            previous_pass_cost = current_cost

        # Фаза 2: Перевірка доцільності терміналів
        if verbose:
            print(f"\n{'='*60}")
            print("Фаза 2: Перевірка доцільності терміналів")
            print("-" * 60)

        deactivation_iterations = 0
        max_deactivation_iterations = 10

        while deactivation_iterations < max_deactivation_iterations:
            deactivation_iterations += 1
            deactivated = self._try_deactivate_terminals(current_cost, verbose)

            if deactivated:
                new_cost = self.network.calculate_costs()['total_cost']
                if new_cost < current_cost:
                    current_cost = new_cost
                    if verbose:
                        total_improvement = ((self.initial_cost - current_cost) / self.initial_cost) * 100
                        print(f"  → Загальне покращення: {total_improvement:.2f}%")
                else:
                    break
            else:
                if verbose:
                    print("Всі активні термінали необхідні")
                break

        self.final_cost = current_cost

        if verbose:
            print(f"\n{'='*60}")
            print(f"Оптимізація завершена:")
            print(f"  - Фаза 1 (оптимізація позицій): {pass_number} проходів")
            print(f"  - Фаза 2 (деактивація): {deactivation_iterations} перевірок")
            print(f"{'='*60}")

        # Додаємо кількість ітерацій до результатів
        results = self.get_improvement()
        results['iterations'] = pass_number
        return results

    def _get_possible_locations(self) -> List[Tuple[float, float]]:
        """
        Формує список можливих локацій для терміналів

        Створює сітку потенційних локацій на основі розміщення споживачів,
        але НЕ в точних позиціях споживачів (щоб уникнути колізій)

        Returns:
            Список координат (x, y)
        """
        locations = set()

        # Знаходимо межі області
        min_x = min(c.x for c in self.network.consumers)
        max_x = max(c.x for c in self.network.consumers)
        min_y = min(c.y for c in self.network.consumers)
        max_y = max(c.y for c in self.network.consumers)

        # Створюємо сітку з кроком 5 одиниць
        grid_step = 5
        for x in range(int(min_x), int(max_x) + 1, grid_step):
            for y in range(int(min_y), int(max_y) + 1, grid_step):
                # Перевіряємо що ця локація не співпадає з споживачем
                is_consumer_location = any(
                    abs(c.x - x) < 0.1 and abs(c.y - y) < 0.1
                    for c in self.network.consumers
                )

                if not is_consumer_location:
                    locations.add((float(x), float(y)))

        # Додаємо позицію центру (завжди дозволена)
        for center in self.network.centers:
            locations.add((center.x, center.y))

        return list(locations)

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
