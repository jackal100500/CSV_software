import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class MultiParameterPlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Визуализация нескольких параметров")
        self.root.geometry("1300x900") # Возможно, потребуется больше места
        
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            print("Тема 'clam' не найдена, используется тема по умолчанию.")
            
        style.configure('Black.TFrame', background='black')
        style.configure('Black.TLabel', background='black', foreground='white')
        style.configure('Black.TLabelframe', background='black', foreground='white')
        style.configure('Black.TLabelframe.Label', background='black', foreground='white')
        
        self.df = None
        self.params = []
        self.datetime_column = None
        self.colors = ['red', 'green', 'white', 'cyan', 'magenta', 'yellow', 
                       'blue', 'orange', 'purple', 'brown', 'pink', 'lime']
        
        self.v_line = None
        self._motion_notify_cid = None
        self.param_value_labels = {}

        self.time_frame = ttk.LabelFrame(root, text="Временной диапазон")
        self.time_frame.pack(fill="x", padx=10, pady=(10,5))
        
        self.load_button = ttk.Button(self.time_frame, text="Загрузить файл", command=self.load_data)
        self.load_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Label(self.time_frame, text="Начало:").grid(row=0, column=1, padx=5, pady=5, sticky="e")
        self.start_date_entry = ttk.Entry(self.time_frame, width=20)
        self.start_date_entry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        ttk.Label(self.time_frame, text="Конец:").grid(row=0, column=3, padx=5, pady=5, sticky="e")
        self.end_date_entry = ttk.Entry(self.time_frame, width=20)
        self.end_date_entry.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        
        self.apply_time_button = ttk.Button(self.time_frame, text="Применить", command=self.update_time_range)
        self.apply_time_button.grid(row=0, column=5, padx=5, pady=5, sticky="ew")
        
        self.reset_time_button = ttk.Button(self.time_frame, text="Сбросить", command=self.reset_time_range)
        self.reset_time_button.grid(row=0, column=6, padx=5, pady=5, sticky="ew")
        
        self.time_frame.grid_columnconfigure(2, weight=1)
        self.time_frame.grid_columnconfigure(4, weight=1)

        self.time_presets_frame = ttk.Frame(self.time_frame)
        self.time_presets_frame.grid(row=1, column=0, columnspan=7, padx=5, pady=5, sticky="ew")
        
        presets = [
            ("Последний час", {"hours": 1}), ("Последние 6 часов", {"hours": 6}),
            ("Последние 24 часа", {"hours": 24}), ("Последние 7 дней", {"days": 7}),
            ("Последний месяц", {"days": 30})
        ]
        for i, (text, kwargs) in enumerate(presets):
            btn = ttk.Button(self.time_presets_frame, text=text, command=lambda kw=kwargs: self.set_time_preset(**kw))
            btn.pack(side="left", padx=2, pady=2, fill="x", expand=True)
            
        self.info_frame = ttk.LabelFrame(root, text="Значения под курсором", style='Black.TLabelframe')
        self.info_frame.pack(fill="x", padx=10, pady=5)
        
        self.plot_frame = ttk.Frame(root)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=(5,10))
        
        self.fig = None
        self.canvas = None
        self.axes = [] # Будет хранить все оси Y
        self.lines = []
        
        self.init_plot()
        
    def init_plot(self):
        if self.canvas:
            for widget in self.plot_frame.winfo_children(): widget.destroy()
        
        self.fig, self.ax1 = plt.subplots(figsize=(12, 5), facecolor='black') # figsize можно будет настраивать
        self.ax1.set_facecolor('black')
        self.ax1.grid(color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
        
        self.ax1.tick_params(axis='x', colors='white')
        self.ax1.tick_params(axis='y', colors='white') # Начальные для ax1
        self.ax1.spines['bottom'].set_color('white')
        self.ax1.spines['top'].set_color('white')
        self.ax1.spines['left'].set_color('white')
        self.ax1.spines['right'].set_color('white') # Для первой оси правую можно тоже белой
        
        self.axes = [self.ax1]
        self.lines = []
        self.v_line = None
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if not file_path: return
        try:
            self.df = pd.read_excel(file_path)
            self.select_columns()
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", f"Ошибка при загрузке файла: {str(e)}")
    
    def select_columns(self):
        # ... (код select_columns остается таким же, как в предыдущей версии)
        select_window = tk.Toplevel(self.root)
        select_window.title("Выбор столбцов для отображения")
        select_window.geometry("450x550")

        main_frame = ttk.Frame(select_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        datetime_frame = ttk.LabelFrame(main_frame, text="Выберите столбец с датой и временем:")
        datetime_frame.pack(fill="x", padx=5, pady=5)

        datetime_var = tk.StringVar()
        datetime_combo = ttk.Combobox(datetime_frame, textvariable=datetime_var, values=list(self.df.columns), state="readonly")
        datetime_combo.pack(pady=5, padx=10, fill="x")

        for col in self.df.columns:
            if any(kw in col.lower() for kw in ['date', 'time', 'datetime', 'дата', 'время']):
                datetime_combo.set(col)
                break
        
        params_label_frame = ttk.LabelFrame(main_frame, text="Выберите параметры для отображения:")
        params_label_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(params_label_frame)
        scrollbar = ttk.Scrollbar(params_label_frame, orient="vertical", command=canvas.yview)
        param_scrollable_frame = ttk.Frame(canvas)
        
        param_scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=param_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        param_vars = {}
        param_colors_vars = {} 
        
        available_colors = self.colors + ['black', 'gray', 'silver', 'maroon', 'olive', 'navy', 'teal', 'purple']

        for i, col in enumerate(self.df.columns):
            if col == datetime_var.get(): continue

            row_frame = ttk.Frame(param_scrollable_frame)
            row_frame.pack(fill="x", pady=2, padx=5)
            
            var = tk.BooleanVar(value=False)
            param_vars[col] = var
            
            cb = ttk.Checkbutton(row_frame, text=col, variable=var, width=25)
            cb.pack(side="left", padx=(0, 5))
            
            color_var = tk.StringVar(value=self.colors[i % len(self.colors)])
            param_colors_vars[col] = color_var
            
            color_combo = ttk.Combobox(row_frame, textvariable=color_var, values=available_colors, width=10, state="readonly")
            color_combo.pack(side="left", padx=(10,0))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            button_frame, text="Применить", 
            command=lambda: self.apply_selection(datetime_var.get(), param_vars, param_colors_vars, select_window)
        ).pack(pady=5)
        
        canvas.bind_all("<MouseWheel>", lambda event, c=canvas: c.yview_scroll(int(-1*(event.delta/120)), "units"))
        select_window.bind("<Destroy>", lambda event: self.root.unbind_all("<MouseWheel>"))

    def apply_selection(self, datetime_column, param_vars, param_colors_vars, window):
        # ... (код apply_selection остается таким же)
        self.datetime_column = datetime_column
        if not self.datetime_column:
            messagebox.showerror("Ошибка", "Не выбран столбец с датой и временем.")
            return

        try:
            self.df[self.datetime_column] = pd.to_datetime(self.df[self.datetime_column])
        except Exception as e:
            messagebox.showerror("Ошибка преобразования", f"Ошибка при преобразовании столбца даты/времени: {str(e)}")
            return
        
        self.params = []
        self.param_colors = {}
        
        for col, var in param_vars.items():
            if var.get():
                self.params.append(col)
                self.param_colors[col] = param_colors_vars[col].get()
        
        if not self.params:
            messagebox.showwarning("Предупреждение", "Не выбрано ни одного параметра для отображения")
            return
        
        window.destroy()
        
        min_date = self.df[self.datetime_column].min()
        max_date = self.df[self.datetime_column].max()
        
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, min_date.strftime("%Y-%m-%d %H:%M:%S"))
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, max_date.strftime("%Y-%m-%d %H:%M:%S"))
        
        self.update_plot()
        
    def update_plot(self):
        if self.df is None or not self.params:
            self.init_plot()
            return
            
        if self.fig and self._motion_notify_cid:
            try: self.fig.canvas.mpl_disconnect(self._motion_notify_cid)
            except Exception: pass
        self._motion_notify_cid = None
        self.v_line = None

        for widget in self.plot_frame.winfo_children(): widget.destroy()
        for widget in self.info_frame.winfo_children(): widget.destroy()
        self.param_value_labels.clear()
        
        # Создаем новый график
        self.fig, self.ax1 = plt.subplots(facecolor='black') # figsize теперь не здесь, а в subplots_adjust
        self.ax1.set_facecolor('black')
        self.axes = [self.ax1] # Начинаем с ax1
        self.lines = []
        
        # Настройка основной оси ax1
        self.ax1.tick_params(axis='x', colors='white', labelsize=8)
        self.ax1.grid(color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
        self.ax1.spines['bottom'].set_color('white')
        self.ax1.spines['top'].set_color('black') # Сделаем верхнюю рамку основной оси черной
        self.ax1.spines['right'].set_color('black')# И правую тоже, если она не будет использоваться параметром

        try:
            start_date = pd.to_datetime(self.start_date_entry.get())
            end_date = pd.to_datetime(self.end_date_entry.get())
            mask = (self.df[self.datetime_column] >= start_date) & (self.df[self.datetime_column] <= end_date)
            filtered_df = self.df[mask].copy()
            
            if filtered_df.empty:
                messagebox.showwarning("Предупреждение", "Нет данных в выбранном диапазоне.")
                self.init_plot()
                return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при анализе диапазона дат: {str(e)}")
            self.init_plot()
            return
        
        # Базовый отступ для осей Y справа
        base_right_offset = 0.90 # Начнем с 90% ширины, остальное для осей
        num_params = len(self.params)
        # Уменьшаем правый отступ, если много параметров
        # Это значение нужно будет подбирать экспериментально
        # Чем больше параметров, тем меньше должен быть base_right_offset
        # (т.е. больше места справа выделяется под оси)
        if num_params > 1:
            # Примерная логика: каждый доп. параметр "съедает" ~3-5% ширины
            # Это очень грубо, и зависит от шрифтов, длины меток и т.д.
            # Уменьшаем отступ справа, чтобы дать место осям.
            # Чем больше параметров, тем больше места нужно справа.
            # plt.subplots_adjust требует значения от 0 до 1 для right.
            # Если right = 0.9, то 10% справа для осей.
            # Если right = 0.7, то 30% справа для осей.
            # Попробуем уменьшать right_margin_factor с ростом числа осей
            right_margin_factor = max(0.60, 0.95 - (num_params -1) * 0.05)
            # self.fig.subplots_adjust(right=right_margin_factor) # Применим позже, после создания всех осей

        # Отображаем каждый параметр
        for i, param in enumerate(self.params):
            param_color = self.param_colors.get(param, 'white')
            
            current_ax = None
            if i == 0: # Первый параметр использует self.ax1
                current_ax = self.ax1
                current_ax.set_ylabel(param, color=param_color, fontsize=9)
                current_ax.tick_params(axis='y', colors=param_color, labelsize=8)
                current_ax.spines['left'].set_color(param_color)
                # Если только один параметр, правую рамку ax1 можно сделать невидимой
                if len(self.params) == 1:
                    current_ax.spines['right'].set_visible(False)

            else: # Последующие параметры создают новые оси Y
                current_ax = self.ax1.twinx()
                self.axes.append(current_ax) # Добавляем новую ось в список
                
                current_ax.set_ylabel(param, color=param_color, fontsize=9)
                current_ax.tick_params(axis='y', colors=param_color, labelsize=8)
                
                # Позиционирование правой оси Y
                # Отступ для i-й дополнительной оси (i начинается с 1 для twinx)
                # Уменьшаем множитель для более плотного размещения
                offset = (i-1) * 45  # (i-1) потому что i=0 это ax1, i=1 это первый twinx
                current_ax.spines['right'].set_position(('outward', offset))
                current_ax.spines['right'].set_color(param_color)
                current_ax.spines['left'].set_visible(False) # Скрываем левую рамку для twinx осей
                current_ax.spines['top'].set_visible(False)  # И верхнюю
                current_ax.spines['bottom'].set_visible(False)# И нижнюю

                # Для очень большого количества осей можно попробовать скрыть сами метки тиков, оставив только ylabel
                # if i > 3: # Например, для 5-й и далее оси
                #    current_ax.set_yticklabels([])
            
            line, = current_ax.plot(filtered_df[self.datetime_column], filtered_df[param], 
                                  color=param_color, linewidth=1.5, label=param if i==0 else "_nolegend_") # Легенда только для первой оси
            self.lines.append(line) # Все линии добавляем в общий список для трекера
            
            # Инфо-панель
            info_item_frame = ttk.Frame(self.info_frame, style='Black.TFrame')
            info_item_frame.pack(side="left", padx=10, pady=2, fill="x")
            param_name_label = ttk.Label(info_item_frame, text=f"{param}:", foreground=param_color, background='black', style='Black.TLabel')
            param_name_label.pack(side="left")
            value_label = ttk.Label(info_item_frame, text="N/A", width=10, background='black', foreground='white', style='Black.TLabel', anchor="w")
            value_label.pack(side="left", padx=5)
            self.param_value_labels[param] = value_label
        
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S\n%d.%m.%y'))
        plt.setp(self.ax1.get_xticklabels(), rotation=0, ha="center")
        
        self.ax1.set_title("Мультипараметрический график", color='white', fontsize=10)
        
        # Легенда. Если много осей, легенда может быть не так важна, т.к. есть ylabel.
        # Можно сделать ее опциональной или разместить по-другому.
        # Пока оставим, но только для параметров на первой оси (если их несколько на ней будет).
        # В нашем случае label добавляется только для первой линии.
        # Если нужно легенду для всех, то надо добавлять label для всех линий и self.fig.legend()
        handles, labels = [], []
        for i, line in enumerate(self.lines):
             # Создаем псевдо-линию для легенды, чтобы цвет соответствовал
            param_name = self.params[i]
            param_color = self.param_colors.get(param_name, 'white')
            # Добавляем в легенду только если это первый параметр или если мы хотим видеть все
            # В данном случае, мы хотим видеть все, т.к. линии на разных шкалах.
            # Но matplotlib.pyplot.legend() привязывается к оси.
            # Лучше использовать fig.legend() если оси разные.
            # Или, как сделано, label только у первой линии и легенда на ax1.
            # Если хотим легенду для всех, то нужно дать label всем линиям
            # и потом собрать их:
            # for ax_ in self.axes:
            #    h, l = ax_.get_legend_handles_labels()
            #    handles.extend(h)
            #    labels.extend(l)
            # if handles:
            #    self.fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.05, 0.95), 
            #                    fontsize='small', facecolor='#333333', edgecolor='white', labelcolor='white')

        # Пока оставим простую легенду на ax1 (если первая линия имеет label)
        if self.ax1.get_legend_handles_labels()[0]:
             self.ax1.legend(loc='upper left', fontsize='small', facecolor='#333333', edgecolor='white', labelcolor='white')


        # Важно: subplots_adjust вызывается ПОСЛЕ создания всех осей twinx.
        # Значение right должно быть таким, чтобы все метки осей поместились.
        # Это самый сложный момент для автоматизации.
        # Увеличиваем отступ слева для ylabel основной оси,
        # и регулируем отступ справа в зависимости от количества доп. осей
        num_extra_axes = len(self.axes) - 1
        right_margin = 0.95 - num_extra_axes * 0.06 # Каждый доп. параметр "требует" ~6% справа
        right_margin = max(0.6, right_margin) # Не менее 60% для графика

        # Также немного увеличим левый отступ, если есть ylabel
        left_margin = 0.08
        if self.ax1.get_ylabel():
            left_margin = 0.10 # или больше, если метки длинные

        try:
            self.fig.subplots_adjust(left=left_margin, right=right_margin, top=0.92, bottom=0.15)
        except ValueError as ve:
            print(f"Ошибка при subplots_adjust: {ve}. Используются значения по умолчанию.")
            # В случае ошибки можно просто не вызывать subplots_adjust или использовать try-except с tight_layout
            # self.fig.tight_layout(pad=0.5) # tight_layout может лучше справиться, но тоже не всегда идеально

        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        self._motion_notify_cid = self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('figure_leave_event', self.on_mouse_leave)

    def on_mouse_move(self, event):
        if not event.inaxes or not self.lines:
            if self.v_line:
                self.v_line.set_visible(False)
                if self.canvas: self.canvas.draw_idle()
            return

        x_cursor_val = event.xdata 

        if self.v_line is None:
            self.v_line = self.ax1.axvline(x_cursor_val, color='xkcd:light grey', linestyle='--', lw=0.8, zorder=3)
        else:
            # Для Line2D, set_xdata ожидает последовательность. 
            # Для вертикальной линии, обе x-координаты должны быть одинаковы.
            self.v_line.set_xdata([x_cursor_val, x_cursor_val]) 
            self.v_line.set_visible(True)

        # ... остальная часть функции ...
        any_value_updated = False
        for i, line_obj in enumerate(self.lines): # Переименовал line в line_obj для ясности
            param_name = self.params[i]
            
            x_data_plot = line_obj.get_xdata() 
            y_data_plot = line_obj.get_y_data() 

            if len(x_data_plot) == 0:
                if param_name in self.param_value_labels:
                    self.param_value_labels[param_name].config(text="N/A")
                continue
            
            idx = np.searchsorted(x_data_plot, x_cursor_val)
            
            actual_idx = -1
            if idx == 0:
                actual_idx = 0
            elif idx == len(x_data_plot):
                actual_idx = len(x_data_plot) - 1
            else:
                if abs(x_data_plot[idx-1] - x_cursor_val) < abs(x_data_plot[idx] - x_cursor_val):
                    actual_idx = idx - 1
                else:
                    actual_idx = idx
            
            if actual_idx != -1:
                try:
                    value_at_cursor = y_data_plot[actual_idx]
                    if param_name in self.param_value_labels:
                        self.param_value_labels[param_name].config(text=f"{value_at_cursor:.3f}")
                        any_value_updated = True
                except (IndexError, TypeError, ValueError) as e:
                    if param_name in self.param_value_labels:
                         self.param_value_labels[param_name].config(text="Err")
            else: 
                if param_name in self.param_value_labels:
                    self.param_value_labels[param_name].config(text="N/A")


        if any_value_updated or (self.v_line and self.v_line.get_visible()):
            if self.canvas: self.canvas.draw_idle()

    def on_mouse_leave(self, event):
        # ... (код on_mouse_leave остается таким же)
        if self.v_line:
            self.v_line.set_visible(False)
        for param_name in self.param_value_labels:
            self.param_value_labels[param_name].config(text="N/A")
        if self.canvas:
            self.canvas.draw_idle()
            
    def update_time_range(self): self.update_plot()
    
    def reset_time_range(self):
        # ... (код reset_time_range остается таким же)
        if self.df is not None and self.datetime_column is not None:
            min_date = self.df[self.datetime_column].min()
            max_date = self.df[self.datetime_column].max()
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, min_date.strftime("%Y-%m-%d %H:%M:%S"))
            self.end_date_entry.delete(0, tk.END)
            self.end_date_entry.insert(0, max_date.strftime("%Y-%m-%d %H:%M:%S"))
            self.update_plot()

    def set_time_preset(self, hours=None, days=None):
        # ... (код set_time_preset остается таким же)
        if self.df is None or self.datetime_column is None: return
        max_date = self.df[self.datetime_column].max()
        if hours: min_date = max_date - timedelta(hours=hours)
        elif days: min_date = max_date - timedelta(days=days)
        else: return
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, min_date.strftime("%Y-%m-%d %H:%M:%S"))
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, max_date.strftime("%Y-%m-%d %H:%M:%S"))
        self.update_plot()

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiParameterPlotApp(root)
    root.mainloop()