# -*- coding: utf-8 -*-
"""
Data Manager для Multi-Parameter Data Analyzer v2.0
===================================================

Управление загрузкой, обработкой и валидацией данных.

Связанные файлы:
- ../ui/main_window.py: Основной потребитель данных
- timeline_manager.py: Передача данных для создания временной шкалы
- ../utils/file_utils.py: Низкоуровневая загрузка файлов
- ../config/settings.py: Настройки обработки данных

Функции v2.0:
- Централизованное управление DataFrame
- Кэширование обработанных данных
- Валидация структуры данных
- Метаданные о колонках и типах данных

Автор: j15
Версия: 2.0.0-dev
GitHub: https://github.com/jackal100500/CSV_software
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging


class DataManager:
    """
    Менеджер данных для централизованной работы с DataFrame.
    
    Связанные компоненты:
    - timeline_manager: Получает данные для создания временной шкалы (timeline_manager.py)
    - main_window: Основной потребитель данных (ui/main_window.py)
    - file_utils: Загрузка данных из файлов (utils/file_utils.py)
    """
    
    def __init__(self):
        """Инициализация менеджера данных"""
        self.df = None  # Основной DataFrame
        self.file_path = None  # Путь к загруженному файлу
        self.metadata = {}  # Метаданные о колонках
        self.cache = {}  # Кэш обработанных данных
        
        # Настройка логирования
        self.logger = logging.getLogger(__name__)
        
        print("DataManager v2.0 инициализирован")
        print("Связанные модули:")
        print("- timeline_manager.py: Передача данных для временной шкалы")
        print("- file_utils.py: Загрузка файлов")
    
    def set_dataframe(self, df: pd.DataFrame, file_path: Optional[str] = None):
        """
        Установка основного DataFrame
        
        Args:
            df: DataFrame с данными
            file_path: Путь к файлу (опционально)
            
        Связанные методы:
        - analyze_columns(): Анализ структуры данных
        - validate_dataframe(): Проверка корректности
        """
        self.df = df.copy()
        self.file_path = file_path
        self.cache.clear()  # Очистка кэша при смене данных
        
        # Анализ структуры данных
        self.analyze_columns()
        
        # Валидация данных
        if self.validate_dataframe():
            self.logger.info(f"DataFrame установлен: {len(self.df)} строк, {len(self.df.columns)} столбцов")
            print(f"DataManager: Загружены данные ({len(self.df)} x {len(self.df.columns)})")
        else:
            self.logger.warning("DataFrame содержит потенциальные проблемы")
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Получение копии основного DataFrame
        
        Returns:
            pd.DataFrame: Копия данных для безопасного использования
        """
        if self.df is not None:
            return self.df.copy()
        return None
    
    def analyze_columns(self):
        """
        Анализ колонок для определения типов данных
        
        Результат сохраняется в self.metadata для использования в:
        - timeline_manager.py: Определение временных колонок
        - column_selector.py: Фильтрация подходящих колонок
        """
        if self.df is None:
            return
        
        self.metadata = {
            'columns': {},
            'time_candidates': [],
            'numeric_columns': [],
            'text_columns': [],
            'total_rows': len(self.df),
            'analysis_timestamp': datetime.now()
        }
        
        for col in self.df.columns:
            col_info = self.analyze_single_column(col)
            self.metadata['columns'][col] = col_info
            
            # Классификация колонок
            if col_info['type'] == 'time':
                self.metadata['time_candidates'].append(col)
            elif col_info['type'] == 'numeric':
                self.metadata['numeric_columns'].append(col)
            elif col_info['type'] == 'text':
                self.metadata['text_columns'].append(col)
        
        print(f"Анализ колонок завершен:")
        print(f"  Временные колонки: {len(self.metadata['time_candidates'])}")
        print(f"  Числовые колонки: {len(self.metadata['numeric_columns'])}")
        print(f"  Текстовые колонки: {len(self.metadata['text_columns'])}")
    
    def analyze_single_column(self, column_name: str) -> Dict[str, Any]:
        """
        Анализ отдельной колонки
        
        Args:
            column_name: Имя колонки для анализа
            
        Returns:
            Dict: Метаданные колонки
            
        Используется в:
        - timeline_manager.detect_time_columns(): Поиск временных данных
        """
        col_data = self.df[column_name]
        col_info = {
            'name': column_name,
            'dtype': str(col_data.dtype),
            'non_null_count': col_data.count(),
            'null_count': col_data.isnull().sum(),
            'unique_values': col_data.nunique(),
            'type': 'unknown'
        }
          # Определение типа колонки
        if self.is_time_column(col_data):
            col_info['type'] = 'time'
            col_info['time_format'] = self.detect_time_format(col_data)
            col_info['time_range'] = self.get_time_range(col_data)
        elif self.is_numeric_column(col_data):
            col_info['type'] = 'numeric'
            col_info['min_value'] = col_data.min()
            col_info['max_value'] = col_data.max()
            col_info['mean_value'] = col_data.mean()
        else:
            col_info['type'] = 'text'
            col_info['sample_values'] = col_data.dropna().head(3).tolist()
        
        return col_info
    
    def is_time_column(self, series: pd.Series) -> bool:
        """
        Проверка, является ли колонка временной
        
        Args:
            series: Данные колонки
            
        Returns:
            bool: True если колонка содержит временные данные
            
        Используется в:
        - timeline_manager.detect_time_columns(): Автоматическое определение времени
        """
        if series.empty:
            return False
          # Проверка по названию колонки
        time_keywords = ['time', 'timestamp', 'datetime', 'date', 'время', 'дата']
        col_name_lower = series.name.lower() if series.name else ""
        
        # Исключаем колонки с явно НЕ временными словами
        non_time_keywords = ['information', 'info', 'value', 'val', 'data', 'param', 'parameter']
        has_non_time_keyword = any(keyword in col_name_lower for keyword in non_time_keywords)
        
        if has_non_time_keyword:
            return False
        
        # Строгая проверка: название должно содержать ключевое слово
        name_matches = any(keyword in col_name_lower for keyword in time_keywords)
        if not name_matches:
            return False
        
        # Попытка парсинга как временные данные
        try:
            non_null_data = series.dropna().head(100)  # Тестируем первые 100 значений
            if len(non_null_data) == 0:
                return False
            
            # Проверяем, что это не числовые ID
            if series.name and series.name.lower() in ['id', 'index', 'номер']:
                return False
            
            # Попытка конвертации в datetime
            datetime_series = pd.to_datetime(non_null_data, errors='raise')
            
            # Дополнительная проверка: временные данные должны иметь разброс
            if datetime_series.nunique() < 2:
                return False
                
            return True
            
        except (ValueError, TypeError, pd.errors.ParserError):
            # Попытка числового времени (Unix timestamp)
            try:
                numeric_data = pd.to_numeric(non_null_data, errors='raise')
                # Проверка разумных диапазонов timestamp и что это не просто ID
                if (numeric_data.min() > 1_000_000_000 and 
                    numeric_data.max() < 3_000_000_000 and
                    numeric_data.nunique() > len(numeric_data) * 0.8):  # Высокая уникальность
                    return True
            except (ValueError, TypeError):
                pass
        
        return False
    
    def is_numeric_column(self, series: pd.Series) -> bool:
        """
        Проверка, является ли колонка числовой
        
        Args:
            series: Данные колонки
            
        Returns:
            bool: True если колонка содержит числовые данные
        """
        if series.empty:
            return False
        
        # Проверка типа данных pandas
        if pd.api.types.is_numeric_dtype(series):
            return True
        
        # Попытка конвертации в числовой тип
        try:
            non_null_data = series.dropna().head(100)
            if len(non_null_data) == 0:
                return False
            
            pd.to_numeric(non_null_data, errors='raise')
            return True
            
        except (ValueError, TypeError):
            return False
    
    def detect_time_format(self, series: pd.Series) -> Optional[str]:
        """
        Определение формата временных данных
        
        Args:
            series: Временная колонка
            
        Returns:
            str: Определенный формат времени
            
        Используется в:
        - timeline_manager.py: Корректная обработка времени
        """
        if not self.is_time_column(series):
            return None
        
        sample_data = series.dropna().head(10)
        if len(sample_data) == 0:
            return None
        
        # Популярные форматы времени
        formats_to_try = [
            '%Y-%m-%d %H:%M:%S',
            '%d.%m.%Y %H:%M:%S',
            '%Y-%m-%d',
            '%d.%m.%Y',
            '%H:%M:%S',
            'timestamp'  # Unix timestamp
        ]
        
        for fmt in formats_to_try:
            try:
                if fmt == 'timestamp':
                    # Проверка Unix timestamp
                    numeric_data = pd.to_numeric(sample_data)
                    if numeric_data.min() > 1_000_000_000:
                        return 'timestamp'
                else:
                    # Проверка строкового формата
                    pd.to_datetime(sample_data, format=fmt)
                    return fmt
            except (ValueError, TypeError):
                continue
        
        return 'auto'  # Автоматическое определение pandas
    
    def get_time_range(self, series: pd.Series) -> Optional[Tuple[Any, Any]]:
        """
        Получение временного диапазона колонки
        
        Args:
            series: Временная колонка
            
        Returns:
            Tuple: (минимальное время, максимальное время)
        """
        if not self.is_time_column(series):
            return None
        
        try:
            time_data = pd.to_datetime(series, errors='coerce').dropna()
            if len(time_data) > 0:
                return (time_data.min(), time_data.max())
        except Exception:
            pass
        
        return None
    
    def validate_dataframe(self) -> bool:
        """
        Валидация загруженного DataFrame
        
        Returns:
            bool: True если данные корректны
            
        Проверки:
        - Наличие данных
        - Корректность индексов
        - Отсутствие критических проблем
        """
        if self.df is None:
            self.logger.error("DataFrame не установлен")
            return False
        
        if self.df.empty:
            self.logger.warning("DataFrame пустой")
            return False
        
        # Проверка дублированных колонок
        duplicate_columns = self.df.columns[self.df.columns.duplicated()].tolist()
        if duplicate_columns:
            self.logger.warning(f"Найдены дублированные колонки: {duplicate_columns}")
        
        # Проверка полностью пустых колонок
        empty_columns = [col for col in self.df.columns if self.df[col].isnull().all()]
        if empty_columns:
            self.logger.warning(f"Полностью пустые колонки: {empty_columns}")
        
        # Проверка наличия временных данных
        if not self.metadata.get('time_candidates'):
            self.logger.warning("Не найдено временных колонок")
        
        return True
    
    def get_column_metadata(self, column_name: str) -> Optional[Dict[str, Any]]:
        """
        Получение метаданных конкретной колонки
        
        Args:
            column_name: Имя колонки
            
        Returns:
            Dict: Метаданные колонки
            
        Используется в:
        - column_selector.py: Отображение информации о колонках
        - timeline_manager.py: Валидация временных колонок
        """
        return self.metadata.get('columns', {}).get(column_name)
    
    def get_time_candidates(self) -> List[str]:
        """
        Получение списка потенциальных временных колонок
        
        Returns:
            List[str]: Имена временных колонок
            
        Используется в:
        - timeline_manager.detect_time_columns(): Поиск временных данных
        - column_selector.py: Фильтрация временных колонок
        """
        return self.metadata.get('time_candidates', [])
    
    def get_numeric_columns(self) -> List[str]:
        """
        Получение списка числовых колонок
        
        Returns:
            List[str]: Имена числовых колонок
            
        Используется в:
        - column_selector.py: Фильтрация параметров для отображения
        """
        return self.metadata.get('numeric_columns', [])
    
    def cache_processed_data(self, key: str, data: Any):
        """
        Кэширование обработанных данных
        
        Args:
            key: Ключ для кэша
            data: Данные для сохранения
            
        Используется в:
        - timeline_manager.py: Кэширование интерполированных данных
        """
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """
        Получение данных из кэша
        
        Args:
            key: Ключ кэша
            
        Returns:
            Any: Кэшированные данные или None
        """
        cache_entry = self.cache.get(key)
        if cache_entry:
            return cache_entry['data']
        return None
    
    def clear_cache(self):
        """Очистка кэша обработанных данных"""
        self.cache.clear()
        print("Кэш DataManager очищен")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Получение сводной информации о данных
        
        Returns:
            Dict: Сводная информация
            
        Используется в:
        - main_window.py: Отображение информации о файле
        """
        if self.df is None:
            return {"status": "no_data"}
        
        return {
            "status": "loaded",
            "file_path": self.file_path,
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "time_columns": len(self.metadata.get('time_candidates', [])),
            "numeric_columns": len(self.metadata.get('numeric_columns', [])),
            "text_columns": len(self.metadata.get('text_columns', [])),
            "memory_usage": self.df.memory_usage(deep=True).sum(),
            "analysis_time": self.metadata.get('analysis_timestamp')
        }


# Связанные файлы для импорта в других модулях:
# from core.data_manager import DataManager
