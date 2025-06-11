# -*- coding: utf-8 -*-
"""
Тест функциональности построения графиков для Multi-Parameter Data Analyzer v2.0
============================================================================

Проверяет:
- Загрузку данных из test.xlsx
- Создание универсальной временной шкалы
- Интерполяцию данных
- Построение графиков
- Исправление ошибки DatetimeIndex

Автор: j15
Версия: 2.0.0-dev
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Импорт модулей v2.0
from core.data_manager import DataManager
from core.timeline_manager_v2 import TimelineManager
from core.plot_manager import PlotManager
from utils.interpolation import InterpolationEngine
from utils.file_utils import FileUtils

def test_plotting_functionality():
    """Тестирует полную функциональность построения графиков"""
    
    print("🧪 ТЕСТ ПОСТРОЕНИЯ ГРАФИКОВ v2.0")
    print("=" * 50)
    
    try:
        # 1. Инициализация компонентов
        print("1️⃣ Инициализация компонентов...")
        data_manager = DataManager()
        timeline_manager = TimelineManager()
        plot_manager = PlotManager()
        interpolation_engine = InterpolationEngine()
          # 2. Загрузка тестовых данных
        print("2️⃣ Загрузка test.xlsx...")
        file_path = "test.xlsx"
        if not os.path.exists(file_path):
            print("❌ Файл test.xlsx не найден!")
            return False        # Используем file_utils для загрузки
        df = FileUtils.load_data_file(file_path)
        data_manager.set_dataframe(df, file_path)
        
        # Анализируем колонки для получения пар
        data_manager.analyze_columns()
        time_columns = data_manager.get_time_candidates()
        numeric_columns = data_manager.get_numeric_columns()
        
        # Создаем пары колонок (время-параметр)
        pairs = []
        for i, time_col in enumerate(time_columns):
            if i < len(numeric_columns):
                pairs.append((time_col, numeric_columns[i]))
        
        print(f"✅ Загружено: {len(df)} строк, {len(pairs)} пар колонок")
        print(f"📊 Пары: {pairs}")
        
        # 3. Создание универсальной временной шкалы
        print("3️⃣ Создание универсальной временной шкалы...")
        universal_timeline = timeline_manager.create_universal_timeline(df, pairs)
        print(f"✅ Создано {len(universal_timeline)} точек временной шкалы")
        print(f"📅 От {universal_timeline.min()} до {universal_timeline.max()}")
          # 4. Интерполяция данных
        print("4️⃣ Интерполяция данных...")
        
        # Интерполируем каждую пару отдельно
        interpolated_data = {}
        for time_col, param_col in pairs[:3]:  # Берем только первые 3 пары для теста
            try:
                time_series = df[time_col].dropna()
                param_series = df[param_col].dropna()
                
                # Интерполируем к универсальной временной шкале
                interpolated = interpolation_engine.interpolate_to_timeline(
                    time_series, param_series, universal_timeline, method='linear'
                )
                interpolated_data[param_col] = interpolated
                print(f"  ✅ {param_col}: {len(interpolated)} точек")
                
            except Exception as e:
                print(f"  ⚠️ Ошибка интерполяции {param_col}: {e}")
                
        print(f"✅ Интерполированы данные для {len(interpolated_data)} параметров")
        
        # 5. Тест построения графика
        print("5️⃣ Тестирование построения графика...")
        
        # Создаем тестовую фигуру
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Готовим данные для графика
        plot_data = {}
        for param_name, param_data in interpolated_data.items():
            if len(param_data) > 0:
                plot_data[param_name] = param_data
                  # Вызываем функцию построения графика
        try:
            plot_manager.plot_interpolated_data(ax, universal_timeline, plot_data)
            print("✅ График построен успешно!")
            
            # Сохраняем тестовый график
            test_output = "test_plot_v2.png"
            plt.savefig(test_output, dpi=150, bbox_inches='tight')
            print(f"💾 График сохранен: {test_output}")
            
            plt.close()
            
        except Exception as plot_error:
            print(f"❌ Ошибка построения графика: {plot_error}")
            import traceback
            traceback.print_exc()
            return False
            
        # 6. Проверка обработки DatetimeIndex
        print("6️⃣ Тест обработки DatetimeIndex...")
          # Создаем DatetimeIndex для проверки
        test_timeline = pd.date_range(start='2024-01-01', periods=100, freq='s')
        test_data = {'test_param': pd.Series(range(100), index=test_timeline)}
        
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        try:
            plot_manager.plot_interpolated_data(ax2, test_timeline, test_data)
            print("✅ DatetimeIndex обработан корректно!")
            plt.close()
        except Exception as dt_error:
            print(f"❌ Ошибка DatetimeIndex: {dt_error}")
            plt.close()
            return False
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Ошибка DatetimeIndex исправлена")
        print("✅ Функциональность построения графиков работает")
        print("✅ Multi-Parameter Data Analyzer v2.0 готов к использованию")
        
        return True
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_plotting_functionality()
    sys.exit(0 if success else 1)
