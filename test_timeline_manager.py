"""
Тест для SimpleTimelineManager
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from simple_timeline_manager import SimpleTimelineManager


def create_test_data():
    """Создает тестовые данные с парами время+параметр"""
    
    # Базовое время
    base_time = datetime(2025, 6, 12, 10, 0, 0)
    
    # Создаем три различных временных ряда
    data = {
        'Date/Time1': [base_time + timedelta(seconds=i*10) for i in range(20)],
        'Information1': np.random.normal(100, 10, 20),
        'Date/Time2': [base_time + timedelta(seconds=i*15) for i in range(15)],
        'Information2': np.random.normal(50, 5, 15),
        'Date/Time3': [base_time + timedelta(seconds=i*20) for i in range(10)],
        'Information3': np.random.normal(200, 20, 10),
        'Other_Column': ['text'] * 20  # Не числовой столбец
    }
    
    # Выравниваем длины для DataFrame
    max_len = max(len(v) for v in data.values())
    for key, values in data.items():
        if len(values) < max_len:
            data[key] = values + [None] * (max_len - len(values))
    
    return pd.DataFrame(data)


def test_timeline_manager():
    """Основной тест менеджера временных шкал"""
    
    print("=== Тест SimpleTimelineManager ===\n")
    
    # Создаем тестовые данные
    df = create_test_data()
    print("Тестовые данные:")
    print(df.head())
    print(f"Размер данных: {df.shape}")
    print(f"Столбцы: {list(df.columns)}\n")
    
    # Создаем менеджер
    manager = SimpleTimelineManager()
    
    # Тест 1: Автоопределение столбцов времени
    print("1. Автоопределение столбцов времени:")
    time_columns = manager.detect_time_columns(df)
    print(f"Найденные столбцы времени: {time_columns}\n")
    
    # Тест 2: Автоопределение пар
    print("2. Автоопределение пар время+параметр:")
    auto_pairs = manager.auto_detect_pairs(df)
    print(f"Автоопределенные пары: {auto_pairs}\n")
    
    # Тест 3: Валидация пар
    print("3. Валидация пар:")
    valid_pairs = manager.validate_pairs(df, auto_pairs)
    print(f"Валидные пары: {valid_pairs}\n")
    
    # Тест 4: Создание объединенной временной шкалы
    print("4. Создание объединенной временной шкалы:")
    combined_timeline = manager.create_combined_timeline(df, valid_pairs)
    print(f"Количество уникальных временных меток: {len(combined_timeline)}")
    print(f"Временной диапазон: {combined_timeline.min()} - {combined_timeline.max()}\n")
    
    # Тест 5: Подготовка данных для графика
    print("5. Подготовка данных для графика:")
    plot_data = manager.prepare_plot_data(df, valid_pairs)
    
    for param_name, data in plot_data.items():
        print(f"  Параметр '{param_name}':")
        print(f"    Количество точек: {len(data['values'])}")
        print(f"    Временной столбец: {data['time_column']}")
        print(f"    Диапазон значений: {data['values'].min():.2f} - {data['values'].max():.2f}")
    
    print("\n")
    
    # Тест 6: Временной диапазон
    print("6. Общий временной диапазон:")
    min_time, max_time = manager.get_time_range(df, valid_pairs)
    print(f"Диапазон: {min_time} - {max_time}\n")
    
    # Тест 7: Ручное управление парами
    print("7. Ручное управление парами:")
    manager.set_pairs([('Date/Time1', 'Information1')])
    print(f"Установленные пары: {manager.get_pairs()}")
    
    manager.add_pair('Date/Time2', 'Information2')
    print(f"После добавления: {manager.get_pairs()}")
    
    manager.remove_pair('Date/Time1', 'Information1')
    print(f"После удаления: {manager.get_pairs()}\n")
    
    print("=== Тест завершен успешно! ===")


if __name__ == "__main__":
    test_timeline_manager()
