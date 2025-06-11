#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Parameter Data Analyzer v2.0 - Точка входа
==================================================

Главный файл приложения с универсальной временной шкалой.

Связанные файлы:
- ui/main_window.py: Основной интерфейс пользователя
- core/timeline_manager.py: Новая система управления временем v2.0
- DEVELOPMENT_PLAN_v2.0.md: План разработки версии 2.0

Автор: j15
Версия: 2.0.0-dev
GitHub: https://github.com/jackal100500/CSV_software
"""

import tkinter as tk
import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Импорт MultiParameterPlotApp...")
    from ui.main_window import MultiParameterPlotApp
    print("✅ Импорт успешен")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Проверяем доступные модули...")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def main():
    """Главная функция запуска приложения"""
    # Создание главного окна tkinter
    root = tk.Tk()
    
    # Настройка иконки и заголовка (опционально)
    root.title("Multi-Parameter Data Analyzer v2.0")
    
    try:
        # Создание экземпляра приложения
        app = MultiParameterPlotApp(root)
        
        # Запуск главного цикла событий
        root.mainloop()
        
    except Exception as e:
        print(f"Критическая ошибка при запуске приложения: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
