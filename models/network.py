# -*- coding: utf-8 -*-
"""
Клас логістичної мережі
"""

from typing import List, Dict
from models.element import Center, Terminal, Consumer
from services.distance import euclidean_distance, find_nearest_terminal


class LogisticsNetwork:
    """
    Представляє логістичну мережу з центрами, терміналами та споживачами
    """

    def __init__(self, centers: List[Center], terminals: List[Terminal], consumers: List[Consumer]):
        """
        Ініціалізує мережу

        Args:
            centers: Список розподільчих центрів
            terminals: Список терміналів
            consumers: Список споживачів
        """
        self.centers = centers
        self.terminals = terminals
        self.consumers = consumers

        # Ініціалізація початкової мережі
        self._initialize_network()

    def _initialize_network(self):
        """
        Ініціалізує початковий стан мережі:
        - Всі термінали активні
        - Споживачі прив'язані до найближчих терміналів
        """
        # Всі термінали активні за замовчуванням (встановлено в класі Terminal)

        # Прив'язуємо кожного споживача до найближчого терміналу
        for consumer in self.consumers:
            nearest_terminal, _ = find_nearest_terminal(consumer, self.terminals)
            consumer.assigned_terminal = nearest_terminal.id

    def assign_consumers_to_terminals(self):
        """
        Прив'язує всіх споживачів до найближчих активних терміналів
        """
        for consumer in self.consumers:
            nearest_terminal, _ = find_nearest_terminal(consumer, self.terminals, active_only=True)
            consumer.assigned_terminal = nearest_terminal.id

    def get_terminal_by_id(self, terminal_id: int) -> Terminal:
        """Отримує термінал за ID"""
        for terminal in self.terminals:
            if terminal.id == terminal_id:
                return terminal
        raise ValueError(f"Термінал з ID {terminal_id} не знайдено")

    def get_center(self) -> Center:
        """Повертає розподільчий центр (припускаємо один центр для MVP)"""
        if not self.centers:
            raise ValueError("Мережа не має центру")
        return self.centers[0]

    def get_active_terminals(self) -> List[Terminal]:
        """Повертає список активних терміналів"""
        return [t for t in self.terminals if t.is_active]

    def get_consumers_for_terminal(self, terminal_id: int) -> List[Consumer]:
        """Повертає список споживачів, прив'язаних до конкретного терміналу"""
        return [c for c in self.consumers if c.assigned_terminal == terminal_id]

    def get_terminal_load(self, terminal_id: int) -> float:
        """Обчислює загальний попит для терміналу"""
        consumers = self.get_consumers_for_terminal(terminal_id)
        return sum(c.demand for c in consumers)

    def print_network_state(self):
        """Виводить поточний стан мережі"""
        print("\n" + "=" * 60)
        print("ПОТОЧНИЙ СТАН МЕРЕЖІ")
        print("=" * 60)

        center = self.get_center()
        print(f"\nЦентр: {center}")

        print(f"\nАктивні термінали ({len(self.get_active_terminals())}/{len(self.terminals)}):")
        for terminal in self.get_active_terminals():
            load = self.get_terminal_load(terminal.id)
            num_consumers = len(self.get_consumers_for_terminal(terminal.id))
            print(f"  {terminal}")
            print(f"    -> Обслуговує: {num_consumers} споживачів, навантаження: {load:.2f}")

        inactive = [t for t in self.terminals if not t.is_active]
        if inactive:
            print(f"\nНеактивні термінали ({len(inactive)}):")
            for terminal in inactive:
                print(f"  {terminal}")

        print(f"\nСпоживачі ({len(self.consumers)}):")
        for i, consumer in enumerate(self.consumers[:5]):
            terminal = self.get_terminal_by_id(consumer.assigned_terminal)
            distance = euclidean_distance(consumer, terminal)
            print(f"  {consumer} -> Термінал {terminal.id} (відстань: {distance:.2f})")
        if len(self.consumers) > 5:
            print(f"  ... та ще {len(self.consumers) - 5}")

        print("=" * 60)
