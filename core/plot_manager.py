# -*- coding: utf-8 -*-
"""
Plot Manager для Multi-Parameter Data Analyzer v2.0
===================================================

Управление построением и отображением графиков.

Связанные файлы:
- ../ui/main_window.py: Интеграция с matplotlib в tkinter
- timeline_manager.py: Получение данных универсальной временной шкалы
- data_manager.py: Исходные данные для построения
- ../config/settings.py: Настройки стилей и цветов графиков

Функции v2.0:
- Построение графиков с универсальной временной шкалой
- Отображение интерполированных данных
- Управление стилями и цветами
- Координатная сетка и навигация

Автор: j15
Версия: 2.0.0-dev
GitHub: https://github.com/jackal100500/CSV_software
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional, Any
import logging


class PlotManager:
    """
    Менеджер построения графиков для многопараметрических данных.
    
    Связанные компоненты:
    - main_window: Интеграция с matplotlib canvas (ui/main_window.py)
    - timeline_manager: Источник универсальной временной шкалы (timeline_manager.py)
    - data_manager: Исходные данные (data_manager.py)
    """
    
    def __init__(self):
        """Инициализация менеджера графиков"""
        # Настройки отображения
        self.colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        self.line_styles = ['-', '--', '-.', ':']
        self.marker_styles = ['o', 's', '^', 'v', 'D', '*', '+', 'x']
        
        # Настройки сетки и осей
        self.grid_alpha = 0.3
        self.legend_loc = 'best'
        self.date_format = '%H:%M:%S'
        
        # Настройка логирования
        self.logger = logging.getLogger(__name__)
        
        print("PlotManager v2.0 инициализирован")
        print("Связанные модули:")
        print("- main_window.py: Интеграция с tkinter")
        print("- timeline_manager.py: Универсальная временная шкала")
    
    def plot_interpolated_data(self, ax: Axes, universal_timeline: pd.Series, 
                             interpolated_data: Dict[str, pd.Series],
                             enable_multiple_y_axes: bool = True):
        """
        Построение графика с интерполированными данными на универсальной временной шкале
        
        Args:
            ax: Matplotlib Axes для рисования
            universal_timeline: Универсальная временная шкала из timeline_manager
            interpolated_data: Интерполированные параметры {param_name: values}
            enable_multiple_y_axes: Создавать отдельную ось Y для каждого параметра
            
        Returns:
            List[Axes]: Список всех созданных осей (основная + дополнительные)
        """
        ax.clear()
        if universal_timeline is None or not interpolated_data:
            ax.text(0.5, 0.5, 'Нет данных для отображения', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=14, color='red')
            return [ax]
        # Подготовка временной оси
        time_values = universal_timeline
        if not isinstance(time_values, pd.DatetimeIndex):
            if hasattr(time_values, 'iloc') and len(time_values) > 0:
                first_element = time_values.iloc[0] if hasattr(time_values, 'iloc') else time_values[0]
                if not isinstance(first_element, datetime):
                    try:
                        time_values = pd.to_datetime(time_values)
                    except Exception:
                        pass
            else:
                try:
                    time_values = pd.to_datetime(time_values)
                except Exception:
                    pass
        # Построение графиков для каждого параметра с отдельными осями Y
        axes_list = [ax]  # Основная ось
        param_names = list(interpolated_data.keys())
        for i, (param_name, param_values) in enumerate(interpolated_data.items()):
            if param_values is None or len(param_values) == 0:
                continue
            color = self.colors[i % len(self.colors)]
            if enable_multiple_y_axes and i > 0:
                current_ax = ax.twinx()
                offset = 60 * (i - 1)
                current_ax.spines['right'].set_position(('outward', offset))
                current_ax.set_ylabel(param_name, color=color, fontsize=10, fontweight='bold')
                current_ax.tick_params(axis='y', colors=color, labelsize=9)
                current_ax.spines['right'].set_color(color)
                axes_list.append(current_ax)
            else:
                current_ax = ax
                if enable_multiple_y_axes:
                    current_ax.set_ylabel(param_name, color=color, fontsize=10, fontweight='bold')
                    current_ax.tick_params(axis='y', colors=color, labelsize=9)
            valid_mask = ~pd.isna(param_values)
            if valid_mask.any():
                valid_time = time_values[valid_mask]
                valid_values = param_values[valid_mask]
                current_ax.plot(valid_time, valid_values, 
                              color=color, linewidth=1.5,
                              label=param_name, alpha=0.8)
                if enable_multiple_y_axes and len(valid_values) > 0:
                    y_margin = (valid_values.max() - valid_values.min()) * 0.1
                    current_ax.set_ylim(valid_values.min() - y_margin, 
                                       valid_values.max() + y_margin)
                print(f"  📈 {param_name}: {len(valid_values)} точек, цвет {color}")
            else:
                print(f"  ⚠️ {param_name}: нет валидных данных")
        self.setup_plot_appearance(ax, time_values)
        print(f"Построен график с {len(interpolated_data)} параметрами на универсальной временной шкале")
        return axes_list
    
    def plot_raw_data(self, ax: Axes, df: pd.DataFrame, pairs: List[Tuple[str, str]]):
        """
        Построение графика с исходными данными (режим совместимости с v1.0)
        
        Args:
            ax: Matplotlib Axes для рисования
            df: Исходный DataFrame
            pairs: Пары (time_column, param_column)
            
        Используется в:
        - main_window.plot_data(): Когда интерполяция отключена
        """
        ax.clear()
        
        if df is None or not pairs:
            ax.text(0.5, 0.5, 'Нет данных для отображения', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=14, color='red')
            return
        
        color_idx = 0
        all_time_values = []
        
        # Построение каждой пары отдельно
        for time_col, param_col in pairs:
            try:
                # Получение данных пары
                time_data = df[time_col].dropna()
                param_data = df[param_col].dropna()
                
                # Синхронизация по индексу (простой подход)
                common_index = time_data.index.intersection(param_data.index)
                if len(common_index) == 0:
                    continue
                
                sync_time = time_data.loc[common_index]
                sync_param = param_data.loc[common_index]
                
                # Конвертация времени
                try:
                    sync_time = pd.to_datetime(sync_time)
                    all_time_values.extend(sync_time.tolist())
                except Exception:
                    # Если конвертация не удалась, используем как есть
                    all_time_values.extend(sync_time.tolist())
                
                # Построение линии
                color = self.colors[color_idx % len(self.colors)]
                ax.plot(sync_time, sync_param, 
                       color=color, label=f"{param_col} ({time_col})", 
                       linewidth=1.5, alpha=0.8)
                
                color_idx += 1
                
            except Exception as e:
                self.logger.warning(f"Ошибка построения пары {time_col}-{param_col}: {e}")
                continue
        
        # Настройка осей
        if all_time_values:
            self.setup_plot_appearance(ax, pd.Series(all_time_values))
        else:
            ax.text(0.5, 0.5, 'Не удалось построить ни одного графика', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=12, color='orange')
        
        print(f"Построен график в режиме совместимости с {len(pairs)} парами")
    
    def setup_plot_appearance(self, ax: Axes, time_values: pd.Series):
        """
        Настройка внешнего вида графика
        
        Args:
            ax: Matplotlib Axes
            time_values: Временные значения для настройки оси X
            
        Настраивает:
        - Сетку и стили
        - Формат временной оси
        - Легенду и подписи
        """
        # Настройка сетки
        ax.grid(True, alpha=self.grid_alpha, linestyle='-', linewidth=0.5)
        ax.grid(True, alpha=self.grid_alpha/2, linestyle=':', linewidth=0.3, which='minor')        
        # Настройка временной оси
        if len(time_values) > 0:
            # Проверяем тип первого элемента в зависимости от типа time_values
            first_element = None
            if isinstance(time_values, pd.DatetimeIndex):
                first_element = time_values[0]
            elif hasattr(time_values, 'iloc'):
                first_element = time_values.iloc[0]
            else:
                first_element = time_values[0]
                
            if isinstance(first_element, datetime):
                # Автоматический выбор формата в зависимости от диапазона
                time_range = time_values.max() - time_values.min()
                
                if time_range <= timedelta(hours=1):
                    # Для диапазонов до часа - показываем секунды
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
                elif time_range <= timedelta(days=1):
                    # Для диапазонов до дня - показываем минуты
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                else:
                    # Для больших диапазонов - показываем дни
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M'))
                    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
                
                # Поворот подписей для лучшей читаемости
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Подписи осей
        ax.set_xlabel('Время', fontsize=12, fontweight='bold')
        ax.set_ylabel('Значения параметров', fontsize=12, fontweight='bold')
        
        # Настройка легенды
        if ax.get_legend_handles_labels()[0]:  # Если есть данные для легенды
            legend = ax.legend(loc=self.legend_loc, frameon=True, 
                             fancybox=True, shadow=True, ncol=1)
            legend.get_frame().set_alpha(0.9)
        
        # Автоматическое масштабирование
        ax.autoscale(enable=True, axis='both', tight=True)
        
        # Настройка заголовка
        ax.set_title('Multi-Parameter Data Analysis v2.0', 
                    fontsize=14, fontweight='bold', pad=20)
    
    def add_cursor_line(self, ax: Axes, x_position: float):
        """
        Добавление вертикальной линии курсора
        
        Args:
            ax: Matplotlib Axes
            x_position: Позиция курсора по оси X
            
        Используется в:
        - main_window.on_mouse_move(): Отображение текущей позиции мыши
        """
        # Удаление предыдущих линий курсора
        for line in ax.lines:
            if hasattr(line, '_cursor_line'):
                line.remove()
        
        # Добавление новой линии курсора
        cursor_line = ax.axvline(x=x_position, color='black', 
                               linestyle='--', alpha=0.7, linewidth=1)
        cursor_line._cursor_line = True  # Маркер для идентификации
    
    def set_zoom_region(self, ax: Axes, x_min: float, x_max: float, 
                       y_min: Optional[float] = None, y_max: Optional[float] = None):
        """
        Установка области масштабирования
        
        Args:
            ax: Matplotlib Axes
            x_min, x_max: Границы по оси X
            y_min, y_max: Границы по оси Y (опционально)
            
        Используется в:
        - main_window.on_mouse_scroll(): Масштабирование колесом мыши
        """
        ax.set_xlim(x_min, x_max)
        
        if y_min is not None and y_max is not None:
            ax.set_ylim(y_min, y_max)
        else:
            # Автоматическое масштабирование по Y в пределах X
            ax.relim()
            ax.autoscale_view(scalex=False, scaley=True)
    
    def export_plot(self, ax: Axes, filename: str, dpi: int = 300):
        """
        Экспорт графика в файл
        
        Args:
            ax: Matplotlib Axes
            filename: Имя файла для сохранения
            dpi: Разрешение изображения
            
        Поддерживаемые форматы:
        - PNG, JPG, PDF, SVG
        """
        try:
            fig = ax.get_figure()
            fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            print(f"График сохранен: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка сохранения графика: {e}")
            return False
    
    def get_plot_statistics(self, interpolated_data: Dict[str, pd.Series]) -> Dict[str, Any]:
        """
        Получение статистики построенного графика
        
        Args:
            interpolated_data: Данные графика
            
        Returns:
            Dict: Статистическая информация
            
        Используется в:
        - main_window.py: Отображение информации о графике
        """
        stats = {
            'parameters_count': len(interpolated_data),
            'total_points': 0,
            'parameter_stats': {}
        }
        
        for param_name, param_values in interpolated_data.items():
            if param_values is not None:
                valid_values = param_values.dropna()
                
                param_stat = {
                    'points': len(valid_values),
                    'min': valid_values.min() if len(valid_values) > 0 else None,
                    'max': valid_values.max() if len(valid_values) > 0 else None,
                    'mean': valid_values.mean() if len(valid_values) > 0 else None,
                    'std': valid_values.std() if len(valid_values) > 0 else None
                }
                
                stats['parameter_stats'][param_name] = param_stat
                stats['total_points'] += len(valid_values)
        
        return stats
    
    def clear_plot(self, ax: Axes):
        """
        Очистка графика
        
        Args:
            ax: Matplotlib Axes для очистки
        """
        ax.clear()
        ax.text(0.5, 0.5, 'Загрузите данные и выберите параметры для отображения', 
               transform=ax.transAxes, ha='center', va='center',
               fontsize=12, color='gray', style='italic')
        
        # Базовые настройки пустого графика
        ax.set_xlabel('Время')
        ax.set_ylabel('Значения параметров')
        ax.set_title('Multi-Parameter Data Analyzer v2.0')
        ax.grid(True, alpha=0.3)


# Связанные файлы для импорта в других модулях:
# from core.plot_manager import PlotManager
