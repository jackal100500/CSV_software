# -*- coding: utf-8 -*-
"""
Settings для Multi-Parameter Data Analyzer v2.0
===============================================

Управление настройками приложения.

Связанные файлы:
- ../ui/main_window.py: Использует настройки интерфейса
- ../core/timeline_manager.py: Настройки интерполяции и временной шкалы
- ../core/plot_manager.py: Настройки стилей графиков
- ../utils/interpolation.py: Методы интерполяции по умолчанию

Категории настроек:
- Интерполяция и временная шкала
- Стили и цвета графиков
- Интерфейс пользователя
- Производительность

Автор: j15
Версия: 2.0.0-dev
GitHub: https://github.com/jackal100500/CSV_software
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import timedelta
import logging


class Settings:
    """
    Менеджер настроек приложения.
    
    Связанные компоненты:
    - main_window: Настройки интерфейса (ui/main_window.py)
    - timeline_manager: Настройки интерполяции (core/timeline_manager.py)
    - plot_manager: Настройки графиков (core/plot_manager.py)
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Инициализация настроек
        
        Args:
            config_file: Путь к файлу конфигурации (опционально)
        """
        self.config_file = config_file or "config.json"
        self.logger = logging.getLogger(__name__)
        
        # Настройки по умолчанию
        self._defaults = self._get_default_settings()
        
        # Текущие настройки
        self._settings = self._defaults.copy()
        
        # Загрузка сохраненных настроек
        self.load_settings()
        
        print("Settings v2.0 инициализированы")
        print("Связанные модули:")
        print("- timeline_manager.py: Настройки интерполяции")
        print("- plot_manager.py: Стили графиков")
        print("- main_window.py: Настройки интерфейса")
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """
        Получение настроек по умолчанию
        
        Returns:
            Dict: Настройки по умолчанию для всех модулей
        """
        return {
            # Настройки интерполяции (для timeline_manager.py)
            'interpolation': {
                'default_method': 'linear',  # linear, nearest, cubic, polynomial, step
                'default_time_step': 1.0,    # секунды
                'auto_detect_step': True,    # Автоматическое определение шага
                'enable_extrapolation': False,  # Экстраполяция за границы данных
                'max_interpolation_points': 100000,  # Максимум точек интерполяции
                'quality_threshold': 0.8     # Порог качества интерполяции
            },
            
            # Настройки временной шкалы (для timeline_manager.py)
            'timeline': {
                'auto_time_detection': True,     # Автоопределение временных колонок
                'time_column_keywords': [        # Ключевые слова для поиска времени
                    'time', 'timestamp', 'datetime', 'date',
                    'время', 'дата', 'временная_метка'
                ],
                'time_formats': [                # Поддерживаемые форматы времени
                    '%Y-%m-%d %H:%M:%S',
                    '%d.%m.%Y %H:%M:%S',
                    '%Y-%m-%d',
                    '%d.%m.%Y',
                    '%H:%M:%S'
                ],
                'unix_timestamp_detection': True,  # Определение Unix timestamp
                'min_time_points': 2             # Минимум точек для временной колонки
            },
            
            # Настройки графиков (для plot_manager.py)
            'plotting': {
                'default_colors': [
                    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                    '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
                ],
                'line_styles': ['-', '--', '-.', ':'],
                'line_width': 1.5,
                'marker_size': 4,
                'grid_alpha': 0.3,
                'legend_location': 'best',
                'figure_dpi': 100,
                'auto_scale': True,
                'show_data_points': False,       # Показывать точки данных
                'max_legend_items': 20          # Максимум элементов в легенде
            },
            
            # Настройки интерфейса (для main_window.py)
            'ui': {
                'window_width': 1200,
                'window_height': 800,
                'remember_window_size': True,
                'default_file_path': '',         # Последняя папка с файлами
                'recent_files_count': 10,        # Количество недавних файлов
                'auto_save_interval': 300,       # Автосохранение настроек (сек)
                'show_tooltips': True,
                'theme': 'default',              # Тема интерфейса
                'language': 'ru'                 # Язык интерфейса
            },
            
            # Настройки производительности
            'performance': {
                'max_file_size_mb': 100,         # Максимальный размер файла
                'chunk_size': 10000,             # Размер блока для обработки
                'memory_limit_mb': 512,          # Лимит памяти
                'enable_caching': True,          # Кэширование результатов
                'parallel_processing': False,    # Параллельная обработка
                'max_preview_rows': 1000        # Максимум строк для предпросмотра
            },
            
            # Настройки файлов (для file_utils.py)
            'files': {
                'auto_detect_encoding': True,    # Автоопределение кодировки
                'default_encoding': 'utf-8',     # Кодировка по умолчанию
                'auto_detect_delimiter': True,   # Автоопределение разделителя CSV
                'default_delimiter': ',',        # Разделитель по умолчанию
                'skip_empty_rows': True,         # Пропускать пустые строки
                'backup_on_save': True          # Создавать резервные копии
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Получение значения настройки по пути
        
        Args:
            key_path: Путь к настройке (например, 'interpolation.default_method')
            default: Значение по умолчанию
            
        Returns:
            Any: Значение настройки
            
        Используется в:
        - timeline_manager.py: self.settings.get('interpolation.default_method')
        - plot_manager.py: self.settings.get('plotting.default_colors')
        """
        keys = key_path.split('.')
        value = self._settings
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """
        Установка значения настройки
        
        Args:
            key_path: Путь к настройке
            value: Новое значение
            
        Используется в:
        - main_window.py: Сохранение пользовательских предпочтений
        """
        keys = key_path.split('.')
        setting_dict = self._settings
        
        # Создание вложенных словарей при необходимости
        for key in keys[:-1]:
            if key not in setting_dict or not isinstance(setting_dict[key], dict):
                setting_dict[key] = {}
            setting_dict = setting_dict[key]
        
        # Установка значения
        setting_dict[keys[-1]] = value
        
        print(f"Настройка изменена: {key_path} = {value}")
    
    def get_interpolation_settings(self) -> Dict[str, Any]:
        """
        Получение всех настроек интерполяции
        
        Returns:
            Dict: Настройки интерполяции
            
        Используется в:
        - timeline_manager.py: Инициализация параметров интерполяции
        """
        return self._settings.get('interpolation', {})
    
    def get_timeline_settings(self) -> Dict[str, Any]:
        """
        Получение настроек временной шкалы
        
        Returns:
            Dict: Настройки временной шкалы
            
        Используется в:
        - timeline_manager.py: Настройки определения временных колонок
        """
        return self._settings.get('timeline', {})
    
    def get_plotting_settings(self) -> Dict[str, Any]:
        """
        Получение настроек графиков
        
        Returns:
            Dict: Настройки графиков
            
        Используется в:
        - plot_manager.py: Стили и цвета графиков
        """
        return self._settings.get('plotting', {})
    
    def get_ui_settings(self) -> Dict[str, Any]:
        """
        Получение настроек интерфейса
        
        Returns:
            Dict: Настройки интерфейса
            
        Используется в:
        - main_window.py: Размеры окна и пользовательские предпочтения
        """
        return self._settings.get('ui', {})
    
    def get_performance_settings(self) -> Dict[str, Any]:
        """
        Получение настроек производительности
        
        Returns:
            Dict: Настройки производительности
        """
        return self._settings.get('performance', {})
    
    def get_file_settings(self) -> Dict[str, Any]:
        """
        Получение настроек файлов
        
        Returns:
            Dict: Настройки работы с файлами
            
        Используется в:
        - file_utils.py: Параметры загрузки файлов
        """
        return self._settings.get('files', {})
    
    def update_recent_file(self, file_path: str):
        """
        Обновление списка недавних файлов
        
        Args:
            file_path: Путь к файлу
            
        Используется в:
        - main_window.py: Сохранение истории открытых файлов
        """
        recent_files = self.get('ui.recent_files', [])
        
        # Удаление файла из списка, если он уже есть
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Добавление в начало списка
        recent_files.insert(0, file_path)
        
        # Ограничение размера списка
        max_count = self.get('ui.recent_files_count', 10)
        recent_files = recent_files[:max_count]
        
        self.set('ui.recent_files', recent_files)
    
    def get_recent_files(self) -> List[str]:
        """
        Получение списка недавних файлов
        
        Returns:
            List[str]: Список путей к недавним файлам
        """
        recent_files = self.get('ui.recent_files', [])
        
        # Фильтрация существующих файлов
        existing_files = [f for f in recent_files if os.path.exists(f)]
        
        # Обновление списка, если некоторые файлы больше не существуют
        if len(existing_files) != len(recent_files):
            self.set('ui.recent_files', existing_files)
        
        return existing_files
    
    def save_settings(self):
        """
        Сохранение настроек в файл
        
        Используется в:
        - main_window.py: При закрытии приложения
        - Автоматическое сохранение по таймеру
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"Настройки сохранены в {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения настроек: {e}")
    
    def load_settings(self):
        """
        Загрузка настроек из файла
        
        Используется в:
        - __init__(): Автоматическая загрузка при инициализации
        """
        if not os.path.exists(self.config_file):
            print("Файл настроек не найден, используются значения по умолчанию")
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
            
            # Объединение с настройками по умолчанию
            self._merge_settings(loaded_settings)
            
            print(f"Настройки загружены из {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки настроек: {e}")
            print("Используются настройки по умолчанию")
    
    def _merge_settings(self, loaded_settings: Dict[str, Any]):
        """
        Объединение загруженных настроек с настройками по умолчанию
        
        Args:
            loaded_settings: Загруженные настройки
        """
        def deep_merge(default_dict: Dict, loaded_dict: Dict) -> Dict:
            """Глубокое объединение словарей"""
            result = default_dict.copy()
            
            for key, value in loaded_dict.items():
                if (key in result and 
                    isinstance(result[key], dict) and 
                    isinstance(value, dict)):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            
            return result
        
        self._settings = deep_merge(self._defaults, loaded_settings)
    
    def reset_to_defaults(self):
        """
        Сброс всех настроек к значениям по умолчанию
        
        Используется в:
        - main_window.py: Кнопка сброса настроек
        """
        self._settings = self._defaults.copy()
        print("Настройки сброшены к значениям по умолчанию")
    
    def reset_category(self, category: str):
        """
        Сброс настроек категории к значениям по умолчанию
        
        Args:
            category: Имя категории (interpolation, plotting, ui, etc.)
        """
        if category in self._defaults:
            self._settings[category] = self._defaults[category].copy()
            print(f"Настройки категории '{category}' сброшены к значениям по умолчанию")
    
    def export_settings(self, file_path: str) -> bool:
        """
        Экспорт настроек в файл
        
        Args:
            file_path: Путь для экспорта
            
        Returns:
            bool: True если экспорт успешен
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"Настройки экспортированы в {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка экспорта настроек: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """
        Импорт настроек из файла
        
        Args:
            file_path: Путь к файлу настроек
            
        Returns:
            bool: True если импорт успешен
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            self._merge_settings(imported_settings)
            
            print(f"Настройки импортированы из {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка импорта настроек: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Получение всех настроек
        
        Returns:
            Dict: Все текущие настройки
        """
        return self._settings.copy()


# Связанные файлы для импорта в других модулях:
# from config.settings import Settings
