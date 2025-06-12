#!/usr/bin/env python3
"""
Генератор тестовых данных для проверки Multi-Parameter Data Analyzer v1.1
Создает файл с несколькими столбцами времени для тестирования парной привязки
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_test_data():
    """Создание тестовых данных с различными временными рядами"""
    
    # Базовое время
    base_time = datetime(2025, 6, 12, 10, 0, 0)
    
    # Система A - данные каждые 30 секунд
    times_a = [base_time + timedelta(seconds=30*i) for i in range(120)]  # 60 минут
    temperature_a = 20 + 5 * np.sin(np.linspace(0, 4*np.pi, len(times_a))) + np.random.normal(0, 0.5, len(times_a))
    
    # Система B - данные каждые 60 секунд, смещение на 15 секунд
    times_b = [base_time + timedelta(seconds=15 + 60*i) for i in range(60)]  # 60 минут
    pressure_b = 100 + 10 * np.cos(np.linspace(0, 3*np.pi, len(times_b))) + np.random.normal(0, 1, len(times_b))
    
    # Система C - данные каждые 2 минуты
    times_c = [base_time + timedelta(minutes=2*i) for i in range(30)]  # 60 минут
    flow_rate_c = 50 + 15 * np.sin(np.linspace(0, 2*np.pi, len(times_c))) + np.random.normal(0, 2, len(times_c))
    
    # Система D - те же времена что у A, но другой параметр
    humidity_d = 60 + 20 * np.cos(np.linspace(0, 5*np.pi, len(times_a))) + np.random.normal(0, 1, len(times_a))
    
    # Создание DataFrame
    max_len = max(len(times_a), len(times_b), len(times_c))
    
    data = {
        'timestamp_system_A': times_a + [None] * (max_len - len(times_a)),
        'temperature_A': list(temperature_a) + [None] * (max_len - len(times_a)),
        'humidity_A': list(humidity_d) + [None] * (max_len - len(times_a)),
        
        'timestamp_system_B': times_b + [None] * (max_len - len(times_b)),
        'pressure_B': list(pressure_b) + [None] * (max_len - len(times_b)),
        
        'timestamp_system_C': times_c + [None] * (max_len - len(times_c)),
        'flow_rate_C': list(flow_rate_c) + [None] * (max_len - len(times_c)),
    }
    
    df = pd.DataFrame(data)
    
    # Сохранение в CSV
    filename = 'test_manual_pairs_v11_final.csv'
    df.to_csv(filename, index=False)
    print(f"✅ Тестовый файл создан: {filename}")
    print(f"📊 Параметры:")
    print(f"   - Система A: {len(times_a)} записей (30сек интервал)")
    print(f"   - Система B: {len(times_b)} записей (60сек интервал)")  
    print(f"   - Система C: {len(times_c)} записей (2мин интервал)")
    print(f"📁 Структура данных:")
    print(f"   timestamp_system_A → temperature_A, humidity_A")
    print(f"   timestamp_system_B → pressure_B")
    print(f"   timestamp_system_C → flow_rate_C")
    
    return filename

if __name__ == "__main__":
    create_test_data()
