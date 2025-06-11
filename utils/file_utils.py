# -*- coding: utf-8 -*-
"""
File Utils для Multi-Parameter Data Analyzer v2.0
=================================================

Утилиты для работы с файлами данных.

Связанные файлы:
- ../ui/main_window.py: Использует load_data_file() для загрузки файлов
- ../core/data_manager.py: Получает DataFrame через данный модуль
- ../config/settings.py: Настройки кодировок и форматов файлов

Поддерживаемые форматы:
- Excel (.xlsx, .xls)
- CSV (.csv) с различными кодировками
- Автоматическое определение разделителей и кодировок

Автор: j15
Версия: 2.0.0-dev
GitHub: https://github.com/jackal100500/CSV_software
"""

import pandas as pd
import os
try:
    import chardet
except ImportError:
    # Fallback: если chardet недоступен, используем utf-8 по умолчанию
    print("⚠️ chardet недоступен, используется utf-8 по умолчанию")
    chardet = None
from typing import Optional, Dict, Any, List
import logging


class FileUtils:
    """
    Утилиты для работы с файлами данных.
    
    Связанные компоненты:
    - main_window: Загрузка файлов пользователем (ui/main_window.py)
    - data_manager: Передача загруженных данных (core/data_manager.py)
    """
    
    @staticmethod
    def load_data_file(file_path: str) -> pd.DataFrame:
        """
        Универсальная загрузка файла данных
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            pd.DataFrame: Загруженные данные
            
        Raises:
            Exception: При ошибке загрузки
            
        Используется в:
        - main_window.load_file(): Основная функция загрузки
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        print(f"Загрузка файла: {os.path.basename(file_path)} ({file_ext})")
        
        try:
            if file_ext in ['.xlsx', '.xls']:
                return FileUtils._load_excel_file(file_path)
            elif file_ext == '.csv':
                return FileUtils._load_csv_file(file_path)
            else:
                # Попытка загрузки как CSV с автоопределением
                print(f"Неизвестное расширение {file_ext}, пробуем как CSV")
                return FileUtils._load_csv_file(file_path)
                
        except Exception as e:
            raise Exception(f"Ошибка загрузки файла {os.path.basename(file_path)}: {str(e)}")
    
    @staticmethod
    def _load_excel_file(file_path: str) -> pd.DataFrame:
        """
        Загрузка Excel файла
        
        Args:
            file_path: Путь к Excel файлу
            
        Returns:
            pd.DataFrame: Данные из Excel
            
        Связанные возможности:
        - Автоматический выбор листа с данными
        - Обработка заголовков и пустых строк
        """
        try:
            # Пробуем загрузить первый лист
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Проверка на пустой DataFrame
            if df.empty:
                # Пробуем другие листы
                excel_file = pd.ExcelFile(file_path)
                for sheet_name in excel_file.sheet_names:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                        if not df.empty:
                            print(f"Данные загружены с листа: {sheet_name}")
                            break
                    except Exception:
                        continue
            
            if df.empty:
                raise ValueError("Все листы Excel файла пусты")
            
            # Очистка от полностью пустых строк и столбцов
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            print(f"Excel файл загружен: {len(df)} строк, {len(df.columns)} столбцов")
            return df
            
        except Exception as e:
            raise Exception(f"Ошибка чтения Excel файла: {str(e)}")
    
    @staticmethod
    def _load_csv_file(file_path: str) -> pd.DataFrame:
        """
        Загрузка CSV файла с автоопределением параметров
        
        Args:
            file_path: Путь к CSV файлу
            
        Returns:
            pd.DataFrame: Данные из CSV
            
        Функции:
        - Автоопределение кодировки
        - Автоопределение разделителя
        - Обработка различных форматов чисел
        """
        # Определение кодировки
        encoding = FileUtils._detect_encoding(file_path)
        print(f"Определена кодировка: {encoding}")
        
        # Определение разделителя
        delimiter = FileUtils._detect_delimiter(file_path, encoding)
        print(f"Определен разделитель: '{delimiter}'")
        
        try:
            # Загрузка с определенными параметрами
            df = pd.read_csv(file_path, 
                           encoding=encoding,
                           delimiter=delimiter,
                           skipinitialspace=True,
                           na_values=['', 'NA', 'N/A', 'null', 'NULL'],
                           keep_default_na=True)
            
            # Очистка от полностью пустых строк и столбцов
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            if df.empty:
                raise ValueError("CSV файл пуст после загрузки")
            
            print(f"CSV файл загружен: {len(df)} строк, {len(df.columns)} столбцов")
            return df
            
        except Exception as e:
            raise Exception(f"Ошибка чтения CSV файла: {str(e)}")
    
    @staticmethod
    def _detect_encoding(file_path: str) -> str:
        """
        Автоматическое определение кодировки файла
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            str: Определенная кодировка
              Используется в:
        - _load_csv_file(): Корректная загрузка CSV с русскими символами
        """
        try:
            # Читаем первые 10KB для анализа
            with open(file_path, 'rb') as file:
                raw_data = file.read(10240)
            
            # Определение кодировки через chardet (если доступен)
            if chardet is not None:
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                print(f"Chardet: {encoding} (уверенность: {confidence:.2f})")
                
                # Если уверенность низкая, пробуем популярные кодировки
                if confidence < 0.7:
                    common_encodings = ['utf-8', 'windows-1251', 'cp1252', 'iso-8859-1']
                    for enc in common_encodings:
                        try:
                            with open(file_path, 'r', encoding=enc) as test_file:
                                test_file.read(1024)  # Пробуем прочитать
                            print(f"Успешная проверка кодировки: {enc}")
                            return enc
                        except (UnicodeDecodeError, UnicodeError):
                            continue
                
                return encoding or 'utf-8'
            else:
                # Fallback: пробуем популярные кодировки без chardet
                print("chardet недоступен, используем эвристический поиск кодировки...")
                common_encodings = ['utf-8', 'windows-1251', 'cp1252', 'iso-8859-1']
                for enc in common_encodings:
                    try:
                        with open(file_path, 'r', encoding=enc) as test_file:
                            test_file.read(1024)  # Пробуем прочитать                        print(f"Успешная проверка кодировки: {enc}")
                        return enc
                    except (UnicodeDecodeError, UnicodeError):
                        continue
                
                return 'utf-8'  # Fallback по умолчанию
            
        except Exception:
            # Fallback на UTF-8
            return 'utf-8'
    
    @staticmethod
    def _detect_delimiter(file_path: str, encoding: str) -> str:
        """
        Автоматическое определение разделителя CSV
        
        Args:
            file_path: Путь к файлу
            encoding: Кодировка файла
            
        Returns:
            str: Определенный разделитель
            
        Проверяет популярные разделители:
        - Запятая (,)
        - Точка с запятой (;)
        - Табуляция (\t)
        """
        delimiters = [',', ';', '\t', '|']
        
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                # Читаем первые несколько строк
                sample_lines = [file.readline() for _ in range(5)]
                sample_text = ''.join(sample_lines)
            
            # Подсчитываем частоту каждого разделителя
            delimiter_counts = {}
            for delimiter in delimiters:
                count = sample_text.count(delimiter)
                if count > 0:
                    delimiter_counts[delimiter] = count
            
            if delimiter_counts:
                # Выбираем наиболее частый разделитель
                best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
                print(f"Частота разделителей: {delimiter_counts}")
                return best_delimiter
            else:
                # Fallback на запятую
                return ','
                
        except Exception:
            return ','
    
    @staticmethod
    def validate_file_format(file_path: str) -> Dict[str, Any]:
        """
        Предварительная валидация формата файла
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Dict: Информация о файле и его пригодности
            
        Используется в:
        - main_window.py: Проверка файла перед загрузкой
        """
        if not os.path.exists(file_path):
            return {
                'valid': False,
                'error': 'Файл не найден',
                'file_size': 0
            }
        
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Проверка размера файла
        max_size = 100 * 1024 * 1024  # 100 MB
        if file_size > max_size:
            return {
                'valid': False,
                'error': f'Файл слишком большой ({file_size / 1024 / 1024:.1f} MB)',
                'file_size': file_size
            }
        
        # Проверка расширения
        supported_extensions = ['.csv', '.xlsx', '.xls']
        if file_ext not in supported_extensions:
            return {
                'valid': False,
                'error': f'Неподдерживаемый формат: {file_ext}',
                'file_size': file_size
            }
        
        # Попытка быстрого чтения заголовков
        try:
            if file_ext in ['.xlsx', '.xls']:
                # Пробуем прочитать только первые строки Excel
                df_sample = pd.read_excel(file_path, nrows=5)
            else:
                # Пробуем прочитать первые строки CSV
                encoding = FileUtils._detect_encoding(file_path)
                delimiter = FileUtils._detect_delimiter(file_path, encoding)
                df_sample = pd.read_csv(file_path, nrows=5, 
                                      encoding=encoding, delimiter=delimiter)
            
            return {
                'valid': True,
                'file_size': file_size,
                'columns_count': len(df_sample.columns),
                'sample_columns': list(df_sample.columns[:10]),  # Первые 10 колонок
                'estimated_rows': 'unknown'  # Для полной оценки нужна полная загрузка
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Ошибка чтения файла: {str(e)}',
                'file_size': file_size
            }
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        Получение детальной информации о файле
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Dict: Детальная информация
            
        Используется в:
        - main_window.py: Отображение информации о загруженном файле
        """
        if not os.path.exists(file_path):
            return {'exists': False}
        
        file_stats = os.stat(file_path)
        
        return {
            'exists': True,
            'name': os.path.basename(file_path),
            'full_path': file_path,
            'size': file_stats.st_size,
            'size_mb': file_stats.st_size / 1024 / 1024,
            'modified': file_stats.st_mtime,
            'extension': os.path.splitext(file_path)[1].lower(),
            'directory': os.path.dirname(file_path)
        }
    
    @staticmethod
    def save_processed_data(df: pd.DataFrame, output_path: str, 
                          format: str = 'auto') -> bool:
        """
        Сохранение обработанных данных
        
        Args:
            df: DataFrame для сохранения
            output_path: Путь для сохранения
            format: Формат файла ('auto', 'csv', 'excel')
            
        Returns:
            bool: True если сохранение успешно
            
        Используется в:
        - main_window.py: Экспорт результатов обработки
        """
        try:
            if format == 'auto':
                # Определение формата по расширению
                file_ext = os.path.splitext(output_path)[1].lower()
                if file_ext in ['.xlsx', '.xls']:
                    format = 'excel'
                else:
                    format = 'csv'
            
            if format == 'excel':
                df.to_excel(output_path, index=False)
            else:
                df.to_csv(output_path, index=False, encoding='utf-8')
            
            print(f"Данные сохранены: {output_path}")
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    @staticmethod
    def backup_file(file_path: str) -> Optional[str]:
        """
        Создание резервной копии файла
        
        Args:
            file_path: Путь к исходному файлу
            
        Returns:
            str: Путь к резервной копии или None при ошибке
            
        Используется в:
        - Предотвращение потери данных при перезаписи
        """
        if not os.path.exists(file_path):
            return None
        
        try:
            backup_path = f"{file_path}.backup"
            
            # Если резервная копия уже существует, добавляем номер
            counter = 1
            while os.path.exists(backup_path):
                backup_path = f"{file_path}.backup{counter}"
                counter += 1
            
            # Копирование файла
            import shutil
            shutil.copy2(file_path, backup_path)
            
            print(f"Создана резервная копия: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"Ошибка создания резервной копии: {e}")
            return None


# Связанные файлы для импорта в других модулях:
# from utils.file_utils import FileUtils
