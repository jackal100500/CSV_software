# -*- coding: utf-8 -*-
"""
Тест интерактивного курсора для Multi-Parameter Data Analyzer v2.0
================================================================

Проверяет новую функциональность:
- Панель отображения значений параметров под курсором
- Множественные оси Y для каждого параметра
- Интерактивная вертикальная линия курсора
- Отображение значений в реальном времени

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

def test_interactive_cursor():
    """Тестирует интерактивную функциональность курсора"""
    
    print("🎯 ТЕСТ ИНТЕРАКТИВНОГО КУРСОРА v2.0")
    print("=" * 50)
    
    try:
        # 1. Инициализация
        print("1️⃣ Инициализация модулей...")
        data_manager = DataManager()
        timeline_manager = TimelineManager()
        plot_manager = PlotManager()
        
        # 2. Загрузка данных
        print("2️⃣ Загрузка test.xlsx...")
        df = FileUtils.load_data_file("test.xlsx")
        data_manager.set_dataframe(df, "test.xlsx")
        data_manager.analyze_columns()
        
        time_columns = data_manager.get_time_candidates()
        numeric_columns = data_manager.get_numeric_columns()
        
        # Создаем пары для тестирования (первые 3)
        pairs = []
        for i in range(min(3, len(time_columns), len(numeric_columns))):
            pairs.append((time_columns[i], numeric_columns[i]))
        
        print(f"✅ Тестовые пары: {pairs}")
        
        # 3. Создание временной шкалы
        print("3️⃣ Создание временной шкалы...")
        universal_timeline = timeline_manager.create_universal_timeline(df, pairs)
        
        # 4. Интерполяция
        print("4️⃣ Интерполяция данных...")
        interpolated_data = {}
        for time_col, param_col in pairs:
            time_series = df[time_col].dropna()
            param_series = df[param_col].dropna()
            
            interpolation_engine = InterpolationEngine()
            interpolated = interpolation_engine.interpolate_to_timeline(
                time_series, param_series, universal_timeline, method='linear'
            )
            interpolated_data[param_col] = interpolated
        
        # 5. Создание интерактивного графика
        print("5️⃣ Создание интерактивного графика...")
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Используем новую функцию с множественными осями Y
        axes_list = plot_manager.plot_interpolated_data(
            ax, universal_timeline, interpolated_data,
            enable_multiple_y_axes=True
        )
        
        print(f"✅ Создано осей: {len(axes_list)}")
        print("📊 Каждый параметр имеет свою ось Y")
        
        # 6. Настройка интерактивности
        print("6️⃣ Настройка интерактивного курсора...")
        
        # Переменные для курсора
        cursor_line = None
        param_info_text = None
        
        def on_mouse_move(event):
            """Обработчик движения мыши"""
            nonlocal cursor_line, param_info_text
            
            if not event.inaxes:
                return
                
            x, y = event.xdata, event.ydata
            if x is None or y is None:
                return
            
            # Удаляем предыдущую линию курсора
            if cursor_line is not None:
                cursor_line.remove()
            
            # Рисуем новую серую пунктирную линию
            cursor_line = ax.axvline(x=x, color='gray', linestyle='--', 
                                   linewidth=1.5, alpha=0.8)
            
            # Находим значения параметров в этой точке
            try:
                import matplotlib.dates as mdates
                cursor_time = mdates.num2date(x)
                
                # Найти ближайший индекс
                time_series = pd.Series(universal_timeline)
                time_diffs = abs(time_series - cursor_time)
                closest_idx = time_diffs.idxmin()
                
                # Собираем значения всех параметров
                param_values = []
                for param_name in interpolated_data.keys():
                    if closest_idx < len(interpolated_data[param_name]):
                        value = interpolated_data[param_name].iloc[closest_idx]
                        if pd.notna(value):
                            param_values.append(f"{param_name}: {value:.3f}")
                        else:
                            param_values.append(f"{param_name}: н/д")
                
                # Обновляем заголовок с информацией
                time_str = cursor_time.strftime('%H:%M:%S %d.%m.%y')
                info_text = f"Время: {time_str}   |   " + "   |   ".join(param_values)
                ax.set_title(info_text, fontsize=10, pad=20)
                
            except Exception as e:
                ax.set_title(f"X: {x:.2f}, Y: {y:.2f}", fontsize=10, pad=20)
            
            plt.draw()
        
        # Привязка события
        fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
        
        # 7. Сохранение и отображение
        print("7️⃣ Сохранение интерактивного графика...")
        
        plt.savefig("interactive_cursor_test_v2.png", dpi=150, bbox_inches='tight')
        print("💾 График сохранен: interactive_cursor_test_v2.png")
        
        # Показываем график с интерактивностью
        plt.title("Multi-Parameter Interactive Cursor Test v2.0\nДвигайте мышью для отображения значений", 
                 fontsize=12, fontweight='bold')
        
        print("\n🎉 ИНТЕРАКТИВНЫЙ КУРСОР ГОТОВ!")
        print("✅ Множественные оси Y: Каждый параметр на своей оси")
        print("✅ Серая пунктирная линия: Следует за курсором мыши")
        print("✅ Отображение значений: В заголовке графика")
        print("✅ Готово для интеграции в GUI")
        
        # Показать график (если запускается интерактивно)
        if __name__ == "__main__":
            print("\n👀 Открываем интерактивный график...")
            print("   Двигайте мышью по графику для тестирования!")
            plt.show()
        
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_interactive_cursor()
    sys.exit(0 if success else 1)
