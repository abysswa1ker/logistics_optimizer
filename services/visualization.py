# -*- coding: utf-8 -*-
"""
Візуалізація логістичної мережі
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import List, Optional
from models.network import LogisticsNetwork
from models.element import Center, Terminal, Consumer
import copy


class NetworkVisualizer:
    """
    Клас для візуалізації логістичної мережі
    """

    def __init__(self, figsize=(12, 8)):
        """
        Ініціалізація візуалізатора

        Args:
            figsize: Розмір фігури (ширина, висота)
        """
        self.figsize = figsize
        self.colors = {
            'center': '#FF6B6B',      # Червоний
            'terminal_active': '#4ECDC4',  # Бірюзовий
            'terminal_inactive': '#95A5A6', # Сірий
            'consumer': '#45B7D1',    # Синій
            'connection': '#BDC3C7',  # Світло-сірий
        }

    def plot_network(self, network: LogisticsNetwork, title: str = "Логістична мережа",
                    show_connections: bool = True, ax=None):
        """
        Малює мережу на графіку

        Args:
            network: Логістична мережа
            title: Заголовок графіка
            show_connections: Показувати з'єднання між елементами
            ax: Matplotlib axes (якщо None, створюється новий)

        Returns:
            Matplotlib axes
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)

        # Малюємо з'єднання (якщо потрібно)
        if show_connections:
            self._draw_connections(network, ax)

        # Малюємо центр
        center = network.get_center()
        ax.scatter(center.x, center.y, c=self.colors['center'], 
                  s=500, marker='s', label='Розподільчий центр',
                  edgecolors='black', linewidths=2, zorder=5)
        ax.text(center.x, center.y - 5, f'DC', 
               ha='center', va='top', fontsize=10, fontweight='bold')

        # Малюємо термінали
        for terminal in network.terminals:
            if terminal.is_active:
                color = self.colors['terminal_active']
                label = 'Активний термінал'
                marker = '^'
            else:
                color = self.colors['terminal_inactive']
                label = 'Неактивний термінал'
                marker = 'x'

            ax.scatter(terminal.x, terminal.y, c=color, s=300, 
                      marker=marker, label=label,
                      edgecolors='black', linewidths=1.5, zorder=4)
            
            status = "✓" if terminal.is_active else "✗"
            ax.text(terminal.x, terminal.y + 5, f'T{terminal.id} {status}', 
                   ha='center', va='bottom', fontsize=9, fontweight='bold')

        # Малюємо споживачів
        consumer_x = [c.x for c in network.consumers]
        consumer_y = [c.y for c in network.consumers]
        ax.scatter(consumer_x, consumer_y, c=self.colors['consumer'], 
                  s=100, marker='o', label='Споживач',
                  edgecolors='black', linewidths=0.5, alpha=0.7, zorder=3)

        # Підписи для перших 5 споживачів
        for i, consumer in enumerate(network.consumers[:5]):
            ax.text(consumer.x + 2, consumer.y + 2, f'C{consumer.id}', 
                   fontsize=7, alpha=0.7)

        # Налаштування графіка
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('X координата', fontsize=11)
        ax.set_ylabel('Y координата', fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Видаляємо дублікати в легенді
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), 
                 loc='upper right', fontsize=9, framealpha=0.9)

        # Додаємо відступи
        ax.margins(0.1)

        return ax

    def _draw_connections(self, network: LogisticsNetwork, ax):
        """
        Малює з'єднання між елементами мережі

        Args:
            network: Логістична мережа
            ax: Matplotlib axes
        """
        center = network.get_center()

        # З'єднання центр → активні термінали
        for terminal in network.get_active_terminals():
            ax.plot([center.x, terminal.x], [center.y, terminal.y],
                   color=self.colors['connection'], linewidth=2, 
                   linestyle='-', alpha=0.4, zorder=1)

        # З'єднання термінали → споживачі
        for consumer in network.consumers:
            terminal = network.get_terminal_by_id(consumer.assigned_terminal)
            if terminal.is_active:
                ax.plot([terminal.x, consumer.x], [terminal.y, consumer.y],
                       color=self.colors['connection'], linewidth=0.5, 
                       linestyle='--', alpha=0.3, zorder=1)

    def compare_networks(self, network_before: LogisticsNetwork, 
                        network_after: LogisticsNetwork,
                        costs_before: dict, costs_after: dict,
                        save_path: Optional[str] = None):
        """
        Порівнює дві мережі (до та після оптимізації)

        Args:
            network_before: Мережа до оптимізації
            network_after: Мережа після оптимізації
            costs_before: Витрати до оптимізації
            costs_after: Витрати після оптимізації
            save_path: Шлях для збереження графіка
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

        # Ліва панель - до оптимізації
        self.plot_network(network_before, 
                         title=f"До оптимізації\nВитрати: {costs_before['total_cost']:,.2f}",
                         ax=ax1)

        # Права панель - після оптимізації
        improvement_pct = ((costs_before['total_cost'] - costs_after['total_cost']) / 
                          costs_before['total_cost']) * 100
        self.plot_network(network_after,
                         title=f"Після оптимізації (МПО)\nВитрати: {costs_after['total_cost']:,.2f} (↓{improvement_pct:.1f}%)",
                         ax=ax2)

        # Загальний заголовок
        fig.suptitle('ПОРІВНЯННЯ МЕРЕЖІ ДО ТА ПІСЛЯ ОПТИМІЗАЦІЇ', 
                    fontsize=16, fontweight='bold', y=0.98)

        plt.tight_layout(rect=[0, 0, 1, 0.96])

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n📊 Графік збережено: {save_path}")

        plt.show()

    def plot_cost_comparison(self, costs_before: dict, costs_after: dict,
                            save_path: Optional[str] = None):
        """
        Малює порівняння витрат

        Args:
            costs_before: Витрати до оптимізації
            costs_after: Витрати після оптимізації
            save_path: Шлях для збереження графіка
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Категорії витрат
        categories = ['Фіксовані\nвитрати', 'Обробка', 'Транспорт\nЦентр→Термінали',
                     'Транспорт\nТермінали→Споживачі']
        
        before_values = [
            costs_before['fixed_costs'],
            costs_before['processing_costs'],
            costs_before['transport_center_to_terminal'],
            costs_before['transport_terminal_to_consumer']
        ]
        
        after_values = [
            costs_after['fixed_costs'],
            costs_after['processing_costs'],
            costs_after['transport_center_to_terminal'],
            costs_after['transport_terminal_to_consumer']
        ]

        # Графік 1: Стовпчикова діаграма
        x = range(len(categories))
        width = 0.35

        bars1 = ax1.bar([i - width/2 for i in x], before_values, width, 
                       label='До оптимізації', color='#E74C3C', alpha=0.8)
        bars2 = ax1.bar([i + width/2 for i in x], after_values, width,
                       label='Після оптимізації', color='#27AE60', alpha=0.8)

        ax1.set_xlabel('Категорія витрат', fontsize=11)
        ax1.set_ylabel('Вартість', fontsize=11)
        ax1.set_title('Порівняння витрат по категоріях', fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories, fontsize=9)
        ax1.legend(fontsize=10)
        ax1.grid(axis='y', alpha=0.3)

        # Графік 2: Загальні витрати
        total_before = costs_before['total_cost']
        total_after = costs_after['total_cost']
        saving = total_before - total_after
        saving_pct = (saving / total_before) * 100

        bars = ax2.bar(['До оптимізації', 'Після оптимізації'], 
                      [total_before, total_after],
                      color=['#E74C3C', '#27AE60'], alpha=0.8, width=0.5)

        # Додаємо значення на стовпчиках
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.0f}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

        # Стрілка економії
        ax2.annotate('', xy=(1, total_after), xytext=(1, total_before),
                    arrowprops=dict(arrowstyle='<->', color='green', lw=2))
        ax2.text(1.15, (total_before + total_after) / 2,
                f'Економія:\n{saving:,.0f}\n({saving_pct:.1f}%)',
                fontsize=10, color='green', fontweight='bold',
                va='center')

        ax2.set_ylabel('Загальні витрати', fontsize=11)
        ax2.set_title('Загальні витрати', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n📊 Графік витрат збережено: {save_path}")

        plt.show()
