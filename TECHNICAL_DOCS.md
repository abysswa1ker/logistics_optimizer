# Технічна документація - Система оптимізації логістичної мережі

## 📚 Зміст

1. [Архітектура проекту](#архітектура-проекту)
2. [Структура класів](#структура-класів)
3. [Алгоритми оптимізації](#алгоритми-оптимізації)
4. [Обчислення витрат](#обчислення-витрат)
5. [Візуалізація](#візуалізація)
6. [Розширення системи](#розширення-системи)

---

## Архітектура проекту

### Загальна структура

```
logistics_optimizer/
├── data/                      # Вхідні дані
├── models/                    # Моделі даних
│   ├── element.py            # Базові елементи мережі
│   └── network.py            # Логістична мережа
├── services/                  # Сервіси та утиліти
│   ├── data_loader.py        # Завантаження даних
│   ├── distance.py           # Обчислення відстаней
│   ├── cost_calculator.py    # Розрахунок витрат
│   └── visualization.py      # Візуалізація
├── optimizers/                # Алгоритми оптимізації
│   ├── base.py               # Базовий клас
│   └── coordinate.py         # МПО
├── results/                   # Згенеровані результати
└── main.py                   # Точка входу
```

### Патерни проектування

1. **Strategy Pattern** - різні алгоритми оптимізації (МПО, генетичний)
2. **Template Method** - базовий клас `Optimizer` з абстрактним методом `optimize()`
3. **Facade** - клас `LogisticsNetwork` спрощує роботу з мережею
4. **Builder** - поступове створення мережі через `data_loader`

---

## Структура класів

### 1. Моделі елементів (`models/element.py`)

#### Базовий клас Element

```python
@dataclass
class Element:
    id: int          # Унікальний ідентифікатор
    x: float         # X координата
    y: float         # Y координата
    type: str        # Тип елемента
```

**Призначення:** Базовий клас для всіх елементів мережі

#### Center (Розподільчий центр)

```python
class Center(Element):
    def __init__(self, id: int, x: float, y: float)
```

**Атрибути:**
- Успадковує всі атрибути від `Element`
- `type` автоматично встановлюється як `'center'`

**Призначення:** Центральний склад, з якого товар відправляється до терміналів

#### Terminal (Проміжний термінал)

```python
class Terminal(Element):
    terminal_cost: float      # Фіксована вартість утримання
    processing_cost: float    # Вартість обробки одиниці товару
    is_active: bool = True    # Статус активності
```

**Методи:**
- `__init__(id, x, y, terminal_cost, processing_cost)` - конструктор
- `__repr__()` - строкове представлення з статусом

**Призначення:** Проміжний пункт між центром та споживачами. Може бути вимкнений оптимізацією.

#### Consumer (Споживач)

```python
class Consumer(Element):
    demand: float                    # Попит (об'єм замовлення)
    assigned_terminal: Optional[int] # ID призначеного терміналу
```

**Методи:**
- `__init__(id, x, y, demand)` - конструктор
- `__repr__()` - строкове представлення

**Призначення:** Кінцевий споживач товарів

---

### 2. Логістична мережа (`models/network.py`)

#### Клас LogisticsNetwork

```python
class LogisticsNetwork:
    centers: List[Center]
    terminals: List[Terminal]
    consumers: List[Consumer]
    cost_calculator: CostCalculator
```

**Основні методи:**

##### Ініціалізація

```python
def __init__(self, centers, terminals, consumers, 
             transport_cost_per_unit=1.0)
```

Автоматично викликає `_initialize_network()`, яка:
- Активує всі термінали
- Прив'язує споживачів до найближчих терміналів

##### Управління мережею

```python
def assign_consumers_to_terminals(self)
```
Перерозподіляє всіх споживачів до найближчих **активних** терміналів.

```python
def get_terminal_by_id(self, terminal_id: int) -> Terminal
```
Знаходить термінал за ID. Викидає `ValueError` якщо не знайдено.

```python
def get_active_terminals(self) -> List[Terminal]
```
Повертає список активних терміналів.

##### Обчислення витрат

```python
def calculate_costs(self) -> Dict[str, float]
```

Повертає словник:
```python
{
    'fixed_costs': float,                    # Фіксовані витрати терміналів
    'processing_costs': float,               # Витрати на обробку
    'transport_center_to_terminal': float,   # Центр → Термінали
    'transport_terminal_to_consumer': float, # Термінали → Споживачі
    'transport_total': float,                # Загальні транспортні
    'total_cost': float                      # ЗАГАЛЬНІ ВИТРАТИ
}
```

---

### 3. Обчислення відстаней (`services/distance.py`)

#### Функції

```python
def euclidean_distance(elem1, elem2) -> float
```
**Формула:** `√((x2-x1)² + (y2-y1)²)`

**Параметри:**
- `elem1, elem2` - елементи типу `Element` або кортежі `(x, y)`

```python
def manhattan_distance(elem1, elem2) -> float
```
**Формула:** `|x2-x1| + |y2-y1|`

```python
def find_nearest_terminal(consumer, terminals, 
                         active_only=True) -> tuple
```
**Повертає:** `(terminal, distance)` - найближчий термінал та відстань

**Складність:** O(n), де n - кількість терміналів

---

### 4. Калькулятор витрат (`services/cost_calculator.py`)

#### Клас CostCalculator

```python
class CostCalculator:
    transport_cost_per_unit: float  # Вартість транспорту за одиницю відстані
```

##### Компоненти витрат

**1. Фіксовані витрати терміналів**

```python
def calculate_terminal_fixed_costs(terminals) -> float
```

Формула:
```
Σ(terminal_cost) для всіх активних терміналів
```

**2. Витрати на обробку**

```python
def calculate_processing_costs(terminals, consumers) -> float
```

Формула:
```
Σ(processing_cost × demand) для кожного терміналу
```

**3. Витрати на транспортування**

```python
def calculate_transportation_costs(center, terminals, consumers) 
    -> Tuple[float, float, float]
```

Формули:
```
Центр → Термінал:
  cost = distance(center, terminal) × transport_cost × total_demand

Термінал → Споживач:
  cost = distance(terminal, consumer) × transport_cost × demand
```

**Повертає:** `(center_to_terminal, terminal_to_consumer, total)`

---

## Алгоритми оптимізації

### Базовий клас Optimizer (`optimizers/base.py`)

```python
class Optimizer(ABC):
    network: LogisticsNetwork
    initial_cost: float
    final_cost: float
    optimization_history: list
    
    @abstractmethod
    def optimize(self) -> Dict[str, float]:
        pass
```

**Методи:**
- `get_improvement()` - обчислює покращення
- `print_results()` - виводить результати

---

### Метод покоординатного спуску (МПО)

**Файл:** `optimizers/coordinate.py`

**Реалізація:** Класична специфікація p-median problem з перебором локацій

#### Алгоритм

```python
class CoordinateOptimizer(Optimizer):
    step_size: float        # Не використовується (для сумісності)
    max_iterations: int     # Макс. проходів (default: 100)
    tolerance: float        # Мін. покращення між проходами (default: 0.01)
```

#### Псевдокод

```
function OPTIMIZE():
    initial_cost = calculate_costs()
    possible_locations = create_location_grid()  // Сітка з кроком 5

    // Фаза 1: Оптимізація позицій терміналів
    for pass in 1..max_iterations:
        pass_start_cost = current_cost

        // Оптимізація кожного терміналу
        for each active_terminal:
            best_location = current_location
            best_cost = current_cost

            // Перебір ВСІХ можливих локацій
            for each location in possible_locations:
                terminal.move_to(location)
                reassign_consumers()
                new_cost = calculate_costs()

                if new_cost < best_cost:
                    best_cost = new_cost
                    best_location = location

            terminal.move_to(best_location)
            current_cost = best_cost

        // Перевірка збіжності між проходами
        if (pass_start_cost - current_cost) < tolerance:
            break

    // Фаза 2: Перевірка доцільності терміналів
    for each active_terminal:
        deactivate(terminal)
        new_cost = calculate_costs()
        if new_cost < current_cost:
            current_cost = new_cost  // Залишаємо деактивованим
        else:
            activate(terminal)       // Повертаємо назад

    return results
```

#### Формування можливих локацій

```python
def _get_possible_locations() -> List[Tuple[float, float]]:
    """
    Створює сітку потенційних локацій:
    1. Знаходить межі області (min/max координат споживачів)
    2. Створює регулярну сітку з кроком 5 одиниць
    3. Виключає локації, що співпадають зі споживачами (epsilon < 0.1)
    4. Додає позицію центру

    Результат: набір дискретних локацій для розміщення терміналів
    """
```

**Складність:** O(L × C × N × P), де:
- L - кількість можливих локацій (~400 для області 100×100)
- C - кількість споживачів
- N - кількість терміналів
- P - кількість проходів (зазвичай 2-5)

#### Вимикання терміналів

```python
def _try_deactivate_terminals(current_cost, verbose) -> bool:
    """
    1. Для кожного активного терміналу:
       - Тимчасово вимикає
       - Перерозподіляє споживачів
       - Обчислює нові витрати
       - Якщо витрати менші → залишає вимкненим
       - Інакше → повертає назад
    2. Повертає True якщо хоча б 1 термінал вимкнено
    """
```

**Обробка помилок:**
- `ValueError` якщо неможливо вимкнути (немає інших активних терміналів)
- Автоматично повертає термінал назад

---

### Цільова функція

**Загальна формула:**

```
F(x) = Σ(fixed_costs) + Σ(processing_costs) + Σ(transport_costs)

де:
  fixed_costs = Σ(terminal_cost_i) для активних терміналів i

  processing_costs = Σ(processing_cost_i × demand_i) для терміналів i

  transport_costs =
    Σ(dist(center, terminal_i) × transport_cost × demand_i × 0.1) +
    Σ(dist(terminal_i, consumer_j) × transport_cost × demand_j)
```

**Коефіцієнт 0.1 для центр→термінали:**
- Логіка: транспорт оптом від центру дешевший ніж роздрібна доставка
- Великі вантажівки центр→термінали vs малі машини термінали→споживачі
- Без цього коефіцієнта оптимально розміщувати всі термінали в центрі

**Мета:** Мінімізувати F(x)

---

## Візуалізація

### Клас NetworkVisualizer (`services/visualization.py`)

```python
class NetworkVisualizer:
    figsize: tuple         # Розмір графіка
    colors: dict          # Кольорова схема
```

#### Кольорова схема

```python
colors = {
    'center': '#FF6B6B',              # Червоний (центр)
    'terminal_active': '#4ECDC4',     # Бірюзовий (активний)
    'terminal_inactive': '#95A5A6',   # Сірий (неактивний)
    'consumer': '#45B7D1',            # Синій (споживач)
    'connection': '#BDC3C7',          # Сірий (з'єднання)
}
```

#### Методи

##### Малювання мережі

```python
def plot_network(network, title, show_connections=True, ax=None)
```

**Елементи візуалізації:**
1. Центр - червоний квадрат (500pt, alpha=1.0)
2. Активні термінали - бірюзові трикутники (300pt, alpha=1.0) з підписами
3. Неактивні термінали - сірі хрестики (150pt, alpha=0.4) **без підписів**
4. Споживачі - сині кружки (100pt, alpha=0.8)
5. З'єднання - сірі лінії (alpha=0.3)

**Покращення візуалізації неактивних терміналів:**
- Менший розмір: 300pt → 150pt (не перекривають споживачів)
- Напівпрозорі: alpha=0.4 (менш помітні)
- Без підписів: тільки сірий хрестик (уникає плутанини)
- Нижчий шар: zorder=2 (під споживачами)

**Z-order шари:**
- 5: Центр (найвище)
- 4: Активні термінали
- 3: Споживачі
- 2: Неактивні термінали
- 1: З'єднання (найнижче)

##### Порівняння мереж

```python
def compare_networks(network_before, network_after, 
                    costs_before, costs_after, save_path)
```

Створює графік 2×1:
- Ліва панель: до оптимізації
- Права панель: після оптимізації
- Автоматично створює директорію `results/`
- Зберігає з DPI=300

##### Порівняння витрат

```python
def plot_cost_comparison(costs_before, costs_after, save_path)
```

Створює 2 графіки:
1. **Стовпчикова діаграма** - витрати по категоріях
2. **Загальні витрати** - до/після зі стрілкою економії

---

## Інтерактивний режим

### Вибір файлів даних (main.py)

Програма підтримує інтерактивний вибір CSV файлів з директорії `data/`.

#### Функції

```python
def get_csv_files(data_dir: str = 'data') -> list
```
**Призначення:** Сканує директорію та повертає список CSV файлів

```python
def display_file_menu(csv_files: list) -> int
```
**Призначення:**
- Відображає пронумерований список файлів
- Приймає вибір користувача (1-N)
- Повертає індекс обраного файлу або -1 для виходу

#### Робочий процес

```
1. get_csv_files('data/') → список CSV
2. display_file_menu(csv_files) → вибір користувача
3. selected_file = csv_files[selected_idx]
4. file_basename = selected_file.stem
5. Оптимізація...
6. Збереження результатів: results/{file_basename}_*.png
```

**Переваги:**
- Зручна робота з кількома тестовими мережами
- Результати зберігаються з унікальними іменами
- Можливість порівняння різних конфігурацій

---

## Завантаження даних

### data_loader.py

#### Формат CSV

```csv
id,x,y,type,demand,terminal_cost,processing_cost
```

**Колонки:**
- `id` (int) - унікальний ідентифікатор
- `x, y` (float) - координати
- `type` (str) - тип: 'center', 'terminal', 'consumer'
- `demand` (float) - попит (тільки для consumer)
- `terminal_cost` (float) - фіксована вартість (тільки для terminal)
- `processing_cost` (float) - вартість обробки (тільки для terminal)

#### Функції

```python
def load_network_from_csv(file_path) -> Tuple[List[Center], 
                                              List[Terminal], 
                                              List[Consumer]]
```

**Процес:**
1. Відкриває CSV з кодуванням UTF-8
2. Читає рядки через `csv.DictReader`
3. Створює об'єкти відповідного типу
4. Повертає 3 списки

```python
def validate_network_data(centers, terminals, consumers) -> bool
```

**Перевірки:**
- Хоча б 1 центр
- Хоча б 1 термінал
- Хоча б 1 споживач
- Унікальність ID
- Позитивні значення витрат і попиту

**Викидає `ValueError`** при помилках

---

## Розширення системи

### Додавання нового оптимізатора

1. **Створіть клас успадкувавши від `Optimizer`:**

```python
from optimizers.base import Optimizer

class GeneticOptimizer(Optimizer):
    def __init__(self, network, population_size=50, generations=100):
        super().__init__(network)
        self.population_size = population_size
        self.generations = generations
    
    def optimize(self) -> Dict[str, float]:
        # Реалізація генетичного алгоритму
        self.initial_cost = self.network.calculate_costs()['total_cost']
        
        # ... ваш код ...
        
        self.final_cost = ...
        return self.get_improvement()
```

2. **Використання:**

```python
from optimizers.genetic import GeneticOptimizer

optimizer = GeneticOptimizer(network, population_size=100)
results = optimizer.optimize()
optimizer.print_results()
```

### Додавання нових обмежень

**Приклад: капацитет терміналу**

1. Додайте атрибут до `Terminal`:

```python
class Terminal(Element):
    capacity: float  # Максимальний об'єм
```

2. Додайте перевірку в оптимізатор:

```python
def _check_capacity_constraint(self, terminal):
    load = self.network.get_terminal_load(terminal.id)
    return load <= terminal.capacity
```

3. Використовуйте в оптимізації:

```python
if new_cost < best_cost and self._check_capacity_constraint(terminal):
    best_cost = new_cost
```

### Додавання нових метрик

**Приклад: час доставки**

1. Додайте до `CostCalculator`:

```python
def calculate_delivery_time(self, center, terminals, consumers, 
                           speed=50) -> float:
    """
    speed: км/год
    """
    max_time = 0
    for consumer in consumers:
        terminal = get_terminal_by_id(consumer.assigned_terminal)
        distance = euclidean_distance(center, terminal) + \
                   euclidean_distance(terminal, consumer)
        time = distance / speed
        max_time = max(max_time, time)
    return max_time
```

2. Додайте до цільової функції:

```python
total_cost = costs + α × delivery_time
```

---

## Оптимізація продуктивності

### Поточна складність

**МПО (з перебором локацій):**
- Один прохід: O(L × N × C)
- Де L - кількість можливих локацій, N - термінали, C - споживачі
- Загальна: O(P × L × N × C), P - кількість проходів

### Можливі покращення

1. **Кешування відстаней:**

```python
self._distance_cache = {}

def get_distance(self, elem1, elem2):
    key = (elem1.id, elem2.id)
    if key not in self._distance_cache:
        self._distance_cache[key] = euclidean_distance(elem1, elem2)
    return self._distance_cache[key]
```

2. **Паралелізація:**

```python
from multiprocessing import Pool

def optimize_terminals_parallel(self):
    with Pool() as pool:
        results = pool.map(self._optimize_terminal_position, 
                          self.network.get_active_terminals())
```

3. **Numpy для масових обчислень:**

```python
import numpy as np

def calculate_all_distances(self, terminals, consumers):
    t_coords = np.array([[t.x, t.y] for t in terminals])
    c_coords = np.array([[c.x, c.y] for c in consumers])
    # Векторизовані обчислення
    distances = np.linalg.norm(t_coords[:, None] - c_coords, axis=2)
    return distances
```

---

## Тестування

### Unit тести

```python
import unittest
from models.element import Terminal, Consumer
from services.distance import euclidean_distance

class TestDistance(unittest.TestCase):
    def test_euclidean_distance(self):
        elem1 = Terminal(1, 0, 0, 100, 10)
        elem2 = Consumer(2, 3, 4, 50)
        self.assertAlmostEqual(euclidean_distance(elem1, elem2), 5.0)
```

### Інтеграційні тести

```python
class TestOptimization(unittest.TestCase):
    def test_mpo_reduces_cost(self):
        network = load_test_network()
        initial_cost = network.calculate_costs()['total_cost']
        
        optimizer = CoordinateOptimizer(network)
        optimizer.optimize(verbose=False)
        
        final_cost = network.calculate_costs()['total_cost']
        self.assertLess(final_cost, initial_cost)
```

---

## Логування

### Додавання логування

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('optimization.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Використання
logger.info(f"Iteration {iteration}: cost improved by {improvement}%")
logger.warning(f"Terminal {terminal.id} has no consumers")
logger.error(f"Failed to optimize: {error}")
```

---

## Конфігурація

### config.py

```python
class Config:
    # Оптимізація
    STEP_SIZE = 2.0
    MAX_ITERATIONS = 50
    TOLERANCE = 0.1
    
    # Витрати
    TRANSPORT_COST_PER_UNIT = 1.0
    
    # Візуалізація
    FIGURE_SIZE = (12, 8)
    DPI = 300
    
    # Шляхи
    DATA_PATH = 'data/network_data.csv'
    RESULTS_PATH = 'results/'
```

---

## API для розширення

### Інтерфейси

```python
from abc import ABC, abstractmethod

class OptimizationStrategy(ABC):
    @abstractmethod
    def optimize(self, network: LogisticsNetwork) -> float:
        pass

class CostFunction(ABC):
    @abstractmethod
    def calculate(self, network: LogisticsNetwork) -> float:
        pass

class Visualizer(ABC):
    @abstractmethod
    def plot(self, network: LogisticsNetwork):
        pass
```

---

## Діаграми

### Діаграма класів (спрощена)

```
┌─────────────┐
│   Element   │
└──────┬──────┘
       │
   ┌───┴────┬─────────┬──────────┐
   │        │         │          │
┌──▼──┐ ┌──▼────┐ ┌──▼─────┐    │
│Center│ │Terminal│ │Consumer│    │
└──────┘ └────────┘ └────────┘    │
                                  │
                    ┌─────────────▼────────┐
                    │  LogisticsNetwork    │
                    │  - centers           │
                    │  - terminals         │
                    │  - consumers         │
                    │  - cost_calculator   │
                    └──────────────────────┘
                              │
                              │
                    ┌─────────▼──────────┐
                    │   CostCalculator   │
                    └────────────────────┘
```

### Потік даних

```
CSV Файл
   ↓
data_loader.load_network_from_csv()
   ↓
Elements (Center, Terminal, Consumer)
   ↓
LogisticsNetwork.__init__()
   ↓
_initialize_network()
   ↓
CoordinateOptimizer.optimize()
   ↓
Оптимізована мережа
   ↓
NetworkVisualizer.compare_networks()
   ↓
Графіки PNG
```

---

**Версія:** 1.0  
**Дата оновлення:** 2025-01-12  
**Автор:** Logistics Optimizer Team
