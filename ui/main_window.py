# -*- coding: utf-8 -*-
"""
Главное окно Multi-Parameter Data Analyzer v2.0
===============================================

Основной пользовательский интерфейс с универсальной временной шкалой.

Связанные файлы:
- ../main.py: Точка входа приложения (запускает данный модуль)
- column_selector.py: Новый интерфейс выбора колонок с парным режимом
- ../core/timeline_manager.py: Управление универсальной временной шкалой
- ../core/data_manager.py: Загрузка и обработка файлов
- ../core/plot_manager.py: Построение графиков
- ../utils/file_utils.py: Утилиты работы с файлами
- ../config/settings.py: Настройки приложения

Отличия от v1.0:
- Интеграция с TimelineManager для универсальной временной шкалы
- Новый интерфейс выбора пар "время + параметр"
- Улучшенная обработка разнородных временных данных
- Модульная архитектура вместо монолитного файла

Автор: j15
Версия: 2.0.0-dev
GitHub: https://github.com/jackal100500/CSV_software
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import sys
import os

# Импорт модулей v2.0 с cross-references
try:
    from ..core.timeline_manager_v2 import TimelineManager
    from ..core.data_manager import DataManager
    from ..core.plot_manager import PlotManager
    from .column_selector import ColumnSelector
    from ..utils.file_utils import FileUtils
    from ..config.settings import Settings
except ImportError:
    # Fallback для запуска из main.py
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.timeline_manager_v2 import TimelineManager
    from core.data_manager import DataManager
    from core.plot_manager import PlotManager
    from ui.column_selector import ColumnSelector
    from utils.file_utils import FileUtils
    from config.settings import Settings


class MultiParameterPlotApp:
    """
    Главное окно приложения для анализа многопараметрических данных.
    
    Основные компоненты:
    - timeline_manager: Управление универсальной временной шкалой (core/timeline_manager.py)
    - data_manager: Загрузка и обработка данных (core/data_manager.py)
    - plot_manager: Построение и управление графиками (core/plot_manager.py)
    - column_selector: Выбор пар колонок время+параметр (ui/column_selector.py)
    """
    
    def __init__(self, root):
        """
        Инициализация главного окна
        
        Args:
            root: Корневое окно tkinter (создается в main.py)
        """
        self.root = root
        self.root.title("Multi-Parameter Data Analyzer v2.0")
        self.root.geometry("1200x800")
        
        # Инициализация модулей v2.0
        self.timeline_manager = TimelineManager()
        self.data_manager = DataManager()
        self.plot_manager = PlotManager()
        self.settings = Settings()
          # Данные приложения
        self.df = None
        self.current_file = None
        self.selected_pairs = []  # [(time_col, param_col), ...]
        self.universal_data = None  # Данные после интерполяции
        self.current_axes = []  # Список всех осей (основная + twinx)
        self.cursor_line = None  # Вертикальная линия курсора
        self.param_value_labels = {}  # Метки для отображения значений параметров
        
        # Инициализация интерфейса
        self.setup_ui()
        self.setup_plot_area()
        
        print("Multi-Parameter Data Analyzer v2.0 запущен")
        print("Связанные модули:")
        print("- core/timeline_manager.py: Универсальная временная шкала")
        print("- core/data_manager.py: Управление данными")
        print("- ui/column_selector.py: Выбор пар колонок")
    
    def setup_ui(self):
        """
        Создание элементов интерфейса
        
        Связанные методы:
        - load_file(): Использует utils/file_utils.py
        - select_columns(): Открывает ui/column_selector.py
        - plot_data(): Использует core/plot_manager.py
        """
        # Создание главного фрейма
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Панель управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки управления файлами
        ttk.Button(control_frame, text="Загрузить файл", 
                  command=self.load_file).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="Выбрать колонки", 
                  command=self.select_columns).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="Построить график", 
                  command=self.plot_data).pack(side=tk.LEFT, padx=(0, 5))
        
        # Информационная панель
        info_frame = ttk.LabelFrame(control_frame, text="Информация")
        info_frame.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.info_label = ttk.Label(info_frame, text="Файл не загружен")
        self.info_label.pack(padx=5, pady=2)
        
        # Панель настроек v2.0
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки универсальной временной шкалы")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Настройки интерполяции        ttk.Label(settings_frame, text="Шаг временной сетки (сек):").pack(side=tk.LEFT, padx=5)
        self.time_step_var = tk.DoubleVar(value=1.0)
        ttk.Entry(settings_frame, textvariable=self.time_step_var, width=10).pack(side=tk.LEFT, padx=5)
        
        self.interpolation_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Включить интерполяцию", 
                       variable=self.interpolation_enabled).pack(side=tk.LEFT, padx=10)
        
        # Панель отображения значений параметров (как в старой версии)
        self.param_values_frame = ttk.LabelFrame(main_frame, text="Значения параметров под курсором")
        self.param_values_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Контейнер для значений параметров (будет заполняться динамически)
        self.param_values_container = ttk.Frame(self.param_values_frame)
        self.param_values_container.pack(fill=tk.X, padx=5, pady=5)
        
        # Область для графика (будет создана в setup_plot_area)
        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)
    
    def setup_plot_area(self):
        """
        Настройка области отображения графиков
        
        Связанные компоненты:
        - core/plot_manager.py: Управление matplotlib Figure
        - Координаты мыши и навигация (перенесено из v1.0)
        """
        # Создание matplotlib Figure
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Встраивание в tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Панель навигации matplotlib
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        toolbar.update()
        
        # Статус-бар для координат мыши
        self.status_frame = ttk.Frame(self.plot_frame)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.coord_label = ttk.Label(self.status_frame, text="Координаты: X=0, Y=0")
        self.coord_label.pack(side=tk.LEFT, padx=5)
        
        # Привязка событий мыши (функциональность из v1.0)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_click)
        self.canvas.mpl_connect('scroll_event', self.on_mouse_scroll)
        
        # Переменные для панорамирования
        self.pan_start = None
        self.original_xlim = None
        self.original_ylim = None
    
    def load_file(self):
        """
        Загрузка файла данных
        
        Использует:
        - utils/file_utils.py: FileUtils.load_data_file()
        - core/data_manager.py: DataManager.process_loaded_data()
        """
        file_path = filedialog.askopenfilename(
            title="Выберите файл данных",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Загрузка через модуль file_utils.py
                self.df = FileUtils.load_data_file(file_path)
                self.current_file = file_path
                
                # Обработка через data_manager.py
                self.data_manager.set_dataframe(self.df)
                
                # Автоматическое определение временных колонок
                time_columns = self.timeline_manager.detect_time_columns(self.df)
                auto_pairs = self.timeline_manager.auto_detect_pairs(self.df)
                
                # Обновление информации
                self.update_file_info()
                
                messagebox.showinfo("Успех", 
                    f"Файл загружен: {os.path.basename(file_path)}\n"
                    f"Строк: {len(self.df)}\n"
                    f"Столбцов: {len(self.df.columns)}\n"
                    f"Обнаружено временных колонок: {len(time_columns)}\n"
                    f"Автоматически определено пар: {len(auto_pairs)}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def select_columns(self):
        """
        Открытие диалога выбора пар колонок
        
        Использует:
        - ui/column_selector.py: ColumnSelector с двумя режимами
        - core/timeline_manager.py: Для автоматического определения пар
        """
        if self.df is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл")
            return
        
        # Создание диалога выбора колонок
        selector = ColumnSelector(self.root, self.df, self.timeline_manager)
        self.root.wait_window(selector.dialog)
        
        # Получение результата
        if selector.result:
            self.selected_pairs = selector.result
            self.update_selection_info()
            print(f"Выбрано пар: {len(self.selected_pairs)}")
            for time_col, param_col in self.selected_pairs:
                print(f"  {time_col} -> {param_col}")
    
    def plot_data(self):
        """
        Построение графика с универсальной временной шкалой
        
        Использует:
        - core/timeline_manager.py: Создание универсальной временной сетки
        - core/plot_manager.py: Построение графиков
        """
        if self.df is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл")
            return
        
        if not self.selected_pairs:
            messagebox.showwarning("Предупреждение", "Сначала выберите пары колонок")
            return
        
        try:
            # Настройка параметров интерполяции
            self.timeline_manager.set_interpolation_step(self.time_step_var.get())
            
            if self.interpolation_enabled.get():
                # Создание универсальной временной шкалы
                self.universal_timeline = self.timeline_manager.create_universal_timeline(
                    self.df, self.selected_pairs
                )
                
                # Интерполяция данных
                self.universal_data = self.timeline_manager.interpolate_parameters(
                    self.df, self.selected_pairs
                )
                
                # Построение графика с множественными осями Y
                self.current_axes = self.plot_manager.plot_interpolated_data(
                    self.ax, self.universal_timeline, self.universal_data,
                    enable_multiple_y_axes=True
                )
            else:
                # Простое построение без интерполяции (режим совместимости с v1.0)
                self.plot_manager.plot_raw_data(
                    self.ax, self.df, self.selected_pairs
                )
                self.current_axes = [self.ax]
            
            # Создание меток для отображения значений параметров
            self.setup_param_value_labels()
            
            # Обновление графика
            self.ax.grid(True, alpha=0.3)
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить график:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def update_file_info(self):
        """Обновление информации о загруженном файле"""
        if self.df is not None and self.current_file:
            filename = os.path.basename(self.current_file)
            info_text = f"Файл: {filename} ({len(self.df)} строк, {len(self.df.columns)} столбцов)"
            self.info_label.config(text=info_text)
    
    def update_selection_info(self):
        """Обновление информации о выбранных парах"""
        if self.selected_pairs:
            info_text = f"Выбрано пар: {len(self.selected_pairs)}"
            # Можно добавить дополнительную информацию
    
    # События мыши (перенесено из v1.0 graf_csv.py)
    def on_mouse_move(self, event):
        """
        Обработка движения мыши с отображением значений параметров
        
        Функциональность (перенесена из v1.0):
        - Отображение координат курсора
        - Вертикальная линия под курсором  
        - Значения всех параметров в точке пересечения
        """
        if not event.inaxes:
            # Очистка при выходе из области графика
            self.coord_label.config(text="Координаты: --")
            self.clear_cursor_line()
            self.clear_param_values()
            return
            
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
            
        # Базовые координаты
        self.coord_label.config(text=f"Координаты: X={x:.2f}, Y={y:.4f}")
        
        # Если есть данные для анализа - показываем значения параметров
        if (self.universal_data is not None and 
            hasattr(self, 'universal_timeline') and 
            self.selected_pairs):
            
            try:
                self.update_cursor_line(x)
                self.update_param_values(x)
            except Exception as e:
                print(f"Ошибка обновления значений параметров: {e}")
                
    def update_cursor_line(self, x_position):
        """Обновление вертикальной линии курсора"""
        # Удаляем предыдущую линию
        self.clear_cursor_line()
        
        # Рисуем новую серую пунктирную линию
        self.cursor_line = self.ax.axvline(x=x_position, color='gray', 
                                         linestyle='--', linewidth=1.5, alpha=0.8)
        self.canvas.draw_idle()
        
    def clear_cursor_line(self):
        """Очистка вертикальной линии курсора"""
        if self.cursor_line is not None:
            try:
                self.cursor_line.remove()
            except:
                pass
            self.cursor_line = None
            
    def update_param_values(self, x_position):
        """
        Обновление значений параметров под курсором
        
        Args:
            x_position: Позиция курсора по оси X (время)
        """
        if not hasattr(self, 'universal_timeline') or self.universal_timeline is None:
            return
            
        try:
            # Найти ближайшую точку во времени
            import matplotlib.dates as mdates
            
            # Конвертируем X-координату в datetime
            if isinstance(x_position, (int, float)):
                cursor_time = mdates.num2date(x_position)
            else:
                cursor_time = x_position
            
            # Убираем информацию о часовом поясе для сравнения
            if hasattr(cursor_time, 'tzinfo') and cursor_time.tzinfo is not None:
                cursor_time = cursor_time.replace(tzinfo=None)
                
            # Найти ближайший индекс во временной шкале
            time_series = pd.Series(self.universal_timeline)
            
            # Убеждаемся, что все времена без часовых поясов
            if hasattr(time_series.iloc[0], 'tz') and time_series.iloc[0].tz is not None:
                time_series = time_series.dt.tz_localize(None)
            elif hasattr(time_series.iloc[0], 'tzinfo') and time_series.iloc[0].tzinfo is not None:
                time_series = time_series.apply(lambda x: x.replace(tzinfo=None))
            
            # Найти ближайший по времени элемент
            time_diffs = abs(time_series - cursor_time)
            closest_idx = time_diffs.idxmin()
            
            # Обновить значения для каждого параметра
            for param_name in self.universal_data.keys():
                if param_name in self.param_value_labels:
                    try:
                        param_values = self.universal_data[param_name]
                        if closest_idx < len(param_values):
                            value = param_values.iloc[closest_idx]
                            if pd.notna(value):
                                self.param_value_labels[param_name].config(text=f"{value:.3f}")
                            else:
                                self.param_value_labels[param_name].config(text="н/д")
                    except Exception as e:
                        self.param_value_labels[param_name].config(text="--")
                        
        except Exception as e:
            print(f"Ошибка обновления значений: {e}")
            # import traceback
            # traceback.print_exc()
            
    def clear_param_values(self):
        """Очистка значений параметров"""
        for label in self.param_value_labels.values():
            try:
                label.config(text="--")
            except:
                pass
                
    def setup_param_value_labels(self):
        """
        Создание меток для отображения значений параметров
        Вызывается после построения графика
        """
        # Очистка предыдущих меток
        for widget in self.param_values_container.winfo_children():
            widget.destroy()
        self.param_value_labels.clear()
        
        if not self.selected_pairs:
            return
            
        # Создание меток для каждого параметра
        colors = self.plot_manager.colors
        for i, (time_col, param_col) in enumerate(self.selected_pairs):
            color = colors[i % len(colors)]
            
            # Фрейм для параметра
            param_frame = ttk.Frame(self.param_values_container)
            param_frame.pack(side=tk.LEFT, padx=10, pady=2)
            
            # Название параметра (цветное)
            name_label = tk.Label(param_frame, text=f"{param_col}:", 
                                foreground=color, background='white',
                                font=('Arial', 10, 'bold'))
            name_label.pack(side=tk.LEFT)
            
            # Значение параметра
            value_label = tk.Label(param_frame, text="--",
                                 foreground='black', background='white',
                                 font=('Arial', 10), width=8)
            value_label.pack(side=tk.LEFT, padx=(5, 0))
            
            self.param_value_labels[param_col] = value_label
    
    def on_mouse_click(self, event):
        """Обработка клика мыши (начало панорамирования)"""
        if event.button == 1 and event.inaxes:  # Левая кнопка мыши
            self.pan_start = (event.xdata, event.ydata)
            self.original_xlim = self.ax.get_xlim()
            self.original_ylim = self.ax.get_ylim()
    
    def on_mouse_scroll(self, event):
        """Обработка скролла мыши (масштабирование)"""
        if event.inaxes:
            # Логика масштабирования из v1.0
            base_scale = 1.1
            if event.button == 'up':
                scale_factor = 1 / base_scale
            else:
                scale_factor = base_scale
            
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            # Масштабирование относительно курсора
            new_width = (xlim[1] - xlim[0]) * scale_factor
            new_height = (ylim[1] - ylim[0]) * scale_factor
            
            relx = (xlim[1] - event.xdata) / (xlim[1] - xlim[0])
            rely = (ylim[1] - event.ydata) / (ylim[1] - ylim[0])
            
            self.ax.set_xlim([event.xdata - new_width * (1 - relx),
                             event.xdata + new_width * relx])
            self.ax.set_ylim([event.ydata - new_height * (1 - rely),
                             event.ydata + new_height * rely])
            
            self.canvas.draw()


# Связанные файлы для импорта в других модулях:
# from ui.main_window import MultiParameterPlotApp
