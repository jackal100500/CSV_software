# -*- coding: utf-8 -*-
"""
UI модуль для Multi-Parameter Data Analyzer v2.0
================================================

Пользовательский интерфейс приложения.

Связанные модули:
- main_window.py: Главное окно приложения (перенесено из монолитного graf_csv.py)
- column_selector.py: Новый интерфейс выбора пар колонок (функция v2.0)

Автор: j15
Версия: 2.0.0-dev
GitHub: https://github.com/jackal100500/CSV_software
"""

# Импорты компонентов UI модуля
from .main_window import MultiParameterPlotApp
from .column_selector import ColumnSelector

__all__ = ['MultiParameterPlotApp', 'ColumnSelector']
