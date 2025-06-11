# utils/__init__.py
# -*- coding: utf-8 -*-
"""
Utils модуль для Multi-Parameter Data Analyzer v2.0
===================================================

Вспомогательные утилиты и функции.

Связанные модули:
- file_utils.py: Работа с файлами (загрузка CSV/Excel с автоопределением)
- interpolation.py: Алгоритмы интерполяции для универсальной временной шкалы

Автор: j15
Версия: 2.0.0-dev
GitHub: https://github.com/jackal100500/CSV_software
"""

# Импорты утилит
from .file_utils import FileUtils
from .interpolation import InterpolationEngine, interpolation_engine

__all__ = ['FileUtils', 'InterpolationEngine', 'interpolation_engine']
