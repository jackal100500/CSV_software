# -*- coding: utf-8 -*-
"""
Timeline Manager для Multi-Parameter Data Analyzer v2.0 - исправленная версия
=============================================================================

Управление универсальной временной шкалой и интерполяцией данных.

Связанные файлы:
- data_manager.py: Источник данных и анализа колонок
- ../ui/column_selector.py: Интерфейс выбора пар "время + параметр"
- ../utils/interpolation.py: Алгоритмы интерполяции

Автор: j15
Версия: 2.0.0-dev
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
        
        # Настройки интерполяции
        self.interpolation_step: float = 1.0  # секунды
        self.interpolation_method: str = 'linear'
        
        # Кэш результатов
        self.interpolated_data: Optional[pd.DataFrame] = None
        self.last_processed_hash: Optional[str] = None
        
        print("TimelineManager v2.0 инициализирован")
    
    def detect_time_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Автоматическое определение столбцов времени через DataManager
        
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
        print(f"Обнаружено временных колонок: {len(self.time_columns)}")
        
        return self.time_columns
    
    def auto_detect_pairs(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """
        Автоматическое определение пар "время + параметр"
        
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
                                pairs: List[Tuple[str, str]] = None,
                                step_seconds: float = None) -> pd.DatetimeIndex:
        """
        Создание универсальной временной шкалы
        
        Args:
            df: DataFrame с данными
            pairs: Пары колонок (опционально)
            step_seconds: Шаг временной сетки в секундах
            
        Returns:
            Универсальная временная шкала
        """
        if step_seconds is not None:
            self.interpolation_step = step_seconds
        
        if pairs is None:
            pairs = self.param_pairs
        
        if not pairs:
            pairs = self.auto_detect_pairs(df)
        
        # Собираем все временные данные
        all_times = []
        for time_col, _ in pairs:
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
        
        print(f"Временной диапазон: {min_time} - {max_time}")
          # Создаем равномерную временную сетку
        freq_str = f'{self.interpolation_step}s'  # Секунды (новый формат)
        timeline = pd.date_range(
            start=min_time,
            end=max_time,
            freq=freq_str
        )
        
        self.universal_timeline = timeline
        print(f"Создана универсальная временная шкала: {len(timeline)} точек с шагом {self.interpolation_step}с")
        
        return timeline
    
    def interpolate_parameters(self, df: pd.DataFrame, 
                             pairs: List[Tuple[str, str]] = None) -> Dict[str, pd.Series]:
        """
        Интерполяция всех параметров на универсальную временную шкалу
        
        Args:
            df: Исходные данные
            pairs: Пары для интерполяции
            
        Returns:
            Словарь с интерполированными данными
        """
        if self.universal_timeline is None:
            self.create_universal_timeline(df, pairs)
        
        if pairs is None:
            pairs = self.param_pairs
        
        result = {}
        
        # Интерполируем каждую пару "время + параметр"
        for time_col, param_col in pairs:
            try:
                # Подготавливаем данные для интерполяции
                temp_df = df[[time_col, param_col]].dropna()
                if temp_df.empty:
                    continue
                
                # Преобразуем время
                temp_df[time_col] = pd.to_datetime(temp_df[time_col])
                temp_df = temp_df.sort_values(time_col)
                
                # Выполняем интерполяцию
                interpolated_values = self._interpolate_series(
                    temp_df[time_col], 
                    temp_df[param_col],
                    self.universal_timeline
                )
                
                # Сохраняем результат
                result[param_col] = pd.Series(interpolated_values, index=self.universal_timeline)
                print(f"Интерполирован параметр {param_col}: {len(interpolated_values)} точек")
                
            except Exception as e:
                print(f"Ошибка интерполяции {time_col}+{param_col}: {e}")
                continue
        
        return result
    
    def _interpolate_series(self, time_series: pd.Series, 
                          value_series: pd.Series,
                          target_timeline: pd.DatetimeIndex) -> np.ndarray:
        """
        Интерполяция одной серии данных
        
        Args:
            time_series: Временные метки
            value_series: Значения параметра
            target_timeline: Целевая временная шкала
            
        Returns:
            Интерполированные значения
        """
        # Преобразуем время в численный формат для интерполяции
        time_numeric = time_series.astype(np.int64) / 10**9  # Unix timestamp
        target_numeric = target_timeline.astype(np.int64) / 10**9
        
        # Выполняем линейную интерполяцию
        interpolated = np.interp(
            target_numeric,
            time_numeric,
            value_series.values
        )
        
        return interpolated
    
    def _extract_number(self, column_name: str) -> Optional[int]:
        """Извлечение номера из названия столбца"""
        import re
        numbers = re.findall(r'\d+', str(column_name))
        if numbers:
            return int(numbers[-1])  # Берем последний номер
        return None
    
    def set_interpolation_step(self, step_seconds: float):
        """Установка шага интерполяции"""
        self.interpolation_step = step_seconds
        print(f"Шаг интерполяции установлен: {step_seconds} сек")
    
    def validate_time_column(self, df: pd.DataFrame, column_name: str) -> bool:
        """Валидация временной колонки"""
        if column_name not in df.columns:
            return False
        
        try:
            time_data = pd.to_datetime(df[column_name].dropna())
            return len(time_data) >= 2 and time_data.nunique() >= 2
        except Exception:
            return False
    
    def get_interpolation_info(self) -> Dict[str, Union[str, int, float]]:
        """Получение информации о текущей интерполяции"""
        info = {
            'time_columns_count': len(self.time_columns),
            'param_pairs_count': len(self.param_pairs),
            'interpolation_step': self.interpolation_step,
            'interpolation_method': self.interpolation_method,
            'timeline_points': len(self.universal_timeline) if self.universal_timeline is not None else 0,
        }
        
        if self.universal_timeline is not None:
            info['timeline_start'] = self.universal_timeline[0]
            info['timeline_end'] = self.universal_timeline[-1]
            info['timeline_duration'] = str(self.universal_timeline[-1] - self.universal_timeline[0])
        
        return info


# Связанные файлы для импорта в других модулях:
# from core.timeline_manager_v2 import TimelineManager
