# -*- coding: utf-8 -*-
"""
Обчислення відстаней між елементами мережі
"""

import math
from typing import Union
from models.element import Element, Center, Terminal, Consumer


def euclidean_distance(elem1: Union[Element, tuple], elem2: Union[Element, tuple]) -> float:
    """
    Обчислює евклідову відстань між двома елементами або точками

    Args:
        elem1: Перший елемент (Element) або кортеж (x, y)
        elem2: Другий елемент (Element) або кортеж (x, y)

    Returns:
        Евклідова відстань між елементами
    """
    if isinstance(elem1, Element):
        x1, y1 = elem1.x, elem1.y
    else:
        x1, y1 = elem1

    if isinstance(elem2, Element):
        x2, y2 = elem2.x, elem2.y
    else:
        x2, y2 = elem2

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def manhattan_distance(elem1: Union[Element, tuple], elem2: Union[Element, tuple]) -> float:
    """
    Обчислює манхеттенську відстань між двома елементами

    Args:
        elem1: Перший елемент (Element) або кортеж (x, y)
        elem2: Другий елемент (Element) або кортеж (x, y)

    Returns:
        Манхеттенська відстань між елементами
    """
    if isinstance(elem1, Element):
        x1, y1 = elem1.x, elem1.y
    else:
        x1, y1 = elem1

    if isinstance(elem2, Element):
        x2, y2 = elem2.x, elem2.y
    else:
        x2, y2 = elem2

    return abs(x2 - x1) + abs(y2 - y1)


def find_nearest_terminal(consumer: Consumer, terminals: list, active_only: bool = True) -> tuple:
    """
    Знаходить найближчий термінал для споживача

    Args:
        consumer: Споживач
        terminals: Список терміналів
        active_only: Враховувати тільки активні термінали

    Returns:
        Кортеж (terminal, distance) - найближчий термінал та відстань до нього
    """
    available_terminals = terminals
    if active_only:
        available_terminals = [t for t in terminals if t.is_active]

    if not available_terminals:
        raise ValueError("Немає доступних терміналів")

    nearest = None
    min_distance = float('inf')

    for terminal in available_terminals:
        distance = euclidean_distance(consumer, terminal)
        if distance < min_distance:
            min_distance = distance
            nearest = terminal

    return nearest, min_distance
