#!/usr/bin/env python3
"""
Быстрый тест основного приложения с интерактивным курсором
Загружает тестовые данные и проверяет функциональность курсора
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import tkinter as tk
from ui.main_window import MultiParameterPlotApp

def create_test_file():
    """Создание файла с тестовыми данными"""
    data = {
        'Time': [
            '2024-01-01 10:00:00',
            '2024-01-01 10:01:00', 
            '2024-01-01 10:02:00',
            '2024-01-01 10:03:00',
            '2024-01-01 10:04:00',
            '2024-01-01 10:05:00',
            '2024-01-01 10:06:00',
            '2024-01-01 10:07:00',
            '2024-01-01 10:08:00',
            '2024-01-01 10:09:00',
            '2024-01-01 10:10:00'
        ],
        'Temperature': [25.5, 25.7, 25.9, 26.1, 26.3, 26.5, 26.7, 26.9, 27.1, 27.3, 27.5],
        'Pressure': [1.013, 1.014, 1.015, 1.016, 1.017, 1.018, 1.019, 1.020, 1.021, 1.022, 1.023],
        'Flow': [120.5, 121.2, 122.0, 122.8, 123.5, 124.2, 125.0, 125.7, 126.5, 127.2, 128.0]
    }
    
    df = pd.DataFrame(data)
    test_file = 'test_cursor_app_data.csv'
    df.to_csv(test_file, index=False)
    return test_file

def main():
    """Запуск теста основного приложения"""
    print("🧪 Создание тестовых данных для приложения...")
    test_file = create_test_file()
    print(f"✅ Тестовый файл создан: {test_file}")
    
    print("🚀 Запуск Multi-Parameter Data Analyzer v2.0...")
    print("📋 Инструкции для тестирования:")
    print("1. Загрузите файл:", test_file)
    print("2. Выберите пары колонок:")
    print("   - Time -> Temperature")
    print("   - Time -> Pressure") 
    print("   - Time -> Flow")
    print("3. Нажмите 'Построить график'")
    print("4. Наведите мышь на график - должны появиться:")
    print("   - Серая пунктирная линия курсора")
    print("   - Значения параметров в верхней панели")
    print("   - Разные цветные Y-оси для каждого параметра")
    print()
    
    # Запуск основного приложения
    root = tk.Tk()
    app = MultiParameterPlotApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
