"""
Тест для проверки обновленного поведения курсора в режиме v1.1
Теперь курсор использует объединенную временную шкалу вместо первого столбца времени
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import subprocess
import os
import sys

def create_test_data_for_cursor():
    """Создает специальные тестовые данные для проверки курсора"""
    print("Создание тестовых данных для проверки курсора...")
    
    # Базовое время
    base_time = datetime(2025, 6, 12, 10, 0, 0)
    
    # Создаем три системы с РАЗНЫМИ временными интервалами
    # Система A: каждые 10 секунд (более частая)
    time_a = [base_time + timedelta(seconds=i*10) for i in range(30)]
    temp_a = np.random.normal(25.0, 2.0, 30)  # Температура 25±2°C
    
    # Система B: каждые 15 секунд (средняя частота)
    time_b = [base_time + timedelta(seconds=i*15) for i in range(20)]
    pressure_b = np.random.normal(1013.0, 10.0, 20)  # Давление 1013±10 гПа
    
    # Система C: каждые 30 секунд (более редкая)
    time_c = [base_time + timedelta(seconds=i*30) for i in range(10)]
    flow_c = np.random.normal(100.0, 5.0, 10)  # Поток 100±5 л/мин
    
    # Объединяем в DataFrame с разной длиной
    max_len = max(len(time_a), len(time_b), len(time_c))
    
    # Дополняем короткие списки значениями None
    def pad_list(lst, target_len):
        return lst + [None] * (target_len - len(lst))
    
    data = {
        'Timestamp_SystemA': pad_list(time_a, max_len),
        'Temperature_A': pad_list(temp_a.tolist(), max_len),
        'Timestamp_SystemB': pad_list(time_b, max_len),
        'Pressure_B': pad_list(pressure_b.tolist(), max_len),
        'Timestamp_SystemC': pad_list(time_c, max_len),
        'Flow_C': pad_list(flow_c.tolist(), max_len),
        'Notes': ['System data'] * max_len
    }
    
    df = pd.DataFrame(data)
    
    # Сохраняем в файл Excel
    filename = 'test_cursor_combined_timeline.xlsx'
    df.to_excel(filename, index=False)
    print(f"Тестовые данные сохранены в файл: {filename}")
    
    # Выводим информацию о временных шкалах
    print("\n=== ИНФОРМАЦИЯ О ВРЕМЕННЫХ ШКАЛАХ ===")
    print(f"Система A: {len([t for t in time_a if t is not None])} точек, интервал 10 сек")
    print(f"  Время: {time_a[0]} - {time_a[-1]}")
    print(f"Система B: {len([t for t in time_b if t is not None])} точек, интервал 15 сек")
    print(f"  Время: {time_b[0]} - {time_b[-1]}")
    print(f"Система C: {len([t for t in time_c if t is not None])} точек, интервал 30 сек")
    print(f"  Время: {time_c[0]} - {time_c[-1]}")
    
    # Подсчитываем объединенную временную шкалу
    all_times = set()
    for t in time_a + time_b + time_c:
        if t is not None:
            all_times.add(t)
    
    combined_times = sorted(list(all_times))
    print(f"\nОбъединенная временная шкала: {len(combined_times)} уникальных точек")
    print(f"Общий диапазон: {combined_times[0]} - {combined_times[-1]}")
    
    return filename

def test_cursor_improvement():
    """Основной тест улучшенного курсора"""
    print("=" * 60)
    print("ТЕСТ: Улучшенное поведение курсора в режиме v1.1")
    print("=" * 60)
    
    # Создаем тестовые данные
    test_file = create_test_data_for_cursor()
    
    print("\n=== ИНСТРУКЦИИ ДЛЯ ТЕСТИРОВАНИЯ ===")
    print("1. Запустится приложение Multi-Parameter Data Analyzer")
    print("2. Загрузите файл:", test_file)
    print("3. Выберите режим v1.1 (парная привязка)")
    print("4. Создайте следующие пары:")
    print("   • Timestamp_SystemA → Temperature_A (красный)")
    print("   • Timestamp_SystemB → Pressure_B (синий)")
    print("   • Timestamp_SystemC → Flow_C (зеленый)")
    print("5. Нажмите OK для построения графика")
    print("\n=== ЧТО ТЕСТИРОВАТЬ ===")
    print("✓ Курсор теперь должен двигаться по ОБЪЕДИНЕННОЙ временной шкале")
    print("✓ Линия курсора должна привязываться к ЛЮБОЙ временной точке из всех систем")
    print("✓ Раньше курсор привязывался только к Timestamp_SystemA")
    print("✓ Теперь курсор учитывает временные точки всех трех систем")
    print("\n=== ОЖИДАЕМОЕ ПОВЕДЕНИЕ ===")
    print("• Курсор должен останавливаться на временных точках всех систем")
    print("• При движении мыши курсор должен 'прыгать' между разными временными метками")
    print("• Должна отображаться информация о параметрах в момент времени под курсором")
    
    input("\nНажмите Enter для запуска приложения...")
    
    # Запускаем приложение
    try:
        subprocess.run([sys.executable, "graf_csv.py"], cwd=os.getcwd())
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")

if __name__ == "__main__":
    test_cursor_improvement()
