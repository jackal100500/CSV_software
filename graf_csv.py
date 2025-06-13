import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import Button, TextBox
import numpy as np
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Импортируем наш SimpleTimelineManager
try:
    from test_simple import SimpleTimelineManager
except ImportError:
    print("Внимание: SimpleTimelineManager не найден, используется упрощенная версия")
    SimpleTimelineManager = None

class MultiParameterPlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Parameter Data Analyzer")
        self.root.geometry("1200x850")
        
        # Создание меню
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_separator()
        help_menu.add_command(label="GitHub", command=self.open_github)
        
        # Настройка стилей
        style = ttk.Style()
        style.configure('Black.TFrame', background='black')
        style.configure('Black.TLabel', background='black')        # Переменные для хранения данных
        self.df = None
        self.params = []
        self.datetime_column = None
        self.colors = ['red', 'green', 'white', 'cyan', 'magenta', 'yellow']
        
        # Инициализируем SimpleTimelineManager для версии 1.1
        self.timeline_manager = SimpleTimelineManager() if SimpleTimelineManager else None
        self.use_paired_mode = False  # Режим работы: False = простой, True = парный
        self.time_param_pairs = []  # Пары время+параметр для парного режима
        
        # Переменная для вертикальной линии курсора
        self.cursor_line = None
        
        # Переменные для панорамирования (перетаскивания) графика
        self.is_panning = False
        self.pan_start_point = None
        self.pan_start_xlim = None
        self.pan_start_ylim = None
        
        # Создание фрейма для временного диапазона
        self.time_frame = ttk.LabelFrame(root, text="Временной диапазон")
        self.time_frame.pack(fill="x", padx=10, pady=5)
        
        # Кнопка загрузки данных (теперь в временном фрейме)
        self.load_button = ttk.Button(self.time_frame, text="Загрузить файл", command=self.load_data)
        self.load_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Поля для ввода временного диапазона
        ttk.Label(self.time_frame, text="Начало:").grid(row=0, column=1, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(self.time_frame, width=20)
        self.start_date_entry.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(self.time_frame, text="Конец:").grid(row=0, column=3, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(self.time_frame, width=20)
        self.end_date_entry.grid(row=0, column=4, padx=5, pady=5)
        
        # Кнопка применения временного диапазона
        self.apply_time_button = ttk.Button(self.time_frame, text="Применить", command=self.update_time_range)
        self.apply_time_button.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка сброса временного диапазона
        self.reset_time_button = ttk.Button(self.time_frame, text="Сбросить", command=self.reset_time_range)
        self.reset_time_button.grid(row=0, column=6, padx=5, pady=5)
        
        # Предустановленные временные диапазоны
        self.time_presets_frame = ttk.Frame(self.time_frame)
        self.time_presets_frame.grid(row=1, column=0, columnspan=7, padx=5, pady=5)
        
        ttk.Button(self.time_presets_frame, text="Последний час", 
                  command=lambda: self.set_time_preset(hours=1)).pack(side="left", padx=5)
        ttk.Button(self.time_presets_frame, text="Последние 6 часов", 
                  command=lambda: self.set_time_preset(hours=6)).pack(side="left", padx=5)
        ttk.Button(self.time_presets_frame, text="Последние 24 часа", 
                  command=lambda: self.set_time_preset(hours=24)).pack(side="left", padx=5)
        ttk.Button(self.time_presets_frame, text="Последние 7 дней", 
                  command=lambda: self.set_time_preset(days=7)).pack(side="left", padx=5)
        ttk.Button(self.time_presets_frame, text="Последний месяц", 
                  command=lambda: self.set_time_preset(days=30)).pack(side="left", padx=5)
        
        # Создание области для отображения информации о параметрах
        self.info_frame = ttk.LabelFrame(root, text="Информация о параметрах", style='Black.TLabelframe')
        self.info_frame.pack(fill="x", padx=10, pady=5)
        
        # Добавьте стиль для LabelFrame
        style.configure('Black.TLabelframe', background='black', foreground='white')
        style.configure('Black.TLabelframe.Label', background='black', foreground='white')
        
        # Создание фрейма для графика
        self.plot_frame = ttk.Frame(root)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=5)
          # Установка начальных значений
        self.fig = None
        self.canvas = None
        self.axes = []
        self.lines = []
        self.param_labels = []
        self.cursor_line = None  # Добавляем переменную для вертикальной линии курсора
        
        # Инициализация пустого графика
        self.init_plot()
        
    def init_plot(self):
        """Инициализация пустого графика"""
        if self.canvas:
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
        
        self.fig, self.ax1 = plt.subplots(figsize=(12, 5), facecolor='black')  # Уменьшена высота
        self.ax1.set_facecolor('black')
        self.ax1.grid(color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
        
        # Настройка осей и меток
        self.ax1.tick_params(axis='x', colors='white')
        self.ax1.tick_params(axis='y', colors='white')
        self.ax1.spines['bottom'].set_color('white')
        self.ax1.spines['top'].set_color('white')
        self.ax1.spines['left'].set_color('white')
        self.ax1.spines['right'].set_color('white')
        
        self.axes = [self.ax1]
        self.lines = []
        
        # Создание холста Matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # Добавление панели инструментов
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Отключение отображения координат в стандартной панели инструментов
        self.toolbar.set_message = lambda s: None
        
        # Метка для координат - размещаем во всю ширину сверху, с выравниванием по центру
        self.coords_label = tk.Label(self.plot_frame, text="", bg='black', fg='white', 
                                    font=('Courier', 10), anchor='center', justify='center',
                                    wraplength=800)  # Большая ширина переноса текста
                                    
        # Располагаем метку по центру вверху
        self.coords_label.place(relx=0.5, rely=0.0, anchor='n')
        
        # Подключение обработчика движения мыши
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # Подключение обработчика прокрутки колесика мыши для масштабирования
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        
        # Подключение обработчиков для панорамирования
        self.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.canvas.mpl_connect('button_release_event', self.on_button_release)
        
        # Регулировка пространства для осей
        plt.subplots_adjust(
            top=0.95,        # Увеличиваем до 0.95 (меньше места сверху)
            right=0.85,      # Освобождает место для осей справа
            bottom=0.15      # Место для оси X с датами
        )

        # Автоматически подстраиваем компоновку с минимальными отступами
        self.fig.tight_layout(pad=0.5)  # Уменьшенный отступ (было по умолчанию ~3.0)
    
    def load_data(self):
        """Загрузка данных из файла"""
        file_path = filedialog.askopenfilename(
                # filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx;*.xls")]  # старая строка
                filetypes=[("Excel files", "*.xlsx;*.xls")]  # только Excel файлы
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(file_path)
            else:
                self.df = pd.read_csv(file_path)            # Открываем окно выбора столбцов
            self.select_columns()
            
        except Exception as e:
            tk.messagebox.showerror("Ошибка загрузки", f"Ошибка при загрузке файла: {str(e)}")
    
    def select_columns(self):
        """Открытие окна для выбора столбцов для отображения - v1.1"""
        select_window = tk.Toplevel(self.root)
        select_window.title("Выбор столбцов для отображения - v1.1")
        select_window.geometry("600x700")

        # Основной фрейм
        main_frame = ttk.Frame(select_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # === ВЫБОР РЕЖИМА РАБОТЫ ===
        mode_frame = ttk.LabelFrame(main_frame, text="Режим работы:")
        mode_frame.pack(fill="x", padx=5, pady=5)
        
        mode_var = tk.StringVar(value="v1.0")
        
        ttk.Radiobutton(mode_frame, text="Режим v1.0 (один столбец времени для всех)", 
                       variable=mode_var, value="v1.0").pack(anchor="w", padx=10, pady=2)
        ttk.Radiobutton(mode_frame, text="Режим v1.1 (парная привязка время → параметр)", 
                       variable=mode_var, value="v1.1").pack(anchor="w", padx=10, pady=2)

        # === РЕЖИМ v1.0 (СОВМЕСТИМОСТЬ) ===
        v10_frame = ttk.LabelFrame(main_frame, text="Режим v1.0:")
        v10_frame.pack(fill="x", padx=5, pady=5)

        # Выбор столбца времени
        datetime_frame = ttk.Frame(v10_frame)
        datetime_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(datetime_frame, text="Столбец времени:").pack(anchor="w")
        datetime_var = tk.StringVar()
        datetime_combo = ttk.Combobox(datetime_frame, textvariable=datetime_var, 
                                    values=list(self.df.columns), state="readonly")
        datetime_combo.pack(fill="x", pady=2)

        # Автоопределение столбца времени
        for col in self.df.columns:
            if any(kw in col.lower() for kw in ['date', 'time', 'datetime', 'дата', 'время']):
                datetime_combo.set(col)
                break        # Выбор параметров
        params_frame = ttk.Frame(v10_frame)
        params_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        ttk.Label(params_frame, text="Параметры для отображения:").pack(anchor="w")
        
        param_vars = {}
        param_colors_vars = {}
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        # Словарь с RGB значениями цветов для отображения
        colors_with_rgb = {
            'red': '#FF0000',
            'blue': '#0000FF',
            'green': '#00FF00', 
            'orange': '#FFA500',
            'purple': '#800080',
            'brown': '#A52A2A',
            'pink': '#FFC0CB',
            'gray': '#808080',
            'olive': '#808000',
            'cyan': '#00FFFF',
            'magenta': '#FF00FF',
            'yellow': '#FFFF00',
            'black': '#000000',
            'white': '#FFFFFF'
        }
        
        # Функция для создания комбо-бокса с цветным индикатором
        def create_color_combobox(parent, color_var, width=10):
            """Создаёт комбо-бокс с цветным индикатором"""
            frame = ttk.Frame(parent)
            
            # Создаем комбо-бокс
            combo = ttk.Combobox(frame, textvariable=color_var, 
                               values=list(colors_with_rgb.keys()), state="readonly", width=width)
            combo.pack(side="right", padx=(5, 0))
            
            # Создаем цветной индикатор (Canvas)
            color_indicator = tk.Canvas(frame, width=16, height=16, bg=colors_with_rgb.get(color_var.get(), '#FFFFFF'))
            color_indicator.pack(side="right", padx=(0, 5))
            
            # Функция обновления индикатора при изменении выбора
            def update_color(event=None):
                color_name = color_var.get()
                color_indicator.config(bg=colors_with_rgb.get(color_name, '#FFFFFF'))
            
            # Привязываем обновление цвета к событию выбора
            combo.bind("<<ComboboxSelected>>", update_color)
            
            # Инициализируем индикатор при создании
            update_color()
            
            return frame
        
        # Скроллируемый фрейм для параметров
        params_canvas = tk.Canvas(params_frame, height=400)
        params_scrollbar = ttk.Scrollbar(params_frame, orient="vertical", command=params_canvas.yview)
        params_scrollable_frame = ttk.Frame(params_canvas)
        
        params_scrollable_frame.bind(
            "<Configure>",
            lambda e: params_canvas.configure(scrollregion=params_canvas.bbox("all"))
        )
        
        params_canvas.create_window((0, 0), window=params_scrollable_frame, anchor="nw")
        params_canvas.configure(yscrollcommand=params_scrollbar.set)
        
        params_canvas.pack(side="left", fill="both", expand=True)
        params_scrollbar.pack(side="right", fill="y")
          # Создание чекбоксов для каждого столбца (кроме времени)
        for i, col in enumerate(self.df.columns):
            if col != datetime_var.get():
                # Создаем чекбокс для выбора параметра
                param_frame = ttk.Frame(params_scrollable_frame)
                param_frame.pack(fill="x", pady=2)
                
                # Переменная для чекбокса
                var = tk.BooleanVar(value=False)
                param_vars[col] = var
                
                # Создаем чекбокс с названием параметра
                ttk.Checkbutton(param_frame, text=col, variable=var).pack(side="left", padx=5)
                
                # Переменная для выбора цвета
                color_var = tk.StringVar(value=colors[i % len(colors)])
                param_colors_vars[col] = color_var
                
                # Создаем комбо-бокс с цветным индикатором вместо обычного
                color_frame = create_color_combobox(param_frame, color_var)
                color_frame.pack(side="right", padx=(10, 0))

        # === РЕЖИМ v1.1 (ПАРНАЯ ПРИВЯЗКА) ===
        v11_frame = ttk.LabelFrame(main_frame, text="Режим v1.1 - Пары время → параметр:")
        v11_frame.pack(fill="x", padx=5, pady=5)        # Список для хранения пар
        pairs_list = []
        
        def add_pair(auto_fill_index=None):
            """Добавить новую пару время → параметр"""
            pair_frame = ttk.Frame(pairs_container)
            pair_frame.pack(fill="x", pady=2)
            
            # Выпадающий список времени
            time_var = tk.StringVar()
            time_combo = ttk.Combobox(pair_frame, textvariable=time_var, 
                                    values=list(self.df.columns), state="readonly", width=15)
            time_combo.pack(side="left", padx=2)
            
            # Стрелка
            ttk.Label(pair_frame, text="→").pack(side="left", padx=5)
            
            # Выпадающий список параметров
            param_var = tk.StringVar()
            param_combo = ttk.Combobox(pair_frame, textvariable=param_var, 
                                     values=list(self.df.columns), state="readonly", width=15)
            param_combo.pack(side="left", padx=2)
            
            # Автозаполнение колонками, если указан индекс
            if auto_fill_index is not None and auto_fill_index < len(self.df.columns):
                columns = list(self.df.columns)
                
                # Для времени берем колонку по индексу (если четный) или следующую
                time_idx = auto_fill_index * 2 if auto_fill_index * 2 < len(columns) else auto_fill_index
                if time_idx < len(columns):
                    time_var.set(columns[time_idx])
                
                # Для параметра берем следующую колонку
                param_idx = time_idx + 1 if time_idx + 1 < len(columns) else (time_idx - 1 if time_idx > 0 else time_idx)
                if param_idx < len(columns) and param_idx != time_idx:
                    param_var.set(columns[param_idx])
            
            # Выбор цвета с индикатором
            color_var = tk.StringVar(value=colors[len(pairs_list) % len(colors)])
            
            # Создаем и размещаем комбо-бокс с цветным индикатором вместо обычного
            color_frame = create_color_combobox(pair_frame, color_var, width=8)
            color_frame.pack(side="left", padx=2)
            
            # Кнопка удаления
            def remove_pair():
                pair_frame.destroy()
                pairs_list.remove(pair_data)
            
            ttk.Button(pair_frame, text="×", command=remove_pair, width=3).pack(side="left", padx=2)
            
            # Сохранение данных пары
            pair_data = {
                'frame': pair_frame,
                'time_var': time_var,
                'param_var': param_var,
                'color_var': color_var
            }
            pairs_list.append(pair_data)
          # Контейнер для пар
        pairs_container = ttk.Frame(v11_frame)
        pairs_container.pack(fill="x", padx=5, pady=5)
          # Автоматически создаем 5 пар при инициализации с автозаполнением
        for i in range(5):
            add_pair(auto_fill_index=i)
        
        # Кнопка добавления пары
        ttk.Button(v11_frame, text="+ Добавить пару", command=add_pair).pack(pady=5)

        # Функция переключения интерфейса
        def toggle_mode():
            """Переключение между режимами v1.0 и v1.1"""
            if mode_var.get() == "v1.0":
                v10_frame.pack(fill="x", padx=5, pady=5)
                v11_frame.pack_forget()
            else:
                v10_frame.pack_forget()
                v11_frame.pack(fill="x", padx=5, pady=5)
        
        # Привязка переключения режима
        mode_var.trace("w", lambda *args: toggle_mode())
        
        # Изначально показываем v1.0
        toggle_mode()

        # === КНОПКИ УПРАВЛЕНИЯ ===
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        def apply_selection():
            """Применить выбранные настройки"""
            selected_mode = mode_var.get()
            
            if selected_mode == "v1.0":
                # Режим v1.0 - старая логика
                selected_params = {}
                selected_colors = {}
                
                for col, var in param_vars.items():
                    if var.get():
                        selected_params[col] = True
                        selected_colors[col] = param_colors_vars[col].get()
                
                if not selected_params:
                    tk.messagebox.showwarning("Предупреждение", "Выберите хотя бы один параметр!")
                    return
                
                if not datetime_var.get():
                    tk.messagebox.showwarning("Предупреждение", "Выберите столбец времени!")
                    return
                
                # Применяем настройки v1.0
                self.apply_selection_v10(datetime_var.get(), selected_params, selected_colors, select_window)
                
            else:
                # Режим v1.1 - новая логика с парами
                if not pairs_list:
                    tk.messagebox.showwarning("Предупреждение", "Добавьте хотя бы одну пару время → параметр!")
                    return
                
                # Проверка корректности пар
                valid_pairs = []
                for pair in pairs_list:
                    time_col = pair['time_var'].get()
                    param_col = pair['param_var'].get()
                    color = pair['color_var'].get()
                    
                    if time_col and param_col and time_col != param_col:
                        valid_pairs.append((time_col, param_col, color))
                
                if not valid_pairs:
                    tk.messagebox.showwarning("Предупреждение", "Настройте корректные пары время → параметр!")
                    return
                  # Применяем настройки v1.1
                self.apply_selection_v11(valid_pairs, select_window)
        
        ttk.Button(button_frame, text="OK", command=apply_selection).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Отмена", command=select_window.destroy).pack(side="left", padx=5)

    def apply_selection_v10(self, datetime_column, selected_params, selected_colors, window):
        """Применение выбранных столбцов - режим v1.0 (совместимость)"""
        # Устанавливаем простой режим
        self.use_paired_mode = False
        self.datetime_column = datetime_column
        
        # Проверяем что выбран столбец даты/времени
        if not self.datetime_column:
            tk.messagebox.showerror("Ошибка", "Не выбран столбец с датой и временем.")
            return
        
        # Преобразуем столбец с датой/временем
        try:
            self.df[self.datetime_column] = pd.to_datetime(self.df[self.datetime_column])
        except Exception as e:
            tk.messagebox.showerror("Ошибка преобразования", 
                                  f"Ошибка при преобразовании столбца даты/времени: {str(e)}")
            return
        
        # Получаем выбранные параметры
        self.params = []
        self.param_colors = {}
        
        for col, selected in selected_params.items():
            if selected and col != self.datetime_column:
                self.params.append(col)
                self.param_colors[col] = selected_colors[col]
        
        if not self.params:
            tk.messagebox.showwarning("Предупреждение", "Не выбрано ни одного параметра для отображения")
            return
        
        # Устанавливаем начальный временной диапазон
        min_date = self.df[self.datetime_column].min()
        max_date = self.df[self.datetime_column].max()
        
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, min_date.strftime("%Y-%m-%d %H:%M:%S"))
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, max_date.strftime("%Y-%m-%d %H:%M:%S"))
        
        window.destroy()
        self.update_plot()

    def apply_selection_v11(self, valid_pairs, window):
        """Применение выбранных пар - режим v1.1 (парная привязка)"""
        # Устанавливаем парный режим
        self.use_paired_mode = True
        self.time_param_pairs = []
        self.param_colors = {}
        
        # Обрабатываем пары
        for time_col, param_col, color in valid_pairs:
            # Преобразуем столбец времени
            try:
                self.df[time_col] = pd.to_datetime(self.df[time_col])
            except Exception as e:
                tk.messagebox.showerror("Ошибка преобразования", 
                                      f"Ошибка при преобразовании столбца времени '{time_col}': {str(e)}")
                return
            
            self.time_param_pairs.append((time_col, param_col))
            self.param_colors[param_col] = color
        
        # Создаем объединенную временную шкалу
        if self.time_param_pairs:
            combined_timeline = self.create_combined_timeline()
            if combined_timeline is not None:
                min_date = combined_timeline.index.min()
                max_date = combined_timeline.index.max()
                
                self.start_date_entry.delete(0, tk.END)
                self.start_date_entry.insert(0, min_date.strftime("%Y-%m-%d %H:%M:%S"))
                self.end_date_entry.delete(0, tk.END)
                self.end_date_entry.insert(0, max_date.strftime("%Y-%m-%d %H:%M:%S"))
        
        window.destroy()
        self.update_plot()

    def create_combined_timeline(self):
        """Создание объединенной временной шкалы из всех пар время-параметр"""
        if not self.time_param_pairs:
            return None
        
        try:
            # Собираем все данные в общий DataFrame
            all_data = []
            
            for time_col, param_col in self.time_param_pairs:
                # Извлекаем данные пары
                pair_data = self.df[[time_col, param_col]].dropna()
                if not pair_data.empty:
                    # Переименовываем колонки для унификации
                    pair_data = pair_data.rename(columns={time_col: 'timestamp', param_col: param_col})
                    pair_data = pair_data.set_index('timestamp')
                    all_data.append(pair_data)
            
            if not all_data:
                return None            # Объединяем все данные по временной метке
            combined_df = pd.concat(all_data, axis=1, sort=True)
            
            return combined_df
            
        except Exception as e:
            print(f"Ошибка создания объединенной временной шкалы: {e}")
            return None

    def apply_selection(self, datetime_column, param_vars, param_colors_vars, window):
        """Старая функция для обратной совместимости"""
        # Преобразуем param_vars в формат для apply_selection_v10        selected_params = {}
        selected_colors = {}
        
        for col, var in param_vars.items():
            if var.get():
                selected_params[col] = True
                selected_colors[col] = param_colors_vars[col].get()
        
        # Перенаправляем на новую функцию v1.0
        self.apply_selection_v10(datetime_column, selected_params, selected_colors, window)

    def update_plot(self):
        """Обновление графика с выбранными параметрами - поддержка v1.0 и v1.1"""
        # Проверяем наличие данных
        if self.df is None:
            return
        
        # Проверяем режим работы
        if self.use_paired_mode:
            if not self.time_param_pairs:
                return
        else:
            if not hasattr(self, 'params') or not self.params:
                return
        
        # Очищаем ссылки на старые виджеты параметров
        if hasattr(self, 'param_value_labels'):
            self.param_value_labels.clear()
        
        # Очищаем предыдущий график
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        # Создаем новый график
        self.fig, self.ax1 = plt.subplots(figsize=(12, 6), facecolor='black')
        self.ax1.set_facecolor('black')
        self.axes = [self.ax1]
        self.lines = []
        
        # Настройка основной оси
        self.ax1.tick_params(axis='x', colors='white')
        self.ax1.tick_params(axis='y', colors='white')
        self.ax1.grid(color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
        
        # Получаем временной диапазон
        try:
            start_date = pd.to_datetime(self.start_date_entry.get())
            end_date = pd.to_datetime(self.end_date_entry.get())
        except Exception as e:
            tk.messagebox.showerror("Ошибка", f"Ошибка при анализе диапазона дат: {str(e)}")
            return
        
        if self.use_paired_mode:
            # Режим v1.1 - парная привязка
            filtered_pairs = []
            
            for i, (time_col, param_col) in enumerate(self.time_param_pairs):
                # Фильтруем данные пары по временному диапазону
                pair_data = self.df[[time_col, param_col]].dropna()
                if not pair_data.empty:
                    mask = (pair_data[time_col] >= start_date) & (pair_data[time_col] <= end_date)
                    filtered_pair = pair_data[mask]
                    
                    if not filtered_pair.empty:
                        filtered_pairs.append((time_col, param_col, filtered_pair))
            
            if not filtered_pairs:
                tk.messagebox.showwarning("Предупреждение", "Нет данных в выбранном диапазоне")
                return
            
            # Отображаем каждую пару
            for i, (time_col, param_col, pair_data) in enumerate(filtered_pairs):
                if i == 0:
                    ax = self.ax1
                    ax.set_ylabel(param_col, color=self.param_colors[param_col], fontsize=8)
                else:
                    # Создаем новую ось Y для каждого дополнительного параметра
                    ax = self.ax1.twinx()
                    ax.spines['right'].set_position(('outward', 40 * (i-1)))
                    ax.set_ylabel(param_col, color=self.param_colors[param_col], fontsize=8)
                    self.axes.append(ax)
                
                # Отрисовываем линию
                line, = ax.plot(pair_data[time_col], pair_data[param_col], 
                              color=self.param_colors[param_col], linewidth=1.5, 
                              label=f"{param_col} ({time_col})")
                self.lines.append(line)
                
                # Настройка цвета оси и делений
                ax.tick_params(axis='y', colors=self.param_colors[param_col], labelsize=8)
                ax.spines['right'].set_color(self.param_colors[param_col])
                
                # Добавляем информацию о паре
                frame = ttk.Frame(self.info_frame, style='Black.TFrame')
                frame.pack(side="left", padx=10, pady=5)
                
                param_label = ttk.Label(frame, text=f"{param_col} ({time_col}):", 
                                      foreground=self.param_colors[param_col],
                                      background='black',
                                      style='Black.TLabel')
                param_label.pack(side="left")
                
                # Создаем метку для значения
                value_label = ttk.Label(frame, text="--",
                                      background='black',
                                      foreground='white',
                                      style='Black.TLabel')
                value_label.pack(side="left", padx=5)
                
                # Сохраняем ссылку на метку
                if not hasattr(self, 'param_value_labels'):
                    self.param_value_labels = {}
                self.param_value_labels[param_col] = value_label
        
        else:
            # Режим v1.0 - совместимость
            # Фильтруем данные по временному диапазону
            mask = (self.df[self.datetime_column] >= start_date) & (self.df[self.datetime_column] <= end_date)
            filtered_df = self.df[mask]
            
            if filtered_df.empty:
                tk.messagebox.showwarning("Предупреждение", "Нет данных в выбранном диапазоне")
                return
            
            # Отображаем каждый параметр
            for i, param in enumerate(self.params):
                if i == 0:
                    ax = self.ax1
                    ax.set_ylabel(param, color=self.param_colors[param], fontsize=8)
                else:
                    # Создаем новую ось Y для каждого дополнительного параметра
                    ax = self.ax1.twinx()
                    ax.spines['right'].set_position(('outward', 40 * (i-1)))
                    ax.set_ylabel(param, color=self.param_colors[param], fontsize=8)
                    self.axes.append(ax)
                
                # Отрисовываем линию
                line, = ax.plot(filtered_df[self.datetime_column], filtered_df[param], 
                              color=self.param_colors[param], linewidth=1.5)
                self.lines.append(line)
                
                # Настройка цвета оси и делений
                ax.tick_params(axis='y', colors=self.param_colors[param], labelsize=8)
                ax.spines['right'].set_color(self.param_colors[param])
                
                # Добавляем информацию о параметре
                frame = ttk.Frame(self.info_frame, style='Black.TFrame')
                frame.pack(side="left", padx=10, pady=5)
                
                param_label = ttk.Label(frame, text=f"{param}:", 
                                      foreground=self.param_colors[param],
                                      background='black',
                                      style='Black.TLabel')
                param_label.pack(side="left")
                
                # Создаем метку для значения
                value_label = ttk.Label(frame, text="--",
                                      background='black',
                                      foreground='white',
                                      style='Black.TLabel')
                value_label.pack(side="left", padx=5)
                
                # Сохраняем ссылку на метку
                if not hasattr(self, 'param_value_labels'):
                    self.param_value_labels = {}
                self.param_value_labels[param] = value_label
        
        # Настройка форматирования оси X (дата)
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S\n%d.%m.%y'))
        plt.setp(self.ax1.get_xticklabels(), rotation=0)
        self.ax1.tick_params(axis='x', colors='white', labelsize=8)
        
        # Создание холста Matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # Добавление панели инструментов
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Отключение отображения координат в стандартной панели инструментов
        self.toolbar.set_message = lambda s: None
        
        # Метка для координат
        self.coords_label = tk.Label(
            self.plot_frame, 
            text="", 
            bg='black', 
            fg='white', 
            font=('Courier', 10),
            anchor='w',
            justify='left',
            wraplength=1200,
            padx=15,
            pady=2
        )
        
        # Позиционируем метку вверху окна
        self.coords_label.pack(side=tk.TOP, fill=tk.X, before=self.canvas.get_tk_widget())
        
        # Подключение обработчика движения мыши
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # Подключение обработчика прокрутки колесика мыши для масштабирования
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        
        # Подключение обработчиков для панорамирования
        self.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.canvas.mpl_connect('button_release_event', self.on_button_release)
          # Регулировка пространства для осей
        plt.subplots_adjust(
            top=0.95,        # Увеличиваем до 0.95 (меньше места сверху)
            right=0.85,      # Освобождает место для осей справа
            bottom=0.15      # Место для оси X с датами
        )        # Автоматически подстраиваем компоновку с минимальными отступами
        self.fig.tight_layout(pad=1)  # Уменьшенный отступ (было по умолчанию ~3.0)
    
    def update_time_range(self):
        """Обновление временного диапазона"""
        self.update_plot()
    
    def reset_time_range(self):
        """Сброс временного диапазона к полному"""
        if self.df is None:
            return
            
        min_date = None
        max_date = None
        
        if self.use_paired_mode:
            # Режим v1.1 - используем объединенную временную шкалу
            if hasattr(self, 'time_param_pairs') and self.time_param_pairs:
                combined_timeline = self.create_combined_timeline()
                if combined_timeline is not None and not combined_timeline.empty:
                    min_date = combined_timeline.index.min()
                    max_date = combined_timeline.index.max()
        else:
            # Режим v1.0 - используем единый столбец времени
            if hasattr(self, 'datetime_column') and self.datetime_column is not None:
                min_date = self.df[self.datetime_column].min()
                max_date = self.df[self.datetime_column].max()
        
        if min_date is not None and max_date is not None:
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, min_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            self.end_date_entry.delete(0, tk.END)
            self.end_date_entry.insert(0, max_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            self.update_plot()
    
    def set_time_preset(self, hours=None, days=None):
        """Установка предустановленного временного диапазона"""
        if self.df is None:
            return
            
        max_date = None
        
        if self.use_paired_mode:
            # Режим v1.1 - используем объединенную временную шкалу
            if hasattr(self, 'time_param_pairs') and self.time_param_pairs:
                combined_timeline = self.create_combined_timeline()
                if combined_timeline is not None and not combined_timeline.empty:
                    max_date = combined_timeline.index.max()
        else:
            # Режим v1.0 - используем единый столбец времени
            if hasattr(self, 'datetime_column') and self.datetime_column is not None:
                max_date = self.df[self.datetime_column].max()
        
        if max_date is None:
            return
            
        if hours:
            min_date = max_date - timedelta(hours=hours)
        elif days:
            min_date = max_date - timedelta(days=days)
        else:
            return
            
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, min_date.strftime("%Y-%m-%d %H:%M:%S"))
        
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, max_date.strftime("%Y-%m-%d %H:%M:%S"))
        
        self.update_plot()
    
    def on_mouse_move(self, event):
        """Обработчик движения мыши для отображения координат вверху и панорамирования"""
        # Обработка панорамирования
        if self.is_panning and event.inaxes and self.pan_start_point:
            # Вычисляем смещение курсора
            dx = event.xdata - self.pan_start_point[0]
            dy = event.ydata - self.pan_start_point[1]
            
            # Применяем смещение к осям
            if self.pan_start_xlim and self.pan_start_ylim:
                # Новые пределы с учетом смещения
                new_xlim = [self.pan_start_xlim[0] - dx, self.pan_start_xlim[1] - dx]
                new_ylim = [self.pan_start_ylim[0] - dy, self.pan_start_ylim[1] - dy]
                
                # Применяем к текущей оси
                event.inaxes.set_xlim(new_xlim)
                event.inaxes.set_ylim(new_ylim)
                
                # Синхронизируем ось X для всех осей (мультипараметрический график)
                if hasattr(self, 'axes') and len(self.axes) > 1:
                    for ax in self.axes:
                        ax.set_xlim(new_xlim)
                
                # Обновляем график
                self.canvas.draw_idle()
            return
        
        # Остальная логика для отображения координат (только если не панорамируем)
        if self.is_panning:
            return
            
        if event.inaxes is None:
            self.coords_label.config(text="")
            # Удаляем вертикальную линию, если курсор вне графика
            if self.cursor_line is not None:
                self.cursor_line.remove()
                self.cursor_line = None
                self.canvas.draw_idle()
            
            # Очищаем значения в информационном блоке
            if hasattr(self, 'param_value_labels'):
                for param, param_label in list(self.param_value_labels.items()):
                    try:
                        if param_label.winfo_exists():
                            param_label.config(text="--")
                    except tk.TclError:
                        del self.param_value_labels[param]
            return
            
        x_coord = event.xdata
        y_coord = event.ydata
        
        if x_coord is not None and y_coord is not None:
            try:
                # Удаляем предыдущую вертикальную линию
                if self.cursor_line is not None:
                    self.cursor_line.remove()
                
                date_coord = mdates.num2date(x_coord)
                date_str = date_coord.strftime('%H:%M:%S %d.%m.%y')
                
                # Начинаем с времени с фиксированной шириной
                coord_parts = [f"Время: {date_str:<20}"]
                  # Найдем ближайшую точку во временном ряду
                if self.df is not None:
                    try:
                        # Получаем текущий временной диапазон для поиска только в отфильтрованных данных
                        start_date = pd.to_datetime(self.start_date_entry.get())
                        end_date = pd.to_datetime(self.end_date_entry.get())
                        
                        param_values = []
                        closest_x = x_coord  # По умолчанию используем позицию курсора
                        
                        if self.use_paired_mode:
                            # Режим v1.1 - парная привязка
                            if hasattr(self, 'time_param_pairs') and self.time_param_pairs:
                                # Преобразуем координату X в формат timestamp
                                timestamp = date_coord.timestamp()
                                
                                # Для каждой пары время-параметр находим ближайшую точку
                                for time_col, param_col in self.time_param_pairs:
                                    # Фильтруем данные пары по временному диапазону
                                    pair_data = self.df[[time_col, param_col]].dropna()
                                    if not pair_data.empty:
                                        mask = (pair_data[time_col] >= start_date) & (pair_data[time_col] <= end_date)
                                        filtered_pair = pair_data[mask]
                                        
                                        if not filtered_pair.empty:
                                            # Преобразуем столбец времени в timestamp для поиска ближайшей точки
                                            timestamps = filtered_pair[time_col].apply(lambda x: x.timestamp())
                                            
                                            # Находим индекс ближайшей точки в этой паре
                                            closest_idx = (timestamps - timestamp).abs().idxmin()
                                            
                                            # Получаем значение параметра
                                            value = filtered_pair.loc[closest_idx, param_col]
                                            if pd.notna(value):
                                                param_short = param_col[:15]
                                                param_text = f"{param_short:<15}: {value:>8.2f}"
                                                param_values.append(param_text)
                                                  # Обновляем значение в информационном блоке
                                                if hasattr(self, 'param_value_labels') and param_col in self.param_value_labels:
                                                    try:
                                                        if self.param_value_labels[param_col].winfo_exists():
                                                            self.param_value_labels[param_col].config(text=f"{value:.2f}")
                                                    except tk.TclError:
                                                        del self.param_value_labels[param_col]
                                            else:
                                                param_short = param_col[:15]
                                                param_text = f"{param_short:<15}: {'н/д':>8}"
                                                param_values.append(param_text)
                                                
                                                if hasattr(self, 'param_value_labels') and param_col in self.param_value_labels:
                                                    try:
                                                        if self.param_value_labels[param_col].winfo_exists():
                                                            self.param_value_labels[param_col].config(text="н/д")
                                                    except tk.TclError:
                                                        del self.param_value_labels[param_col]
                                
                                # Для позиционирования линии курсора используем объединенную временную шкалу
                                if self.time_param_pairs:
                                    # Создаем объединенную временную шкалу из всех пар
                                    combined_timeline = self.create_combined_timeline()
                                    
                                    if combined_timeline is not None and not combined_timeline.empty:
                                        # Фильтруем объединенную временную шкалу по диапазону
                                        timeline_index = combined_timeline.index
                                        mask = (timeline_index >= start_date) & (timeline_index <= end_date)
                                        filtered_timeline = timeline_index[mask]
                                        
                                        if not filtered_timeline.empty:
                                            # Ищем ближайшую точку в объединенной временной шкале
                                            timestamps = pd.Series([t.timestamp() for t in filtered_timeline])
                                            closest_idx = (timestamps - timestamp).abs().idxmin()
                                            closest_time = filtered_timeline[timestamps.index[closest_idx]]
                                            closest_x = mdates.date2num(closest_time)
                        
                        else:
                            # Режим v1.0 - совместимость
                            if self.datetime_column is not None and hasattr(self, 'params') and self.params:
                                # Фильтруем данные по временному диапазону
                                mask = (self.df[self.datetime_column] >= start_date) & (self.df[self.datetime_column] <= end_date)
                                filtered_df = self.df[mask]
                                
                                if not filtered_df.empty:
                                    # Преобразуем координату X в формат timestamp
                                    timestamp = date_coord.timestamp()
                                    
                                    # Преобразуем столбец даты/времени в timestamp для поиска ближайшей точки
                                    timestamps = filtered_df[self.datetime_column].apply(lambda x: x.timestamp())
                                    
                                    # Находим индекс ближайшей точки
                                    closest_idx = (timestamps - timestamp).abs().idxmin()
                                    
                                    # Получаем точное время ближайшей точки для более точного позиционирования линии
                                    closest_time = filtered_df.loc[closest_idx, self.datetime_column]
                                    closest_x = mdates.date2num(closest_time)
                                    
                                    # Собираем значения всех параметров в этой точке
                                    for param in self.params:
                                        if param in filtered_df.columns:
                                            value = filtered_df.loc[closest_idx, param]
                                            if pd.notna(value):
                                                param_short = param[:15]
                                                param_text = f"{param_short:<15}: {value:>8.2f}"
                                                param_values.append(param_text)
                                                
                                                # Обновляем значение в информационном блоке
                                                if hasattr(self, 'param_value_labels') and param in self.param_value_labels:
                                                    try:
                                                        if self.param_value_labels[param].winfo_exists():
                                                            self.param_value_labels[param].config(text=f"{value:.2f}")
                                                    except tk.TclError:
                                                        del self.param_value_labels[param]
                                            else:
                                                param_short = param[:15]
                                                param_text = f"{param_short:<15}: {'н/д':>8}"
                                                param_values.append(param_text)
                                                
                                                if hasattr(self, 'param_value_labels') and param in self.param_value_labels:
                                                    try:
                                                        if self.param_value_labels[param].winfo_exists():
                                                            self.param_value_labels[param].config(text="н/д")
                                                    except tk.TclError:
                                                        del self.param_value_labels[param]
                        
                        # Рисуем СЕРУЮ ПУНКТИРНУЮ вертикальную линию курсора
                        self.cursor_line = event.inaxes.axvline(x=closest_x, color='gray', linestyle='--', 
                                                               linewidth=1.5, alpha=0.8)
                          # Добавляем параметры с увеличенными отступами
                        if param_values:
                            coord_parts.extend(param_values)
                    
                    except Exception as inner_e:
                        print(f"Ошибка при получении значений параметров: {inner_e}")
                        # Рисуем простую серую пунктирную линию при ошибке
                        self.cursor_line = event.inaxes.axvline(x=x_coord, color='gray', linestyle='--', 
                                                               linewidth=1.5, alpha=0.8)
                else:
                    # Рисуем простую серую пунктирную линию если нет данных
                    self.cursor_line = event.inaxes.axvline(x=x_coord, color='gray', linestyle='--', 
                                                           linewidth=1.5, alpha=0.8)
                
                # Объединяем все части в одну строку с увеличенными разделителями
                coord_text = "   |   ".join(coord_parts)
                self.coords_label.config(text=coord_text)
                
                # Обновляем canvas для отображения линии
                self.canvas.draw_idle()
                
            except Exception as e:
                # При ошибке возвращаемся к простому формату
                coord_text = f"x: {x_coord:.2f}, y: {y_coord:.2f}"
                self.coords_label.config(text=coord_text)
                print(f"Ошибка в on_mouse_move: {e}")
        else:
            self.coords_label.config(text="")
            # Очищаем значения в информационном блоке когда нет координат
            if hasattr(self, 'param_value_labels'):
                for param, param_label in list(self.param_value_labels.items()):
                    try:
                        # Проверяем, что виджет еще существует
                        if param_label.winfo_exists():
                            param_label.config(text="--")
                    except tk.TclError:                        # Виджет был уничтожен, удаляем его из словаря
                        del self.param_value_labels[param]

    def on_scroll(self, event):
        """Обработчик прокрутки колесика мыши для масштабирования графика"""
        if event.inaxes is None:
            return
        
        # Получаем текущие пределы осей
        xlim = event.inaxes.get_xlim()
        ylim = event.inaxes.get_ylim()
        
        # Получаем позицию курсора
        xdata = event.xdata
        ydata = event.ydata
        
        if xdata is None or ydata is None:
            return
        
        # Коэффициент масштабирования
        scale_factor = 0.9 if event.button == 'up' else 1.1
        
        # Вычисляем новые пределы с центром в позиции курсора
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        
        # Новые размеры диапазонов
        new_x_range = x_range * scale_factor
        new_y_range = y_range * scale_factor
        
        # Вычисляем смещение относительно курсора
        x_offset_left = (xdata - xlim[0]) / x_range
        x_offset_right = (xlim[1] - xdata) / x_range
        y_offset_bottom = (ydata - ylim[0]) / y_range
        y_offset_top = (ylim[1] - ydata) / y_range
        
        # Новые пределы с центром в позиции курсора
        new_xlim = [
            xdata - new_x_range * x_offset_left,
            xdata + new_x_range * x_offset_right
        ]
        new_ylim = [
            ydata - new_y_range * y_offset_bottom,
            ydata + new_y_range * y_offset_top
        ]
        
        # Применяем новые пределы
        event.inaxes.set_xlim(new_xlim)
        event.inaxes.set_ylim(new_ylim)
        
        # Обновляем все связанные оси Y (для мультипараметрического графика)
        if hasattr(self, 'axes') and len(self.axes) > 1:
            for ax in self.axes[1:]:  # Пропускаем основную ось
                ax.set_xlim(new_xlim)  # Устанавливаем тот же X диапазон для всех осей
        
        # Перерисовываем график
        self.canvas.draw_idle()

    def on_button_press(self, event):
        """Обработчик нажатия кнопки мыши для начала панорамирования"""
        if event.button == 1 and event.inaxes:  # Левая кнопка мыши
            self.is_panning = True
            self.pan_start_point = (event.xdata, event.ydata)
            self.pan_start_xlim = event.inaxes.get_xlim()
            self.pan_start_ylim = event.inaxes.get_ylim()
            
            # Изменяем курсор для индикации режима панорамирования
            self.canvas.get_tk_widget().config(cursor="fleur")

    def on_button_release(self, event):
        """Обработчик отпускания кнопки мыши для окончания панорамирования"""
        if event.button == 1:  # Левая кнопка мыши
            self.is_panning = False
            self.pan_start_point = None
            self.pan_start_xlim = None
            self.pan_start_ylim = None
            
            # Возвращаем обычный курсор
            self.canvas.get_tk_widget().config(cursor="")

    def show_about(self):
        """Показ информации о программе"""
        about_text = """Multi-Parameter Data Analyzer v1.1
    
Профессиональный инструмент для визуализации
многопараметрических данных из CSV/Excel файлов.

🆕 Новинка v1.1: Парная привязка время → параметр

Разработчик: j15
GitHub: https://github.com/jackal100500/CSV_software.git

© 2025"""
        tk.messagebox.showinfo("About", about_text)

    def open_github(self):
        """Открытие GitHub репозитория"""
        import webbrowser
        webbrowser.open("https://github.com/jackal100500/CSV_software.git")
        
# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = MultiParameterPlotApp(root)
    root.mainloop()