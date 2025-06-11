import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import Button, TextBox
import numpy as np
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class MultiParameterPlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Визуализация нескольких параметров")
        self.root.geometry("1200x850")
        
        # Настройка стилей
        style = ttk.Style()
        style.configure('Black.TFrame', background='black')
        style.configure('Black.TLabel', background='black')
          # Переменные для хранения данных
        self.df = None
        self.params = []
        self.datetime_column = None
        self.colors = ['red', 'green', 'white', 'cyan', 'magenta', 'yellow']
        
        # Переменная для вертикальной линии курсора
        self.cursor_line = None
        
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
        
        # Регулировка пространства для осей
        plt.subplots_adjust(right=0.85)  # Освобождает место для осей справа

        # Автоматически подстраиваем компоновку
        self.fig.tight_layout()
    
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
        select_window.title("Выбор столбцов для отображения")
        select_window.geometry("400x500")  # Увеличиваем начальную высоту
        
        # Основной фрейм
        main_frame = ttk.Frame(select_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Фрейм для выбора столбца даты/времени
        datetime_frame = ttk.LabelFrame(main_frame, text="Выберите столбец с датой и временем:")
        datetime_frame.pack(fill="x", padx=5, pady=5)
        
        datetime_var = tk.StringVar()
        datetime_combo = ttk.Combobox(datetime_frame, textvariable=datetime_var, values=list(self.df.columns))
        datetime_combo.pack(pady=5, padx=10, fill="x")
        
        # Определение столбца с датой/временем автоматически
        for col in self.df.columns:
            if 'date' in col.lower() or 'time' in col.lower() or 'datetime' in col.lower():
                datetime_combo.set(col)
                break
        
        # Создаем контейнер с прокруткой для параметров
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
        param_colors = {}
        
        for i, col in enumerate(self.df.columns):
            frame = ttk.Frame(param_scrollable_frame)
            frame.pack(fill="x", pady=2, padx=5)
            
            var = tk.BooleanVar(value=False)
            param_vars[col] = var
            
            ttk.Checkbutton(frame, text=col, variable=var).pack(side="left", padx=(0, 5))
            
            color_label = ttk.Label(frame, text="Цвет:")
            color_label.pack(side="left", padx=(20, 5))
            
            color_var = tk.StringVar(value=self.colors[i % len(self.colors)])
            param_colors[col] = color_var
            
            color_combo = ttk.Combobox(frame, textvariable=color_var, values=self.colors, width=10)
            color_combo.pack(side="left")
        
        # Добавляем кнопку внизу окна в отдельном фрейме
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            button_frame, 
            text="Применить", 
            command=lambda: self.apply_selection(datetime_var.get(), param_vars, param_colors, select_window)
        ).pack(pady=5)
        
        # Привязка прокрутки колесиком мыши
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
    
    
    def apply_selection(self, datetime_column, param_vars, param_colors, window):
        """Применение выбранных столбцов и отображение графика"""
        self.datetime_column = datetime_column
        
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
                self.param_colors[col] = param_colors[col].get()
        
        if not self.params:
            tk.messagebox.showwarning("Предупреждение", "Не выбрано ни одного параметра для отображения")
            return
        
        window.destroy()
        
        # Устанавливаем начальный временной диапазон
        min_date = self.df[self.datetime_column].min()
        max_date = self.df[self.datetime_column].max()
        
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, min_date.strftime("%Y-%m-%d %H:%M:%S"))
        
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, max_date.strftime("%Y-%m-%d %H:%M:%S"))
        
        # Обновляем график
        self.update_plot()
        
    def update_plot(self):
        """Обновление графика с выбранными параметрами"""
        if self.df is None or not self.params:
            return
        
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
            
            # Добавляем информацию о текущем значении параметра
            frame = ttk.Frame(self.info_frame, style='Black.TFrame')
            frame.pack(side="left", padx=10, pady=5)
            
            param_label = ttk.Label(frame, text=f"{param}:", 
                                  foreground=self.param_colors[param],
                                  background='black',
                                  style='Black.TLabel')
            param_label.pack(side="left")
            
            last_value = filtered_df[param].iloc[-1] if not filtered_df.empty else "Н/Д"
            value_label = ttk.Label(frame, text=str(last_value),
                                  background='black',
                                  foreground='white',
                                  style='Black.TLabel')
            value_label.pack(side="left", padx=5)
        
        # Настройка форматирования оси X (дата)
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S\n%d.%m.%y'))
        plt.setp(self.ax1.get_xticklabels(), rotation=0)
        self.ax1.tick_params(axis='x', colors='white', labelsize=8)  # Уменьшенный размер шрифта на оси X        # Настройка заголовка
        self.ax1.set_title("Мультипараметрический график", color='white', fontsize=10)  # Уменьшенный заголовок
        
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
            pady=8    # Увеличенный отступ сверху и снизу
        )
        
        # Позиционируем метку вверху окна, растягивая на всю ширину
        self.coords_label.pack(side=tk.TOP, fill=tk.X, before=self.canvas.get_tk_widget())
        
        # Подключение обработчика движения мыши
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # Регулировка пространства для осей
        plt.subplots_adjust(right=0.85)  # Освобождает место для осей справа        # Автоматически подстраиваем компоновку        self.fig.tight_layout()
    
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
        else:
            return            
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, min_date.strftime("%Y-%m-%d %H:%M:%S"))
        
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, max_date.strftime("%Y-%m-%d %H:%M:%S"))
        
        self.update_plot()
    
    def on_mouse_move(self, event):
        """Обработчик движения мыши для отображения координат вверху"""
        if event.inaxes is None:
            self.coords_label.config(text="")
            # Удаляем вертикальную линию, если курсор вне графика
            if self.cursor_line is not None:
                self.cursor_line.remove()
                self.cursor_line = None
                self.canvas.draw_idle()
            return
        
        x_coord = event.xdata
        y_coord = event.ydata
        
        if x_coord is not None and y_coord is not None:
            try:
                # Удаляем предыдущую вертикальную линию
                if self.cursor_line is not None:
                    self.cursor_line.remove()
                
                # Рисуем новую вертикальную линию курсора
                self.cursor_line = event.inaxes.axvline(x=x_coord, color='white', linestyle='--', 
                                                       linewidth=1, alpha=0.7)
                
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
                            
                            # Обновляем позицию вертикальной линии для точного совпадения с данными
                            if self.cursor_line is not None:
                                self.cursor_line.remove()
                            self.cursor_line = event.inaxes.axvline(x=closest_x, color='yellow', linestyle='-', 
                                                                   linewidth=2, alpha=0.8)
                            
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
                                    else:
                                        param_short = param[:15]
                                        param_text = f"{param_short:<15}: {'н/д':>8}"
                                        param_values.append(param_text)
                            
                            # Добавляем параметры с увеличенными отступами
                            if param_values:
                                coord_parts.extend(param_values)
                    
                    except Exception as inner_e:
                        print(f"Ошибка при получении значений параметров: {inner_e}")
                        coord_parts.append(f"y: {y_coord:>8.2f}")
                
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

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = MultiParameterPlotApp(root)
    root.mainloop()