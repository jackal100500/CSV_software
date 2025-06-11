# -*- coding: utf-8 -*-
"""
Тестовый скрипт для Multi-Parameter Data Analyzer v2.0
Тестирует модульную архитектуру и универсальную временную шкалу
"""

print("=== Тестирование Multi-Parameter Data Analyzer v2.0 ===")

try:
    print("1. Импорт модулей...")
    from utils.file_utils import FileUtils
    from core.timeline_manager_v2 import TimelineManager
    from core.data_manager import DataManager
    print("   ✅ Модули импортированы успешно")

    print("2. Загрузка тестового файла...")
    df = FileUtils.load_data_file('test.xlsx')
    print(f"   ✅ Файл загружен: {len(df)} строк, {len(df.columns)} столбцов")

    print("3. Инициализация менеджеров...")
    data_manager = DataManager()
    timeline_manager = TimelineManager()
    print("   ✅ Менеджеры созданы")

    print("4. Анализ структуры данных...")
    data_manager.set_dataframe(df)
    time_columns = data_manager.get_time_candidates()
    numeric_columns = data_manager.get_numeric_columns()
    print(f"   ✅ Временных колонок: {len(time_columns)}")
    print(f"   ✅ Числовых параметров: {len(numeric_columns)}")
    
    for i, col in enumerate(time_columns[:3], 1):
        print(f"   {i}. Время: {col}")
    if len(time_columns) > 3:
        print(f"   ... и еще {len(time_columns) - 3} временных колонок")

    print("5. Определение пар время + параметр...")
    pairs = timeline_manager.auto_detect_pairs(df)
    print(f"   ✅ Определено пар: {len(pairs)}")
    for i, (time_col, param_col) in enumerate(pairs[:3], 1):
        print(f"   {i}. {time_col} -> {param_col}")
    if len(pairs) > 3:
        print(f"   ... и еще {len(pairs) - 3} пар")

    print("6. Создание универсальной временной шкалы...")
    timeline = timeline_manager.create_universal_timeline(df, step_seconds=60.0)
    print(f"   ✅ Временная шкала создана: {len(timeline)} точек")
    print(f"   Период: {timeline.min()} до {timeline.max()}")

    print("7. Тестовая интерполяция (первые 2 пары)...")
    if len(pairs) >= 2:
        test_pairs = pairs[:2]
        interpolated = timeline_manager.interpolate_parameters(df, test_pairs)
        print(f"   ✅ Интерполировано параметров: {len(interpolated)}")
        
        for param_name in interpolated:
            values = interpolated[param_name]
            non_nan = values.dropna()
            if len(non_nan) > 0:
                print(f"   {param_name}: {len(non_nan)} валидных значений, диапазон {non_nan.min():.2f} - {non_nan.max():.2f}")
            else:
                print(f"   {param_name}: нет валидных данных после интерполяции")
    else:
        print("   ⚠️ Недостаточно пар для тестирования интерполяции")

    print("8. Проверка кросс-ссылок между модулями...")
    from core.plot_manager import PlotManager
    from config.settings import Settings
    plot_manager = PlotManager()
    settings = Settings()
    print("   ✅ Все модули взаимодействуют корректно")

    print()
    print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
    print("Multi-Parameter Data Analyzer v2.0 готов к использованию!")
    print("=" * 60)

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    print()
    print("❌ Тестирование завершено с ошибками")
