# -*- coding: utf-8 -*-
"""
Core модуль для Multi-Parameter Data Analyzer v2.0
==================================================

Основная бизнес-логика приложения.

Связанные модули:
- timeline_manager.py: Управление универсальной временной шкалой (новинка v2.0)
- data_manager.py: Централизованное управление данными
- plot_manager.py: Управление построением графиков

Автор: j15
Версия: 2.0.0-dev
GitHub: https://github.com/jackal100500/CSV_software
"""

# Импорты основных компонентов
from .timeline_manager_v2 import TimelineManager
from .data_manager import DataManager
from .plot_manager import PlotManager

__all__ = ['TimelineManager', 'DataManager', 'PlotManager']
