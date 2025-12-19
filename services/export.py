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
            writer = csv.DictWriter(f, fieldnames=data_row.keys(), quoting=csv.QUOTE_MINIMAL)
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
            writer = csv.DictWriter(f, fieldnames=mpo_row.keys(), quoting=csv.QUOTE_MINIMAL)
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
            writer = csv.DictWriter(f, fieldnames=data_row.keys(), quoting=csv.QUOTE_MINIMAL)
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

        # Визначення кількості ітерацій
        if optimizer_type in ['МПО', 'mpo']:
            # Для МПО - це кількість фактичних проходів
            iterations = results.get('iterations', '')
        else:
            # Для ЕМ-ГА - це кількість поколінь
            iterations = parameters.get('generations', '')

        # Спрощена структура для дипломної роботи
        row = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'dataset': dataset_name,
            'method': 'MPO' if optimizer_type in ['МПО', 'mpo'] else 'GA',
            'initial_cost': round(results.get('initial_cost', 0), 2),
            'final_cost': round(results.get('final_cost', 0), 2),
            'improvement_abs': round(results.get('absolute_improvement', 0), 2),
            'improvement_pct': round(results.get('percentage_improvement', 0), 2),
            'terminals_before': active_before,
            'terminals_after': active_after,
            'execution_time': round(execution_time, 2),
            'iterations': iterations,
        }

        return row
