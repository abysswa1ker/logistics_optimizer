# -*- coding: utf-8 -*-
"""
Класи елементів логістичної мережі
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Element:
    """Базовий клас для елементів мережі"""
    id: int
    x: float
    y: float
    type: str

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, x={self.x}, y={self.y})"


@dataclass
class Center(Element):
    """Розподільчий центр (DC)"""

    def __init__(self, id: int, x: float, y: float):
        super().__init__(id=id, x=x, y=y, type='center')


@dataclass
class Terminal(Element):
    """Термінал (проміжний пункт)"""
    terminal_cost: float  # Фіксована вартість утримання терміналу
    processing_cost: float  # Вартість обробки одиниці продукції
    is_active: bool = True  # Чи активний термінал

    def __init__(self, id: int, x: float, y: float, terminal_cost: float, processing_cost: float):
        super().__init__(id=id, x=x, y=y, type='terminal')
        self.terminal_cost = terminal_cost
        self.processing_cost = processing_cost
        self.is_active = True

    def __repr__(self):
        status = "active" if self.is_active else "inactive"
        return f"Terminal(id={self.id}, x={self.x}, y={self.y}, cost={self.terminal_cost}, {status})"


@dataclass
class Consumer(Element):
    """Споживач"""
    demand: float  # Попит (об'єм замовлення)
    assigned_terminal: Optional[int] = None  # ID призначеного терміналу

    def __init__(self, id: int, x: float, y: float, demand: float):
        super().__init__(id=id, x=x, y=y, type='consumer')
        self.demand = demand
        self.assigned_terminal = None

    def __repr__(self):
        return f"Consumer(id={self.id}, x={self.x}, y={self.y}, demand={self.demand})"
