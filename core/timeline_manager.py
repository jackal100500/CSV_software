# -*- coding: utf-8 -*-
"""
Timeline Manager для Multi-Parameter Data Analyzer v2.0
========================================================

Управление универсальной временной шкалой и интерполяцией данных.

Связанные файлы:
- ../ui/column_selector.py: Интерфейс выбора пар "время + параметр"
- ../utils/interpolation.py: Алгоритмы интерполяции
- ../core/data_manager.py: Источник данных для обработки
- ../DEVELOPMENT_PLAN_v2.0.md: Техническая спецификация

Основные возможности v2.0:
- Автоматическое определение столбцов времени
- Парная привязка "время + параметр"
- Создание универсальной временной сетки
- Интерполяция всех параметров на единую шкалу

Автор: j15
GitHub: https://github.com/jackal100500/CSV_software
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional, Union


class TimelineManager:
    """
    Менеджер универсальной временной шкалы для v2.0
    
    Связанные компоненты:
    - utils.interpolation: Методы интерполяции
    - core.data_manager: Источник данных
    - ui.column_selector: Интерфейс выбора пар
    """
    
    def __init__(self):
        """Инициализация менеджера временной шкалы"""
        # Основные данные
        self.time_columns: List[str] = []
        self.param_pairs: List[Tuple[str, str]] = []  # [(time_col, param_col), ...]
        self.universal_timeline: Optional[pd.DatetimeIndex] = None
          # Настройки интерполяции (связаны с config/settings.py)
        self.interpolation_step: float = 1.0  # секунды
        self.interpolation_method: str = 'linear'  # 'linear', 'nearest', 'cubic'
        
        # Кэш результатов (связан с core/plot_manager.py)
        self.interpolated_data: Optional[pd.DataFrame] = None
        self.last_processed_hash: Optional[str] = None
    
    def detect_time_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Автоматическое определение столбцов времени
        
        Связанные файлы:
        - core/data_manager.py: Использует улучшенный алгоритм анализа колонок
        
        Args:
            df: DataFrame для анализа
            
        Returns:
            Список названий столбцов с временными данными
        """
        from .data_manager import DataManager
        
        # Используем DataManager для точного определения временных колонок
        temp_data_manager = DataManager()
        temp_data_manager.set_dataframe(df)
        
        # Получаем временные колонки из улучшенного алгоритма
        time_candidates = temp_data_manager.get_time_candidates()
        
        self.time_columns = time_candidates
        return self.time_columns
    
    def auto_detect_pairs(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """
        Автоматическое определение пар "время + параметр"
        
        Связанные файлы:
        - ui/column_selector.py: Использует результат для предзаполнения интерфейса
        - core/data_manager.py: Использует данные о типах колонок
        
        Args:
            df: DataFrame для анализа
            
        Returns:
            Список пар (time_column, parameter_column)
        """
        from .data_manager import DataManager
        
        # Используем DataManager для получения актуальной информации о колонках
        temp_data_manager = DataManager()
        temp_data_manager.set_dataframe(df)
        
        time_columns = temp_data_manager.get_time_candidates()
        numeric_columns = temp_data_manager.get_numeric_columns()
        
        if not time_columns:
            print("Не найдено временных колонок для создания пар")
            return []
        
        if not numeric_columns:
            print("Не найдено числовых колонок для создания пар")
            return []
        
        pairs = []
        available_params = numeric_columns.copy()
        
        # Умный алгоритм сопоставления пар
        for time_col in time_columns:
            best_match = None
            
            # Извлекаем номер из названия временной колонки
            time_number = self._extract_number(time_col)
            
            # Ищем параметр с тем же номером
            if time_number is not None:
                for param_col in available_params:
                    param_number = self._extract_number(param_col)
                    if param_number == time_number:
                        best_match = param_col
                        break
            
            # Если не нашли по номеру, берем первый доступный параметр
            if not best_match and available_params:
                best_match = available_params[0]
            
            if best_match:
                pairs.append((time_col, best_match))
                available_params.remove(best_match)
                print(f"Создана пара: {time_col} -> {best_match}")
        
        self.param_pairs = pairs
        return pairs
    
    def create_universal_timeline(self, df: pd.DataFrame, 
                                step_seconds: float = None) -> pd.DatetimeIndex:
        """
        Создание универсальной временной шкалы
        
        Связанные файлы:
        - config/settings.py: Настройки шага интерполяции
        - core/plot_manager.py: Использует результат для построения графиков
        
        Args:
            df: DataFrame с данными
            step_seconds: Шаг временной сетки в секундах
            
        Returns:
            Универсальная временная шкала
        """
        if step_seconds is not None:
            self.interpolation_step = step_seconds
        
        if not self.time_columns:
            self.detect_time_columns(df)
        
        # Преобразуем все временные столбцы к datetime
        all_times = []
        for time_col in self.time_columns:
            try:
                times = pd.to_datetime(df[time_col].dropna())
                all_times.extend(times.tolist())
            except Exception as e:
                print(f"Ошибка преобразования столбца {time_col}: {e}")
                continue
        
        if not all_times:
            raise ValueError("Не найдено валидных временных данных")
        
        # Определяем границы временного диапазона
        min_time = min(all_times)
        max_time = max(all_times)
        
        # Создаем равномерную временную сетку
        freq_str = f'{self.interpolation_step}S'  # Секунды
        timeline = pd.date_range(
            start=min_time,
            end=max_time,
            freq=freq_str
        )
        
        self.universal_timeline = timeline
        return timeline
    
    def interpolate_parameters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Интерполяция всех параметров на универсальную временную шкалу
        
        Связанные файлы:
        - utils/interpolation.py: Реализация алгоритмов интерполяции
        - core/plot_manager.py: Потребитель интерполированных данных
        
        Args:
            df: Исходные данные
            
        Returns:
            DataFrame с интерполированными данными
        """
        if self.universal_timeline is None:
            self.create_universal_timeline(df)
        
        if not self.param_pairs:
            self.auto_detect_pairs(df)
        
        # Создаем результирующий DataFrame
        result = pd.DataFrame({
            'universal_time': self.universal_timeline
        })
        
        # Интерполируем каждую пару "время + параметр"
        for time_col, param_col in self.param_pairs:
            try:
                # Подготавливаем данные для интерполяции
                temp_df = df[[time_col, param_col]].dropna()
                if temp_df.empty:
                    continue
                
                # Преобразуем время
                temp_df[time_col] = pd.to_datetime(temp_df[time_col])
                temp_df = temp_df.sort_values(time_col)
                
                # Выполняем интерполяцию (связано с utils/interpolation.py)
                interpolated_values = self._interpolate_series(
                    temp_df[time_col], 
                    temp_df[param_col],
                    self.universal_timeline
                )
                
                # Добавляем в результат
                result[f"{param_col}_interpolated"] = interpolated_values
                
            except Exception as e:
                print(f"Ошибка интерполяции {time_col}+{param_col}: {e}")
                continue
        
        self.interpolated_data = result
        return result
    
    def _interpolate_series(self, time_series: pd.Series, 
                          value_series: pd.Series,
                          target_timeline: pd.DatetimeIndex) -> np.ndarray:
        """
        Интерполяция одной серии данных
        
        Связанные файлы:
        - utils/interpolation.py: Расширенные алгоритмы интерполяции
        
        Args:
            time_series: Временные метки
            value_series: Значения параметра
            target_timeline: Целевая временная шкала
            
        Returns:
            Интерполированные значения
        """
        # Преобразуем время в численный формат для интерполяции
        time_numeric = time_series.astype(np.int64) // 10**9  # Unix timestamp
        target_numeric = target_timeline.astype(np.int64) // 10**9
        
        # Выполняем интерполяцию
        interpolated = np.interp(
            target_numeric,
            time_numeric,
            value_series.values
        )
        
        return interpolated
    
    def _extract_base_name(self, column_name: str) -> str:
        """Извлечение базового имени столбца (без номеров)"""
        import re
        # Удаляем числа и специальные символы с конца
        base = re.sub(r'[\d\s\._-]+$', '', str(column_name))
        return base.strip()
    
    def _extract_number(self, column_name: str) -> Optional[int]:
        """Извлечение номера из названия столбца"""
        import re
        numbers = re.findall(r'\d+', str(column_name))
        if numbers:
            return int(numbers[-1])  # Берем последний номер
        return None
    
    def get_interpolation_info(self) -> Dict[str, Union[str, int, float]]:
        """
        Получение информации о текущей интерполяции
        
        Связанные файлы:
        - ui/main_window.py: Отображение статистики интерполяции
        
        Returns:
            Словарь с информацией об интерполяции
        """
        info = {
            'time_columns_count': len(self.time_columns),
            'param_pairs_count': len(self.param_pairs),
            'interpolation_step': self.interpolation_step,
            'interpolation_method': self.interpolation_method,
            'timeline_points': len(self.universal_timeline) if self.universal_timeline is not None else 0,
            'has_interpolated_data': self.interpolated_data is not None
        }
        
        if self.universal_timeline is not None:
            info['timeline_start'] = self.universal_timeline[0]
            info['timeline_end'] = self.universal_timeline[-1]
            info['timeline_duration'] = str(self.universal_timeline[-1] - self.universal_timeline[0])
        
        return info
    
    def set_interpolation_step(self, step_seconds: float):
        """
        Установка шага интерполяции
        
        Args:
            step_seconds: Шаг в секундах
            
        Используется в:
        - main_window.py: Настройка пользователем
        """
        self.interpolation_step = step_seconds
        print(f"Шаг интерполяции установлен: {step_seconds} сек")
    
    def validate_time_column(self, df: pd.DataFrame, column_name: str) -> bool:
        """
        Валидация временной колонки
        
        Args:
            df: DataFrame с данными
            column_name: Имя колонки для проверки
            
        Returns:
            bool: True если колонка содержит корректные временные данные
            
        Используется в:
        - column_selector.py: Проверка выбранных временных колонок
        """
        if column_name not in df.columns:
            return False
        
        try:
            # Пробуем преобразовать в datetime
            time_data = pd.to_datetime(df[column_name].dropna())
            
            # Проверяем, что есть хотя бы несколько валидных временных точек
            if len(time_data) < 2:
                return False
            
            # Проверяем, что время не одинаковое
            if time_data.nunique() < 2:
                return False
            
            return True
            
        except Exception:
            return False
