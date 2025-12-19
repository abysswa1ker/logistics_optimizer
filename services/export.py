"""
Модуль для експорту результатів оптимізації у CSV-файли
"""

import csv
import os
from datetime import datetime
from typing import Dict, Any, Optional
from models.network import LogisticsNetwork


class ResultsExporter:
    """Клас для експорту результатів оптимізації"""

    def __init__(self, export_dir: str = "results/exports"):
        """
        Ініціалізація експортера

        Args:
            export_dir: Директорія для збереження файлів експорту
        """
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)

    def export_single_optimization(self,
                                   dataset_name: str,
                                   optimizer_type: str,
                                   parameters: Dict[str, Any],
                                   results: Dict[str, Any],
                                   network_before: LogisticsNetwork,
                                   network_after: LogisticsNetwork,
                                   execution_time: float,
                                   filename: Optional[str] = None) -> str:
        """
        Експорт результатів одиночної оптимізації

        Args:
            dataset_name: Назва тестового набору даних
            optimizer_type: Тип оптимізатора ('mpo' або 'ga')
            parameters: Параметри оптимізації
            results: Результати оптимізації
            network_before: Мережа до оптимізації
            network_after: Мережа після оптимізації
            execution_time: Час виконання (секунди)
            filename: Опціональне ім'я файлу (за замовчуванням генерується автоматично)

        Returns:
            Шлях до збереженого файлу
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{dataset_name}_{optimizer_type}_{timestamp}.csv"

        filepath = os.path.join(self.export_dir, filename)

        # Підготовка даних
        data_row = self._prepare_single_row(
            dataset_name, optimizer_type, parameters,
            results, network_before, network_after, execution_time
        )

        # Запис у CSV
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=data_row.keys(), quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerow(data_row)

        return filepath

    def export_comparison(self,
                         dataset_name: str,
                         mpo_data: Dict[str, Any],
                         ga_data: Dict[str, Any],
                         network_before: LogisticsNetwork,
                         filename: Optional[str] = None) -> str:
        """
        Експорт результатів порівняльного аналізу

        Args:
            dataset_name: Назва тестового набору даних
            mpo_data: Дані про МПО (parameters, results, network, execution_time)
            ga_data: Дані про ЕМ-ГА (parameters, results, network, execution_time)
            network_before: Мережа до оптимізації
            filename: Опціональне ім'я файлу

        Returns:
            Шлях до збереженого файлу
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{dataset_name}_comparison_{timestamp}.csv"

        filepath = os.path.join(self.export_dir, filename)

        # Підготовка рядків для обох методів
        mpo_row = self._prepare_single_row(
            dataset_name, 'МПО', mpo_data['parameters'],
            mpo_data['results'], network_before, mpo_data['network'],
            mpo_data['execution_time']
        )

        ga_row = self._prepare_single_row(
            dataset_name, 'ЕМ-ГА', ga_data['parameters'],
            ga_data['results'], network_before, ga_data['network'],
            ga_data['execution_time']
        )

        # Запис у CSV
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=mpo_row.keys(), quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerow(mpo_row)
            writer.writerow(ga_row)

        return filepath

    def append_to_experiments_log(self,
                                  dataset_name: str,
                                  optimizer_type: str,
                                  parameters: Dict[str, Any],
                                  results: Dict[str, Any],
                                  network_before: LogisticsNetwork,
                                  network_after: LogisticsNetwork,
                                  execution_time: float,
                                  log_filename: str = "experiments_log.csv") -> str:
        """
        Додає результат до загального лог-файлу експериментів

        Args:
            dataset_name: Назва тестового набору даних
            optimizer_type: Тип оптимізатора
            parameters: Параметри оптимізації
            results: Результати оптимізації
            network_before: Мережа до оптимізації
            network_after: Мережа після оптимізації
            execution_time: Час виконання
            log_filename: Ім'я лог-файлу

        Returns:
            Шлях до лог-файлу
        """
        filepath = os.path.join(self.export_dir, log_filename)

        # Підготовка даних
        data_row = self._prepare_single_row(
            dataset_name, optimizer_type, parameters,
            results, network_before, network_after, execution_time
        )

        # Перевірка чи існує файл
        file_exists = os.path.isfile(filepath)

        # Додавання до файлу
        with open(filepath, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=data_row.keys(), quoting=csv.QUOTE_ALL)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data_row)

        return filepath

    def _prepare_single_row(self,
                           dataset_name: str,
                           optimizer_type: str,
                           parameters: Dict[str, Any],
                           results: Dict[str, Any],
                           network_before: LogisticsNetwork,
                           network_after: LogisticsNetwork,
                           execution_time: float) -> Dict[str, Any]:
        """
        Підготовка одного рядка даних для експорту

        Returns:
            Словник з даними для CSV
        """
        # Підрахунок активних терміналів
        active_before = sum(1 for t in network_before.terminals if t.is_active)
        active_after = sum(1 for t in network_after.terminals if t.is_active)

        # Базові дані
        row = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'dataset_name': dataset_name,
            'optimizer_type': optimizer_type,

            # Результати
            'initial_cost': results.get('initial_cost', 0),
            'final_cost': results.get('final_cost', 0),
            'absolute_improvement': results.get('absolute_improvement', 0),
            'percentage_improvement': results.get('percentage_improvement', 0),
            'execution_time_sec': execution_time,

            # Конфігурація мережі
            'terminals_count': len(network_before.terminals),
            'consumers_count': len(network_before.consumers),
            'active_terminals_before': active_before,
            'active_terminals_after': active_after,
            'terminals_deactivated': active_before - active_after,
        }

        # Додавання параметрів оптимізації (залежно від типу)
        if optimizer_type in ['МПО', 'mpo']:
            row.update({
                'mpo_step_size': parameters.get('step_size', ''),
                'mpo_max_iterations': parameters.get('max_iterations', ''),
                'mpo_tolerance': parameters.get('tolerance', ''),
                'ga_population_size': '',
                'ga_generations': '',
                'ga_mutation_rate': '',
                'ga_crossover_rate': '',
            })
        else:  # ЕМ-ГА
            row.update({
                'mpo_step_size': '',
                'mpo_max_iterations': '',
                'mpo_tolerance': '',
                'ga_population_size': parameters.get('population_size', ''),
                'ga_generations': parameters.get('generations', ''),
                'ga_mutation_rate': parameters.get('mutation_rate', ''),
                'ga_crossover_rate': parameters.get('crossover_rate', ''),
            })

        # Додавання детальної конфігурації терміналів
        terminals_config_before = ';'.join([
            f"T{t.id}:{'ON' if t.is_active else 'OFF'}@({t.x:.1f},{t.y:.1f})"
            for t in network_before.terminals
        ])
        terminals_config_after = ';'.join([
            f"T{t.id}:{'ON' if t.is_active else 'OFF'}@({t.x:.1f},{t.y:.1f})"
            for t in network_after.terminals
        ])

        row['terminals_config_before'] = terminals_config_before
        row['terminals_config_after'] = terminals_config_after

        return row
