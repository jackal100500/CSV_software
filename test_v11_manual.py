#!/usr/bin/env python3
"""
Тест функциональности Multi-Parameter Data Analyzer v1.1
Ручная парная привязка время → параметр
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_test_data():
    """Создает тестовые данные с несколькими временными колонками"""
    
    # Создаем базовое время
    base_time = datetime(2024, 1, 1, 10, 0, 0)
    
    # Первая временная последовательность (каждые 5 минут)
    time1 = [base_time + timedelta(minutes=5*i) for i in range(100)]
    
    # Вторая временная последовательность (каждые 3 минуты, сдвинута на 2 минуты)
    time2 = [base_time + timedelta(minutes=2) + timedelta(minutes=3*i) for i in range(150)]
    
    # Третья временная последовательность (каждые 10 минут, сдвинута на 1 минуту)
    time3 = [base_time + timedelta(minutes=1) + timedelta(minutes=10*i) for i in range(50)]
    
    # Создаем параметры
    param1 = [20 + 5 * np.sin(i * 0.1) + np.random.normal(0, 0.5) for i in range(100)]
    param2 = [50 + 10 * np.cos(i * 0.05) + np.random.normal(0, 1) for i in range(150)]
    param3 = [100 + 20 * np.sin(i * 0.2) + np.random.normal(0, 2) for i in range(50)]
    
    # Создаем DataFrame с максимальной длиной
    max_len = max(len(time1), len(time2), len(time3))
    
    # Дополняем данные до одинаковой длины
    def pad_data(data, target_len):
        return data + [None] * (target_len - len(data))
    
    df = pd.DataFrame({
        'timestamp_system_A': pad_data(time1, max_len),
        'temperature_A': pad_data(param1, max_len),
        'timestamp_system_B': pad_data(time2, max_len),
        'pressure_B': pad_data(param2, max_len),
        'timestamp_system_C': pad_data(time3, max_len),
        'flow_rate_C': pad_data(param3, max_len)
    })
    
    return df

def main():
    """Основная функция тестирования"""
    print("Создание тестовых данных для v1.1...")
    
    # Создаем тестовые данные
    df = create_test_data()
    
    # Сохраняем в CSV файл
    output_file = "test_manual_pairs_v11.csv"
    df.to_csv(output_file, index=False)
    
    print(f"Тестовые данные сохранены в файл: {output_file}")
    print(f"Строк данных: {len(df)}")
    print(f"Столбцов: {len(df.columns)}")
    print()
    print("Структура данных:")
    print("- timestamp_system_A → temperature_A (каждые 5 мин)")
    print("- timestamp_system_B → pressure_B (каждые 3 мин)")
    print("- timestamp_system_C → flow_rate_C (каждые 10 мин)")
    print()
    print("Для тестирования:")
    print("1. Запустите graf_csv.py")
    print("2. Загрузите файл test_manual_pairs_v11.csv")
    print("3. В окне выбора столбцов выберите 'Режим v1.1'")
    print("4. Добавьте пары вручную:")
    print("   - timestamp_system_A → temperature_A")
    print("   - timestamp_system_B → pressure_B")
    print("   - timestamp_system_C → flow_rate_C")
    print("5. Нажмите OK и проверьте отображение графика")

if __name__ == "__main__":
    main()
