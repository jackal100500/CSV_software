"""
Simple Timeline Manager для версии 1.1
Управляет парами "время + параметр" без сложной интерполяции
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Tuple, Dict, Optional


class SimpleTimelineManager:
    """
    Простой менеджер временных шкал для версии 1.1
    
    Основные функции:
    - Автоопределение столбцов времени
    - Автоматическая привязка пар "время + параметр"
    - Создание объединенной временной шкалы
    - Подготовка данных для графика
    """
    
    def __init__(self):
        self.time_param_pairs = []  # [(time_col, param_col), ...]
        self.combined_timeline = None
        self.time_keywords = ['date', 'time', 'datetime', 'дата', 'время', 'timestamp']
        
    def detect_time_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Автоматически находит столбцы времени по ключевым словам
        
        Args:
            df: DataFrame для анализа
            
        Returns:
            Список имен столбцов времени
        """
        time_columns = []
        
        for col in df.columns:
            col_lower = str(col).lower()
            
            # Проверяем по ключевым словам
            if any(keyword in col_lower for keyword in self.time_keywords):
                time_columns.append(col)
                continue
                
            # Проверяем тип данных (пытаемся преобразовать к datetime)
            try:
                sample = df[col].dropna().head(10)
                if len(sample) > 0:
                    pd.to_datetime(sample, errors='raise')
                    time_columns.append(col)
            except:
                continue
                
        return time_columns
    
    def auto_detect_pairs(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """
        Автоматически связывает столбцы времени с параметрами
        
        Логика: ищет числовой столбец справа от каждого столбца времени
        
        Args:
            df: DataFrame для анализа
            
        Returns:
            Список пар (time_column, param_column)
        """
        time_columns = self.detect_time_columns(df)
        pairs = []
        columns_list = list(df.columns)
        
        for time_col in time_columns:
            time_idx = columns_list.index(time_col)
            
            # Ищем ближайший числовой столбец справа
            for i in range(time_idx + 1, len(columns_list)):
                param_col = columns_list[i]
                
                # Проверяем, что это числовой столбец
                if pd.api.types.is_numeric_dtype(df[param_col]):
                    # Проверяем, что столбец еще не использован
                    if not any(pair[1] == param_col for pair in pairs):
                        pairs.append((time_col, param_col))
                        break
                        
        return pairs
    
    def validate_pairs(self, df: pd.DataFrame, pairs: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        Проверяет валидность пар и удаляет невалидные
        
        Args:
            df: DataFrame
            pairs: Список пар для проверки
            
        Returns:
            Список валидных пар
        """
        valid_pairs = []
        
        for time_col, param_col in pairs:
            try:
                # Проверяем существование столбцов
                if time_col not in df.columns or param_col not in df.columns:
                    continue
                    
                # Проверяем, что столбец времени можно преобразовать к datetime
                time_sample = df[time_col].dropna().head(5)
                if len(time_sample) == 0:
                    continue
                    
                pd.to_datetime(time_sample, errors='raise')
                
                # Проверяем, что параметр числовой
                if not pd.api.types.is_numeric_dtype(df[param_col]):
                    continue
                    
                # Проверяем, что есть непустые данные
                param_sample = df[param_col].dropna()
                if len(param_sample) == 0:
                    continue
                    
                valid_pairs.append((time_col, param_col))
                
            except Exception as e:
                print(f"Ошибка валидации пары {time_col}-{param_col}: {e}")
                continue
                
        return valid_pairs
    
    def create_combined_timeline(self, df: pd.DataFrame, pairs: List[Tuple[str, str]]) -> pd.DatetimeIndex:
        """
        Создает объединенную временную шкалу из всех столбцов времени
        
        Args:
            df: DataFrame
            pairs: Список пар (time_col, param_col)
            
        Returns:
            Объединенный и отсортированный DatetimeIndex
        """
        all_times = []
        
        for time_col, _ in pairs:
            try:
                time_series = pd.to_datetime(df[time_col].dropna())
                all_times.extend(time_series.tolist())
            except Exception as e:
                print(f"Ошибка преобразования времени в столбце {time_col}: {e}")
                continue
        
        if not all_times:
            return pd.DatetimeIndex([])
            
        # Убираем дубликаты и сортируем
        unique_times = sorted(list(set(all_times)))
        return pd.DatetimeIndex(unique_times)
    
    def prepare_plot_data(self, df: pd.DataFrame, pairs: List[Tuple[str, str]]) -> Dict:
        """
        Подготавливает данные для построения графика
        
        Args:
            df: DataFrame
            pairs: Список пар (time_col, param_col)
            
        Returns:
            Словарь с данными для каждого параметра
        """
        plot_data = {}
        
        for time_col, param_col in pairs:
            try:
                # Получаем временные метки и значения
                time_data = pd.to_datetime(df[time_col])
                param_data = df[param_col]
                
                # Создаем DataFrame для удобства
                temp_df = pd.DataFrame({
                    'time': time_data,
                    'value': param_data
                }).dropna()
                
                if len(temp_df) == 0:
                    continue
                    
                # Сортируем по времени
                temp_df = temp_df.sort_values('time')
                
                plot_data[param_col] = {
                    'time': temp_df['time'].values,
                    'values': temp_df['value'].values,
                    'time_column': time_col,
                    'param_column': param_col
                }
                
            except Exception as e:
                print(f"Ошибка подготовки данных для пары {time_col}-{param_col}: {e}")
                continue
                
        return plot_data
    
    def set_pairs(self, pairs: List[Tuple[str, str]]):
        """Устанавливает пары вручную"""
        self.time_param_pairs = pairs
        
    def get_pairs(self) -> List[Tuple[str, str]]:
        """Возвращает текущие пары"""
        return self.time_param_pairs
    
    def add_pair(self, time_col: str, param_col: str):
        """Добавляет новую пару"""
        if (time_col, param_col) not in self.time_param_pairs:
            self.time_param_pairs.append((time_col, param_col))
    
    def remove_pair(self, time_col: str, param_col: str):
        """Удаляет пару"""
        if (time_col, param_col) in self.time_param_pairs:
            self.time_param_pairs.remove((time_col, param_col))
    
    def get_time_range(self, df: pd.DataFrame, pairs: List[Tuple[str, str]]) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Возвращает общий временной диапазон для всех пар
        
        Returns:
            (min_time, max_time) или (None, None) если нет данных
        """
        all_times = []
        
        for time_col, _ in pairs:
            try:
                time_series = pd.to_datetime(df[time_col].dropna())
                if len(time_series) > 0:
                    all_times.extend([time_series.min(), time_series.max()])
            except:
                continue
                
        if not all_times:
            return None, None
            
        return min(all_times), max(all_times)
