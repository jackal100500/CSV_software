# -*- coding: utf-8 -*-
"""
Interpolation Utils для Multi-Parameter Data Analyzer v2.0
==========================================================

Алгоритмы интерполяции для универсальной временной шкалы.

Связанные файлы:
- ../core/timeline_manager.py: Основной потребитель алгоритмов интерполяции
- ../config/settings.py: Настройки методов интерполяции по умолчанию
- ../ui/main_window.py: Пользовательский выбор методов интерполяции

Поддерживаемые методы:
- Линейная интерполяция
- Интерполяция ближайшего соседа
- Сплайн-интерполяция (cubic spline)
- Полиномиальная интерполяция

Автор: j15
Версия: 2.0.0-dev
GitHub: https://github.com/jackal100500/CSV_software
"""

import pandas as pd
import numpy as np
from scipy import interpolate
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Union, Dict, Any
import logging


class InterpolationEngine:
    """
    Движок интерполяции для универсальной временной шкалы.
    
    Связанные компоненты:
    - timeline_manager: Основной потребитель (core/timeline_manager.py)
    - settings: Настройки по умолчанию (config/settings.py)
    """
    
    def __init__(self):
        """Инициализация движка интерполяции"""
        self.logger = logging.getLogger(__name__)
        
        # Поддерживаемые методы
        self.available_methods = {
            'linear': self._linear_interpolation,
            'nearest': self._nearest_interpolation,
            'cubic': self._cubic_interpolation,
            'polynomial': self._polynomial_interpolation,
            'step': self._step_interpolation
        }
        
        print("InterpolationEngine v2.0 инициализирован")
        print("Связанные модули:")
        print("- timeline_manager.py: Создание универсальной временной шкалы")
        print(f"Доступные методы: {list(self.available_methods.keys())}")
    
    def interpolate_to_timeline(self, time_data: pd.Series, param_data: pd.Series,
                              target_timeline: pd.Series, 
                              method: str = 'linear') -> pd.Series:
        """
        Интерполяция параметра на универсальную временную шкалу
        
        Args:
            time_data: Исходные временные метки параметра
            param_data: Исходные значения параметра
            target_timeline: Целевая универсальная временная шкала
            method: Метод интерполяции
            
        Returns:
            pd.Series: Интерполированные значения на целевой временной шкале
            
        Используется в:
        - timeline_manager.interpolate_parameters(): Основная функция интерполяции
        """
        if method not in self.available_methods:
            self.logger.warning(f"Неизвестный метод {method}, используем linear")
            method = 'linear'
        
        try:
            # Подготовка данных
            clean_data = self._prepare_data(time_data, param_data)
            if clean_data is None:
                return pd.Series(index=target_timeline, dtype=float)
            
            source_time, source_values = clean_data
            
            # Конвертация времени в числовой формат для интерполяции
            time_numeric = self._convert_time_to_numeric(source_time)
            target_numeric = self._convert_time_to_numeric(target_timeline)
            
            # Выполнение интерполяции
            interpolated_values = self.available_methods[method](
                time_numeric, source_values, target_numeric
            )
            
            # Создание результирующей Series
            result = pd.Series(interpolated_values, index=target_timeline)
            
            # Обработка значений вне диапазона исходных данных
            result = self._handle_extrapolation(result, source_time, target_timeline)
            
            print(f"Интерполяция {method}: {len(source_values)} -> {len(result)} точек")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка интерполяции методом {method}: {e}")
            # Возвращаем пустую Series при ошибке
            return pd.Series(index=target_timeline, dtype=float)
    
    def _prepare_data(self, time_data: pd.Series, 
                     param_data: pd.Series) -> Optional[Tuple[pd.Series, pd.Series]]:
        """
        Подготовка данных для интерполяции
        
        Args:
            time_data: Временные метки
            param_data: Значения параметра
            
        Returns:
            Tuple: (очищенное время, очищенные значения) или None
        """
        # Объединение по индексу и удаление NaN
        combined = pd.DataFrame({'time': time_data, 'values': param_data}).dropna()
        
        if len(combined) < 2:
            self.logger.warning("Недостаточно данных для интерполяции (< 2 точек)")
            return None
        
        # Сортировка по времени
        combined = combined.sort_values('time')
        
        # Удаление дублированных временных меток
        combined = combined.drop_duplicates(subset=['time'], keep='first')
        
        if len(combined) < 2:
            self.logger.warning("После очистки осталось < 2 точек")
            return None
        
        return combined['time'], combined['values']
    
    def _convert_time_to_numeric(self, time_series: pd.Series) -> np.ndarray:
        """
        Конвертация времени в числовой формат
        
        Args:
            time_series: Временные данные
            
        Returns:
            np.ndarray: Числовое представление времени
        """
        if pd.api.types.is_datetime64_any_dtype(time_series):
            # Конвертация datetime в Unix timestamp
            return time_series.astype(np.int64) / 10**9
        elif pd.api.types.is_numeric_dtype(time_series):
            # Уже числовые данные
            return time_series.values
        else:
            # Попытка конвертации через pd.to_datetime
            try:
                datetime_series = pd.to_datetime(time_series)
                return datetime_series.astype(np.int64) / 10**9
            except Exception:
                # Fallback: использование индексов как время
                return np.arange(len(time_series), dtype=float)
    
    def _linear_interpolation(self, x_source: np.ndarray, y_source: np.ndarray,
                            x_target: np.ndarray) -> np.ndarray:
        """
        Линейная интерполяция
        
        Args:
            x_source: Исходные X координаты
            y_source: Исходные Y значения  
            x_target: Целевые X координаты
            
        Returns:
            np.ndarray: Интерполированные значения
        """
        return np.interp(x_target, x_source, y_source)
    
    def _nearest_interpolation(self, x_source: np.ndarray, y_source: np.ndarray,
                             x_target: np.ndarray) -> np.ndarray:
        """
        Интерполяция ближайшего соседа
        
        Args:
            x_source: Исходные X координаты
            y_source: Исходные Y значения
            x_target: Целевые X координаты
            
        Returns:
            np.ndarray: Интерполированные значения
        """
        f = interpolate.interp1d(x_source, y_source, kind='nearest', 
                               bounds_error=False, fill_value=np.nan)
        return f(x_target)
    
    def _cubic_interpolation(self, x_source: np.ndarray, y_source: np.ndarray,
                           x_target: np.ndarray) -> np.ndarray:
        """
        Кубическая сплайн-интерполяция
        
        Args:
            x_source: Исходные X координаты
            y_source: Исходные Y значения
            x_target: Целевые X координаты
            
        Returns:
            np.ndarray: Интерполированные значения
        """
        if len(x_source) < 4:
            # Для кубической интерполяции нужно минимум 4 точки
            # Fallback на линейную
            return self._linear_interpolation(x_source, y_source, x_target)
        
        try:
            f = interpolate.interp1d(x_source, y_source, kind='cubic',
                                   bounds_error=False, fill_value=np.nan)
            return f(x_target)
        except Exception:
            # Fallback на линейную при ошибке
            return self._linear_interpolation(x_source, y_source, x_target)
    
    def _polynomial_interpolation(self, x_source: np.ndarray, y_source: np.ndarray,
                                x_target: np.ndarray) -> np.ndarray:
        """
        Полиномиальная интерполяция
        
        Args:
            x_source: Исходные X координаты
            y_source: Исходные Y значения
            x_target: Целевые X координаты
            
        Returns:
            np.ndarray: Интерполированные значения
        """
        try:
            # Степень полинома ограничена количеством точек и максимумом
            degree = min(len(x_source) - 1, 5)
            if degree < 1:
                return self._linear_interpolation(x_source, y_source, x_target)
            
            # Полиномиальная аппроксимация
            coeffs = np.polyfit(x_source, y_source, degree)
            poly = np.poly1d(coeffs)
            
            return poly(x_target)
            
        except Exception:
            # Fallback на линейную при ошибке
            return self._linear_interpolation(x_source, y_source, x_target)
    
    def _step_interpolation(self, x_source: np.ndarray, y_source: np.ndarray,
                          x_target: np.ndarray) -> np.ndarray:
        """
        Ступенчатая интерполяция (предыдущее значение)
        
        Args:
            x_source: Исходные X координаты
            y_source: Исходные Y значения
            x_target: Целевые X координаты
            
        Returns:
            np.ndarray: Интерполированные значения
        """
        f = interpolate.interp1d(x_source, y_source, kind='previous',
                               bounds_error=False, fill_value=np.nan)
        return f(x_target)
    
    def _handle_extrapolation(self, interpolated_series: pd.Series,
                            source_time: pd.Series, 
                            target_timeline: pd.Series) -> pd.Series:
        """
        Обработка экстраполяции (значений вне исходного временного диапазона)
        
        Args:
            interpolated_series: Интерполированная серия
            source_time: Исходные временные метки
            target_timeline: Целевая временная шкала
            
        Returns:
            pd.Series: Серия с обработанной экстраполяцией
        """
        if len(source_time) == 0:
            return interpolated_series
        
        # Определение границ исходных данных
        source_min = source_time.min()
        source_max = source_time.max()
        
        # Конвертация в сопоставимый формат
        if pd.api.types.is_datetime64_any_dtype(target_timeline):
            target_min = target_timeline.min()
            target_max = target_timeline.max()
        else:
            try:
                target_timeline_dt = pd.to_datetime(target_timeline)
                target_min = target_timeline_dt.min()
                target_max = target_timeline_dt.max()
            except Exception:
                # Если конвертация не удалась, не применяем фильтр
                return interpolated_series
        
        # Маска для значений в пределах исходного диапазона
        valid_mask = (target_timeline >= source_min) & (target_timeline <= source_max)
        
        # Установка NaN для значений вне диапазона
        result = interpolated_series.copy()
        result.loc[~valid_mask] = np.nan
        
        return result
    
    def get_interpolation_quality(self, time_data: pd.Series, param_data: pd.Series,
                                target_timeline: pd.Series, 
                                method: str = 'linear') -> Dict[str, Any]:
        """
        Оценка качества интерполяции
        
        Args:
            time_data: Исходные временные метки
            param_data: Исходные значения
            target_timeline: Целевая временная шкала
            method: Метод интерполяции
            
        Returns:
            Dict: Метрики качества интерполяции
            
        Используется в:
        - timeline_manager.py: Выбор оптимального метода интерполяции
        """
        try:
            # Выполнение интерполяции
            interpolated = self.interpolate_to_timeline(
                time_data, param_data, target_timeline, method
            )
            
            # Подсчет метрик
            total_points = len(target_timeline)
            valid_points = interpolated.notna().sum()
            coverage = valid_points / total_points if total_points > 0 else 0
            
            # Анализ временного покрытия
            source_range = time_data.max() - time_data.min() if len(time_data) > 1 else timedelta(0)
            target_range = target_timeline.max() - target_timeline.min() if len(target_timeline) > 1 else timedelta(0)
            
            return {
                'method': method,
                'total_target_points': total_points,
                'valid_interpolated_points': valid_points,
                'coverage_ratio': coverage,
                'source_data_points': len(time_data),
                'source_time_range': source_range,
                'target_time_range': target_range,
                'interpolation_ratio': total_points / len(time_data) if len(time_data) > 0 else 0
            }
            
        except Exception as e:
            return {
                'method': method,
                'error': str(e),
                'valid': False
            }
    
    def compare_interpolation_methods(self, time_data: pd.Series, param_data: pd.Series,
                                    target_timeline: pd.Series) -> Dict[str, Dict[str, Any]]:
        """
        Сравнение различных методов интерполяции
        
        Args:
            time_data: Исходные временные метки
            param_data: Исходные значения
            target_timeline: Целевая временная шкала
            
        Returns:
            Dict: Результаты сравнения методов
            
        Используется в:
        - ui/column_selector.py: Предварительный просмотр методов
        """
        results = {}
        
        for method in self.available_methods.keys():
            results[method] = self.get_interpolation_quality(
                time_data, param_data, target_timeline, method
            )
        
        return results
    
    def suggest_best_method(self, time_data: pd.Series, param_data: pd.Series,
                          target_timeline: pd.Series) -> str:
        """
        Предложение лучшего метода интерполяции
        
        Args:
            time_data: Исходные временные метки
            param_data: Исходные значения
            target_timeline: Целевая временная шкала
            
        Returns:
            str: Рекомендуемый метод интерполяции
        """
        comparison = self.compare_interpolation_methods(time_data, param_data, target_timeline)
        
        # Критерии выбора:
        # 1. Покрытие данных (coverage_ratio)
        # 2. Количество исходных точек
        # 3. Отношение интерполяции
        
        best_method = 'linear'  # По умолчанию
        best_score = 0
        
        for method, metrics in comparison.items():
            if 'error' in metrics:
                continue
            
            # Простая система оценок
            score = 0
            score += metrics.get('coverage_ratio', 0) * 100  # Покрытие важнее всего
            
            # Бонус для методов в зависимости от количества данных
            data_points = metrics.get('source_data_points', 0)
            if data_points >= 10 and method == 'cubic':
                score += 10  # Кубическая для больших данных
            elif data_points >= 4 and method == 'polynomial':
                score += 5   # Полиномиальная для средних данных
            elif method == 'linear':
                score += 15  # Линейная всегда надежна
            
            if score > best_score:
                best_score = score
                best_method = method
        
        print(f"Рекомендуемый метод интерполяции: {best_method} (оценка: {best_score:.1f})")
        return best_method


# Создание глобального экземпляра для удобства импорта
interpolation_engine = InterpolationEngine()

# Связанные файлы для импорта в других модулях:
# from utils.interpolation import interpolation_engine, InterpolationEngine
