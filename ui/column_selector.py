# -*- coding: utf-8 -*-
"""
Селектор колонок для Multi-Parameter Data Analyzer v2.0
=======================================================

Новый интерфейс выбора пар "время + параметр" с двумя режимами работы.

Связанные файлы:
- main_window.py: Вызывает данный диалог для выбора колонок
- ../core/timeline_manager.py: Автоматическое определение временных колонок
- ../utils/file_utils.py: Валидация колонок времени
- ../config/settings.py: Сохранение пользовательских предпочтений

Режимы работы:
1. Простой режим: Один общий столбец времени (совместимость с v1.0)
2. Продвинутый режим: Парная привязка время + параметр (новинка v2.0)

Функции v2.0:
- Автоматическое определение пар по именам колонок
- Ручная настройка связей между колонками
- Предварительный просмотр данных
- Валидация выбранных пар

Автор: j15
Версия: 2.0.0-dev
GitHub: https://github.com/jackal100500/CSV_software
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from typing import List, Tuple, Optional, Dict


class ColumnSelector:
    """
    Диалог выбора пар колонок время + параметр.
    
    Связанные компоненты:
    - timeline_manager: Автоматическое определение пар (core/timeline_manager.py)
    - main_window: Родительское окно (ui/main_window.py)
    """
    
    def __init__(self, parent, dataframe: pd.DataFrame, timeline_manager):
        """
        Инициализация диалога выбора колонок
        
        Args:
            parent: Родительское окно (main_window.py)
            dataframe: Загруженные данные
            timeline_manager: Менеджер временных шкал (core/timeline_manager.py)
        """
        self.parent = parent
        self.df = dataframe
        self.timeline_manager = timeline_manager
        self.result = None  # Результат выбора: [(time_col, param_col), ...]
        
        # Создание диалогового окна
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Выбор пар колонок - Multi-Parameter Analyzer v2.0")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрирование окна
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"800x600+{x}+{y}")
        
        # Данные для работы
        self.column_names = list(self.df.columns)
        self.auto_detected_pairs = []
        self.manual_pairs = []
        self.selected_mode = tk.StringVar(value="simple")
        
        # Инициализация интерфейса
        self.setup_ui()
        self.auto_detect_pairs()
        
        print("ColumnSelector v2.0 инициализирован")
        print(f"Связанные модули: timeline_manager ({type(self.timeline_manager).__name__})")
    
    def setup_ui(self):
        """
        Создание интерфейса диалога
        
        Связанные методы:
        - auto_detect_pairs(): Использует timeline_manager.auto_detect_pairs()
        - validate_pairs(): Использует timeline_manager.validate_time_column()
        """
        # Главный фрейм
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Выбор пар 'Время + Параметр' для универсальной временной шкалы",
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Выбор режима работы
        mode_frame = ttk.LabelFrame(main_frame, text="Режим работы")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="Простой (один общий столбец времени)", 
                       variable=self.selected_mode, value="simple",
                       command=self.on_mode_change).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(mode_frame, text="Продвинутый (пары время + параметр)", 
                       variable=self.selected_mode, value="advanced",
                       command=self.on_mode_change).pack(anchor=tk.W, padx=5, pady=2)
        
        # Область содержимого (зависит от режима)
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Автоопределение", 
                  command=self.auto_detect_pairs).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Предварительный просмотр", 
                  command=self.preview_selection).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="ОК", 
                  command=self.accept_selection).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(button_frame, text="Отмена", 
                  command=self.cancel_selection).pack(side=tk.RIGHT)
        
        # Инициализация простого режима
        self.setup_simple_mode()
    
    def setup_simple_mode(self):
        """
        Настройка простого режима (совместимость с v1.0)
        
        Связанные функции:
        - timeline_manager.detect_time_columns(): Поиск временных колонок
        """
        # Очистка области содержимого
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Фрейм выбора времени
        time_frame = ttk.LabelFrame(self.content_frame, text="Столбец времени")
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.time_column_var = tk.StringVar()
        time_combo = ttk.Combobox(time_frame, textvariable=self.time_column_var,
                                 values=self.column_names, state="readonly")
        time_combo.pack(fill=tk.X, padx=5, pady=5)
        
        # Автоматическое определение времени
        time_columns = self.timeline_manager.detect_time_columns(self.df)
        if time_columns:
            self.time_column_var.set(time_columns[0])
        
        # Фрейм выбора параметров
        param_frame = ttk.LabelFrame(self.content_frame, text="Параметры для отображения")
        param_frame.pack(fill=tk.BOTH, expand=True)
        
        # Список параметров с чекбоксами
        canvas = tk.Canvas(param_frame)
        scrollbar = ttk.Scrollbar(param_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Создание чекбоксов для параметров
        self.param_vars = {}
        for col in self.column_names:
            if col not in time_columns:  # Исключаем временные колонки
                var = tk.BooleanVar()
                self.param_vars[col] = var
                ttk.Checkbutton(scrollable_frame, text=col, variable=var).pack(anchor=tk.W, padx=5, pady=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        print("Настроен простой режим выбора колонок")
    
    def setup_advanced_mode(self):
        """
        Настройка продвинутого режима (новинка v2.0)
        
        Связанные функции:
        - timeline_manager.auto_detect_pairs(): Автоматическое определение пар
        """
        # Очистка области содержимого
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Информационная панель
        info_frame = ttk.Frame(self.content_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_label = ttk.Label(info_frame, 
                              text="В продвинутом режиме каждый параметр может иметь свой столбец времени.\n"
                                   "Это позволяет корректно обрабатывать данные с разными временными метками.",
                              foreground="blue")
        info_label.pack()
        
        # Автоматически обнаруженные пары
        auto_frame = ttk.LabelFrame(self.content_frame, text="Автоматически обнаруженные пары")
        auto_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.auto_tree = ttk.Treeview(auto_frame, columns=("time", "param"), show="headings", height=6)
        self.auto_tree.heading("time", text="Столбец времени")
        self.auto_tree.heading("param", text="Параметр")
        self.auto_tree.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопки управления автопарами
        auto_button_frame = ttk.Frame(auto_frame)
        auto_button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(auto_button_frame, text="Выбрать все", 
                  command=self.select_all_auto).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(auto_button_frame, text="Снять выделение", 
                  command=self.deselect_all_auto).pack(side=tk.LEFT)
        
        # Ручное создание пар
        manual_frame = ttk.LabelFrame(self.content_frame, text="Ручное создание пар")
        manual_frame.pack(fill=tk.BOTH, expand=True)
        
        # Элементы добавления пары
        add_frame = ttk.Frame(manual_frame)
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Время:").pack(side=tk.LEFT)
        self.manual_time_var = tk.StringVar()
        ttk.Combobox(add_frame, textvariable=self.manual_time_var,
                    values=self.column_names, width=20).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(add_frame, text="Параметр:").pack(side=tk.LEFT)
        self.manual_param_var = tk.StringVar()
        ttk.Combobox(add_frame, textvariable=self.manual_param_var,
                    values=self.column_names, width=20).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(add_frame, text="Добавить пару", 
                  command=self.add_manual_pair).pack(side=tk.LEFT, padx=(5, 0))
        
        # Список ручных пар
        self.manual_tree = ttk.Treeview(manual_frame, columns=("time", "param"), show="headings", height=8)
        self.manual_tree.heading("time", text="Столбец времени")
        self.manual_tree.heading("param", text="Параметр")
        self.manual_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 0))
        
        # Кнопки управления ручными парами
        manual_button_frame = ttk.Frame(manual_frame)
        manual_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(manual_button_frame, text="Удалить выбранную", 
                  command=self.remove_manual_pair).pack(side=tk.LEFT)
        
        print("Настроен продвинутый режим выбора пар")
    
    def on_mode_change(self):
        """
        Обработка изменения режима работы
        
        Связанные методы:
        - setup_simple_mode(): Переключение в простой режим
        - setup_advanced_mode(): Переключение в продвинутый режим
        """
        mode = self.selected_mode.get()
        if mode == "simple":
            self.setup_simple_mode()
        else:
            self.setup_advanced_mode()
        
        print(f"Переключен режим: {mode}")
    
    def auto_detect_pairs(self):
        """
        Автоматическое определение пар время + параметр
        
        Использует:
        - timeline_manager.auto_detect_pairs(): Основной алгоритм определения
        """
        try:
            # Получение автоматически определенных пар
            self.auto_detected_pairs = self.timeline_manager.auto_detect_pairs(self.df)
            
            if self.selected_mode.get() == "advanced":
                # Обновление дерева автоматических пар
                self.auto_tree.delete(*self.auto_tree.get_children())
                for time_col, param_col in self.auto_detected_pairs:
                    self.auto_tree.insert("", "end", values=(time_col, param_col))
            
            messagebox.showinfo("Автоопределение", 
                              f"Обнаружено {len(self.auto_detected_pairs)} пар колонок")
            
            print(f"Автоматически определено пар: {len(self.auto_detected_pairs)}")
            for time_col, param_col in self.auto_detected_pairs:
                print(f"  {time_col} -> {param_col}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка автоопределения:\n{str(e)}")
    
    def select_all_auto(self):
        """Выбор всех автоматически определенных пар"""
        for item in self.auto_tree.get_children():
            self.auto_tree.selection_add(item)
    
    def deselect_all_auto(self):
        """Снятие выделения с автоматических пар"""
        self.auto_tree.selection_remove(self.auto_tree.get_children())
    
    def add_manual_pair(self):
        """
        Добавление ручной пары время + параметр
        
        Использует:
        - timeline_manager.validate_time_column(): Проверка корректности времени
        """
        time_col = self.manual_time_var.get()
        param_col = self.manual_param_var.get()
        
        if not time_col or not param_col:
            messagebox.showwarning("Предупреждение", "Выберите оба столбца")
            return
        
        if time_col == param_col:
            messagebox.showwarning("Предупреждение", "Столбцы должны быть разными")
            return
        
        # Проверка, что пара не существует
        if (time_col, param_col) in self.manual_pairs:
            messagebox.showwarning("Предупреждение", "Такая пара уже существует")
            return
        
        try:
            # Валидация временного столбца через timeline_manager
            if not self.timeline_manager.validate_time_column(self.df, time_col):
                messagebox.showwarning("Предупреждение", 
                                     f"Столбец '{time_col}' не содержит корректных временных данных")
                return
            
            # Добавление пары
            self.manual_pairs.append((time_col, param_col))
            self.manual_tree.insert("", "end", values=(time_col, param_col))
            
            # Очистка полей
            self.manual_time_var.set("")
            self.manual_param_var.set("")
            
            print(f"Добавлена ручная пара: {time_col} -> {param_col}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка добавления пары:\n{str(e)}")
    
    def remove_manual_pair(self):
        """Удаление выбранной ручной пары"""
        selected = self.manual_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пару для удаления")
            return
        
        for item in selected:
            values = self.manual_tree.item(item, 'values')
            pair = (values[0], values[1])
            if pair in self.manual_pairs:
                self.manual_pairs.remove(pair)
            self.manual_tree.delete(item)
    
    def preview_selection(self):
        """
        Предварительный просмотр выбранных данных
        
        Связанные компоненты:
        - timeline_manager: Создание предварительной временной шкалы
        """
        pairs = self.get_selected_pairs()
        if not pairs:
            messagebox.showwarning("Предупреждение", "Не выбрано ни одной пары")
            return
        
        # Создание окна предварительного просмотра
        preview_window = tk.Toplevel(self.dialog)
        preview_window.title("Предварительный просмотр данных")
        preview_window.geometry("600x400")
        
        # Текстовая область с информацией
        text_frame = ttk.Frame(preview_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Формирование информации о данных
        info_text = f"Выбрано пар: {len(pairs)}\n\n"
        
        for i, (time_col, param_col) in enumerate(pairs, 1):
            info_text += f"{i}. Время: '{time_col}' -> Параметр: '{param_col}'\n"
            
            # Анализ данных в колонках
            time_data = self.df[time_col].dropna()
            param_data = self.df[param_col].dropna()
            
            info_text += f"   Временные точки: {len(time_data)}\n"
            info_text += f"   Значения параметра: {len(param_data)}\n"
            
            if len(time_data) > 0:
                info_text += f"   Диапазон времени: {time_data.min()} - {time_data.max()}\n"
            if len(param_data) > 0:
                info_text += f"   Диапазон значений: {param_data.min():.4f} - {param_data.max():.4f}\n"
            
            info_text += "\n"
        
        text_widget.insert(tk.END, info_text)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def get_selected_pairs(self) -> List[Tuple[str, str]]:
        """
        Получение списка выбранных пар в зависимости от режима
        
        Returns:
            List[Tuple[str, str]]: Список пар (time_column, param_column)
        """
        if self.selected_mode.get() == "simple":
            # Простой режим: один столбец времени + выбранные параметры
            time_col = self.time_column_var.get()
            if not time_col:
                return []
            
            pairs = []
            for param_col, var in self.param_vars.items():
                if var.get():
                    pairs.append((time_col, param_col))
            
            return pairs
        
        else:
            # Продвинутый режим: автоматические + ручные пары
            pairs = []
            
            # Добавление выбранных автоматических пар
            selected_auto = self.auto_tree.selection()
            for item in selected_auto:
                values = self.auto_tree.item(item, 'values')
                pairs.append((values[0], values[1]))
            
            # Добавление всех ручных пар
            pairs.extend(self.manual_pairs)
            
            return pairs
    
    def validate_selection(self, pairs: List[Tuple[str, str]]) -> bool:
        """
        Валидация выбранных пар
        
        Args:
            pairs: Список пар для проверки
            
        Returns:
            bool: True если все пары корректны
            
        Использует:
        - timeline_manager.validate_time_column(): Проверка временных колонок
        """
        if not pairs:
            messagebox.showwarning("Предупреждение", "Не выбрано ни одной пары")
            return False
        
        # Проверка каждой пары
        for time_col, param_col in pairs:
            # Проверка существования колонок
            if time_col not in self.df.columns:
                messagebox.showerror("Ошибка", f"Столбец времени '{time_col}' не существует")
                return False
            
            if param_col not in self.df.columns:
                messagebox.showerror("Ошибка", f"Столбец параметра '{param_col}' не существует")
                return False
            
            # Валидация временной колонки
            try:
                if not self.timeline_manager.validate_time_column(self.df, time_col):
                    messagebox.showerror("Ошибка", 
                                       f"Столбец '{time_col}' не содержит корректных временных данных")
                    return False
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка валидации '{time_col}':\n{str(e)}")
                return False
        
        return True
    
    def accept_selection(self):
        """
        Принятие выбора пользователя
        
        Связанные действия:
        - validate_selection(): Проверка корректности выбора
        - Возврат в main_window.py через self.result
        """
        pairs = self.get_selected_pairs()
        
        if self.validate_selection(pairs):
            self.result = pairs
            print(f"Выбор принят: {len(pairs)} пар")
            for time_col, param_col in pairs:
                print(f"  {time_col} -> {param_col}")
            self.dialog.destroy()
    
    def cancel_selection(self):
        """Отмена выбора"""
        self.result = None
        print("Выбор отменен")
        self.dialog.destroy()


# Связанные файлы для импорта в других модулях:
# from ui.column_selector import ColumnSelector
