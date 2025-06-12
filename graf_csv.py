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
                self.df = pd.read_csv(file_path)
            
            # Открываем окно выбора столбцов
            self.select_columns()
            
        except Exception as e:
            tk.messagebox.showerror("Ошибка загрузки", f"Ошибка при загрузке файла: {str(e)}")
      def select_columns(self):
        """Открытие окна для выбора столбцов для отображения"""
        select_window = tk.Toplevel(self.root)
        select_window.title("Выбор столбцов для отображения - v1.1")
        select_window.geometry("500x650")  # Увеличиваем размер окна

        # Основной фрейм
        main_frame = ttk.Frame(select_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # === НОВЫЙ БЛОК: Выбор режима работы ===
        mode_frame = ttk.LabelFrame(main_frame, text="Режим работы:")
        mode_frame.pack(fill="x", padx=5, pady=5)
        
        mode_var = tk.StringVar(value="simple")
        
        ttk.Radiobutton(mode_frame, text="Простой (один столбец времени для всех)", 
                       variable=mode_var, value="simple").pack(anchor="w", padx=10, pady=2)
        ttk.Radiobutton(mode_frame, text="Парный (свое время для каждого параметра)", 
                       variable=mode_var, value="paired").pack(anchor="w", padx=10, pady=2)

        # === БЛОК: Простой режим (как в v1.0) ===
        simple_frame = ttk.LabelFrame(main_frame, text="Простой режим:")
        simple_frame.pack(fill="x", padx=5, pady=5)

        # Фрейм для выбора столбца даты/времени
        datetime_frame = ttk.Frame(simple_frame)
        datetime_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(datetime_frame, text="Столбец времени:").pack(anchor="w")
        datetime_var = tk.StringVar()
        datetime_combo = ttk.Combobox(datetime_frame, textvariable=datetime_var, 
                                    values=list(self.df.columns), state="readonly")
        datetime_combo.pack(fill="x", pady=2)

        # Улучшенное определение столбца с датой/временем
        for col in self.df.columns:
            if any(kw in col.lower() for kw in ['date', 'time', 'datetime', 'дата', 'время']):                datetime_combo.set(col)
                break

        # === БЛОК: Парный режим (новый в v1.1) ===
        paired_frame = ttk.LabelFrame(main_frame, text="Парный режим - автоопределенные пары:")
        paired_frame.pack(fill="x", padx=5, pady=5)
        
        # Автоопределение пар при наличии менеджера
        auto_pairs = []
        if self.timeline_manager:
            try:
                auto_pairs = self.timeline_manager.auto_detect_pairs(self.df)
            except Exception as e:
                print(f"Ошибка автоопределения пар: {e}")
        
        # Отображаем найденные пары
        pairs_info_label = ttk.Label(paired_frame, 
                                   text=f"Найдено пар: {len(auto_pairs)}" if auto_pairs else "Пары не найдены")
        pairs_info_label.pack(anchor="w", padx=10, pady=2)
        
        if auto_pairs:
            pairs_text = "\n".join([f"• {time_col} → {param_col}" for time_col, param_col in auto_pairs[:5]])
            if len(auto_pairs) > 5:
                pairs_text += f"\n... и еще {len(auto_pairs) - 5} пар"
            
            pairs_display = ttk.Label(paired_frame, text=pairs_text, font=("Consolas", 8))
            pairs_display.pack(anchor="w", padx=20, pady=2)

        # === БЛОК: Выбор параметров ===
        params_label_frame = ttk.LabelFrame(main_frame, text="Выберите параметры для отображения:")
        params_label_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Создаем холст с полосой прокрутки
        canvas = tk.Canvas(params_label_frame)
        scrollbar = ttk.Scrollbar(params_label_frame, orient="vertical", command=canvas.yview)
        
        # Фрейм внутри холста для размещения параметров
        param_scrollable_frame = ttk.Frame(canvas)
        param_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=param_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
          # Размещаем холст и полосу прокрутки
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Создаем чекбоксы для каждого столбца
        param_vars = {}
        param_colors_vars = {}
        
        # Расширенный список доступных цветов
        available_colors = self.colors + ['black', 'gray', 'silver', 'maroon', 'olive', 'navy', 'teal', 'purple']
        
        # Функция для обновления отображения параметров в зависимости от режима
        def update_param_display(*args):
            # Очищаем текущие элементы
            for widget in param_scrollable_frame.winfo_children():
                widget.destroy()
            param_vars.clear()
            param_colors_vars.clear()
            
            current_mode = mode_var.get()
            
            if current_mode == "simple":
                # Простой режим - показываем все числовые столбцы
                for i, col in enumerate(self.df.columns):
                    if col == datetime_var.get(): 
                        continue  # Пропускаем столбец даты/времени
                    if not pd.api.types.is_numeric_dtype(self.df[col]):
                        continue  # Показываем только числовые столбцы

                    # Компактная компоновка в одной строке
                    row_frame = ttk.Frame(param_scrollable_frame)
                    row_frame.pack(fill="x", pady=2, padx=5)
                    
                    var = tk.BooleanVar(value=False)
                    param_vars[col] = var
                    
                    # Чекбокс с фиксированной шириной
                    cb = ttk.Checkbutton(row_frame, text=col, variable=var, width=25)
                    cb.pack(side="left", padx=(0, 5))
                    
                    # Выбор цвета справа от чекбокса
                    color_var = tk.StringVar(value=self.colors[i % len(self.colors)])
                    param_colors_vars[col] = color_var
                    
                    color_combo = ttk.Combobox(row_frame, textvariable=color_var, 
                                             values=available_colors, width=10, state="readonly")
                    color_combo.pack(side="left", padx=(10, 0))
                    
            else:  # paired mode
                # Парный режим - показываем только параметры из автоопределенных пар
                for i, (time_col, param_col) in enumerate(auto_pairs):
                    row_frame = ttk.Frame(param_scrollable_frame)
                    row_frame.pack(fill="x", pady=2, padx=5)
                    
                    var = tk.BooleanVar(value=True)  # По умолчанию включаем автоопределенные пары
                    param_vars[param_col] = var
                    
                    # Показываем пару время + параметр
                    cb = ttk.Checkbutton(row_frame, text=f"{time_col} → {param_col}", 
                                       variable=var, width=30)
                    cb.pack(side="left", padx=(0, 5))
                    
                    # Выбор цвета
                    color_var = tk.StringVar(value=self.colors[i % len(self.colors)])
                    param_colors_vars[param_col] = color_var
                    
                    color_combo = ttk.Combobox(row_frame, textvariable=color_var, 
                                             values=available_colors, width=10, state="readonly")
                    color_combo.pack(side="left", padx=(10, 0))
        
        # Привязываем обновление к изменению режима
        mode_var.trace("w", update_param_display)
        datetime_var.trace("w", update_param_display)
        
        # Инициализируем отображение
        update_param_display()
          # Добавляем кнопку внизу окна в отдельном фрейме
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            button_frame, 
            text="Применить", 
            command=lambda: self.apply_selection_v11(mode_var.get(), datetime_var.get(), 
                                                   param_vars, param_colors_vars, auto_pairs, select_window)
        ).pack(pady=5)
        
        # Улучшенная привязка прокрутки колесиком мыши
        canvas.bind_all("<MouseWheel>", lambda event, c=canvas: c.yview_scroll(int(-1*(event.delta/120)), "units"))
        select_window.bind("<Destroy>", lambda event: self.root.unbind_all("<MouseWheel>"))
    
    
    def apply_selection_v11(self, mode, datetime_column, param_vars, param_colors_vars, auto_pairs, window):
        """Применение выбранных столбцов и отображение графика - версия 1.1"""
        
        self.use_paired_mode = (mode == "paired")
        
        if self.use_paired_mode:
            # Парный режим
            self.time_param_pairs = []
            self.param_colors = {}
            
            # Собираем выбранные пары
            for time_col, param_col in auto_pairs:
                if param_col in param_vars and param_vars[param_col].get():
                    self.time_param_pairs.append((time_col, param_col))
                    self.param_colors[param_col] = param_colors_vars[param_col].get()
            
            if not self.time_param_pairs:
                tk.messagebox.showwarning("Предупреждение", "Не выбрано ни одной пары для отображения")
                return
                
            # Устанавливаем временной диапазон на основе всех пар
            if self.timeline_manager:
                min_time, max_time = self.timeline_manager.get_time_range(self.df, self.time_param_pairs)
                if min_time and max_time:
                    self.start_date_entry.delete(0, tk.END)
                    self.start_date_entry.insert(0, min_time.strftime("%Y-%m-%d %H:%M:%S"))
                    self.end_date_entry.delete(0, tk.END)
                    self.end_date_entry.insert(0, max_time.strftime("%Y-%m-%d %H:%M:%S"))
            
        else:
            # Простой режим (совместимость с v1.0)
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
            
            for col, var in param_vars.items():
                if var.get() and col != self.datetime_column:
                    self.params.append(col)
                    self.param_colors[col] = param_colors_vars[col].get()
            
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
    
      def apply_selection(self, datetime_column, param_vars, param_colors_vars, window):
        """Старая функция для обратной совместимости"""
        # Перенаправляем на новую функцию в простом режиме
        self.apply_selection_v11("simple", datetime_column, param_vars, param_colors_vars, [], window)
        
    def update_plot(self):
        """Обновление графика с выбранными параметрами"""
        if self.df is None or not self.params:
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
            
            # Фильтруем данные по временному диапазону
            mask = (self.df[self.datetime_column] >= start_date) & (self.df[self.datetime_column] <= end_date)
            filtered_df = self.df[mask]
            
            if filtered_df.empty:
                tk.messagebox.showwarning("Предупреждение", "Нет данных в выбранном диапазоне")
                return
                
        except Exception as e:
            tk.messagebox.showerror("Ошибка", f"Ошибка при анализе диапазона дат: {str(e)}")
            return
        
        # Отображаем каждый параметр
        for i, param in enumerate(self.params):
            # Изменить в функции update_plot(), когда создаете дополнительные оси:
            if i == 0:
                ax = self.ax1
                ax.set_ylabel(param, color=self.param_colors[param], fontsize=8)  # Уменьшенный размер шрифта
            else:
                # Создаем новую ось Y для каждого дополнительного параметра
                ax = self.ax1.twinx()
                
                # Настраиваем позицию оси с меньшим отступом
                ax.spines['right'].set_position(('outward', 40 * (i-1)))  # Уменьшено с 60 до 40
                ax.set_ylabel(param, color=self.param_colors[param], fontsize=8)  # Уменьшенный размер шрифта
                
                self.axes.append(ax)
            
            # Отрисовываем линию
            line, = ax.plot(filtered_df[self.datetime_column], filtered_df[param], 
                          color=self.param_colors[param], linewidth=1.5)
            self.lines.append(line)
            
            # Настройка цвета оси и делений
            ax.tick_params(axis='y', colors=self.param_colors[param], labelsize=8)  # Уменьшенный размер цифр
            ax.spines['right'].set_color(self.param_colors[param])
              # Добавляем информацию о параметре (значение будет обновляться при движении курсора)
            frame = ttk.Frame(self.info_frame, style='Black.TFrame')
            frame.pack(side="left", padx=10, pady=5)
            
            param_label = ttk.Label(frame, text=f"{param}:", 
                                  foreground=self.param_colors[param],
                                  background='black',
                                  style='Black.TLabel')
            param_label.pack(side="left")
            
            # Создаем метку для значения, которая будет обновляться
            value_label = ttk.Label(frame, text="--",
                                  background='black',
                                  foreground='white',
                                  style='Black.TLabel')
            value_label.pack(side="left", padx=5)
            
            # Сохраняем ссылку на метку для обновления в on_mouse_move
            if not hasattr(self, 'param_value_labels'):
                self.param_value_labels = {}
            self.param_value_labels[param] = value_label
        
        # Настройка форматирования оси X (дата)
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S\n%d.%m.%y'))
        plt.setp(self.ax1.get_xticklabels(), rotation=0)
        self.ax1.tick_params(axis='x', colors='white', labelsize=8)  # Уменьшенный размер шрифта на оси X        # Настройка заголовка
        # self.ax1.set_title("Мультипараметрический график", color='white', fontsize=10)  # Уменьшенный заголовок
        
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
          # Улучшенная метка для координат - размещаем во всю ширину сверху
        self.coords_label = tk.Label(
            self.plot_frame, 
            text="", 
            bg='black', 
            fg='white', 
            font=('Courier', 10),
            anchor='w',  # Выравнивание по левому краю вместо центра
            justify='left',  # Выравнивание текста по левому краю
            wraplength=1200,  # Ещё больше увеличенная ширина
            padx=15,  # Увеличенные отступы по бокам
            pady=2    # УМЕНЬШЕННЫЙ отступ сверху и снизу (было 8, стало 2)
        )
        
        # Позиционируем метку вверху окна, растягивая на всю ширину
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
        )

        # Автоматически подстраиваем компоновку с минимальными отступами
        self.fig.tight_layout(pad=1)  # Уменьшенный отступ (было по умолчанию ~3.0)
    
    def update_time_range(self):
        """Обновление временного диапазона"""
        self.update_plot()
    
    def reset_time_range(self):
        """Сброс временного диапазона к полному"""
        if self.df is not None and self.datetime_column is not None:
            min_date = self.df[self.datetime_column].min()
            max_date = self.df[self.datetime_column].max()
            
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, min_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            self.end_date_entry.delete(0, tk.END)
            self.end_date_entry.insert(0, max_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            self.update_plot()
    
    def set_time_preset(self, hours=None, days=None):
        """Установка предустановленного временного диапазона"""
        if self.df is None or self.datetime_column is None:
            return
            
        max_date = self.df[self.datetime_column].max()
        
        if hours:
            min_date = max_date - timedelta(hours=hours)
        elif days:
            min_date = max_date - timedelta(days=days)
        else:            return            
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
                if self.df is not None and self.datetime_column is not None and hasattr(self, 'params') and self.params:
                    try:
                        # Получаем текущий временной диапазон для поиска только в отфильтрованных данных
                        start_date = pd.to_datetime(self.start_date_entry.get())
                        end_date = pd.to_datetime(self.end_date_entry.get())
                        
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
                            
                            # Рисуем СЕРУЮ ПУНКТИРНУЮ вертикальную линию курсора
                            self.cursor_line = event.inaxes.axvline(x=closest_x, color='gray', linestyle='--', 
                                                                   linewidth=1.5, alpha=0.8)
                            
                            # Собираем значения всех параметров в этой точке с фиксированной шириной
                            param_values = []
                            for param in self.params:
                                if param in filtered_df.columns:
                                    value = filtered_df.loc[closest_idx, param]
                                    if pd.notna(value):
                                        # Используем фиксированную ширину для названия параметра и значения
                                        param_short = param[:15]  # Обрезаем длинные названия
                                        param_text = f"{param_short:<15}: {value:>8.2f}"
                                        param_values.append(param_text)
                                        
                                        # Обновляем значение в информационном блоке
                                        if hasattr(self, 'param_value_labels') and param in self.param_value_labels:
                                            try:
                                                # Проверяем, что виджет еще существует
                                                if self.param_value_labels[param].winfo_exists():
                                                    self.param_value_labels[param].config(text=f"{value:.2f}")
                                            except tk.TclError:
                                                # Виджет был уничтожен, удаляем его из словаря
                                                del self.param_value_labels[param]
                                    else:
                                        param_short = param[:15]
                                        param_text = f"{param_short:<15}: {'н/д':>8}"
                                        param_values.append(param_text)
                                        
                                        # Обновляем значение в информационном блоке
                                        if hasattr(self, 'param_value_labels') and param in self.param_value_labels:
                                            try:
                                                # Проверяем, что виджет еще существует
                                                if self.param_value_labels[param].winfo_exists():
                                                    self.param_value_labels[param].config(text="н/д")
                                            except tk.TclError:
                                                # Виджет был уничтожен, удаляем его из словаря
                                                del self.param_value_labels[param]
                            
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
        about_text = """Multi-Parameter Data Analyzer v1.0
    
Профессиональный инструмент для визуализации
многопараметрических данных из CSV/Excel файлов.

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