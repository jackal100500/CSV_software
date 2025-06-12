#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест для проверки нового поведения курсора в режиме v1.1
с использованием объединенной временной шкалы
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import subprocess
import os


def create_test_data_for_cursor():
    """Создает тестовые данные с разными временными интервалами для проверки курсора"""
    
    # Базовое время
    base_time = datetime(2025, 6, 12, 10, 0, 0)
    
    # Создаем данные с разными временными интервалами
    data = {}
    
    # Система A: каждые 10 секунд (20 точек)
    data['Time_A'] = [base_time + timedelta(seconds=i*10) for i in range(20)]
    data['Temperature_A'] = np.random.normal(25.0, 2.0, 20)
    
    # Система B: каждые 15 секунд (15 точек)
    data['Time_B'] = [base_time + timedelta(seconds=i*15) for i in range(15)]
    data['Pressure_B'] = np.random.normal(1.5, 0.1, 15)
    
    # Система C: каждые 30 секунд (10 точек)
    data['Time_C'] = [base_time + timedelta(seconds=i*30) for i in range(10)]
    data['Flow_C'] = np.random.normal(100.0, 5.0, 10)
    
    # Дополнительные столбцы для заполнения
    data['Extra_1'] = ['extra'] * 20
    data['Extra_2'] = [1] * 20
    
    # Выравниваем длины для DataFrame
    max_len = 20
    for key, values in data.items():
        if len(values) < max_len:
            data[key] = values + [None] * (max_len - len(values))
    
    df = pd.DataFrame(data)
    return df


def main():
    """Основная функция теста"""
    print("🧪 Создание тестовых данных для проверки курсора v1.1...")
    
    # Создаем тестовые данные
    test_df = create_test_data_for_cursor()
    
    # Сохраняем в CSV
    test_file = "test_cursor_v11.csv"
    test_df.to_csv(test_file, index=False)
    
    print(f"✅ Тестовые данные сохранены в {test_file}")
    print(f"📊 Создано {len(test_df)} строк данных")
    print(f"⏰ Временные столбцы: Time_A (10с интервал), Time_B (15с интервал), Time_C (30с интервал)")
    print(f"📈 Параметры: Temperature_A, Pressure_B, Flow_C")
    
    print("\n🔍 Структура данных:")
    print(test_df.head().to_string())
    
    print("\n📋 Инструкции для тестирования:")
    print("1. Запустите graf_csv.py")
    print("2. Загрузите файл test_cursor_v11.csv")
    print("3. Включите режим v1.1 (используйте пары)")
    print("4. Создайте пары:")
    print("   - Time_A → Temperature_A")
    print("   - Time_B → Pressure_B") 
    print("   - Time_C → Flow_C")
    print("5. Постройте график")
    print("6. Двигайте курсор по графику и проверьте:")
    print("   ✓ Курсор должен двигаться по ОБЪЕДИНЕННОЙ временной шкале")
    print("   ✓ А НЕ только по временной шкале первой пары (Time_A)")
    print("   ✓ Должны отображаться значения всех параметров")
    
    # Запускаем приложение для тестирования
    print(f"\n🚀 Запуск приложения для тестирования...")
    try:
        # Используем PowerShell для запуска
        subprocess.Popen(['python', 'graf_csv.py'], shell=True)
        print("✅ Приложение запущено!")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        print("Запустите graf_csv.py вручную")


if __name__ == "__main__":
    main()
